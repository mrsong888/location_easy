#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import os
import sys
import time

files_list = []

def loop_load_files():
    path = os.environ['TAR_FILE_DIR'] if os.environ.get('TAR_FILE_DIR') else '/home/ftp/xdr/gps'
    cache_files = set(os.listdir(path))
    files_list = list(cache_files)
    while True:
        time.sleep(1)
        temp_cache_files = __cronjob_rm_expired_file(os.listdir(path), path)
        if cache_files.difference(temp_cache_files):
            cache_files = set(os.listdir(path))
            files_list = list(cache_files)

def __cronjob_rm_expired_file(tar_list, path):
    sentinel = os.environ['SENTINEL'] if os.environ.get('SENTINEL') else 1259200
    for fname in tar_list:
        if not fname.startswith("GN_GPS") or not fname.endswith(".txt"):
            continue
        t = fname.split("_")[3]
        stamp = time.mktime(time.strptime(t, '%Y%m%d%H%M%S'))
        if time.time() - stamp >= sentinel:
            try:
                os.remove(os.path.join(path, fname))
            except OSError as e:
                print e
    return set(os.listdir(path))


def __get_line_from_file(file_name):
    for line in file(file_name):
        yield line

def __flist(stime, etime, path="."):
    # RET = []
    F_TIME = 3
    list_dir = files_list if files_list else os.listdir(path)
    for fname in list_dir:
        if not fname.startswith("GN_GPS") or not fname.endswith(".txt"):
            continue
        t = fname.split("_")[F_TIME]
        if cmp(t, stime) < 0 or cmp(t, etime) > 0:
            continue
    #     RET.append(os.path.join(path, fname))
    # return RET
        yield os.path.join(path, fname)

def __loclist(mdn, stime, etime, fname):

    # ARR = []
    for l in __get_line_from_file(fname):
        l = l.strip()
        fs = l.split("|")
        try:
            m = fs[1]
            t = fs[8]
            longitude = float(fs[10])
            latitude = float(fs[11])
        except IndexError:
            print 'the line params is wrong', fs
            continue

        if m != mdn or cmp(t, stime) < 0 or cmp(t, etime) > 0:
            continue
    
    #     ARR.append((t, (longitude, latitude)))
    # return ARR
        yield (t, (longitude, latitude))

def pre_gen_html(mdn, stime, etime):
    path = "/home/ftp/xdr/gps"
    print path
    # ARR = []
    s = "    locations = [\n"
    yield s
    for fname in __flist(stime, etime, path):
        print fname
        for t, v in  __loclist(mdn, stime, etime, fname):
            yield "        [%f, %f], // %s \n" % (v[0], v[1], t)
    yield '    ];'

def gen_html(mdn, stime, etime):

    for line in file('tmpl.html'):
        if "// AUTOGEN-CODE" in line:
            for info in pre_gen_html(mdn, stime, etime):
                yield info
        else:
            yield line

    # ARR.sort(lambda p1,p2 : cmp (p1[0], p2[0]))
    #ARR.sort(key=lambda p: p[0])

    # s = "    locations = [\n"
    # for t,v in iter(ARR):
    #     s += "        [%f, %f], // %s \n" % (v[0], v[1], t)
    # s += '    ];'

    # f = open("tmpl.html", 'r')
    # tmpl = f.read()
    # f.close()
    #
    # html = tmpl.replace("// AUTOGEN-CODE", s)
    # return html

if __name__ == "__main__":
    ARR = []
    for fname in sys.argv[1:]:
        f = open(fname, "r")
        lines = f.readlines()
        print len(lines)
        f.close()

        for l in lines:
            l = l.strip()
            fs = l.split("|")
            # print fs
            stime = fs[8]
            try:
                longitude = float(fs[10])
            except:
                print lines.index(l)
            latitude = float(fs[11])
            ARR.append((stime, (longitude, latitude)))
            print ARR
    # print ARR
    sys.exit(0)
    ARR.sort(lambda p1,p2 : cmp (p1[0], p2[0])) 

    s = "    locations = [\n"
    for stime,v in ARR:
        s += "        [%f, %f], // %s \n" % (v[0], v[1], stime)
        print s
    s += '    ];'
    print s

    f = open("tmpl.html", 'r')
    tmpl = f.read()
    f.close()
    
    html = tmpl.replace("// AUTOGEN-CODE", s)
    f = open("index.html", "w")
    f.write(html)
    f.close()

