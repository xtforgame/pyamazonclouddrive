#!/usr/bin/env python
#
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
 
import os, sys, time, shutil
import unittest
from cStringIO import StringIO

import pyacd
pyacd.debug_level=2

if len(sys.argv)!=4:
  sys.stderr.write("usage: ./test.py email password acdsession")
  sys.exit(2)

email=sys.argv[1]
password=sys.argv[2]
acdsession=sys.argv[3]

print "**** Here are arguments **********"
print "email:",email
print "password:",password
print "acdsession:",acdsession
print "*"*34
print ""

if os.path.isdir(acdsession):
  print >>sys.stderr, "%s must not be directory!"%acdsession
  sys.exit(2)

class AuthTest(unittest.TestCase):
  def setUp(self):
    pass

  def tearDown(self):
    pass

  def test_1_LoginWithEmailAndPassword(self):
    session=pyacd.login(email,password)
    self.assertTrue(session.is_logged_in(),"not logined %s"%session)
    self.assertNotEqual(session.username,None,"username is None %s"%session)
    self.assertNotEqual(session.customer_id,None,"customer_id is None %s"%session)
    str(session)
    session.save_to_file(acdsession)

  def test_2_LoginWithAcdSession(self):
    session = pyacd.Session.load_from_file(acdsession)
    str(session)
    session = pyacd.login(session=session)
    self.assertTrue(session.is_logged_in(),"not logined %s"%session)
    self.assertNotEqual(session.username,None,"username is None %s"%session)
    self.assertNotEqual(session.customer_id,None,"customer_id is None %s"%session)
    str(session)
    session.save_to_file(acdsession)

  def test_3_LoginWithNoneEmail(self):
    try:
      session=pyacd.login(None,password)
    except TypeError,e:
      pass

  def test_4_LoginWithNonePassword(self):
    try:
      session=pyacd.login(email,None)
    except TypeError,e:
      pass

  def test_5_LoginWithNoneArgs(self):
    try:
      session=pyacd.login(None,None,None)
    except TypeError,e:
      pass


class ApiTest(unittest.TestCase):
  def setUp(self):
    session = pyacd.Session.load_from_file(acdsession)
    session = pyacd.login(session=session)

  def tearDown(self):
    pass

  def test_1_UserStorage(self):
    user_storage = pyacd.api.get_user_storage()
    self.assertEqual(user_storage.total_space,user_storage.
        used_space+user_storage.free_space,"total /= used+free %s"%user_storage)
    print >>sys.stderr, user_storage,

  def test_2_SubscriptionProblem(self):
    subscription_problem=pyacd.api.get_subscription_problem()
    print >>sys.stderr, subscription_problem,

  def test_3_InfoByPath_ById(self):
    info_by_path=pyacd.api.get_info_by_path("/")
    print >>sys.stderr, info_by_path,
    info_by_id=pyacd.api.get_info_by_id(info_by_path.object_id)
    print >>sys.stderr, info_by_path,
    self.assertEqual(info_by_path.name,info_by_id.name,"different from byPath(%s) and byId(%s)"%
                    (info_by_path,info_by_id))

  def test_4_ListById(self):
    info=pyacd.api.get_info_by_path("/")
    print >>sys.stderr, pyacd.api.list_by_id(info.object_id),

  def test_5_Folder_Create_Rename_Copy_Recycle_Remove(self):
    root=pyacd.api.get_info_by_path("/")
    folder_created="created_%d"%int(time.time())
    folder_renamed=folder_created.replace("created","renamed")

    # create folder as folder named "created_nnn..."
    folder1=pyacd.api.create_by_id(root.object_id,folder_created)
    # copy folder1 as folder2 into folder1
    pyacd.api.copy_bulk_by_id(root.object_id,[folder1.object_id,])
    folder2 = pyacd.api.get_info_by_path("/"+folder_created+" (2)")
    # rename folder2 to "renamed_nnn..."
    pyacd.api.move_by_id(folder2.object_id,root.object_id,folder_renamed)
    # move folder2 to folder1
    pyacd.api.move_bulk_by_id(folder1.object_id,[folder2.object_id,])
    # recycle folder1
    pyacd.api.recycle_bulk_by_id([folder1.object_id,])

    #http://code.google.com/p/pyamazonclouddrive/issues/detail?id=6
    #pyacd.api.remove_bulk_by_id([folder1.object_id,])

  def test_6_EmptyRecycleBin(self):
    pyacd.api.empty_recycle_bin()

  def test_7_File_Create_Upload_Download(self):
    filename = "test_%d.txt"%int(time.time())
    filedata = "123451234512345123451234512345123451234512345123451234512345"

    # file1 create
    file1 = pyacd.api.create_by_path("/",filename)

    # get upload_url
    upload_url = pyacd.api.get_upload_url_by_id(file1.object_id,len(filedata))
    storage_key=upload_url.storage_key
    object_id=upload_url.object_id
    end_point=upload_url.http_request.end_point
    parameters=upload_url.http_request.parameters

    # upload file
    pyacd.api.upload(end_point,parameters,filename,filedata)

    # completeing file
    pyacd.api.complete_file_upload_by_id(object_id,storage_key)

    # download file
    download_data=pyacd.api.download_by_id(object_id)
    
    self.assertEqual(filedata,download_data,"different from upload and download")

    # recycle file1 and empty recycle_bin
    pyacd.api.recycle_bulk_by_id([file1.object_id])
    pyacd.api.empty_recycle_bin()

