import os
import discord
import datetime
import asyncio
from discord.ext import tasks, commands
from keepAlive import keepAlive
from replit import db
import apiCalls
import audioPlayer
import reminders

import connectFour as c4

bot = commands.Bot(command_prefix='$')

game = discord.Game("$help for more information")

sad_words  = {"sad", "horrible", "lonely", "depressed", ":(", "gloomy", "tragic", "despair", "pain", "forlorn", "hurt", "hurting"}

sleep_words = {"sleep", "sleeping", "going to bed"}

isActive2 = False

#Loop Vars
testReminder = datetime.datetime.now()
#Loop Vars

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

remindTest.start()

bot.add_cog(apiCalls.WallStreetBetsApi(bot))
bot.add_cog(apiCalls.MemeApi(bot))
bot.add_cog(apiCalls.coinflipAPI(bot))
bot.add_cog(apiCalls.diceAPI(bot))
bot.add_cog(apiCalls.insultApi(bot))

bot.add_cog(audioPlayer.audioPlayer(bot))

bot.add_cog(reminders.remindMove(bot))

keepAlive()
bot.run(os.environ['token'])