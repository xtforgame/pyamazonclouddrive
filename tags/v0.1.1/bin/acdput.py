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

import os, sys, getpass
from optparse import OptionParser

try:
  import pyacd
except ImportError:
  pyacd_lib_dir=os.path.dirname(__file__)+os.sep+".."
  if os.path.exists(pyacd_lib_dir) and os.path.isdir(pyacd_lib_dir):
    sys.path.insert(0, pyacd_lib_dir)
  import pyacd

parser=OptionParser(
  epilog="This command uploads file(s) to your Amazon Cloud Drive. "+
         "If the same named file exists, uploading file is renamed "+
         "automatically. (e.g. 'test.mp3' -> 'test (2).mp3')",
  usage="%prog [Options] file1 file2 - ...('-' means STDIN)",
  version=pyacd.__version__
)

parser.add_option(
  "-e",dest="email",action="store",default=None,
  help="email address for Amazon.com"
)
parser.add_option(
  "-p",dest="password",action="store",default=None,
  help="password for Amazon.com"
)
parser.add_option(
  "-s",dest="session",action="store",default=None,metavar="FILE",
  help="save/load login session to/from FILE"
)
parser.add_option(
  "-d",dest="path",action="store",default="/",
  help="upload path [default: %default]"
)
parser.add_option(
  "-v",dest="verbose",action="store_true",default=False,
  help="show verbose message"
)

def main():
  opts,args=parser.parse_args(sys.argv[1:])

  args=list(set(args))
  if "-" in args:
    args.remove("-")
    args += [x.strip() for x in sys.stdin.readlines()]

  if 0==len(args):
    sys.stderr.write("No file selected.\n")
    parser.print_help()
    sys.exit(2)
  else:
    for file in args:
      if not os.path.exists(file):
        sys.stderr.write('Not found "%s"\n'%file)
        sys.exit(2)
      elif os.path.isdir(file):
        sys.stderr.write('"%s" is not file\n'%file)
        sys.exit(2)

  # Check options of authentication
  if opts.email:
    if not opts.password:
      opts.password = getpass.getpass()

  if (opts.email and opts.password) or opts.session:
    pass # OK case
  else:
    print >>sys.stderr, "Either email and password or session is mondatory."
    sys.exit(2)

  session = None; s = None
  if opts.session:
    if opts.verbose:
      print >>sys.stderr, "Loading previous session...",
    try:
      s=pyacd.Session.load_from_file(opts.session)
      if opts.verbose:
        print >>sys.stderr, "Done."
    except:
      s=pyacd.Session()
      if opts.verbose:
        print >>sys.stderr, "Failed."

  if opts.verbose:
    print >>sys.stderr, "Logging into Amazon.com...",
  try:
    if opts.email and opts.password and s:
      session=pyacd.login(opts.email,opts.password,session=s)
    elif opts.email and opts.password:
      session=pyacd.login(opts.email,opts.password)
    else:
      session=pyacd.login(session=s)
    if opts.verbose:
      print >>sys.stderr, "Done."
  except:
    if opts.verbose:
      print >>sys.stderr, "Failed."
      sys.exit(2)

  # Check login status
  if not session:
    sys.stderr.write("Unexpected error occured.\n")
    sys.exit(2)
  elif not session.is_logged_in():
    sys.stderr.write("Login failed.\n%s\n"%session)
    sys.exit(2)

  # Check destination
  path=opts.path
  if path[0]!='/':path='/'+path
  if path[-1]!='/':path=path+'/'
  try:
    dest = pyacd.api.get_info_by_path(path)
    if dest.Type == pyacd.types.FILE:
      sys.stderr.write('"%s" is file\n'%path)
      sys.exit(2)
  except pyacd.PyAmazonCloudDriveApiException,e:
    sys.stderr.write('"%s"\n'%e.message)
    sys.exit(2)


  for f in args:
    filename = os.path.basename(f)
    fp=open(f,"rb")
    filedata = fp.read()
    fp.close()

    if opts.verbose:
      sys.stderr.write("Uploading %s to %s ... "%(filename,path))

    fileobj = pyacd.api.create_by_path(path,filename)
    upload_url = pyacd.api.get_upload_url_by_id(fileobj.object_id,len(filedata))
    end_point=upload_url.http_request.end_point
    parameters=upload_url.http_request.parameters

    storage_key=upload_url.storage_key
    object_id=upload_url.object_id

    if opts.verbose:
      sys.stderr.write("Sending data... ")
    pyacd.api.upload(end_point,parameters,filename,filedata)

    # completeing file
    if opts.verbose:
      sys.stderr.write("Finishing... ")
    pyacd.api.complete_file_upload_by_id(object_id,storage_key)

    if opts.verbose:
      sys.stderr.write("Done\n")


  if opts.verbose:
    print >>sys.stderr, "Updating current session...",
  try:
    session.save_to_file(opts.session)
    if opts.verbose:
      print >>sys.stderr, "Done."
  except:
    if opts.verbose:
      print >>sys.stderr, "Failed."


if __name__=="__main__":
  main()
