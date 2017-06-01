#!/usr/bin/python
# -*- coding: utf-8 -*-
#-----------------------------------------------------------------------
import json
import codecs
#-----------------------------------------------------------------------

def correct(db):
   # Corrects some entries in the dictionnary
   # Missing translation
   db[1132][4] = u'oeuf,'+db[1132][4]
   # These are verbs (JLPT 5)
   applylist = (1130,1138,1190,1228,1248,1256,1309,1316,1346)
   for cid in applylist : db[cid][5].append(u'P:v')
   # These are adjectives (JLPT 5)
   applylist = (1139,1247,1249,1340)
   for cid in applylist : db[cid][5].append(u'P:adj-i')
   # These are verbs (JLPT 4)
   applylist = (1418,1420,1481,1483,1533,1543,1600,1633,1646,1666,
                1680,1687,1690,1692,1693,1700,1726,1733,1734,1785,
                1796)
   for cid in applylist : db[cid][5].append(u'P:v')
   # These are adjectives (JLPT 4)
   applylist = (1701,1703,1724,1735)
   for cid in applylist : db[cid][5].append(u'P:adj-i')

def get_flags():
   # Open and returns dictionnary flags
   with open('./dictionnary/flags.txt','r') as fid:
      FLAGS = json.load(fid)
   return FLAGS

def get_dictionnary(filter_level=0):
   # Open dictionnary
   with codecs.open('./dictionnary/dictionnary.txt','r','utf-8') as fid:
      db = json.load(fid)
   # Filtering
   db2 = dict([(entry[0],entry[1:]) for entry in db if entry[1]>=filter_level ])
   # Correcting
   correct(db2)
   # Return result
   return db2

