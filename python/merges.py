# clear blocks by making them touch potions
# fuse blocks by matching 3 blocks or more of the same color
# (they can only be fused once)
# fusing blocks also brews a potion of the same color

import pygame
from pygame.locals import *

import sys
import os
import random
import math

WINDOWWIDTH = 600
WINDOWHEIGHT = 600
NUMCOLORS = 6
BLOCKSIZE = 40
BOARDSIZE = 6   # amount of stacks
BOARDWIDTH = BOARDSIZE * BLOCKSIZE
STACKLEVEL = 5  # amount of blocks
STACKSIZE = 10
BOARDHEIGHT = STACKSIZE * BLOCKSIZE
#DX = 10
#DY = 25
DEATHTIME = 60

NUMBLOCKTYPES = 1

BLOCKS = {0:'BLOCK',1:'FLASK'}
COLORS = {-1:'EMPTY',0:'RED',1:'GREEN',2:'BLUE',3:'ORANGE',4:'YELLOW',5:'WHITE'}
COLOURS = {-1:(150,100,100),0:(255,0,0),1:(0,255,0),2:(0,0,255),3:(0,255,255),4:(255,255,0),5:(255,255,255)}

pygame.init()
pygame.display.set_caption("Puzzle")
os.chdir(os.path.abspath(os.path.dirname(sys.argv[0])))
clock = pygame.time.Clock()
pygame.mixer.music.load('music.mp3')
pygame.mixer.music.set_volume(0)
pygame.mixer.music.play(-1)
blockSprites = {}
playerSprites = {}

screen = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT), 0, 32)

for c in range(NUMCOLORS):
   blockSprites[c] = pygame.image.load('%s.gif'%COLORS[c]).convert_alpha()
#for c in range(-1,NUMCOLORS):
#   flaskSprites[c] = pygame.image.load('FLASK_%s.gif'%COLORS[c]).convert_alpha()

playerSprites[0] = pygame.image.load('CURSOR.gif').convert_alpha()
playerSprites[1] = pygame.transform.scale2x(pygame.image.load('wizard.jpg').convert_alpha())

class Board():
   def __init__(self,pos,size = BOARDSIZE):
      self.x, self.y = pos[0], pos[1]
      self.size = size
      self.stacks = []
      self.rect = pygame.Rect(self.x,self.y,BOARDWIDTH,BOARDHEIGHT)
      print self
      for s in range(size):
         self.stacks.append(Stack(self,s,STACKLEVEL))
         print self.stacks[s],s
      self.player = Player(self,4)
      pygame.draw.rect(screen, (0,0,0), (0, 0, BOARDWIDTH, BOARDHEIGHT))
   def printBoard(self):
      print
      for s in range(BOARDSIZE):
         self.stacks[s].printStack()
         if s == player.pos:
            for i in range(STACKSIZE - self.stacks[s].size - player.size):
               print 'X',
            player.printStack()
            print '<',player.popSize,
         else:
            for i in range(STACKSIZE - self.stacks[s].size):
               print 'X',
         print
      print

class Stack():
   def __init__(self,board,pos,size = STACKLEVEL):
      self.board = board
      self.pos = pos # 0 to 5
      self.size = size
      self.blocks = [] # contain blocks
      self.checked = False

      self.fill()      

   def fill(self):
      for b in range(self.size):
         self.blocks.append(Block(self.board,self,(self.pos,b),random.randint(0,NUMCOLORS-1),BLOCKS[random.randint(0,NUMBLOCKTYPES-1)]))
