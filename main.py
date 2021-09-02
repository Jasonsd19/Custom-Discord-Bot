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

#                                        ****** LOOK HERE ******
# Reminder to add descriptions for the help function so people can actually learn how to use the bot :)
# It needs to be done eventually so why not do it now haha
#                                        ****** LOOK HERE ******

# Set the prefix symbol for all of the bot's commands
bot = commands.Bot(command_prefix='$', intents=discord.Intents.all())

# Set the activity of the bot, visible to all members of the server
game = discord.Game("$help for more information")

# Load tokens, API keys, and passwords from local file
tokens = json.load(open('tokens.json', 'r'))

# Connect to Redis database, decode all responses from the server into strings instead of bytes objects
r = redis.Redis(host='localhost', port=6379, password=tokens['database'], decode_responses=True)

# Runs everytime the bot logs in
@bot.event
async def on_ready():
  print(f"We have logged in as {bot.user}")
  await bot.change_presence(status=discord.Status.online, activity=game)

# Runs everytime a message is sent in the discord server
@bot.event
async def on_message(message):
  # We have listeners in other modules that utilise this (eg. messageResponder.py)
  # If the message is a bot or us we do nothing
  if message.author == bot.user or message.author.bot:
    return
  
  # await the other bot commands (anything with the $ prefix), otherwise nothing would work
  await bot.process_commands(message)

# Runs everytime someone reacts to a message in the server
@bot.event
async def on_reaction_add(reaction, user):
  # We have listeners in other modules that utilise this (eg. connectFour.py)
  if user.bot:
    return

# Register all of our cogs to our bot, so the bot can utilise their functionality
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

# Finally we actually run the bot (and start the event loop, I think...)
bot.run(tokens['bot'])