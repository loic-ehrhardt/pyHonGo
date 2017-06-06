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

#--------------------------------------------------------------------
import subprocess
import threading
from time import sleep
#--------------------------------------------------------------------

#--------------------------------------------------------------------
# Remote buttons constants
#--------------------------------------------------------------------

OK           = 0
UP           = 1
DOWN         = 2
LEFT         = 3
RIGHT        = 4
NUM_0        = 20
NUM_1        = 21
NUM_2        = 22
NUM_3        = 23
NUM_4        = 24
NUM_5        = 25
NUM_6        = 26
NUM_7        = 27
NUM_8        = 28
NUM_9        = 29
RED          = 72
GREEN        = 73
YELLOW       = 74
BLUE         = 71
CHANNEL_UP   = 30
CHANNEL_DOWN = 31
EXIT         = 21002
BACK         = 1003
OPTIONS      = 1001

#--------------------------------------------------------------------
# Remote class
#--------------------------------------------------------------------

class Remote(threading.Thread):
 
   def run(self):
 
      self._data = []
      self.hasKeys = False
 
      self._p = subprocess.Popen('cec-client',
                shell=True,stdin=subprocess.PIPE,
                stdout=subprocess.PIPE)
 
      while self._p.poll() is None :
         x = self._p.stdout.readline()
         if 'key released' in x:
            try:
               #self._data.append( x.split(':')[-1][1:-1] )
               self._data.append( int(x.split('(')[-1].split(')')[0]
                                  .replace('a','1001').replace('c','1002')
                                  .replace('d','1003')) )
               self.hasKeys = True
            except: pass

   def stop(self):
 
      try:
         self._p.terminate()
         self._p.stdin.close()
      except: pass

   def get_key(self):
 
      l = len(self._data)
      if l>0:
         d = self._data.pop(0)
         if l==1 : self.hasKeys = False
         return d
 
   def command(self,c,wait=True):
 
      if wait : sleep(3.0)
      self._p.stdin.write(c+'\n')
      if wait : sleep(1.0)
 
#--------------------------------------------------------------------
# Test
#--------------------------------------------------------------------

if __name__ == '__main__':

   print 'Starting remote handler'
   r = Remote()
   r.start()
   r.command('as')

   try:
      print 'Ready. CTRL+C to exit'
      while True:
         if r.hasKeys:
            print r.get_key()
   except KeyboardInterrupt:
      print 'Got CTRL+C. Stopping handler'
      r.stop()


