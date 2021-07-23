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
import textGames

bot = commands.Bot(command_prefix='$')

game = discord.Game("$help for more information")

#Game Vars
# isPlaying = False
# player1 = None
# player2 = None
# gameMessage = None
# turn = None
# board = None
#Game Vars

@bot.event
async def on_ready():
  print(f"We have logged in as {bot.user}")
  await bot.change_presence(status=discord.Status.online, activity=game)

@bot.event
async def on_message(message):
  if message.author == bot.user or message.author.bot:
    return

  await bot.process_commands(message)

@bot.event
async def on_reaction_add(reaction, user):
  if user.bot:
    return
  # ############# Everything below is ugly, but it works ;) ############
  # global isPlaying
  # global gameMessage
  # global player1
  # global player2
  # global gameMessage
  # global turn
  # global board
  # if isPlaying == True:
  #   try:
  #     if reaction.message == gameMessage and (user.mention == player1[0] or user.mention == player1[1]) and turn == 1:
  #       col = getColumn(reaction.emoji)
  #       isOver = board.makeMove(1, col)
  #       winner = player1[0]
  #       if turn == 1:
  #         turn = 2
  #       else:
  #         turn = 1
  #       embed = createEmbed(board.print_board())
  #     elif reaction.message == gameMessage and (user.mention == player2[0] or user.mention == player2[1]) and turn == 2:
  #       col = getColumn(reaction.emoji)
  #       isOver = board.makeMove(2, col)
  #       winner = player2[0]
  #       if turn == 1:
  #         turn = 2
  #       else:
  #         turn = 1
  #       embed = createEmbed(board.print_board())
  #     else:
  #       return
  #     await gameMessage.edit(embed=embed)
  #     if isOver:
  #       await reaction.message.channel.send(winner + " Congratulations you win!")
  #       cleanupGame()
  #   except:
  #     await reaction.message.channel.send("Invalid move, try again!")
  #   finally:
  #     await reaction.remove(user)
  #   return

bot.add_cog(apiCalls.WallStreetBetsApi(bot))
bot.add_cog(apiCalls.MemeApi(bot))
bot.add_cog(apiCalls.coinflipAPI(bot))
bot.add_cog(apiCalls.diceAPI(bot))
bot.add_cog(apiCalls.insultApi(bot))

bot.add_cog(audioPlayer.audioPlayer(bot))

bot.add_cog(reminders.remindMove(bot))
bot.add_cog(reminders.remindTest(bot))

bot.add_cog(messageResponder.messageResponder(bot))

bot.add_cog(textGames.connectFourText(bot))

keepAlive()
bot.run(os.environ['token'])