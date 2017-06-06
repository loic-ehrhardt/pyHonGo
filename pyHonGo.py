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
from __future__ import division
import sys
import pygame
#-----------------------------------------------------------------------
import boxes
#-----------------------------------------------------------------------
REVERSE_NUMPAD        = False
WITH_REMOTE           = False
FORCE_RESOLUTION      = True
FORCE_RESOLUTION_SIZE = (800,600)
DEBUG                 = False
MAX_JLPT_FOR_DATABASE = 4
#-----------------------------------------------------------------------

#-----------------------------------------------------------------------
# Initialisations
#-----------------------------------------------------------------------

# --- Logging ---
if DEBUG:
   def log(s,r=0) :
      if r==0 : print s
      else    : print s,'...',
else:
   def log(s,r=0) : pass

# --- Game objects ---

# Database
log('Load database',1)
(FLAGS,DB) = boxes.load_database(MAX_JLPT_FOR_DATABASE)
log('OK')

log('Start box',1)
BOX = boxes.Boxes(DB)
log('OK')

# --- Pygame ---
log('Init pygame <display> and <font>',1)
#pygame.init()
pygame.display.init()
pygame.font.init()
log('OK')

# --- Remote control ---
if WITH_REMOTE:
   #Start remote
   log('Init remote',1)
   import remotecontrol as rc
   remote = rc.Remote()
   remote.start()
   remote.command('as')
   log('OK')
   # Mapping Remote control <-> Pygame event
   REMOTE_MAPPING = {
   rc.EXIT  : ( pygame.QUIT    , {}                                    ) ,
   rc.BLUE  : ( pygame.KEYDOWN , {'key':pygame.K_p,'unicode':u'p'}     ) ,
   rc.OK    : ( pygame.KEYDOWN , {'key':pygame.K_RETURN,'unicode':u''} ) ,
   rc.UP    : ( pygame.KEYDOWN , {'key':pygame.K_UP,'unicode':u''}     ) ,
   rc.DOWN  : ( pygame.KEYDOWN , {'key':pygame.K_DOWN,'unicode':u'p'}  ) ,
   rc.LEFT  : ( pygame.KEYDOWN , {'key':pygame.K_LEFT,'unicode':u'p'}  ) ,
   rc.RIGHT : ( pygame.KEYDOWN , {'key':pygame.K_RIGHT,'unicode':u'p'} ) ,
   rc.NUM_1 : ( pygame.KEYDOWN , {'key':pygame.K_1,'unicode':u'1'}     ) ,
   rc.NUM_2 : ( pygame.KEYDOWN , {'key':pygame.K_2,'unicode':u'2'}     ) ,
   rc.NUM_3 : ( pygame.KEYDOWN , {'key':pygame.K_3,'unicode':u'3'}     ) ,
   rc.NUM_4 : ( pygame.KEYDOWN , {'key':pygame.K_4,'unicode':u'4'}     ) ,
   rc.NUM_5 : ( pygame.KEYDOWN , {'key':pygame.K_5,'unicode':u'5'}     ) ,
   rc.NUM_6 : ( pygame.KEYDOWN , {'key':pygame.K_6,'unicode':u'6'}     ) ,
   rc.NUM_7 : ( pygame.KEYDOWN , {'key':pygame.K_7,'unicode':u'7'}     ) ,
   rc.NUM_8 : ( pygame.KEYDOWN , {'key':pygame.K_8,'unicode':u'8'}     ) ,
   rc.NUM_9 : ( pygame.KEYDOWN , {'key':pygame.K_9,'unicode':u'9'}     ) }

# --- FPS clock ---
clock = pygame.time.Clock()
fps = 0.0

# --- Screen ---
if FORCE_RESOLUTION:
   (screen_w,screen_h) = FORCE_RESOLUTION_SIZE
else:
   screenInfo = pygame.display.Info() # 1214 x 674 on my TV
   screen_w = screenInfo.current_w
   screen_h = screenInfo.current_h
log('Init screen at ('+str(screen_w)+'x'+str(screen_h)+')',1)
DISPLAY = pygame.display.set_mode((screen_w,screen_h))
log('OK')

# --- Font renderers ---
class Font:
   def __init__(self):
      self._fonts={}
   def __getitem__(self,key):
      if not key in self._fonts:
         log('Start new font ('+str(key)+')',1)
         self._fonts[key]=pygame.font.SysFont('TakaoPGothic',key)
         log('OK')
      return self._fonts[key]
   def bold(self,key,isBold):
      self[key].set_bold(isBold)