testdir = "testdir_%s"%time.time()
class BasicCommandTest(unittest.TestCase):
  def setUp(self):
    pass

  def tearDown(self):
    pass

  def test_1_acdsession(self):
    print >>sys.stderr,""
    ret = os.system("bin"+os.sep+"acdsession.py --help")
    self.assertEqual(ret,0,"external command failed.")
    ret = os.system("bin"+os.sep+"acdsession.py -v -e %s -p %s -s %s"%(email,password,acdsession))
    self.assertEqual(ret,0,"external command failed.")

  def test_2_acdmkdir(self):
    global testdir
    print >>sys.stderr,""
    ret = os.system("bin"+os.sep+"acdmkdir.py --help")
    self.assertEqual(ret,0,"external command failed.")
    ret = os.system("bin"+os.sep+"acdmkdir.py -v -s %s %s"%(acdsession,testdir))
    self.assertEqual(ret,0,"external command failed.")

  def test_3_acdput(self):
    global testdir
    print >>sys.stderr,""
    ret = os.system("bin"+os.sep+"acdput.py --help")
    self.assertEqual(ret,0,"external command failed.")
    ret = os.system("bin"+os.sep+"acdput.py -v -s %s LICENSE test.py -d /%s"%(acdsession,testdir))
    self.assertEqual(ret,0,"external command failed.")

  def test_4_acdlist(self):
    global testdir
    print >>sys.stderr,""
    ret = os.system("bin"+os.sep+"acdlist.py --help")
    self.assertEqual(ret,0,"external command failed.")
    ret = os.system("bin"+os.sep+"acdlist.py -v -s %s -l %s"%(acdsession,testdir))
    self.assertEqual(ret,0,"external command failed.")

  def test_5_acdcat(self):
    global testdir
    print >>sys.stderr,""
    ret = os.system("bin"+os.sep+"acdcat.py --help")
    self.assertEqual(ret,0,"external command failed.")
    ret = os.system("bin"+os.sep+"acdcat.py -v -s %s /%s/LICENSE"%(acdsession,testdir))
    self.assertEqual(ret,0,"external command failed.")

  def test_6_acdget(self):
    global testdir
    print >>sys.stderr,""
    ret = os.system("bin"+os.sep+"acdget.py --help")
    self.assertEqual(ret,0,"external command failed.")
    os.mkdir(testdir)
    ret = os.system("bin"+os.sep+"acdget.py -v -s %s /%s/LICENSE /%s/test.py -d %s"%(acdsession,testdir,testdir,testdir))
    self.assertEqual(ret,0,"external command failed.")
    local = open("LICENSE","rb").read()
    remote = open(testdir+os.sep+"LICENSE","rb").read()
    self.assertEqual(local,remote,"differece between local file and remote one (%s)"%"LICENSE")
    local = open("test.py","rb").read()
    remote = open(testdir+os.sep+"test.py","rb").read()
    self.assertEqual(local,remote,"differece between local file and remote one (%s)"%"test.py")
    shutil.rmtree(testdir)

  def test_7_acdrecycle(self):
    global testdir
    print >>sys.stderr,""
    ret = os.system("bin"+os.sep+"acdrecycle.py --help")
    self.assertEqual(ret,0,"external command failed.")
    ret = os.system("bin"+os.sep+"acdrecycle.py -v -s %s %s"%(acdsession,testdir))
    self.assertEqual(ret,0,"external command failed.")


def main():
  suites=[]
  
  suites.append(unittest.TestLoader().loadTestsFromTestCase(AuthTest))
  suites.append(unittest.TestLoader().loadTestsFromTestCase(ApiTest))
  suites.append(unittest.TestLoader().loadTestsFromTestCase(BasicCommandTest))

  runner = unittest.TextTestRunner(verbosity=2)

  suite=unittest.TestSuite(suites)
  runner.run(suite)


if __name__=="__main__":
  main()

