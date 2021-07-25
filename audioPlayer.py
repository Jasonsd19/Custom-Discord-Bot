import datetime
import ffmpeg
import asyncio
import discord
import os
import youtube_dl
from mutagen.mp3 import MP3
from requests import get
from discord.ext import tasks, commands

class audioPlayer(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.voiceClient = None
    self.q = linkedList()
    self.Context = None
    #True means we will loop all songs in queue
    self.doLoop = False
    #True means we are currently removing a song (used in play() and remove())
    self.doRemove = False
    #Start loop to check for inactivity
    self.checkInactivity.start()

  @commands.command(description='$play [filename]\nFilename has to be a file in a local directory\nThe bot will join the voice channel the user is in, play the audio file.',
help='Allows the bot to join in the voice chat and play an audio file!')
  async def play(self, ctx, *args):
    #The play function seems overloaded, it does too many things
    userInput = ' '.join(args)
    #Grabbing context for inactivityCheck loop - seems janky must be better way
    self.Context = ctx

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
      await ctx.send(embed=self.createEmbed('Error', "You need to be in a voice channel!"), delete_after=30)
      return

    #Try to grab audio source - TODO Need to handle HTTP 403 and os errors
    try:
      #Source is a tuple (audioSource, videoTitle, videoDuration, userInput) - don't like this
      source = self.parseCommand(userInput)
    except:
      await ctx.send(embed=self.createEmbed('Error', "Unable to play music file, please check command format is correct. If it's correct try again in a short while.", delete_atfer=30))
      return

    #If queue is empty, we add new song set up the player
    if self.q.isEmpty():
      self.q.add(source)
      # await ctx.send("Added " + source[1] + " to the queue!")
      #React with emote to denote the request was successful
      await ctx.message.add_reaction("<:pogNuts:827445043018858526>")
      #While queue is not empty, loop through and play all the remaining songs
      while self.q.isEmpty() == False:
        #Current song is the front of the queue (or the head of the linkedlist)
        currentSong = self.q.head.data
        self.voiceClient.play(currentSong[0])
        #Create and embeded message to let user know we are playing song, this message will be deleted once the song ends
        await ctx.send(embed=self.createEmbed('Playing', currentSong[1]), delete_after=int(currentSong[2]))
        while self.voiceClient.is_playing() or self.voiceClient.is_paused():
          await asyncio.sleep(1)
        self.voiceClient.stop()
        self.q.remove(0)
        #If we are looping we simply create another audioSource for the current song and add it to the end of the queue, 
        #If we are removing the song currently being played we do not want to re-add it to queue.
        if self.doLoop == True and self.doRemove == False:
          freshSource = self.parseCommand(currentSong[3])
          self.q.add(freshSource)
        self.doRemove = False
    else:
      self.q.add(source)
      # await ctx.send("Added " + source[1] + " to the queue!")
      await ctx.message.add_reaction("<:pogNuts:827445043018858526>")

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
    #Queue must have songs in it to remove
    if not self.q.isEmpty():
      #If we're removing the current song being played we do not want it re-added if looping is True
      if name == self.q.head.data[1]:
        self.doRemove = True
        self.voiceClient.stop()
        # await ctx.send("Removed " + name + " from queue!")
        await ctx.message.add_reaction("<:pogNuts:827445043018858526>")
        return
      #Song to be removed is not current song so we start at index 1
      current = self.q.head.next
      index = 1
      while current != None:
        #Loop until we find the correct song if it exists
        if current.data[1] == name:
          self.q.remove(index)
          # await ctx.send("Removed " + name + " from queue!")
          await ctx.message.add_reaction("<:pogNuts:827445043018858526>")
          return
        current = current.next
        index += 1
      #If we reach end of list without finding song, it doesn't exist
      await ctx.send(embed=self.createEmbed('Error', f'Song {name} is not in the queue'), delete_after=30)
      return
    await ctx.send(embed=self.createEmbed('Error', "Queue is empty"), delete_after=30)

  @commands.command()
  async def loop(self, ctx):
    if self.voiceClient != None:
      if self.doLoop == False:
        self.doLoop = True
        await ctx.send(embed=self.createEmbed('Success', "We are now looping music"), delete_after=30)
      else:
        self.doLoop = False
        await ctx.send(embed=self.createEmbed('Success', "We are no longer looping music"), delete_after=30)

  @commands.command()
  async def leave(self, ctx):
    if self.voiceClient != None:
      self.doLoop = False
      if not self.q.isEmpty():
        self.q = linkedList()
        self.voiceClient.stop()
        #Wait for other processes to finish before disconnecting
        await asyncio.sleep(1)
      await self.voiceClient.disconnect()
      #Reset instance variables
      self.doRemove = False
      self.Context = None
      self.voiceClient = None

  @commands.command()
  async def skip(self, ctx):
    if self.q.isEmpty():
      await ctx.send(self.createEmbed('Error', "Queue is already empty!"), delete_after=30)
      return
    name = self.q.head.data[1]
    self.voiceClient.stop()
    await ctx.send(embed=self.createEmbed('Success', f'Skipped {name}!'), delete_after=30)
    return

  @commands.command()
  async def volume(self, ctx, volume):
    if self.voiceClient.is_playing() or self.voiceClient.is_paused():
      try:
        #Cast input to int
        volume = int(volume)
        volume = volume / 100
      except:
        #Input was not an int
        await ctx.send(embed=self.createEmbed('Error', "Invalid command format"), delete_after=30)
        return
      if volume >= 0 and volume <= 1:
        #Set the volume of the current audioSource to specified volume
        self.q.head.data[0].volume = volume

  @commands.command()
  async def queue(self, ctx):
    #Send an embed displaying current queue of songs and their durations
    if self.q.isEmpty():
      await ctx.send(embed=self.createEmbed('Queue',"The queue is empty."))
      return
    await ctx.send(embed=self.createEmbed('Queue', self.printQueue()))

  @commands.command()
  async def clips(self, ctx):
    #Send a message containing names of audio clips that can be played
    await ctx.send(self.listClips())

  @tasks.loop(seconds=30)
  async def checkInactivity(self):
    #Check if we're the only ones in the voice channel
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

  def grabYTVideo(self, search):
    #Options specify to grab best audio possible, and to not grab playlists
    ydlOptions = {
    'format': 'bestaudio/best',
    'noplaylist': True}
    #Attempt to reconnect if the audioStream is interrupted
    ffmpegOptions = {
      'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
    with youtube_dl.YoutubeDL(ydlOptions) as ydl:
      try:
        #If the get request fails then we have a search string, not a url
        get(search)
      except:
        #Handle the case where the user entered a search
        #Returns a dictionary of search results, we take the first one
        info = ydl.extract_info(f"ytsearch:{search[1:]}", download=False)['entries'][0]
        url = info['url']
        title = info['title']
        duration = info['duration']
      else:
        #Handle the case where the user entered a youtube url
        #Returns a dictionary containing information about the given video
        info = ydl.extract_info(search, download=False)
        url = info['formats'][0]['url']
        title = info['title']
        duration = info['duration']
      try:
        #Randomly got a HTTP 403 Forbidden error once, placeholder to handle that for now
        return (discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url, **ffmpegOptions)), title, duration, search)
      except:
        raise Exception()

  def getAudioClip(self, search):
    # I don't like this implementation btw
    path = 'audio/' + search + '.mp3'
    if os.path.exists(path):
      audioFile = MP3(path)
      duration = int(audioFile.info.length)
      return (discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(path)), search + '.mp3', duration, search)
    else:
      #TODO - Choose specific exception
      raise Exception()

  def createEmbed(self, header, content):
    embed = discord.Embed()
    embed.add_field(name=header, value=content, inline=False)
    return embed

  def listClips(self):
    #TODO - Super ugly, try to format names and make it look nice
    result = ''
    files = os.listdir('audio/')
    i = 0
    for file in files:
      name = file.split('.')[0]
      if i%5 == 0 and i != 0:
        result += f'[{name}]\n'
      else:
        result += f'[{name}]'
      i += 1
    return result

  def printQueue(self):
    #Returns string of names and durations of all songs in queue
    result = ''
    current = self.q.head
    index = 1
    while current != None:
      minutes = current.data[2] // 60
      seconds = current.data[2] % 60
      result += f'{index}) {current.data[1]} - {minutes}:{seconds}\n'
      current = current.next
      index += 1
    return result

