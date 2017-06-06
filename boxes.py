#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of pyHonGo.
#
# pyHonGo is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pyHonGo is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pyHonGo.  If not, see <http://www.gnu.org/licenses/>.

#-----------------------------------------------------------------------
import dictionnary
#-----------------------------------------------------------------------
import random
import json
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# 'Card' class
#-----------------------------------------------------------------------

class Card:

   def __init__(self,level,jap_kanji,jap_kana,english,french,flags,group):
      '''
      Constructor of 'Card'
      - level     : JLPT level (5-1)
      - jap_kanji : Japanese word (kanji writing)
      - jap_kana  : Janapese word (reading in kanas)
      - english   : English word
      - french    : French word
      - flags     : list of flags
      - group     : word group (noun, adj, verb, ...)
      '''
      self.level     = level
      self.jap_kanji = jap_kanji
      self.jap_kana  = jap_kana
      self.english   = english
      self.french    = french
      self.flags     = flags
      self.group     = group

   def summary(self):
      return u'{0}({1}) | {2} / {3} | (JLPT{4}/{5}) {6}'.format(
      self.jap_kanji,self.jap_kana,self.french,self.english,
      self.level,self.group,u','.join(self.flags))

#-----------------------------------------------------------------------
# 'Boxes' class
#-----------------------------------------------------------------------

