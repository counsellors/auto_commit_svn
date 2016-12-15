#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sh
import re
import json
import fnmatch
import datetime
import hashlib
import threading
import logging
import copy
from logging.handlers import RotatingFileHandler
from flask import *

FORMAT = '%(asctime)s-%(levelname)s-(%(funcName)s)>> %(message)s'
logging.basicConfig(format=FORMAT, datefmt='%H:%M',level=logging.INFO)

app = Flask(__name__)
app.debug = True

def CheckToken(token):
    #md5:4bd30f402321f3a8ab48ae0234f15494
    key = "Hold the door!"
    md5 = hashlib.md5(key).hexdigest()
    print md5
    if md5 != token:
        return 0
    return 1

def replace_changed_files(filename):
    match = re.search(r'^[AM]\s+([^\s]+)*', filename)
    if match:
        if match.group(1):
            return str( match.group(1) )

def replace_new_files(filename):
    match = re.search(r'^[?]\s+([^\s]+)*', filename)
    if match:
        if match.group(1):
            return str( match.group(1) )

def get_ignores(ignore_conf):
    ignores = []
    with open(ignore_conf, 'r') as fp:
        content = fp.readlines()
        for line in content:
            if line.strip() != "" and not line.startswith("# "):
                ignores.append( line.strip() )
    return ignores

def ignore_it(ignore_types, filenames):
    ignore_files = []
    p_filenames = filenames
    for ignore in ignore_types:
        filenames = [n for n in filenames if not fnmatch.fnmatch(n, ignore)]
        ignore_files.extend( fnmatch.filter(p_filenames, ignore) )
    # print "ignored files", ignore_files
    # print "not ignored files", filenames
    return filenames,ignore_files

def find_diff_files(repo_path, ignore_types):
    svn_status = sh.svn('st',repo_path)
    changed_files = []
    new_files = []
    logging.info( "svn st {repo_path}\n{svn_status}".format(repo_path=repo_path,svn_status=svn_status) )
    for line in svn_status.split("\n"):
        if line.strip() != "":
            new_file = replace_new_files( line.strip() )
            changed_file = replace_changed_files( line.strip() )
            if new_file is not None: new_files.append( new_file )
            if changed_file is not None: changed_files.append( changed_file  )
    changed_files,ignore_files = ignore_it(ignore_types, changed_files)
    new_files, ignore_files1 = ignore_it(ignore_types, new_files)
    ignore_files.extend(ignore_files1)
    return (new_files, changed_files, ignore_files)


@app.route("/ci/<token>", methods = ['GET'])
def get_sample(token=None):
    ret = {'status':200,'msg':'OK'}
    if CheckToken(token):
        ret['status'] = 201
        return ret
    # pkg_dir = "/tmp"
    filename = request.args.get('filename')
    pkg_type = request.args.get('type')
    resp = ''
    xname = "myrepo/mm"
    with open(xname, 'a') as fp:
        fp.write("This line is auto writed by sunon's robot.\n")
    repo_path = "myrepo"
    ignore_conf = os.path.join(repo_path, "svnignore")
    try:
        ignore_types = get_ignores(ignore_conf)
        new_files, changed_files,ignore_files = find_diff_files( repo_path, ignore_types )
        if len(new_files) !=0: sh.svn.add(new_files)
        changed_files.extend(new_files)
        if len(changed_files) !=0: 
            svn_ci = sh.svn.commit(changed_files, "-m", "\"update code by robot\"")
            logging.info( "svn ci {changed_files}\n{svn_ci}".format(
                                                        changed_files=changed_files,
                                                        svn_ci=svn_ci) )
        logging.info( "New files     : {new_files}".format(new_files=new_files ) )
        logging.info( "Changed files : {changed_files}".format(changed_files=changed_files) )
        logging.info( "Ignore files  : {ignore_files}".format(ignore_files=ignore_files) )
        a = 1/0
    except Exception, e:
        resp = Response("error: {e}".format(e=e))
    else:
        resp = Response("OK! accepted your request.")
    return resp

if __name__ == "__main__":
    logger = logging.getLogger('werkzeug')
    handler = logging.FileHandler('access.log')
    logger.addHandler(handler)
    app.debug = True
    app.run("0.0.0.0", port = 5011)