fonts = Font()
fonts.bold(12,True)

# --- Images ---
log('Load images',1)
imgFolder = {}
for c in ('blue','gray','green','orange','red','yellow'):
   imgFolder[c] = pygame.image.load('./imgs/folder_'+c+'.png').convert_alpha()
temp = pygame.image.load('./imgs/background.jpg').convert()
rect = temp.get_rect()
imgBackground = pygame.Surface((screen_w,screen_h))
imgBackground.blit(temp,(0,0),(rect.w-screen_w,rect.h-screen_h,screen_w,screen_h))
neko = pygame.image.load('./imgs/neko.png').convert()
usagi = pygame.image.load('./imgs/usagi.png').convert()
log('OK')

# --- Others ---

# Question zone rect
QRECT = pygame.Rect((110,0,screen_w-110,screen_h))

# Profiles
profiles   = ['ensemble','usagi','neko']
profilenum = 0

# No mouse
pygame.mouse.set_visible(False)

# Color constants
ALPGRAY  = (   0 ,   0 ,   0 , 150 )
ALPGRAY2 = ( 100 , 100 , 100 , 150 )
ALPGREEN = (  78 , 154 ,   6 , 150 )
ALPRED   = ( 164 ,   0 ,   0 , 150 )

#-----------------------------------------------------------------------
# System functions
#-----------------------------------------------------------------------

def handle_remote():

   # Apply mappings
   while remote.hasKeys:
      key = remote.get_key()
      if key in REMOTE_MAPPING:
         (evt,prop) = REMOTE_MAPPING[key]
         pygame.event.post(pygame.event.Event(evt,**prop))
         log('Remote event : '+str(key)+' -> '+str(evt)+' '+str(prop))
      else:
         log('Remote event : '+str(key)+' -> ???')

def terminate():

   # Quit program nicely
   log('Stopping pygame',1)
   pygame.quit()
   log('OK')
   if WITH_REMOTE:
      log('Stopping remote',1)
      remote.stop()
      log('OK')
   log('Exiting')
   sys.exit()

#-----------------------------------------------------------------------
# Plotting functions
#-----------------------------------------------------------------------

def plot_avatars(profile):
   log('> plot_avatars')

   # Init ugly rects
   surroundingrects = []

   # Plot avatars
   neko_rect = neko.get_rect()
   usagi_rect = usagi.get_rect()
   neko_rect.top  = 5
   usagi_rect.top  = neko_rect.bottom+5
   if profile == 'ensemble':
      neko_rect.left = 5
      usagi_rect.left = 5
   elif profile == 'usagi':
      neko_rect.right = 30
      usagi_rect.left = 5
   elif profile == 'neko':
      neko_rect.left = 5
      usagi_rect.right = 30
   DISPLAY.blit(neko,neko_rect)
   DISPLAY.blit(usagi,usagi_rect)
   pygame.draw.rect(DISPLAY,(80,80,255),neko_rect,2)
   pygame.draw.rect(DISPLAY,(80,80,255),usagi_rect,2)
   surroundingrects.append(neko_rect)
   surroundingrects.append(usagi_rect)

   # Return ugly rects
   if len(surroundingrects)>0 :
      return [surroundingrects[0].unionall(surroundingrects[1:])]
   else:
      return []

def plot_folders(box):
   log('> plot_folders')

   # Init ugly rects
   surroundingrects = []

   # Check current folder picked
   if not box.currentBox is None:
      rect = pygame.Rect(0,0,68,68)
      rect.centerx = 55
      rect.centery = screen_h - 10 - box.currentBox*(64+10) - 32
      pygame.draw.rect(DISPLAY,(114,159,207),rect)

   # List of folders
   boxcolors = ('red','orange','yellow','green','blue')
   for i in range(box.nBoxes):

      # Plot folder
      img = imgFolder[ 'gray' if i>box.unlocked else boxcolors[i] ]
      rect = img.get_rect()
      rect.centerx = 55
      rect.bottom = screen_h - 10 - i*(rect.height+10)
      DISPLAY.blit(img,rect)

      surroundingrects.append(rect)

      # Plot number of cards
      ncards = len(box.boxes[i])
      if not box.currentBox is None and box.currentBox==i : ncards += 1
      txt = fonts[12].render(str(ncards),True,(0,0,0))
      rect2 = txt.get_rect()
      rect2.center = rect.center
      rect2 = rect2.move(0,5)
      DISPLAY.blit(txt,rect2)

   # Return ugly rects
   if len(surroundingrects)>0 :
      return [surroundingrects[0].unionall(surroundingrects[1:])]
   else:
      return []