class Boxes:

   def __init__(self,database,nBoxes=5,freqrate=4,unlockrate=10):
      '''
      Initiates the boxes.
      Arguments :
      - database   : the database of the cards
      - nBoxes     : total number of boxes (default 5)
      - freqrate   : frequency difference between two boxes (default 4)
      - unlockrate : number of cards to unlock new level (default 10)
      '''
      # Save arguments
      self.database     = database
      self.nBoxes       = nBoxes
      self.freqrate     = freqrate
      self.unlockrate   = unlockrate
      # Initialisations
      self.nPicks       = 0
      self.nCards       = 0
      self.boxes        = [[] for _ in range(nBoxes)]
      self.currentCid   = None
      self.currentBox   = None
      self.propositions = None
      self.unlocked     = 0
      # Data file
      self._filename    = './noprofile.box'

   def import_cards(self,profile):
      '''
      Populate boxes, depending on the profile. List of profiles :
      - 1 : Import all JLPT5 cards, removing 'nofrench' group.
      - 2 : Import all JLPT4 and JLPT5 cards, removing 'nofrench' group.
            JLPT4 and 5 cards are shuffled and alterned in first box.
      Return True if cards were successfully loaded.
      '''
      if   profile == 1 :
         # Get list of ids
         cids = [cid for (cid,c) in self.database.iteritems()
                 if c.level==5 and c.group<>'nofrench']
         random.shuffle(cids)
         # Extent box 0
         self.boxes[0].extend(cids)
         self.nCards += len(cids)
         # OK
         return True
      elif profile == 2 :
         # Get list of ids
         cids_l5 = [cid for (cid,c) in self.database.iteritems()
                    if c.level==5 and c.group<>'nofrench']
         cids_l4 = [cid for (cid,c) in self.database.iteritems()
                    if c.level==4 and c.group<>'nofrench']
         random.shuffle(cids_l5)
         random.shuffle(cids_l4)
         m          = min(len(cids_l5),len(cids_l4))
         cids       = 2*m*[None]
         cids[::2]  = cids_l5[:m]
         cids[1::2] = cids_l4[:m]
         cids.extend(cids_l5[m:])
         cids.extend(cids_l4[m:])
         # Extent box 0
         self.boxes[0].extend(cids)
         self.nCards += len(cids)
         # OK
         return True
      else:
         return False

   def pick(self):
      '''
      Pick up one card id from the appropriate box.
      Place the picked card id in 'currentCid', and set 'currentBox'.
      Return True if sucess.
      '''
      # Check that no card is already picked
      if self.currentCid is None:
         # Increase total number of picked cards
         self.nPicks += 1
         # Choose appropriate box
         chosenBox = self._n2box()
         self.currentBox = chosenBox
         # Pop card id and place it to currentCid
         cid = self.boxes[chosenBox].pop(0)
         self.currentCid = cid
         # Add propositions
         group = self.database[self.currentCid].group
         propositions = [(cid,chosenBox)]
         required = 8
         found = 0
         for b in range(self.nBoxes):
            cidlist = [cid for cid in self.boxes[b]
                      if self.database[cid].group == group]
            random.shuffle(cidlist)
            for cid in cidlist:
               found += 1
               propositions.append( (cid,b) )
               if found == required : break
            if found == required : break
         random.shuffle(propositions)
         self.propositions = propositions
         # Choose direction
         self.translationDirection = ('fr2jp','jp2fr')[self.nPicks%2]
         # Ready
         return True
      else:
         # Card already picked
         return False

   def unpick(self):
      '''
      Puts the picked card back in its original box.
      Return True if sucess.
      '''
      # Check if a card is already picked
      if self.currentCid is None:
         # No card picked
         return False
      else:
         # A card is picked
         self.boxes[self.currentBox].insert(0,self.currentCid)
         self.nPicks -= 1
         self.currentCid   = None
         self.currentBox   = None
         self.propositions = None
         return True

   def reply(self,choice):
      '''
      Reply choice number 'choice', after haveing picked a card.
      Reply a tuple (ok,cid,oldbox,newbox,remark), saying if the answer
      was good ('ok'), and that the card with id 'cid' was moved from
      'oldbox' to 'newbox'. If the choice was bad, 'remark' gives the
      right answer. It it was good, 'remark' is -1 unless a new box has
      been unlocked with this answer, in which case the unlocked box
      number is returned.
      '''
      (acid,abox) = self.propositions[choice-1]
      if (acid == self.currentCid): # Good answer
         # Move card id to next box
         newbox = abox + 1
         if newbox == self.nBoxes : newbox = self.nBoxes - 1
         self.boxes[newbox].append(acid)
         # Check if a new box is unlocked
         remark = -1
         if newbox>self.unlocked \
         and len(self.boxes[newbox])>=self.unlockrate:
            # Unlock new box
            self.unlocked = newbox
            remark = newbox
         # Return values
         ret = (True,acid,abox,newbox,remark)
      else: # Bad answer
         # Move card id to previous box
         newbox = self.currentBox - 1
         if newbox == -1 : newbox = 0
         self.boxes[newbox].append(self.currentCid)
         # Returns the good choice
         remark = [i for (i,p) in enumerate(self.propositions)
                   if p[0]==self.currentCid][0]
         # Return values
         ret = (False,self.currentCid,self.currentBox,newbox,remark)
      # Clean picks
      self.currentCid   = None
      self.currentBox   = None
      self.propositions = None
      # Return box response
      return ret

   def save(self,filename=None):
      '''
      Save boxes state to file 'filename'.
      If not providen, save to current filename.
      '''
      # Update filename
      if not filename is None : self._filename = filename
      # Prepare data
      listattr = ('nBoxes','freqrate','unlockrate','nPicks','nCards',
                  'boxes','currentCid','currentBox','propositions',
                  'unlocked')
      data = {}
      for attr in listattr : data[attr] = getattr(self,attr)
      # Save data
      with open(self._filename,'w') as fid : json.dump(data,fid)

   def load(self,filename=None):
      '''
      Load boxes state from file 'filename'.
      If not providen, load from current filename.
      '''
      # Update filename
      if not filename is None : self._filename = filename
      # Load data
      with open(self._filename,'r') as fid : data = json.load(fid)
      # Update data
      for (attr,val) in data.iteritems() : setattr(self,attr,val)

   def _show(self):
      '''
      Print informations.
      '''
      if not self.currentCid is None:
         print 'Current card id :',self.currentCid
         print 'Picked from box :',self.currentBox
      print 'Number of cards :',self.nCards
      print 'Number of picks :',self.nPicks
      for (i,box) in enumerate(self.boxes):
         print 'Box '+str(i)+' : '+', '.join([str(cid) for cid in box])

   def _n2box(self,n=None):
      '''
      Gives the box number where to pick, from the total number of
      picked cards. If 'n' is providen, it is chosen to return the box
      number.
      '''
      # Handle arguments
      if n is None: n = self.nPicks
      # Compute box number
      box = [x for x in range(1,self.nBoxes) if n%(self.freqrate**x)==0]
      if len(box)==0:
         box = 0
      elif n%(self.freqrate**self.nBoxes) == 0:
         box = 0
      else:
         box = box[-1]
      # Check if box is unlocked, otherwise return higher unlocked box
      if box > self.unlocked : box = self.unlocked
      # Check empty box, if yes return first non-empty box number
      if len(self.boxes[box])==0:
         box = [i for i in range(self.nBoxes) if len(self.boxes[i])>0][0]
      # Return value
      return box

#-----------------------------------------------------------------------
# Load database function
#-----------------------------------------------------------------------

