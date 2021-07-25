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
    #Start loop to check for inactivity
    self.Context = None
    self.doLoop = False
    self.doRemove = False
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
    if userVoiceClient:
      if self.voiceClient == None:
        self.voiceClient = await userVoiceClient.channel.connect()
        await asyncio.sleep(0.1)
      elif userVoiceClient.channel != self.voiceClient.channel:
        await ctx.invoke(self.bot.get_command('leave'))
        await asyncio.sleep(0.1)
        self.voiceClient = await userVoiceClient.channel.connect()
        await asyncio.sleep(0.1)
      else:
        #Bot and user are in same voice channel - Do Nothing
        pass
    else:
      await ctx.send("You need to be in a voice channel!")
      return

    #Try to grab audio source - TODO Need to handle HTTP 403 and os errors
    try:
      source = self.parseCommand(name)
    except:
      await ctx.send("Unable to play music file, please check command format is correct. If it's correct try again in a short while.")
      return

    #we only play music if we are not currently playing music
    if self.q.isEmpty():
      self.q.enqueue(source)
      await ctx.send("Added " + source[1] + " to the queue!")
      while self.q.isEmpty() == False:
        currentSong = self.q.peek().data
        self.voiceClient.play(currentSong[0])
        while self.voiceClient.is_playing() or self.voiceClient.is_paused():
          await asyncio.sleep(1)
        self.voiceClient.stop()
        self.q.dequeue()
        if self.doLoop == True and self.doRemove == False:
          #Grab fresh audio source for the current song and requeue it to loop
          freshSource = self.parseCommand(currentSong[2])
          self.q.enqueue(freshSource)
        self.doRemove = False
    else:
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
  async def remove(self, ctx, *args):
    name = ' '.join(args)
    if not self.q.isEmpty():
      if name == self.q.peek().data[1]:
        self.doRemove = True
        self.voiceClient.stop()
        await ctx.send("Removed " + name + " from queue!")
        return
      current = self.q.front.next
      index = 1
      while current != None:
        if current.data[1] == name:
          self.q.lList.remove(index)
          await ctx.send("Removed " + name + " from queue!")
          return
        current = current.next
        index += 1
      await ctx.send("Song " + name + " is not in queue.")
      return
    await ctx.send("Queue is empty")

  @commands.command()
  async def loop(self, ctx):
    if self.voiceClient != None:
      if self.doLoop == False:
        self.doLoop = True
        await ctx.send("We are now looping music")
      else:
        self.doLoop = False
        await ctx.send("We are now not looping music")

  @commands.command()
  async def leave(self, ctx):
    if self.voiceClient != None:
      self.doLoop = False
      if not self.q.isEmpty():
        self.q = queue()
        self.voiceClient.stop()
        #Wait for other processes to finish before disconnecting
        await asyncio.sleep(1)
      await self.voiceClient.disconnect()
      self.doRemove = False
      self.Context = None
      self.voiceClient = None

  @commands.command()
  async def skip(self, ctx):
    if self.q.isEmpty():
      await ctx.send("Queue is already empty!")
      return
    name = self.q.peek().data[1]
    self.voiceClient.stop()
    await ctx.send("Skipped " + name + "!")
    return

  @commands.command()
  async def volume(self, ctx, volume):
    if self.voiceClient.is_playing() or self.voiceClient.is_paused():
      try:
        volume = int(volume)
        volume = volume / 100
      except:
        await ctx.send("Invalid command format")
        return
      if volume >= 0 and volume <= 1:
        self.q.peek().data[0].volume = volume

  @commands.command()
  async def list(self, ctx):
    if self.q.isEmpty():
      await ctx.send(embed=self.createEmbed("The queue is empty."))
      return
    await ctx.send(embed=self.createEmbed(self.printQueue()))

  @tasks.loop(seconds=30)
  async def checkInactivity(self):
    if self.voiceClient != None and len(self.voiceClient.channel.members) == 1:
      await self.Context.invoke(self.bot.get_command('leave'))

  def parseCommand(self, name):
    #Determines whether the commands is to play a youtube link,
    #search and play a song on youtube, or play an audio clip
    if (('youtube.com' in name) or ('youtu.be' in name)) or (len(name) > 1 and name[0] == '-'):
      #here '-' symbolises a youtube search instead of a url
      return self.grabYTVideo(name)
    else:
      return self.getAudioClip(name)

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
        info = ydl.extract_info(f"ytsearch:{name[1:]}", download=False)['entries'][0]
        url = info['url']
        title = info['title']
      else:
        info = ydl.extract_info(name, download=False)
        url = info['formats'][0]['url']
        title = info['title']
      try:
        #Randomly got a HTTP 403 Forbidden error once, placeholder to handle that for now
        return (discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url, **ffmpegOptions)), title, name)
      except:
        raise Exception()

  def getAudioClip(self, name):
    # I don't like this implementation btw
    title = name + '.mp3'
    if title in os.listdir('audio/'):
      return (discord.PCMVolumeTransformer(discord.FFmpegPCMAudio('audio/' + name + '.mp3')), title, name)
    else:
      #TODO - Choose specific exception
      raise Exception()

  def createEmbed(self, content):
    embed = discord.Embed()
    embed.add_field(name='Queue', value=content, inline=False)
    return embed

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

  def printQueue(self):
    result = ''
    current = self.q.front
    index = 1
    while current != None:
      result += str(index) + ' ' + str(current.data[1]) + '\n'
      current = current.next
      index += 1
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

    def get(self, index):
      if index <= self.size:
        if index == 0:
          return self.head
        current = self.head
        for i in range(index):
          current = current.next
        return current
        
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
    if self.size() == 0:
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