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
  epilog="This command download file(s) from your Amazon Cloud Drive. "+
         "If the same named file exists, downloading will be cancelled "+
         "automatically. (or use -f option)",
  usage="%prog [Options] file1 file2 - ...('-' means STDIN)",
  version=pyacd.__version__
)

parser.add_option(
  "--domain",dest="domain",action="store",default="www.amazon.com",
  help="domain of Amazon [default: %default]"
)
parser.add_option(
  "-e",dest="email",action="store",default=None,
  help="email address for Amazon"
)
parser.add_option(
  "-p",dest="password",action="store",default=None,
  help="password for Amazon"
)
parser.add_option(
  "-s",dest="session",action="store",default=None,metavar="FILE",
  help="save/load login session to/from FILE"
)
parser.add_option(
  "-d",dest="path",action="store",default="."+os.sep,
  help="download path [default: %default]"
)
parser.add_option(
  "-f",dest="force",action="store_true",default=False,
  help="override local file if it has same name [default: %default]"
)
parser.add_option(
  "-v",dest="verbose",action="store_true",default=False,
  help="show verbose message"
)

def main():
  opts,args=parser.parse_args(sys.argv[1:])
  pyacd.set_amazon_domain(opts.domain)

  args=list(set(args))
  if "-" in args:
    args.remove("-")
    args += [x.strip() for x in sys.stdin.readlines()]

  if 0==len(args):
    sys.stderr.write("No file selected.\n")
    parser.print_help()
    sys.exit(2)
  else:
    pass

  # Check destination
  path=opts.path
  if path[-1]!=os.sep:path=path+os.sep
  if not os.path.exists(path):
    sys.stderr.write('"%s" does not exist\n'%path)
    sys.exit(2)
  elif not os.path.isdir(path):
    sys.stderr.write('"%s" is not file\n'%path)
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
    print >>sys.stderr, "Logging into %s..."%opts.domain,
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


  for f in args:
    if f[0]!='/':f='/'+f
    filename = os.path.basename(f)

    if opts.verbose:
      sys.stderr.write("Downloading %s to %s ... "%(f,path))

    if os.path.exists(path+filename) and not opts.force:
      sys.stderr.write("Aborted. ('%s' exists.)\n"%(path+filename))
      continue

    # get file
    try:
      fileobj = pyacd.api.get_info_by_path(f)
    except pyacd.PyAmazonCloudDriveApiException,e:
      sys.stderr.write("Aborted. ('%s')\n"%e.message)
      continue
    except pyacd.PyAmazonCloudDriveError,e:
      sys.stderr.write("Not found.\n")
      continue

    if fileobj.Type!= pyacd.types.FILE:
      sys.stderr.write("Aborted. ('%s' is not file.)"%f)
      continue

    # download
    data=pyacd.api.download_by_id(fileobj.object_id)
    

    fp=open(path+filename,"wb")
    fp.truncate()
    fp.write(data)
    fp.close()

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