# class queue:
class linkedList:
  class node:
    def __init__(self, data):
      self.data = data
      self.next = None
  
  def __init__(self):
    self.size = 0
    self.head = None
    self.rear = None

  def add(self, data):
    if self.size == 0:
      self.head = self.node(data)
      self.rear = self.head
      self.size += 1
      return
    # current = self.head
    # while current.next != None:
    #     current = current.next
    self.rear.next = self.node(data)
    self.rear = self.rear.next
    self.size += 1

  def remove(self, index):
    if index == 0 and self.size > 0:
        temp = self.head
        self.head = temp.next
        temp.next = None
        self.size -= 1
        return
    if index <= self.size and self.size > 0:
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

  def isEmpty(self):
    return self.size == 0

  # def __init__(self):
  #   self.lList = self.linkedList()
  #   self.front = None
  #   self.rear = None

  # def enqueue(self, data):
  #   self.lList.add(data)
  #   if self.front == None:
  #     self.front = self.lList.head
  #     self.rear = self.lList.head
  #     return
  #   self.rear = self.rear.next

  # def dequeue(self):
  #   if self.size() == 0:
  #     return
  #   self.front = self.front.next
  #   self.lList.remove(0)
  #   if self.front == None:
  #     self.rear = None

  # def peek(self):
  #   return self.front

  # def size(self):
  #   return self.lList.length()

  # def isEmpty(self):
  #   return self.size() == 0