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
  epilog="This command move file(s) or dir(s) to Recycle of your Amazon Cloud Drive.",
  usage="%prog [Options] path1 path2 - ...('-' means STDIN)",
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
    sys.stderr.write("No path selected.\n")
    parser.print_help()
    sys.exit(2)
  else:
    pass


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


  for path in args:
    if path[0]!='/':path='/'+path

    if opts.verbose:
      sys.stderr.write("Moving %s to Recycle ... "%(path))

    # get path
    try:
      pathobj = pyacd.api.get_info_by_path(path)
    except pyacd.PyAmazonCloudDriveApiException,e:
      sys.stderr.write("Aborted. ('%s')\n"%e.message)
      continue
    except pyacd.PyAmazonCloudDriveError,e:
      sys.stderr.write("Not found.\n")
      continue

    if pathobj.Type!= pyacd.types.FILE and pathobj.Type!= pyacd.types.FOLDER :
      sys.stderr.write("Aborted. ('%s<%s>' is special entity.)"%(path,pathobj.Type))
      continue

    # move
    pyacd.api.recycle_bulk_by_id([pathobj.object_id,])

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
