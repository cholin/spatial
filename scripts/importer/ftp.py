# -*- coding: utf-8 -*-

import ftplib
from StringIO import StringIO

def ftp_connect(host):
    ftp = ftplib.FTP(host)
    ftp.login()
    return ftp

def ftp_list(ftp, path):
    ftp.cwd(path)
    ls = []
    ftp.retrlines('MLSD', ls.append)
    return ((entry.split(';')[-1]) for entry in ls)

def ftp_get_file(ftp, path):
    memfile = StringIO()
    ftp.retrbinary('RETR %s' % path, memfile.write)
    return memfile
