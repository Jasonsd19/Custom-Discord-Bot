import datetime
import ffmpeg
import asyncio
import discord
import os
import youtube_dl
from requests import get
from discord.ext import tasks, commands

class audioPlayer(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.voiceClient = None
    self.isPlaying = False
    #Start loop to check for inactivity
    self.Context = None
    self.q = queue()
    self.checkInactivity.start()

  @commands.command(description='$play [filename]\nFilename has to be a file in a local directory\nThe bot will join the voice channel the user is in, play the audio file, then leave.',
help='Allows the bot to join in the voice chat and play an audio file!')
  async def play(self, ctx, *args):
    name = ' '.join(args)
    #Grabbing context for inactivityCheck loop - seems janky must be better way
    self.Context = ctx
    if name == 'list':
      await ctx.send(self.listClips())
      return

    #connect to voice channel if not in a voice channel currently
    #or connect to a different voice channel from the one we are currently in
    userVoiceClient = ctx.author.voice
    if self.voiceClient == None and userVoiceClient:
      self.voiceClient = await userVoiceClient.channel.connect()
      await asyncio.sleep(0.1)
    elif userVoiceClient and userVoiceClient.channel != self.voiceClient.channel:
      await ctx.invoke(self.bot.get_command('leave'))
      await asyncio.sleep(0.1)
      self.voiceClient = await userVoiceClient.channel.connect()
      await asyncio.sleep(0.1)
    elif userVoiceClient.channel == self.voiceClient.channel:
      #Do nothing
      pass
    else:
      await ctx.send("You need to be in a voice channel!")
      return

    #we only play music if we are not currently playing music
    if self.isPlaying == False:
      source = self.parseCommand(name)
      self.q.enqueue(source)
      await ctx.send("Added " + source[1] + " to the queue!")
      while self.q.isEmpty() == False:
        #flags that we are now playing music, deters future calls
        self.isPlaying = True
        try:
          self.voiceClient.play(self.q.peek().data[0])
        except:
          await ctx.send("Unable to play music file, please check command format is correct.")

        while self.voiceClient.is_playing() or self.voiceClient.is_paused():
          await asyncio.sleep(0.1)
        await asyncio.sleep(1)
        self.voiceClient.stop()
        self.q.dequeue()
        self.isPlaying = False
    else:
      source = self.parseCommand(name)
      self.q.enqueue(source)
      await ctx.send("Added " + source[1] + " to the queue!")

  @commands.command()
  async def pause(self, ctx):
    if self.voiceClient != None and self.voiceClient.is_playing():
      self.voiceClient.pause()
      return

  @commands.command()
  async def resume(self, ctx):
    if self.voiceClient != None and self.voiceClient.is_paused():
      self.voiceClient.resume()
      return

  @commands.command()
  async def stop(self, ctx):
    if (self.voiceClient != None and (self.voiceClient.is_playing() or self.voiceClient.is_paused())):
      self.voiceClient.stop()

  @commands.command()
  async def leave(self, ctx):
    if self.voiceClient != None:
      if self.voiceClient.is_playing() or self.voiceClient.is_paused():
        self.voiceClient.stop()
      await self.voiceClient.disconnect()
      self.clearVars()

  @tasks.loop(seconds=30)
  async def checkInactivity(self):
    if self.voiceClient != None and len(self.voiceClient.channel.members) == 0:
      await self.Context.invoke(self.bot.get_command('leave'))

  def parseCommand(self, name):
    #Determines whether the commands is to play a youtube link,
    #search and play a song on youtube, or play an audio clip
    if (('youtube.com' in name) or ('youtu.be' in name)):
      return self.grabYTVideo(name)
    #here '-' symbolises a youtube search
    elif len(name) > 1 and name[0] == '-':
      return self.grabYTVideo(name[1:])
    else:
      return (discord.FFmpegPCMAudio('audio/' + name + '.mp3'), name)

  def grabYTVideo(self, name):
    ydlOptions = {
    'format': 'bestaudio/best',
    'noplaylist': True}
    ffmpegOptions = {
      'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    with youtube_dl.YoutubeDL(ydlOptions) as ydl:
      try:
        #if the get request fails then we have a search string, not a url
        get(name)
      except:
        info = ydl.extract_info(f"ytsearch:{name}", download=False)['entries'][0]
        url = info['url']
        title = info['title']
      else:
        info = ydl.extract_info(name, download=False)
        url = info['formats'][0]['url']
        title = info['title']
      return (discord.FFmpegPCMAudio(url, **ffmpegOptions), title)

  def clearVars(self):
      self.voiceClient = None
      self.isPlaying = False

  def listClips(self):
    #TODO - Super ugly, try to format names and make it look nice
    result = ''
    files = os.listdir('audio/')
    i = 0
    for file in files:
      name = file.split('.')[0]
      if i%5 == 0 and i != 0:
        result += '[' + name + '] \n'
      else:
        result += '[' + name + '] '
      i += 1
    return result

class queue:
  class linkedList:
    class node:
      def __init__(self, data):
        self.data = data
        self.next = None
    
    def __init__(self):
      self.size = 0
      self.head = None

    def add(self, data):
      if self.size == 0:
        self.head = self.node(data)
        self.size += 1
        return
      current = self.head
      while current.next != None:
          current = current.next
      current.next = self.node(data)
      self.size += 1

    def remove(self, index):
      if index == 0:
          current = self.head
          self.head = current.next
          current.next = None
          self.size -= 1
          return
      if index <= self.size:
        current = self.head
        previous = None
        for i in range(index):
          previous = current
          current = current.next
        previous.next= current.next
        current.next = None
        self.size -= 1
        
    def length(self):
      return self.size

  def __init__(self):
    self.lList = self.linkedList()
    self.front = None
    self.rear = None

  def enqueue(self, data):
    self.lList.add(data)
    if self.front == None:
      self.front = self.lList.head
      self.rear = self.lList.head
      return
    self.rear = self.rear.next

  def dequeue(self):
    if self.size == 0:
      return
    self.front = self.front.next
    self.lList.remove(0)
    if self.front == None:
      self.rear = None

  def peek(self):
    return self.front

  def size(self):
    return self.lList.length()

  def isEmpty(self):
    return self.size() == 0

  def printQueue(self):
    result = ''
    current = self.front
    while current != None:
      result += str(current.data[1]) + '---->'
      current = current.next
    return result
    