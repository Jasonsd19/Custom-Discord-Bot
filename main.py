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
import messageResponder
import connectFour as c4

bot = commands.Bot(command_prefix='$')

game = discord.Game("$help for more information")

#Game Vars
isPlaying = False
player1 = None
player2 = None
gameMessage = None
turn = None
board = None
#Game Vars

@bot.event
async def on_ready():
  print("We have logged in as {0.user}".format(bot))
  await bot.change_presence(status=discord.Status.online, activity=game)

@bot.event
async def on_message(message):
  if message.author == bot.user or message.author.bot:
    return

  await bot.process_commands(message)

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

bot.add_cog(apiCalls.WallStreetBetsApi(bot))
bot.add_cog(apiCalls.MemeApi(bot))
bot.add_cog(apiCalls.coinflipAPI(bot))
bot.add_cog(apiCalls.diceAPI(bot))
bot.add_cog(apiCalls.insultApi(bot))

bot.add_cog(audioPlayer.audioPlayer(bot))

bot.add_cog(reminders.remindMove(bot))
bot.add_cog(reminders.remindTest(bot))

bot.add_cog(messageResponder.messageResponder(bot))

keepAlive()
bot.run(os.environ['token'])