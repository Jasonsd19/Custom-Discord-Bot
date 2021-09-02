import ffmpeg
import asyncio
import discord
import os
import youtube_dl
from mutagen.mp3 import MP3
from mutagen import MutagenError
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

    #Try to grab audio source
    try:
      #Source is a tuple (audioSource, videoTitle, videoDuration, userInput) - don't like this
      source = self.parseCommand(userInput)
    except youtube_dl.utils.DownloadError as e:
      print(f'Here\'s the exception: {e}')
      await ctx.send(embed=self.createEmbed('Error', "Trouble connecting to the YouTube servers. Please make sure the YouTube link provided is working. If it is try again in a short while."), delete_after=30)
      return
    except OSError as e:
      print(f'Here\'s the exception: {e}')
      await ctx.send(embed=self.createEmbed('Error', "There is no audio clip with the given name."), delete_after=30)
      return
    except Exception as e:
      print(f'I don\'t know what happened lol, here\'s the exception: {e}')
      print(f'And here is the user input {userInput}')
      await ctx.send(embed=self.createEmbed('Error', "Something weird happened, please try again in a short while."), delete_after=30)
      return

    #If queue is empty, we add new song set up the player
    if self.q.isEmpty():
      self.q.add(source)
      #React with emote to denote the request was successful
      await ctx.message.add_reaction("<:pogNuts:827445043018858526>")
      #While queue is not empty, loop through and play all the remaining songs
      while self.q.isEmpty() == False:
        #Current song is the front of the queue (or the head of the linkedlist)
        currentSong = self.q.getHead().getData()
        self.voiceClient.play(currentSong[0])
        #Create and embeded message to let user know we are playing song, this message will be deleted once the song ends
        await ctx.send(embed=self.createEmbed('Playing', currentSong[1]), delete_after=int(currentSong[2]))
        while self.voiceClient.is_playing() or self.voiceClient.is_paused():
          await asyncio.sleep(1)
        self.voiceClient.stop()
        if not self.q.isEmpty():
          self.q.remove(0)
        #If we are looping we simply create another audioSource for the current song and add it to the end of the queue, 
        #If we are removing the song currently being played we do not want to re-add it to queue.
        if self.doLoop == True and self.doRemove == False:
          freshSource = self.parseCommand(currentSong[3])
          self.q.add(freshSource)
        self.doRemove = False
    else:
      self.q.add(source)
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
  async def remove(self, ctx, index):
    #Check if user input integer, if so change to 0 based indexing
    try:
      index = int(index) - 1
    except ValueError:
      await ctx.send(embed=self.createEmbed('Error', "Invalid command format, please give a position in the queue that you want removed."), delete_after=30)
      return
    #Queue must have songs in it to remove
    if not self.q.isEmpty():
      #If we're removing the current song, set doRemove flag to True so we don't re-add it when looping
      if index == 0:
        self.doRemove = True
        self.voiceClient.stop()
        await ctx.message.add_reaction("<:pogNuts:827445043018858526>")
        return
      #Delete song from queue
      try:
        self.q.remove(index)
      except IndexError:
        await ctx.send(embed=self.createEmbed('Error', f'There is no song at position {index + 1} in the queue!'), delete_after=30)
      else:
        await ctx.message.add_reaction("<:pogNuts:827445043018858526>")
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
    name = self.q.getHead().getData()[1]
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
      except ValueError:
        #Input was not an int
        await ctx.send(embed=self.createEmbed('Error', "Invalid command format"), delete_after=30)
        return
      if volume >= 0 and volume <= 1:
        #Set the volume of the current audioSource to specified volume
        self.q.getHead().getData()[0].volume = volume

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
    #Need context to invoke leave function
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
        if search[0] == '-':
          #Here we search for a youtube video with the given search
          info = ydl.extract_info(f"ytsearch:{search[1:]}", download=False)['entries'][0]
          url = info['url']
          title = info['title']
          duration = info['duration']
        else:
          #Here we directly access the video with the given url
          #The return value is different for search and direct link lookup, so we handle finding the title differently
          info = ydl.extract_info(search, download=False)
          url = info['url']
          title = info['title']
          duration = info['duration']
        return (discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(url, **ffmpegOptions)), title, duration, search)
      except youtube_dl.utils.DownloadError as e:
        #Either we were given a broken link or the youtube servers are having trouble (these are the most likely reasons, I think anyways)
        raise e
      except Exception as e:
        #Hopefully we never get here :)
        raise e

  def getAudioClip(self, search):
    try:
      path = 'audio/' + search + '.mp3'
      if os.path.exists(path):
        audioFile = MP3(path)
        duration = int(audioFile.info.length)
        return (discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(path)), search + '.mp3', duration, search)
      else:
        #Specified clip doesn't exist
        raise OSError("Clip with given name doesn't exist")
    #We get this exception when the mp3 doesn't have the correct headers/tags so we can't retrieve the duration
    except MutagenError:
      #For right now I just set the duration to 5 seconds b/c all the clips are usually short - maybe work on a better solution
      duration = 5
      return (discord.PCMVolumeTransformer(discord.FFmpegPCMAudio(path)), search + '.mp3', duration, search)

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
    current = self.q.getHead()
    index = 1
    while current != None:
      minutes = current.data[2] // 60
      seconds = current.data[2] % 60
      result += f'{index}) {current.data[1]} - {minutes}:{seconds}\n'
      current = current.next
      index += 1
    return result

# My own scuffed linked list implementation that I use for the queue
class linkedList:
  class Node:
    def __init__(self, data):
      self.data = data
      self.next = None

    def getNext(self):
      return self.next

    def setNext(self, node):
      self.next = node

    def getData(self):
      return self.data
  
  def __init__(self):
    self.size = 0
    self.head = None
    self.rear = None

  def getHead(self):
    return self.head

  def getSize(self):
    return self.size

  def isEmpty(self):
    return self.size == 0

  def add(self, data):
    if self.size == 0:
      self.head = self.Node(data)
      self.rear = self.head
      self.size += 1
      return
    self.rear.next = self.Node(data)
    self.rear = self.rear.next
    self.size += 1

  def remove(self, index):
    if self.size > 0 and index < self.size and index >= 0:
      if index == 0:
          previous = self.head
          self.head = previous.next
          previous.next = None
          self.size -= 1
          return previous
      current = self.head
      previous = None
      for i in range(index):
        previous = current
        current = current.next
      previous.next= current.next
      current.next = None
      self.size -= 1
    else:
      raise IndexError("Invalid index")