def load_database(filter_level=0):
   '''
   Load database. Returns FLAGS and the DATABASE.
   Optional argument 'filter_level' filters the imported cards: only
   cards with level >= 'filter_level' are imported. Defaults to 0 (all).
   For example if filter_level=4, only JLPT4 AND JLPT5 cards are
   imported.
   '''
   # Load dictionnary
   db = dictionnary.get_dictionnary(filter_level)
   # Instanciate class Card from dictionnary values and filter by group
   for (k,v) in db.iteritems():
      flags = v[5]
      if   v[4] == ''           : group = 'nofrench' # No-french group
      elif u'P:v'      in flags \
        or u'P:vi'     in flags \
        or u'P:vt'     in flags : group = 'verb'     # Verb
      elif u'P:adj-i'  in flags \
        or u'P:adj-na' in flags : group = 'adj'      # Adjective
      elif u'P:n'      in flags \
        or u'P:num'    in flags \
        or u'P:ctr'    in flags \
        or u'P:n-t'    in flags : group = 'noun'     # Noun
      else                      : group = 'noun'
      db[k] = Card(v[0],v[1],v[2],v[3],v[4],v[5],group)
   # Load flags
   flags = dictionnary.get_flags()
   # Return data
   return (flags,db)

#-----------------------------------------------------------------------
# Play in terminal
#-----------------------------------------------------------------------

def terminal_play(BOX):

   while True:

      # Boxes status
      s = []
      for boxnum in range(BOX.nBoxes):
         if boxnum > BOX.unlocked :
            s2 = ''
         else:
            s2 = '\033[01;36m'
         s2 += 'Box '+str(boxnum+1)
         s2 += ' ('+str(len(BOX.boxes[boxnum]))+')'
         s2 += '\033[00m'
         s.append(s2)
      s = " | ".join(s)

      # Pick a card
      BOX.pick()

      # Plot question
      print '-'*63
      print s
      print '(pick#'+str(BOX.nPicks)+') From box '+\
            str(1+BOX.currentBox)+', what means :\033[01;36m'
      qcard = DB[BOX.currentCid]
      if BOX.translationDirection == 'jp2fr':
         print u'   ' + qcard.jap_kanji
         if qcard.jap_kanji <> qcard.jap_kana:
            print u'   ' + u'( ' + qcard.jap_kana + u' )'
      else:
         print u'   ' + qcard.french[:60]
         print u'   ' + qcard.english[:60]

      # Plot propositions
      print '\033[00m'+'-'*63
      print 'Propositions :'
      for i in range(9):
         acard = DB[BOX.propositions[i][0]]
         if BOX.translationDirection == 'jp2fr':
            print unicode(i+1) + u'  ' + acard.french[:60]
            print u'   ' + acard.english[:60]
         else:
            print unicode(i+1) + u'  ' + acard.jap_kanji
            if acard.jap_kanji <> acard.jap_kana:
               print u'   ' + u'( ' + acard.jap_kana + u' )'

      # Get user answer
      answer = ''
      while not ( answer.isdigit() or answer == 'q' ):
         answer = raw_input('Your answer (1-9,q to quit) ?\n>>> ')
      if answer == 'q':
         BOX.unpick()
         break
      answer = int(answer)

      # Reply
      ret = BOX.reply(answer)
      print '-'*63
      if ret[0]:
         print '\033[01;32mYeah! Good answer. Card moved from box '+\
               str(1+ret[2])+' to box '+str(1+ret[3])+'.\033[00m'
         if ret[4]>=0:
            print '\033[01;32m >>> UNLOCKED BOX '+str(1+ret[4])+' <<<\033[00m'
      else:
         print '\033[01;31mNoooo! Bad answer. Card moved from box '+\
               str(1+ret[2])+' to box '+str(1+ret[3])+'.'

         print 'The right answer was # '+str(1+ret[4])+'\033[00m'

#-----------------------------------------------------------------------
# Main function
#-----------------------------------------------------------------------

if __name__ == '__main__':

   print '--- Start ---'

   print 'Importing database...',
   (FLAGS,DB) = load_database()
   print 'OK'

   print 'Creating boxes...',
   BOX = Boxes(DB)
   print 'OK'

   print '--- Objects ---'
   print 'FLAGS               - meaning of flags used'
   print 'DB                  - database of the cards'
   print 'BOX                 - empty boxes'
   print '--- Functions ---'
   print 'BOX.import_cards(1) - populate BOX with JLPT4 cards'
   print 'BOX.import_cards(2) - populate BOX with JLPT4 / JLPT5 cards'
   print 'BOX.save(f)         - save status to file f (optional)'
   print 'BOX.load(f)         - load status from file f (optional)'
   print 'terminal_play(BOX)  - play'

