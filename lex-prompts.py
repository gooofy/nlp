#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#
# Copyright 2013, 2014 Guenter Bartsch
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
# 
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#

import re, sys, os
import psycopg2
from gutils import detect_latin1, isgalnum
import ConfigParser
from os.path import expanduser

#
# load config, set up global variables
#

home_path = expanduser("~")

config = ConfigParser.RawConfigParser()
config.read("%s/%s" % (home_path, ".airc"))

db_server = config.get("speech", "dbserver")
db_name   = config.get("speech", "dbname")
db_user   = config.get("speech", "dbuser")
db_pass   = config.get("speech", "dbpass")

#
# connect to db
#

conn_string = "host='%s' dbname='%s' user='%s' password='%s'" % (db_server, db_name, db_user, db_pass)

conn = psycopg2.connect(conn_string)

cur = conn.cursor()

#print "loading prompts...",
sys.stdout.flush() 

words = set()

cur.execute ("SELECT prompt FROM audio") 
rows = cur.fetchall()
for row in rows:

    prompt = row[0].decode('UTF8')

    ws = re.split ('\s+', prompt)

    for word in ws:

        w = re.sub(r"[,.?\-! ;:]", '', word.lstrip().rstrip()).upper()
        if len(w) > 0:
            if not isgalnum(w):
                #print "SKIPPING: %s" % w
                continue

            if not w in words:
                #print "New word from prompts: %s" % w
                words.add(w)

#print "done. %d unique words found." % len(words)

#print "STATS: %d words" % len(words)

count = 0

for word in words:

    cur.execute ("SELECT pronounciations.id FROM words,pronounciations WHERE words.word=%s AND words.id = pronounciations.wid", (word,)) 
   
    if not cur.fetchone():
        print "%s " % word,
        count += 1

        if count > 100:
            break
