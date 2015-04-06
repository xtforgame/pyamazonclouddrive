# Introduction #
PyAmazonCloudDrive (pyacd) is a 3rd-party Python library for accessing "Amazon Cloud Drive".

_Note_: This is just an experimental project for the future like boto which can upload/download files in a few lines in Python.

## These are respective contributors who gives valuable feedback. ##
> - Adam Compton (https://github.com/handyman5)

> - Matt Luongo (https://github.com/mhluongo)

## Got available for www.amazon.co.jp as well in version 0.1.2. ##

# **[WARNING](WARNING.md)** These are matters you must consider #
## 1) Amazon Cloud Drive: Terms of Use ##

This implementation is all based on analysis by me (Youhei Sakurai) and I'm not sure whether everyone who uses this library would be allowed by "Amazon Cloud Drive: Terms of Use" or not. Therefore please read below link carefully, then start to use this.

http://www.amazon.com/gp/help/customer/display.html/?nodeId=200557360
```
  6. Software

  you may not ... (f) modify, reverse engineer, decompile or disassemble, or 
  otherwise tamper with, the Software, whether in whole or in part, or create 
  any derivative works from or of the Software.
```
## 2) Limitation for number of devices. (Up to eight devices) ##

Now below link disappeared but Amazon used to restrict the number of devices within 8, that may be because of something from a legal point of view. This is counted by cookie so I recommend you to use persist session functionality of library; see also code written in bin/acdsession.py.

http://www.amazon.com/gp/help/customer/display.html/?ie=UTF8&nodeId=200557340\n
```
  Frequently Asked Questions
  How many devices can I use to access the files I've stored in my Cloud Drive?
```

# Installation of pyacd #
1) Checkout repository with svn. (Run following command.)
```
  svn checkout http://pyamazonclouddrive.googlecode.com/svn/trunk/
```
2) Run setup.py
```
  setup.py install
```
3) Read source in pyacd and helps of "bin/**.py --help".**

4) It occurred to me that someone said "Use the Source, Luke.".

# Example usage of bin/acdxxx.py #

1) Upload all files in localdir to remotedir.

```
$ acdmkdir.py -e someone@example.com -p xxxx -s ~/.acdsession remotedir
$ ls -F localdir | grep -v / | sed "s/[\*|@]$//g" | sed "s/^/localdir\//g" |\
  acdput.py -s ~/.acdsession -d remotedir -
```
2) Download all files in remotedir to localdir\_else.

```
$ mkdir localdir_else
$ acdlist.py -s ~/.acdsession -t FILE remotedir | sed "s/^/remotedir\//g" |\
  acdget.py -s ~/.acdsession -d localdir_else -
```
3) Make alias if you need.

```
$ alias acdget='acdget.py -s ~/.acdsession --domain=www.amazon.co.jp'
$ alias acdlist='acdlist.py -s ~/.acdsession --domain=www.amazon.co.jp'
$ alias acdmkdir='acdmkdir.py -s ~/.acdsession --domain=www.amazon.co.jp'
$ alias acdrecycle='acdrecycle.py -s ~/.acdsession --domain=www.amazon.co.jp'
$ alias acdput='acdput.py -s ~/.acdsession --domain=www.amazon.co.jp'
$ alias acdcat='acdcat.py -s ~/.acdsession --domain=www.amazon.co.jp'
```

# Example usage of pyacd package #
## How to login and so on ##
```
import pyacd

# Login with email and password
session = pyacd.login("someone@example.com","foobar")

# Save session file to somewhere
session.save_to_file("/home/ubuntu/.acdsession")

# Show user information
print session.username
print session.customer_id

# Show usage of storage
print pyacd.api.get_user_storage()

# Get root object and show information
root = pyacd.api.get_info_by_path("/")
print root.status
print root.version
```
## How to download ##
```
import pyacd

# Load session from file which was saved above section
session = pyacd.Session.load_from_file("/home/ubuntu/.acdsession")

# Login with previous session
session = pyacd.login(session=session)

if session and session.is_logged_in():
  # Get file object by path
  fileobj = pyacd.api.get_info_by_path("/path/to/file")

  # Download file data by using object_id
  data=pyacd.api.download_by_id(fileobj.object_id)

  # Update session file
  session.save_to_file("/home/ubuntu/.acdsession")
```
## How to upload ##
```
import pyacd

# Load session from file which was saved above section
session = pyacd.Session.load_from_file("/home/ubuntu/.acdsession")

# Login with previous session
session = pyacd.login(session=session)

if session and session.is_logged_in() and session.agreed_with_terms:
  # session.agreed_with_terms is added in v0.1.2
  # Create file object by path
  fileobj = pyacd.api.create_by_path("/path/to/upload","filename")

  # Upload file data by using upload_url
  data = open("/path/to/file","rb").read()
  upload_url = pyacd.api.get_upload_url_by_id(fileobj.object_id,len(data))
  pyacd.api.upload(upload_url.http_request.end_point,
                   upload_url.http_request.parameters,
                   "filename",data)

  # Finish to upload file data
  pyacd.api.complete_file_upload_by_id(upload_url.object_id,
                                       upload_url.storage_key)

  # Update session file
  session.save_to_file("/home/ubuntu/.acdsession")
```

# Status #
Released v0.1.2 in 21 Nov 2012.

Released v0.1.0 in 9 Aug 2012.

# Coverage reports #
http://code.google.com/p/pyamazonclouddrive/wiki/CoverageReport