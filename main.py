import os
import discord
import requests
import ffmpeg
import datetime
import random
import asyncio
from discord.ext import tasks, commands
from keep_alive import keep_alive
from replit import db
from bs4 import BeautifulSoup

import connectFour as c4

bot = commands.Bot(command_prefix='$')

game = discord.Game("$help for more information")

sad_words  = {"sad", "horrible", "lonely", "depressed", ":(", "gloomy", "tragic", "despair", "pain", "forlorn", "hurt", "hurting"}

sleep_words = {"sleep", "sleeping", "going to bed"}

isActive = False
isActive2 = False

#Loop Vars
moveReminder = datetime.datetime.now()
testReminder = datetime.datetime.now()
memeReminder = datetime.datetime.now()
#Loop Vars

#Audio Vars
voiceChannel = None
isPlayingAudio = False
leaveTimer = None
#Audio Vars

#Game Vars
isPlaying = False
player1 = None
player2 = None
gameMessage = None
turn = None
board = None
#Game Vars

winnersID = 817519861906669640

@bot.event
async def on_ready():
  print("We have logged in as {0.user}".format(bot))
  await bot.change_presence(status=discord.Status.online, activity=game)

@bot.event
async def on_message(message):
  global isActive
  global isActive2

  if message.author == bot.user or message.author.bot:
    return

  if message.author != bot.user:
    isActive = True
    isActive2 = True

  if sad_words.intersection(message.content.lower().split()):
    await message.channel.send("Well {0}, This server has friends that still care and love you <:patW:673433778944737310>.".format(message.author.mention))
    return

  if sleep_words.intersection(message.content.lower().split()):
    await message.channel.send("Good night {0}, hope you enjoyed your stay <:peepolove:822337341892853790>.".format(message.author.mention))
    return

  if winnersID in message.raw_role_mentions:
    await message.add_reaction("<:pogNuts:827445043018858526>")
    return

  if bot.user.id in message.raw_mentions:
    if message.author.id == 387855771355840512:
      await message.channel.send("I am at your service oh great and powerful Jason <:o7:822333430166454312>.")
      return
    await message.channel.send("<:wutface:823056657110007839> Don't @ me loser")
    return

  await bot.process_commands(message)

@bot.command(description='See what is trending on WSB.',
             help='Displays the 10 most popular tickers from the WallStreetBets subreddit.')
async def wsb(ctx):
  await ctx.send(topTickers())

@bot.command(description='use format\n$suggest [message]\nTo register your suggestion. Jason can review them later',
help='Simply enter any suggestion and it will be recorded in our database.')
async def suggest(ctx, *, message: str):
  try:
    db["Suggestions"].append(message)
    await ctx.send("Thanks for your suggestion, it has been recorded!")
  except:
    await ctx.send("Sorry there was an error recording your suggestion :(")

@bot.command(description='Lists all the suggestions',
             help='Only Jason can use this :)')
async def list(ctx):
  if ctx.author.id == 387855771355840512:
    result = 'Suggestions:\n'
    i = 1
    for suggestion in db['Suggestions']:
      result += str(i) + ': ' + suggestion + '.\n'
      i += 1
    await ctx.send(result)
  else:
    await ctx.send("Nice try, but you're not Jason.")

@bot.command(description='Delete suggestion at given index\n$remove 0\nWill remove the first suggestion.',
help='Only Jason can use this :)')
async def delete(ctx, index: int):
  if ctx.author.id == 387855771355840512:
    if len(db['Suggestions']) == 0:
      await ctx.send("There is nothing to delete!")
      return
    try:
      removed = db['Suggestions'].pop(index)
      await ctx.send("Successfully removed suggestion:\n" + removed)
    except:
      await ctx.send("Unable to remove given index, perhaps it doesn't exist?")
  else:
    await ctx.send("Nice try, but you're not Jason.")

@bot.command()
async def catFact(ctx):
  await ctx.send(getCatFact())

@bot.command()
async def animalPic(ctx):
  await ctx.send(getAnimalPic())

@bot.command()
async def meme(ctx):
  await ctx.send(getMeme())

@bot.command()
async def insultMe(ctx):
  user = ctx.author.mention
  if ctx.author.id == 387855771355840512:
    await ctx.send("I would never insult my creator.")
  else:
    await ctx.send(user + getInsult())

@bot.command()
async def insult(ctx, mention: str):
  try:
    if mention[0] == '<' and mention[-1] == '>':
      if mention == '<@!387855771355840512>':
        await ctx.send("I would never insult my creator, but I would insult you\n" + ctx.author.mention + getInsult())
      else:
        await ctx.send(mention + ' ' + getInsult())
    else:
      raise Exception("Incorrect format")
  except:
    await ctx.send("Incorrect format")

