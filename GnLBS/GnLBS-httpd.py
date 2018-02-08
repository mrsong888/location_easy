#!/usr/bin/python2
# -*- encoding: utf-8 -*-

import os
import re
import posixpath
import urllib
import urlparse
import cgi
import sys
import threading
import shutil
import mimetypes
import gen_html
import itertools

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

SERVER_NAME='GnLBS-HTTP-Server'
SERVER_VERSION='1.0'

###############################################################################

class LBS_HTTP_Handler(BaseHTTPRequestHandler):
    def __rsp(self, body, stat, content_type):
        self.send_response(stat)
        # self.send_header('Content-Length', 124)
        self.send_header('Transfer-Encoding', 'chunked')
        self.send_header('Content-Type', content_type)
        self.end_headers()
        for data in body:
            print data, '*'*20
            self.wfile.write(data)

    def __load_file(self, fname):
        cwd = os.path.abspath(os.path.dirname(__file__))
        fullname = os.path.join(cwd, fname.lstrip('/'))
        t = mimetypes.guess_type(fname)

        try:
            f = open(fullname, "r")
            buf = f.read()
            f.close()
        except Exception,err:
            print err
            return None
        return (t[0], buf)

    def __api(self, opt):
        print opt
        if not opt.has_key("mdn") or \
            not opt.has_key("stime") or \
            not opt.has_key("etime"):
            return None

        html = gen_html.gen_html(opt["mdn"], opt["stime"], opt["etime"])
        return ("text/html", html)

    def do_GET(self):
        self.server_version = SERVER_NAME
        self.sys_version = SERVER_VERSION
        self.protocal_version = 'HTTP/1.1'
        body = ""

        URL = urlparse.urlparse(self.path)
        OPT = dict([(k, v[0]) for k, v in urlparse.parse_qs(URL.query).items()])
        PATH = URL.path

        if PATH == "/api":
            body = self.__api(OPT)
        else:
            if PATH == "/":
                PATH = "index.html"
            body = self.__load_file(PATH)
            print 'body------', body

        if body == None:
            self.__rsp("<h1>404</h1>", 404, "text/html")
        else:
            self.__rsp(body[1], 200, body[0])

def web_server_run():
    HTTPServer(('0.0.0.0', 8080), LBS_HTTP_Handler).serve_forever()

def daemon(need_log=False):
    # do the UNIX double-fork magic
    try:
        pid = os.fork()   
        if pid > 0:  
            sys.exit(0)   # exit first parent  
    except:
        return False

    # decouple from parent environment  
    #os.chdir("/")   
    if os.setsid() == -1:
        sys.exit(0)
    os.umask(0)   

    # do second fork  
    try:   
        pid = os.fork()   
        if pid > 0:  
            sys.exit(0)
    except OSError, e:   
        return False


    # close stdout stderr
    sys.stdout.close()
    sys.stdout = open("/dev/null", 'w')
    sys.stderr.close()
    sys.stderr = open("/dev/null", 'w')
    # web_server_run()
    return True

def daemon_thread():
    t = threading.Thread(target=gen_html.loop_load_files)
    t.setDaemon(True)
    t.start()


if __name__ == "__main__":
    print "starting GnLBS HTTP service ..."
    daemon_thread()
    if len(sys.argv) > 1 and sys.argv[1] == '-d':
        if daemon(False) == False:
            sys.exit(1)
        w = threading.Thread(target=web_server_run)
        w.start()
        w.join(1)
    else:
        web_server_run()


