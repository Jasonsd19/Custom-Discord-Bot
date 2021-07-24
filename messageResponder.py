from discord.ext import tasks, commands

class messageResponder(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.sad_words = {"sad", "horrible", "lonely", "depressed", ":(", "gloomy", "tragic", "despair", "pain", "forlorn", "hurt", "hurting"}
    self.sleep_words = {"sleep", "sleeping", "going to bed"}
    self.winnersID = 817519861906669640

  @commands.Cog.listener('on_message')
  async def respondToSad(self, message):
    if self.sad_words.intersection(message.content.lower().split()) and self.isNotBot(message):
      await message.channel.send("Well {0}, this server has friends that still care and love you <:patW:673433778944737310>.".format(message.author.mention))
      return

  @commands.Cog.listener('on_message')
  async def respondToSleep(self, message):
    if self.sleep_words.intersection(message.content.lower().split()) and self.isNotBot(message):
      await message.channel.send("Good night {0}, hope you enjoyed your stay <:peepolove:822337341892853790>.".format(message.author.mention))
      return

  @commands.Cog.listener('on_message')
  async def respondToWinnersPing(self, message):
    if self.winnersID in message.raw_role_mentions and self.isNotBot(message):
      await message.add_reaction("<:pogNuts:827445043018858526>")
      return

  @commands.Cog.listener('on_message')
  async def respondToMention(self, message):
    if self.bot.user.id in message.raw_mentions and self.isNotBot(message):
      if message.author.id == 387855771355840512:
        #If I (Jason) mention the bot
        await message.channel.send("I am at your service oh great and powerful Jason <:o7:822333430166454312>.")
        return
      if self.bot.user.id in message.raw_mentions and message.author.id == 190583718182780928:
        #If Ray mentions the bot
        await message.channel.send("Hello father. I love you.")
        return
      await message.channel.send("<:wutface:823056657110007839> Don't @ me loser")
      return
  
  def isNotBot(self, message):
    return not(message.author == self.bot.user or message.author.bot)