import datetime
import ffmpeg
import asyncio
import discord
import os
from discord.ext import tasks, commands

class audioPlayer(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.voiceChannel = None
    # Need this to send message about leaving due to inactivity
    # Maybe there is better solution?
    self.commandContext = None
    ###########################################################
    self.isPlaying = False
    self.leaveTimer = datetime.datetime.now()
    #Start loop to check for inactivity
    self.checkInactivity.start()
    

  @commands.command()
  async def join(self, ctx):
    if self.voiceChannel == None:
      connected = ctx.author.voice
      if connected:
        self.voiceChannel = await connected.channel.connect()
        self.commandContext = ctx
        await asyncio.sleep(1)
        self.leaveTimer = datetime.datetime.now() + datetime.timedelta(minutes=5)
      else:
        await ctx.send("You need to be in a voice channel!")

  @commands.command(description='$play [filename]\nFilename has to be a file in a local directory\nThe bot will join the voice channel the user is in, play the audio file, then leave.',
help='Allows the bot to join in the voice chat and play an audio file!')
  async def play(self, ctx, name):
    if name == 'list':
      await ctx.send(self.listClips())
      return

    if self.voiceChannel != None and self.isPlaying == False:
      self.isPlaying = True
      try:
        self.voiceChannel.play(discord.FFmpegPCMAudio('audio/' + name + '.mp3'))
        while self.voiceChannel.is_playing():
          await asyncio.sleep(0.1)
        await asyncio.sleep(1)
        self.voiceChannel.stop()
      except:
        await ctx.send("Unable to play music file, either you entered an incorrect name or it does not exist.")
      finally:
        self.isPlaying = False
        self.leaveTimer = datetime.datetime.now() + datetime.timedelta(minutes=5)

  @commands.command()
  async def leave(self, ctx):
    if self.voiceChannel != None:
      await self.voiceChannel.disconnect()
      self.voiceChannel = None

  @tasks.loop(seconds=30)
  async def checkInactivity(self):
    if self.voiceChannel != None:
      currentTime = datetime.datetime.now()
      if currentTime > self.leaveTimer:
        await self.voiceChannel.disconnect()
        await self.commandContext.send("I have left due to inactivity.")
        self.voiceChannel = None

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