@bot.command()
async def roll(ctx, dice):
  if dice == "d6":
    r = requests.get('http://roll.diceapi.com/html/d6')
    # Holy jank batman
    text = r.text
    link = text.split("\"")[1]
    await ctx.send(link)
    # Can't believe this worked lol
  elif dice == "d20":
    r = requests.get('http://roll.diceapi.com/html/d20')
    # I'll fkin do it again
    text = r.text
    link = text.split("\"")[1]
    await ctx.send(link)
    # Told you
  else:
    await ctx.send("Invalid format!")

@bot.command()
async def join(ctx):
  global voiceChannel
  global leaveTimer
  if voiceChannel == None:
    connected = ctx.author.voice
    if connected:
      voiceChannel = await connected.channel.connect()
      await asyncio.sleep(1)
      leaveTimer = datetime.datetime.now() + datetime.timedelta(hours=1)
      await asyncio.sleep(3600)
      if datetime.datetime.now() >= leaveTimer and voiceChannel != None:
        await voiceChannel.disconnect()
        await ctx.send("I have left the voice channel due to inactivity.")
        voiceChannel = None
    else:
      await ctx.send("You need to be in a voice channel!")

@bot.command(description='$play [filename]\nFilename has to be a file in a local directory\nThe bot will join the voice channel the user is in, play the audio file, then leave.',
help='Allows the bot to join in the voice chat and play an audio file!')
async def play(ctx, name):
  if name == 'list':
    await ctx.send(listClips())
    return

  global voiceChannel
  global isPlayingAudio
  global leaveTimer
  if voiceChannel != None and isPlayingAudio == False:
    isPlayingAudio = True
    try:
      voiceChannel.play(discord.FFmpegPCMAudio('audio/' + name + '.mp3'))
      while voiceChannel.is_playing():
        await asyncio.sleep(0.1)
      await asyncio.sleep(1)
      voiceChannel.stop()
    except:
      await ctx.send("Unable to play music file, either you entered an incorrect name or it does not exist.")
    finally:
      isPlayingAudio = False
      leaveTimer = datetime.datetime.now() + datetime.timedelta(hours=1)
      await asyncio.sleep(3600)
      if datetime.datetime.now() >= leaveTimer and voiceChannel != None:
        await voiceChannel.disconnect()
        await ctx.send("I have left the voice channel due to inactivity.")
        voiceChannel = None

@bot.command()
async def leave(ctx):
  global voiceChannel
  if voiceChannel != None:
    await voiceChannel.disconnect()
    voiceChannel = None

@bot.command()
async def flip(ctx):
  r = requests.get('https://www.random.org/coins/?num=1&cur=60-cad.0100c')
  soup = BeautifulSoup(r.text, 'html.parser')
  for link in soup.find_all('img'):
    img = link.get('src')
  await ctx.send('https://www.random.org/coins/' + img)

@tasks.loop(minutes=10)
async def reminder():
  global isActive
  global moveReminder
  # if discord is active and it has been 2 hours since the last message
  # then we will send another reminder
  if isActive and datetime.datetime.now() >= moveReminder:
    moveReminder = datetime.datetime.now() + datetime.timedelta(hours=2)
    channel = bot.get_channel(866903190082682910)
    await channel.send("Remember to stand up and exercise (or stretch)! Also drink some water and stay hydrated! Especially you <@187083047340998656> ")
    isActive = False

@reminder.before_loop
async def before_reminder():
  await bot.wait_until_ready()

@tasks.loop(minutes=10)
async def remindTest():
  global isActive2
  global testReminder
  # if discord is active and it has been 5 hours since the last message
  # then we will send another reminder
  if isActive2 and datetime.datetime.now() >= testReminder:
    testReminder = datetime.datetime.now() + datetime.timedelta(hours=5)
    channel = bot.get_channel(866903190082682910)
    await channel.send("<@!628081471785009162> Study for your test or you're gonna fail - Patrick")
    isActive2 = False

@remindTest.before_loop
async def before_remindTest():
  await bot.wait_until_ready()

@tasks.loop(minutes=10)
async def factAndPicAndMeme():
  global memeReminder
  # if it has been  hours 8 since the last fact/pic/meme then send another
  if datetime.datetime.now() >= memeReminder:
    memeReminder = datetime.datetime.now() + datetime.timedelta(hours=8)
    animChannel = bot.get_channel(802692284558475305)
    memeChannel = bot.get_channel(866938492596387850)
    await animChannel.send(getCatFact())
    await animChannel.send("Now enjoy a picture of a random animal.")
    await asyncio.sleep(2)
    await animChannel.send(getAnimalPic())
    await asyncio.sleep(2)
    await memeChannel.send(getMeme())