def multiline_text_fr(string,font,rect,maxlines,xgap=5):
   log('> multiline_text_fr')

   # Initialisations
   words = [w for w in string.replace(',',', ').split(' ') if w<>'']
   lines = []
   accumulated_words = []

   # Loop over words to insert in the rect
   while len(words)>0 :
      test_line = ' '.join(accumulated_words+[words[0]])
      if font.size(test_line)[0] > rect.width-2*xgap:
         lines.append(' '.join(accumulated_words))
         accumulated_words = []
         if len(lines)>=maxlines : break
      else:
         accumulated_words.append(words.pop(0))
   if len(accumulated_words)>0 : lines.append(' '.join(accumulated_words))

   # Return list of strings (1 per line)
   return lines

def multiline_text_jp(string,font,rect,maxlines,xgap=5):
   log('> multiline_text_jp')

   # Initialisations
   glyphs = [g for g in string]
   lines = []
   accumulated_glyphs = []

   # Loop over glyphs to insert in the rect
   while len(glyphs)>0 :
      test_line = ''.join(accumulated_glyphs+[glyphs[0]])
      if font.size(test_line)[0] > rect.width-2*xgap:
         lines.append(''.join(accumulated_glyphs))
         accumulated_glyphs = []
         if len(lines)>=maxlines : break
      else:
         accumulated_glyphs.append(glyphs.pop(0))
   if len(accumulated_glyphs)>0 : lines.append(''.join(accumulated_glyphs))

   # Return list of strings (1 per line)
   return lines

def plot_question_text(card,brect,transdir,isQuestion):
   log('> plot_question_text ('+transdir+','+str(isQuestion)+')')

   # Language and size settings
   lang = transdir[:2] if isQuestion else transdir[3:]
   if   lang == 'fr' and isQuestion: # OK
      f1 = fonts[30]
   elif lang == 'fr' and not isQuestion: # OK
      f1 = fonts[24]
   elif lang == 'jp' and isQuestion:
      f1 = fonts[50]
      f2 = fonts[30]
   elif lang == 'jp' and not isQuestion:
      f1 = fonts[30]
      f2 = fonts[30]

   if lang == 'jp':
      # Japanese text
      lines = multiline_text_jp(card.jap_kanji,f1,brect,2)
      txts  = [f1.render(line,True,(255,255,255)) for line in lines]
      if card.jap_kanji <> card.jap_kana:
         lines2 = multiline_text_jp(card.jap_kana,f1,brect,2)
         txts  += [f2.render(line,True,(255,255,255)) for line in lines2]
         lines.extend(lines2)
   else:
      # French text
      lines = multiline_text_fr(card.french,f1,brect,3)
      txts  = [f1.render(line,True,(255,255,255)) for line in lines]

   # Plot text(s)
   txtrs = [s.get_rect() for s in txts]
   height = reduce(lambda x,y:x+y.height,txtrs,0)
   gap = ( brect.height - height ) / (len(txts) + 1.0)
   g = gap
   for (txt,txtr) in zip(txts,txtrs):
      txtr.centerx = brect.centerx
      txtr.top = brect.top + g
      g += gap + txtr.height
      DISPLAY.blit(txt,txtr)