#         print self.blocks[b],b, 'color', self.blocks[b].color

   def update(self):
      for b in range(self.size):
         self.blocks[b].update(self,b)
   def printStack(self):
      dont = False
      count = 0
      for b in range(self.size):
         if self.blocks[b].deathclock <= 0:
            self.blocks[b].destroy() # <---
            dont = True
            self.printStack()
            break
         count += 1
      for b in range(count):
      #for b in range(self.size):
         block = self.blocks[b]
         if dont: break
         if block.breaking:
            print '!',
         else:
            if block.connected:
               if not block.top:
                  print 'T',
               elif not block.bottom:
                  print 'B',
               else:
                  print 'M',
            else:
               print block.color, # terminal
         block.render()
         self.checked = False

   # connect blocks of the same color if not connected yet
   def match(self,pos):
      count = 0
      matches = []

      # go through each block in the stack
      for b in range(self.size):
         # put the first block into matches[]
         if b == 0:
            prev_color = self.blocks[b].color
            matches.append(self.blocks[b])

         # last block in the stack
         elif b == self.size-1:
            # the current block
            this = self.blocks[b]
            color = this.color
            match = matches.pop()
            matches.append(match)
            # if they match
            if color == prev_color:
               # if matches are not breaking and not connected
               if not match.breaking and not match.connected:
                  # add current block to matches
                  matches.append(this)
            # connect blocks if three or more match
            if len(matches) > 2:
               # go through each block in matches[]
               for m in range(len(matches)):
                  # pop it out of matches[]
                  match = matches.pop()
                  match.connected = True
                  if m == 0:
                     prev_match = match
                     continue
                  match.top.append(prev_match)
                  prev_match.bottom.append(match)
                  prev_match = match

         # middle blocks in the stack
         else:
            # the current block
            this = self.blocks[b]
            color = this.color
            if color == prev_color:
               match = matches.pop()
               matches.append(match)
               # if matches not breaking and not connected
               if not match.breaking and not match.connected:
                  # add current block to matches
                  matches.append(this)
            # if they don't match
            else:
               count = len(matches)
               # go through each block in matches[]
               for m in range(count):
                  # pop it out of matches[]
                  match = matches.pop()
                  # connect blocks if three or more match
                  if count > 2:
                     match.connected = True
                     if m == 0:
                        prev_match = match
                        continue
                     match.top.append(prev_match)
                     prev_match.bottom.append(match)
                     prev_match = match
               matches.append(this)
            # current color now prev color for next iteration
            prev_color = color

   # break blocks of the same color if touching potion of same color
   def potion(self,pos):
      count = 0
      matches = []

      # go through each block in the stack
      for b in range(self.size):
         # put the first block into matches[]
         if b == 0:
            prev_color = self.blocks[b].color
            matches.append(self.blocks[b])

         # last block in the stack
         elif b == self.size-1:
            # the current block
            this = self.blocks[b]
            color = this.color
            match = matches.pop()
            matches.append(match)
            # if they match
            if color == prev_color:
               # if matches already breaking, just add to chain
               if match.breaking:
                  if not this.breaking:
                     # add to chain if also not breaking
                     this.chain = match.chain + 1
               else:
                  # update chain of matches
                  for match in matches:
                     match.chain = this.chain
                  # add current block to matches if if not breaking
                  matches.append(this)
            # if they don't match
            else:
               # add to chain if match is breaking
               this.chain = match.chain + 1
            # break blocks if three or more match
            if len(matches) > 2:
               # go through each block in matches[]
               for m in range(len(matches)):
                  # pop it out of matches[]
                  match = matches.pop()
                  match.matched = True

         # middle blocks in the stack
         else:
            # the current block
            this = self.blocks[b]
            color = this.color
            if color == prev_color:
               match = matches.pop()
               matches.append(match)
               # if matches already breaking, just add to chain
               if match.breaking:
                  if not this.breaking:
                     # add to chain if also not breaking
                     this.chain = match.chain + 1
               else:
                  # update chain of matches
                  for match in matches:
                     match.chain = this.chain
                  # add current block to matches if if not breaking
                  matches.append(this)
            # if they don't match
            else:
               count = len(matches)
               # go through each block in matches[]
               for m in range(len(matches)):
                  # pop it out of matches[]
                  match = matches.pop()
                  # add to chain if match is breaking
                  if match.breaking:
                     this.chain = match.chain + 1
                  # break blocks if three or more match
                  if count > 2:
                     match.matched = True
               matches.append(this)
            # current color now prev color for next iteration
            prev_color = color

