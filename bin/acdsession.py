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
  epilog="This command updates/creates your session of Amazon Cloud Drive.",
  usage="%prog -e youremail -p yourpassword -s path/to/sessionfile",
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
  "-v",dest="verbose",action="store_true",default=False,
  help="show verbose message"
)

def main():
  opts,args=parser.parse_args(sys.argv[1:])
  pyacd.set_amazon_domain(opts.domain)

  for m in ["email","session"]:
    if not opts.__dict__[m]:
        print >>sys.stderr, "mandatory option is missing (%s)\n"%m
        parser.print_help()
        exit(2)

  if not opts.password:
    opts.password = getpass.getpass()

  if os.path.isdir(opts.session):
    print >>sys.stderr, "%s should not be directory."%s
    exit(2)

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
    session=pyacd.login(opts.email,opts.password,session=s)
    if opts.verbose:
      print >>sys.stderr, "Done."

    if opts.verbose:
      print >>sys.stderr, "Updating current session...",

    session.save_to_file(opts.session)
    if opts.verbose:
      print >>sys.stderr, "Done."

  except:
    if opts.verbose:
      print >>sys.stderr, "Failed."

if __name__=="__main__":
  main()
