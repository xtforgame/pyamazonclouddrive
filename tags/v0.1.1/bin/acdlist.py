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
import time, datetime
from optparse import OptionParser

try:
  import pyacd
except ImportError:
  pyacd_lib_dir=os.path.dirname(__file__)+os.sep+".."
  if os.path.exists(pyacd_lib_dir) and os.path.isdir(pyacd_lib_dir):
    sys.path.insert(0, pyacd_lib_dir)
  import pyacd

parser=OptionParser(
  epilog="This command lists files and directories of your Amazon Cloud Drive.",
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
  "-l",dest="long_format",action="store_true",default=False,
  help="use a long listing format"
)
parser.add_option(
  "-t",dest="list_type",action="store",default="ALL",metavar="TYPE",
  help="list type (ALL|FILE|FOLDER) [default: %default]"
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
    args.append("/")
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
      sys.stderr.write("Listing %s ... "%(path))

    # get path
    try:
      pathobj = pyacd.api.get_info_by_path(path)
    except pyacd.PyAmazonCloudDriveApiException,e:
      sys.stderr.write("Aborted. ('%s')\n"%e.message)
      continue
    except pyacd.PyAmazonCloudDriveError,e:
      sys.stderr.write("Not found.\n")
      continue

    obj=[]
    if pathobj.Type== pyacd.types.FILE:
      obj.append(pathobj)
    else:
      info = pyacd.api.list_by_id(pathobj.object_id)
      obj+=info.objects

    if opts.verbose:
      sys.stderr.write("Done\n")

    #print obj
    if opts.long_format:
      print "total %s (%s)"%(len(obj),path)
      print "==modified========== ==size/type== ==version== ==name=========="
    for o in obj:
      if opts.list_type!="ALL" and opts.list_type!=o.Type:
        continue
      if opts.long_format:
        print "%s "%datetime.datetime(*time.localtime(o.modified)[:-3]).isoformat(),
        if o.Type == pyacd.types.FILE:
          print "%13s"%(o.size if o.size else -1),
        else:
          print "%13s"%("<"+o.Type+">"),

        print "%11s"%("("+str(o.version)+")"),

      print o.name if o.Type == pyacd.types.FILE else o.name+"/"

    continue


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
