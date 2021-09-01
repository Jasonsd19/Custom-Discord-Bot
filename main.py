import discord
from discord.ext import tasks, commands
import json
import apiCalls
import audioPlayer
import reminders
import messageResponder
import textGames
import currency
import redis

bot = commands.Bot(command_prefix='$', intents=discord.Intents.all())

game = discord.Game("$help for more information")

#Load tokens and API keys from local file
tokens = json.load(open('tokens.json', 'r'))

#Connect to Redis database
r = redis.Redis(host='localhost', port=6379, password=tokens['database'], decode_responses=True)

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
bot.add_cog(apiCalls.MemeApi(bot, tokens['cat-api-key']))
bot.add_cog(apiCalls.coinflipAPI(bot))
bot.add_cog(apiCalls.diceAPI(bot))
bot.add_cog(apiCalls.insultApi(bot))
bot.add_cog(apiCalls.magic8BallApi(bot))
bot.add_cog(apiCalls.complimentApi(bot))
bot.add_cog(apiCalls.excuseApi(bot, r))

bot.add_cog(audioPlayer.audioPlayer(bot))

bot.add_cog(reminders.remindMove(bot, r))

bot.add_cog(messageResponder.messageResponder(bot))

bot.add_cog(textGames.connectFourText(bot))

bot.add_cog(currency.currency(bot, r))

bot.run(tokens['bot'])