def plot_question(box,override=None):
   log('> plot_question'+('' if override is None else ' (override)'))

   # Override is a dict used to change the plotting
   # - qcardid : ID of the question card
   # - propositions : list of the IDs of the answer cards
   # - transldir : translation direction
   # - qcolor : color of the question box
   # - acolors : colors of the asnwers boxes

   # Geometrical constants
   gap    = 20
   qwidth = 0.85

   # Basic block size
   blockwidth  = (QRECT.width - 4*gap) / 3.0
   blockheight = (QRECT.height - 5*gap) / 4.0

   # Plot question block
   qrect = pygame.Rect(0,0,QRECT.width*qwidth,blockheight)
   qrect.centerx = QRECT.centerx
   qrect.top     = QRECT.top + gap
   s = pygame.Surface(qrect.size,pygame.SRCALPHA)
   if override is None:
      s.fill(ALPGRAY)
   else:
      s.fill(override['qcolor'])
   DISPLAY.blit(s,qrect)

   # Plot question text
   if override is None:
      qcard = box.database[box.currentCid]
      plot_question_text(qcard,qrect,box.translationDirection,True)
   else:
      qcard = box.database[override['qcardid']]
      plot_question_text(qcard,qrect,override['transldir'],True)
   txt = fonts[12].render('Tirage '+str(box.nPicks),True,(150,150,150))
   txtr = txt.get_rect()
   txtr.left , txtr.top = qrect.left+2 , qrect.top+2
   DISPLAY.blit(txt,txtr)
   txtr.width += 4
   txtr.height += 4
   txtr.left , txtr.top = qrect.left , qrect.top
   pygame.draw.rect(DISPLAY,(150,150,150),txtr,1)

   # Loop over answer rects
   k = 0
   for ii in range(3):
      for j in range(3):
         k += 1

         # Handle reversed Numpad
         if REVERSE_NUMPAD : i = 2-ii
         else              : i = ii

         # Plot answer block
         s = pygame.Surface((blockwidth,blockheight),pygame.SRCALPHA)
         if override is None:
            s.fill(ALPGRAY)
         else:
            s.fill(override['acolors'][k-1])
         arect = s.get_rect()
         arect.left   = QRECT.left   + gap + (blockwidth+gap)*j
         arect.bottom = QRECT.bottom - gap - (blockheight+gap)*i
         DISPLAY.blit(s,arect)

         # Plot answer text
         if override is None:
            acard = box.database[box.propositions[k-1][0]]
            plot_question_text(acard,arect,box.translationDirection,False)
         else:
            acard = box.database[override['propositions'][k-1][0]]
            plot_question_text(acard,arect,override['transldir'],False)
         txt = fonts[12].render(str(k),True,(150,150,150))
         txtr = txt.get_rect()
         txtr.left , txtr.top = arect.left+2 , arect.top+2
         DISPLAY.blit(txt,txtr)
         txtr.width += 4
         txtr.height += 4
         txtr.left , txtr.top = arect.left , arect.top
         pygame.draw.rect(DISPLAY,(150,150,150),txtr,1)

#-----------------------------------------------------------------------
# Animation functions
#-----------------------------------------------------------------------

def animate_question_answer(box,ret,propositions,transldir,answer):
   log('> animate_question_answer ('+str(ret[0])+')')

   # Animate
   if ret[0]: # GOOD answer

      # Clean question zone
      DISPLAY.blit(imgBackground,QRECT,QRECT)

      # Print questions with green colors
      override={}
      override['qcardid']           = ret[1]
      override['propositions']      = propositions
      override['transldir']         = transldir
      override['qcolor']            = ALPGREEN
      override['acolors']           = [ALPGRAY for _ in range(9)]
      override['acolors'][answer-1] = ALPGREEN
      plot_question(box,override)

      # Plot screen for 1 second
      pygame.display.update()
      pygame.time.wait(1000)

   else: # WRONG answer

      # Clean question zone
      DISPLAY.blit(imgBackground,QRECT,QRECT)

      # Print questions with green colors
      override={}
      override['qcardid']           = ret[1]
      override['propositions']      = propositions
      override['transldir']         = transldir
      override['qcolor']            = ALPRED
      override['acolors']           = [ALPGRAY for _ in range(9)]
      override['acolors'][ret[4]]   = ALPGREEN
      override['acolors'][answer-1] = ALPRED
      plot_question(box,override)

      # Plot screen for 10 seconds
      pygame.display.update()
      pygame.time.wait(10000)

#-----------------------------------------------------------------------
# Game functions
#-----------------------------------------------------------------------

