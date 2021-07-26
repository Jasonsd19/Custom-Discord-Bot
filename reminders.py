import datetime
from discord.ext import tasks, commands

class remindMove(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.moveReminder = datetime.datetime.now()
    self.isActive = False
    self.reminder.start()

  @commands.Cog.listener()
  async def on_message(self, message):
    if not(message.author == self.bot.user or message.author.bot):
      self.isActive = True

  @tasks.loop(minutes=10)
  async def reminder(self):
    # if discord is active and it has been 2 hours since the last message
    # then we will send another reminder
    if self.isActive and datetime.datetime.now() >= self.moveReminder:
      self.moveReminder = datetime.datetime.now() + datetime.timedelta(hours=2)
      channel = self.bot.get_channel(866903190082682910)
      await channel.send("Remember to stand up and exercise (or stretch)! Also drink some water and stay hydrated! Especially you <@187083047340998656> ")
      self.isActive = False

class remindTest(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.testReminder = datetime.datetime.now()
    self.isActive = False
    self.reminder.start()

    @commands.Cog.listener()
    async def on_message(self, message):
      if not(message.author == self.bot.user or message.author.bot):
        self.isActive = True

  @tasks.loop(minutes=10)
  async def reminder(self):
    # if discord is active and it has been 5 hours since the last message
    # then we will send another reminder
    if self.isActive and datetime.datetime.now() >= self.testReminder:
      self.testReminder = datetime.datetime.now() + datetime.timedelta(hours=5)
      channel = self.bot.get_channel(866903190082682910)
      await channel.send("<@!628081471785009162> Study for your test or you're gonna fail - Patrick")
      self.isActive = False