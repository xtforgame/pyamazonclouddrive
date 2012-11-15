# Copyright (c) 2011 anatanokeitai.com(sakurai_youhei)
# 
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.

import re, pickle, threading
import urllib, cookielib

import pyacd

def login(email=None,password=None,session=None):
  if session:
    pyacd.session=Session(session)
  elif email is None or password is None:
    raise TypeError("Invalid args, email:%s, password:%s"%(email,password))
  else:
    pyacd.session=Session()
  
  end_point="https://www.amazon.com/clouddrive"
  html=pyacd.do_get(end_point)

  NOT_LOGGED_IN=r"ue_url='\/gp\/feature\.html"
  CONTINUE_REQUIRED=r'<form action="\/clouddrive" id="continueForm"'

  if re.search(NOT_LOGGED_IN,html):
    if not (email and password):
      raise pyacd.PyAmazonCloudDriveError("Both email and password are required.")
    link = re.search(r'"(\/gp\/drive\/files.*?)"',html).groups()[0]
    html=pyacd.do_get("https://www.amazon.com"+link)
    form = re.search(r'<form name="signIn" method="POST" .*?<\/form>',re.sub(r"\n|\r","",html)).group()
    action = re.search('action="(.*?)"',form).groups()[0]
    inputs = [re.search(' name="(.*?)".*? value="(.*?)"',x) for x in re.findall('<input.*?>',form)]
    params = dict([x.groups() for x in inputs if x!=None])
    params["create"]=0
    params["email"]=email
    params["password"]=password
    body=urllib.urlencode(params)
    html=pyacd.do_post(action,body)
    if re.search(NOT_LOGGED_IN,html):
      raise pyacd.PyAmazonCloudDriveError("Login failed.")

  if re.search(CONTINUE_REQUIRED,html):
    form = re.search(CONTINUE_REQUIRED+r".*?<\/form>",re.sub(r"\n|\r","",html)).group()
    action = re.search('action="(.*?)"',form).groups()[0]
    inputs = [re.search(' name="(.*?)".*? value="(.*?)"',x) for x in re.findall('<input.*?>',form)]
    params = dict([x.groups() for x in inputs if x!=None])
    if action[0]=="/":
      action = "https://www.amazon.com"+action
    body=urllib.urlencode(params)
    html=pyacd.do_post(action,body)

  try:
    customer_id=html.split("customerId",1)[1]
    customer_id=customer_id.split(">",1)[0]
    customer_id=re.sub('.*value="','',customer_id)
    customer_id=re.sub('".*','',customer_id)
    pyacd.session.customer_id=customer_id

    username=html.split("customer_greeting",1)[1]
    username=username.split("<",1)[0]
    username=username.split(",")[1][1:]
    username=re.sub(r'\..*','',username)
    pyacd.session.username=username
  except:
    pass

  return pyacd.session



class Session(object):
  def __init__(self,session=None):
    self.username=None
    self.customer_id=None
    pyacd.session=self
    if session:
      self.cookies = session.cookies
      pyacd.rebuild_opener()
    else:
      self.cookies=PicklableCookieJar()
      pyacd.rebuild_opener()
      end_point = "http://www.amazon.com/"
      pyacd.do_get(end_point)

  @classmethod
  def load_from_file(cls,filepath):
    fp=open(filepath,"rb")
    session=pickle.load(fp)
    fp.close()
    return session

  def save_to_file(self,filepath):
    fp=open(filepath,"wb")
    fp.truncate()
    pickle.dump(self,fp)
    fp.close()

  def __repr__(self):
    return '<Session: username: %s, customer_id: %s>' % (self.username, self.customer_id)

  def __str__(self):
    return '<Session: username: %s, customer_id: %s>' % (self.username, self.customer_id)

  def is_logged_in(self):
    return (self.username and self.customer_id)

  def print_debug(self):
    print "*"*20
    for k,v in self.cookies._cookies.items():
      print "%s=%s"%(k,v)


# This workaround is from "http://stackoverflow.com/questions/1023224/how-to-pickle-a-cookiejar".
class PicklableCookieJar(cookielib.CookieJar):
  def __getstate__(self):
    state = self.__dict__.copy()
    del state['_cookies_lock']
    return state

  def __setstate__(self, state):
    self.__dict__ = state
    self._cookies_lock = threading.RLock()