def game_question(box,profilenum):

   # Load profile
   log('Load box profile '+profiles[profilenum],1)
   box.load('./saves/'+profiles[profilenum]+'.box')
   log('OK')
   box_modified = False

   # Main loop
   while True:

      # Save every 10 picks
      if box.nPicks % 10 == 0 and box_modified :
         log('Save defaulted box profile',1)
         box.save()
         log('OK')
         box_modified = False

      # Pick a card from the box
      box.pick()
      propositions = box.propositions
      transldir    = box.translationDirection
      log('Picked card '+str(box.currentCid)+' from box')

      # Plot screen
      log('DISPLAY STEP 1')
      DISPLAY.blit(imgBackground,(0,0))
      plot_folders(box)
      plot_avatars(profiles[profilenum])
      plot_question(box)
      log('DISPLAY STEP 2')
      pygame.display.update()
      log('DISPLAY DONE')

      # Wait for user action
      answer = -1
      moving = False
      plotmove = False
      pos = (-1,-1)
      repick = False
      while not repick:

         # Catch events
         if WITH_REMOTE : handle_remote()
         for e in pygame.event.get():

            # Quit event
            if e.type == pygame.QUIT :

               # Save box current status
               box.unpick()
               if box_modified:
                  log('Save defaulted box profile',1)
                  box.save()
                  log('OK')
                  box_modified = False

               # Return quit event
               return ('quit',{})

            # Keydown events
            elif e.type == pygame.KEYDOWN:

               # Q : quit game
               if e.key == pygame.K_q:

                  # Save box current status
                  box.unpick()
                  if box_modified:
                     log('Save defaulted box profile',1)
                     box.save()
                     log('OK')
                     box_modified = False

                  # Return quit event
                  return ('quit',{})

               # P : change profile
               elif e.key == pygame.K_p:

                  # Save box current status
                  box.unpick()
                  if box_modified:
                     log('Save defaulted box profile',1)
                     box.save()
                     log('OK')
                     box_modified = False

                  # Return profile change event
                  next = profilenum+1 if profilenum+1<len(profiles) else 0
                  return ('profile',{'next':next})

               # UP : move to choose answer
               elif e.key == pygame.K_UP:

                  plotmove = True
                  if not moving:
                     moving = True
                     pos = [1,1]
                  else:
                     if REVERSE_NUMPAD : pos[1] = max( pos[1]-1 , 0 )
                     else              : pos[1] = min( pos[1]+1 , 2 )

               # DOWN : move to choose answer
               elif e.key == pygame.K_DOWN:

                  plotmove = True
                  if not moving:
                     moving = True
                     pos = [1,1]
                  else:
                     if REVERSE_NUMPAD : pos[1] = min( pos[1]+1 , 2 )
                     else              : pos[1] = max( pos[1]-1 , 0 )

               # RIGHT : move to choose answer
               elif e.key == pygame.K_RIGHT:

                  plotmove = True
                  if not moving:
                     moving = True
                     pos = [1,1]
                  else:
                     pos[0] = min( pos[0]+1 , 2 )

               # LEFT : move to choose answer
               elif e.key == pygame.K_LEFT:

                  plotmove = True
                  if not moving:
                     moving = True
                     pos = [1,1]
                  else:
                     pos[0] = max( pos[0]-1 , 0 )

               # ENTER : select answer
               elif e.key == pygame.K_RETURN:

                  if not moving:
                     plotmove = True
                     moving = True
                     pos = [1,1]
                  else:
                     answer = 1+pos[0]+3*pos[1]

               # 1-9 : try answer
               elif e.unicode.isdecimal():

                  # New answer
                  answer = int(e.unicode)
                  if answer<1 or answer>9 : answer = -1

         # An answer has been entered
         if answer > 0:
            log('answer given : '+str(answer))

            # Reply this answer
            ret = box.reply(answer)
            box_modified = True

            # Animate
            animate_question_answer(box,ret,propositions,transldir,answer)

            # Needs to pick an other card
            repick = True

         # Replot question screen if cursor moved
         if plotmove:
            log('cursor move')
            plotmove = False
            log('DISPLAY STEP 1')
            DISPLAY.blit(imgBackground,QRECT,QRECT)
            override={}
            override['qcardid']           = box.currentCid
            override['propositions']      = box.propositions
            override['transldir']         = box.translationDirection
            override['qcolor']            = ALPGRAY
            override['acolors']           = [ALPGRAY for _ in range(9)]
            override['acolors'][pos[0]+3*pos[1]] = ALPGRAY2
            plot_question(box,override)
            log('DISPLAY STEP 2')
            pygame.display.update()
            log('DISPLAY DONE')

         # Wait
         fps = clock.tick(30.0)

#-----------------------------------------------------------------------
# Main loop
#-----------------------------------------------------------------------

while True:

   # Main game program
   log('start game_question')
   ret = game_question(BOX,profilenum)

   # Handle events
   if ret[0] == 'quit' :
      terminate()

   elif ret[0] == 'profile' :
      profilenum = ret[1]['next']


