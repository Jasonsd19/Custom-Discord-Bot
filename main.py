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

bot = commands.Bot(command_prefix='$', intents=discord.Intents.all())

game = discord.Game("$help for more information")

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

bot.add_cog(apiCalls.WallStreetBetsApi(bot))
bot.add_cog(apiCalls.MemeApi(bot))
bot.add_cog(apiCalls.coinflipAPI(bot))
bot.add_cog(apiCalls.diceAPI(bot))
bot.add_cog(apiCalls.insultApi(bot))
bot.add_cog(apiCalls.magic8BallApi(bot))

bot.add_cog(audioPlayer.audioPlayer(bot))

bot.add_cog(reminders.remindMove(bot))
bot.add_cog(reminders.remindTest(bot))

bot.add_cog(messageResponder.messageResponder(bot))

bot.add_cog(textGames.connectFourText(bot))

keepAlive()
bot.run(os.environ['token'])