@factAndPicAndMeme.before_loop
async def before_factAndPic():
  await bot.wait_until_ready()

def topTickers():
  r = requests.get("https://apewisdom.io/api/v1.0/filter/wallstreetbets")
  json = r.json()
  result = "Top 10 tickers in WSB:\n"
  for i in range(10):
    result += "#{0} {1}\n".format(i+1, json['results'][i]['ticker'])
  return result

def getCatFact():
  r = requests.get('https://catfact.ninja/fact?max_length=500')
  json = r.json()
  return json['fact']

def getAnimalPic():
  i = random.randint(1, 99)
  if i > 66:
    r = requests.get('https://aws.random.cat/meow?ref=apilist.fun')
    return r.json()['file']
  elif i > 33:
    r = requests.get('https://random.dog/woof.json?ref=apilist.fun')
    return r.json()['url']
  else:
    r = requests.get('https://randomfox.ca/floof/')
    return r.json()['image']

def getMeme():
  r = requests.get('https://meme-api.herokuapp.com/gimme')
  return r.json()['url']

def getInsult():
  r = requests.get('https://evilinsult.com/generate_insult.php?lang=en&type=text')
  string = r.text
  return string

def listClips():
  result = ''
  files = os.listdir('audio/')
  for file in files:
    name = file.split('.')[0]
    result += '[' + name + '] '
  return result

###################################
#           Connect Four          #
###################################

@bot.command()
async def connect4(ctx, mention1: str, mention2: str):
  global isPlaying
  global player1
  global player2
  global gameMessage
  global turn
  global board
  if (mention1[0] == '<' and mention1[-1] == '>' and mention2[0] == '<' and mention2    [-1] == '>' and isPlaying == False):
    board = c4.Board()
    turn = 1
    embed = createEmbed(board.print_board())
    gameMessage = await ctx.send(embed=embed)
    reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣']
    for reaction in reactions:
      await gameMessage.add_reaction(reaction)
    isPlaying = True
    player1 = (mention1, mention1.replace('!', ''))
    player2 = (mention2, mention2.replace('!', ''))
  else:
    await ctx.send("Invalid format")

@bot.command()
async def killGame(ctx):
  cleanupGame()
  await ctx.send("Game has been stopped.")

@bot.event
async def on_reaction_add(reaction, user):
  if user.bot:
    return
  ############# Everything below is ugly, but it works ;) ############
  global isPlaying
  global gameMessage
  global player1
  global player2
  global gameMessage
  global turn
  global board
  if isPlaying == True:
    try:
      if reaction.message == gameMessage and (user.mention == player1[0] or user.mention == player1[1]) and turn == 1:
        col = getColumn(reaction.emoji)
        isOver = board.makeMove(1, col)
        winner = player1[0]
        if turn == 1:
          turn = 2
        else:
          turn = 1
        embed = createEmbed(board.print_board())
      elif reaction.message == gameMessage and (user.mention == player2[0] or user.mention == player2[1]) and turn == 2:
        col = getColumn(reaction.emoji)
        isOver = board.makeMove(2, col)
        winner = player2[0]
        if turn == 1:
          turn = 2
        else:
          turn = 1
        embed = createEmbed(board.print_board())
      else:
        return
      await gameMessage.edit(embed=embed)
      if isOver:
        await reaction.message.channel.send(winner + " Congratulations you win!")
        cleanupGame()
    except:
      await reaction.message.channel.send("Invalid move, try again!")
    finally:
      await reaction.remove(user)
    return

def createEmbed(content):
  global turn
  embed = discord.Embed()
  embed.add_field(name='Connect Four - Player ' + str(turn) + ' it is your turn', value=content ,inline=False)
  return embed

def getColumn(emoji):
  i = 1
  reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣']
  for reaction in reactions:
    if emoji == reaction:
      return i
    else:
      i += 1

def cleanupGame():
  global isPlaying
  global player1
  global player2
  global gameMessage
  global turn
  global board
  isPlaying = False
  player1 = None
  player2 = None
  gameMessage = None
  turn = None
  board = None

##########################################
#           Rock Paper Scissors          # (do later lol)
##########################################

# This results in circularReference error not sure why??
# Can't use database to store datetime value, time to add more variables :)
# db['moveReminder'] = datetime.datetime.now()
# db['testReminder'] = datetime.datetime.now()
# db['memeReminder'] = datetime.datetime.now()

reminder.start()
remindTest.start()
factAndPicAndMeme.start()
keep_alive()
bot.run(os.environ['token'])