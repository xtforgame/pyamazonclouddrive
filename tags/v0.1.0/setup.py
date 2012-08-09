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

with open('README') as file:
    long_description = file.read()

# Followings are modified by Youhei Sakurai to make them adjust 
# to project's repository. You can see original one from:
# https://github.com/mhluongo/amazon-cloud-drive/blob/master/setup.py
setup(name = "amazon-cloud-drive",
      version = '0.1.0',
      description = "PyAmazonCloudDrive (pyacd) is a 3rd-party Python"\
                    "library for accessing Amazon Cloud Drives."\
      author = "Youhei Sakurai",
      author_email = "sakurai.youhei@gmail.com",
      scripts = ["bin/acdcat", "bin/acdget", "bin/acdlist", "bin/acdmkdir",
                 "bin/acdput", "bin/acdrecycle", "bin/acdsession"],
      url = "http://code.google.com/p/pyamazonclouddrive/",
      long_description=long_description,
      packages = ["pyacd"],
      license = "MIT",
      classifiers = ["Development Status :: 4 - Beta",
                     "Intended Audience :: Developers",
                     "License :: OSI Approved :: MIT License",
                     "Operating System :: POSIX"]
      )