class Player(Stack):
   def __init__(self,board,pos,size = 0):
      Stack.__init__(self,board,pos,size)
      self.popSize = 0

      self.x = board.x + self.pos * BLOCKSIZE
      self.y = board.y + BOARDHEIGHT - (board.stacks[self.pos].size+1) * BLOCKSIZE

      self.sprite = playerSprites[0]
      self.rect = pygame.Rect(self.x, self.y, BLOCKSIZE, BLOCKSIZE)

      self.new_x = self.x
      self.new_y = self.y

      self.avatar = playerSprites[1]
      self.avatarRect = pygame.Rect(WINDOWWIDTH/2 + 50, 100, 200, 200)

   def printStack(self):
      for b in range(self.size):
         print self.blocks[self.size-1-b].color, #terminal
         self.blocks[self.size-1-b].render()

   def pop(self,pos):
      # pop from current stack and push onto player stack
      block = player.board.stacks[pos].blocks.pop()
      self.blocks.append(block)
      self.size += 1
      self.board.stacks[pos].size -= 1
      # update popped block
      block.update(self,self.size-1)
      return block

   def drop(self,pos):
      # drop contents of player stack onto current stack
      block = self.blocks.pop()
      self.board.stacks[pos].blocks.append(block)
      self.size -= 1
      self.board.stacks[pos].size += 1
      # update dropped block
      block.update(self.board.stacks[pos],self.board.stacks[pos].size-1)

      # check for matches
      #self.board.stacks[pos].match(pos)
      #self.update()

   def update(self):
      Stack.update(self)
      self.new_x = self.board.x + self.pos * BLOCKSIZE
      if self.size == 0:
         self.new_y = self.board.y + BOARDHEIGHT - (self.board.stacks[self.pos].size - self.popSize + 1) * BLOCKSIZE
      else:
         self.new_y = self.board.y + (self.size-1) * BLOCKSIZE

   def updateRect(self):
      dx = abs(self.x-self.new_x)/2
      dy = abs(self.y-self.new_y)/2
      if self.x < self.new_x: self.x += dx
      elif self.x > self.new_x: self.x -= dx
      if self.y < self.new_y: self.y += dy
      elif self.y > self.new_y: self.y -= dy
      if abs(self.x-self.new_x) > dx: self.x = self.new_x
      if abs(self.y-self.new_y) > dy: self.y = self.new_y
      self.rect.x, self.rect.y = self.x, self.y
   def render(self):
      #screen.blit(self.image, (self.x,self.y))
      self.updateRect()
      if self.size == 0:
         screen.blit(self.sprite, (self.x,self.y))
      #pygame.draw.rect(screen, (100,100,100,100) , self.rect)
      screen.blit(self.avatar, self.avatarRect)

# maybe use this later
class Inventory(Stack):
   def __init__(self,board,pos,size = STACKLEVEL):
      Stack.__init__(self,board,pos,size)
      self.fill()

   def fill(self):
      for b in range(self.size):
         self.blocks.append(Flask(self.board,self,(self.pos,b),-1))
         print 'flask',self.blocks[b]
      
class Block():
   def __init__(self,board,stack,pos,color,type='BLOCK'):
      self.board = board
      self.stack = stack
      self.col = pos[0]
      self.row = pos[1]
      self.color = color
      self.type = type
      self.x = board.x + self.col * BLOCKSIZE
      self.y = board.y + BOARDHEIGHT - (1 + self.row) * BLOCKSIZE
      self.new_x = self.x
      self.new_y = self.y
      self.breaking = False
      self.connected = False
      self.top = []  # (not self.top) means it's empty
      self.bottom = []
      self.chain = 0
      self.deathclock = DEATHTIME
      if type == 'BLOCK':
         self.sprite = blockSprites[self.color]
      self.rect = pygame.Rect(self.x, self.y, BLOCKSIZE, BLOCKSIZE)
   def update(self,stack,pos):
      self.stack = stack
      self.row = pos
      self.col = stack.pos
      self.new_x = self.board.x + self.col * BLOCKSIZE
      if stack == player:
         self.new_y = self.board.y + (self.row) * BLOCKSIZE
         self.chain = 0 # reset chain
      else:
         self.new_y = self.board.y + BOARDHEIGHT - (1 + self.row) * BLOCKSIZE
   def updateRect(self):
      dx = abs(self.x-self.new_x)/2
      dy = abs(self.y-self.new_y)/2
      if self.x < self.new_x: self.x += dx
      elif self.x > self.new_x: self.x -= dx
      if self.y < self.new_y: self.y += dy
      elif self.y > self.new_y: self.y -= dy
      if abs(self.x-self.new_x) > dx: self.x = self.new_x
      if abs(self.y-self.new_y) > dy: self.y = self.new_y
      self.rect.x, self.rect.y = self.x, self.y
   def render(self):
      self.updateRect()
      if self.breaking:
         if self.deathclock > 0:
            self.deathclock -= 1
         pygame.draw.rect(screen, (100,100,100), self.rect)
      elif self.connected:
         pygame.draw.rect(screen, COLOURS[self.color], self.rect)
      else:
         if self.type == 'BLOCK':
            screen.blit(self.sprite, (self.x,self.y))
         elif self.type == 'FLASK':
            pygame.draw.rect(screen, (32,32,43), self.rect)           
         #pygame.draw.rect(screen, COLOURS[self.color], self.rect)
   def destroy(self):
      # remove from stack
      self.stack.blocks.remove(self)
      # update size of stack
      self.stack.size -= 1
      # update positions of blocks after it in stack
      self.stack.update()

