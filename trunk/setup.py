#!/usr/bin/env python

# Copyright (c) 2012 Matt Luongo http://mattluongo.com
# All rights reserved.
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

from setuptools import setup

setup(name = "amazon-cloud-drive",
      version = '0.0.6',
      description = "A maintained fork of PyAmazonCloudDrive (pyacd), a "\
                    "3rd-party Python library for accessing Amazon Cloud "\
                    "Drives.",
      author = "Sakurai Youhei",
      maintainer = "Matt Luongo",
      maintainer_email = "mhluongo@gmail.com",
      scripts = ["bin/acdcat", "bin/acdget", "bin/acdlist", "bin/acdmkdir",
                 "bin/acdput", "bin/acdrecycle"],
      url = "https://github.com/mhluongo/amazon-cloud-drive",
      packages = ["pyacd"],
      license = "MIT",
      classifiers = ["Development Status :: 4 - Beta",
                     "Intended Audience :: Developers",
                     "License :: OSI Approved :: MIT License",
                     "Operating System :: POSIX"]
      )