class Flask(Block):
   def __init__(self,board,stack,pos,color):
      self.board = board
      self.stack = stack
      self.col = pos[0]
      self.row = pos[1]
      self.color = color
      self.x = board.x + self.col * BLOCKSIZE
      self.y = board.y + BOARDHEIGHT - (1 + self.row) * BLOCKSIZE
      self.new_x = self.x
      self.new_y = self.y
      self.breaking = False
      self.chain = 0
      self.deathclock = DEATHTIME
      #self.sprite = flaskSprites[self.color]
      self.rect = pygame.Rect(self.x, self.y, BLOCKSIZE, BLOCKSIZE)
   def render(self):
      self.updateRect()
      if self.breaking:
         if self.deathclock > 0:
            self.deathclock -= 1
         pygame.draw.rect(screen, (100,100,100), self.rect)
      else:
         #screen.blit(self.sprite, (self.x,self.y))
         pygame.draw.rect(screen, COLOURS[self.color], self.rect)


playerBoard = Board((WINDOWWIDTH/2 - BOARDWIDTH,WINDOWHEIGHT/2 - .35*BOARDHEIGHT))
player = playerBoard.player
      
def inGame():
   screen.fill((0, 75, 75))
   for event in pygame.event.get():
      if event.type == QUIT:
         sys.exit()
      if event.type == KEYDOWN:
         pos = player.pos
         if event.key == K_ESCAPE:
            pygame.quit()
            sys.exit()
         if event.key == K_a:
            if player.pos > 0 and \
              player.size <= STACKSIZE - player.board.stacks[pos-1].size:
               player.pos -= 1
            player.popSize = 0
         if event.key == K_d:
            if player.pos < BOARDSIZE - 1 and \
              player.size <= STACKSIZE - player.board.stacks[pos+1].size:
               player.pos += 1
            player.popSize = 0
         if event.key == K_j:
            stack = player.board.stacks[pos]  # current stack
            # lower hand if hand is empty
            if player.size == 0:
               # increase popSize until reach a non-connected block
               if player.popSize < stack.size:
                  player.popSize += 1
                  while stack.blocks[stack.size-player.popSize].bottom:
                     player.popSize += 1
            else:
               bottom = player.blocks.pop()
               player.blocks.append(bottom)
               # keep dropping until not connected block at top
               if bottom.connected:
                  while bottom.connected and player.size > 0:
                     player.drop(pos)
                     if player.size > 0:
                        if not bottom.top: break
                        bottom = player.blocks.pop()
                        player.blocks.append(bottom)
                     print 'drop'
               else:
                  player.drop(pos)

         if event.key == K_k:
            if player.size == 0:
               if player.popSize == 0:
                  player.popSize = player.board.stacks[pos].size
                  for b in range(player.popSize):
                     block = player.pop(pos)
                     if block.breaking:
                        print 'putting it back'
                        player.drop(pos)
                        break
               else:
                  for b in range(player.popSize):
                     player.pop(pos)
               player.popSize = 0
            else:
               for b in range(player.size):
                  player.drop(pos)

         player.update()

   # check matches
   for stack in player.board.stacks:
      print 'checking, boss',stack
      stack.match(stack.pos)

   pygame.draw.rect(screen, (0,0,0), player.board.rect)
   player.board.printBoard()

   player.render()
         
while True:
   inGame()
   clock.tick(60)
   pygame.display.flip()
