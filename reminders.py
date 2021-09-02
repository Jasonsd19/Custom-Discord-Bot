import datetime
import redis
from discord.ext import tasks, commands

class remindMove(commands.Cog):
  def __init__(self, bot, db):
    self.bot = bot
    self.db = db
    self.isActive = False
    self.reminder.start()

  @commands.Cog.listener()
  async def on_message(self, message):
    #A listener that detects whether the discord is active or not, very basic can be improved
    if not(message.author == self.bot.user or message.author.bot):
      self.isActive = True

  @tasks.loop(minutes=5)
  #We loop this function every 5 minutes
  async def reminder(self):
    #Check if we have a datetime value already in the database
    if self.db.exists('moveReminder'):
      #Retrieve the string representation of datetime object from database
      timer = self.db.get('moveReminder')
      #Convert the string representation back into datetime object
      timerFormatted = datetime.datetime.strptime(timer, '%Y-%m-%d %H:%M:%S')
      #If discord is active and it has been 4 hours since the last message
      #then we will send another reminder
      if self.isActive and datetime.datetime.now() >= timerFormatted:
        #We create a datetime object 4 hours from current time
        now = datetime.datetime.now() + datetime.timedelta(hours=4)
        #We convert the datetime object into a string for use in database
        nowFormatted = now.strftime('%Y-%m-%d %H:%M:%S')
        #Add the string to the database, the string represents a time 4 hours from now, when we can send the reminder again
        self.db.set('moveReminder', nowFormatted)
        channel = self.bot.get_channel(866903190082682910)
        await channel.send("Remember to stand up and exercise (or stretch)! Also drink some water and stay hydrated! Especially you <@187083047340998656> ")
        self.isActive = False
    else:
      #There is no datetime value in database, so we add one
      now = datetime.datetime.now()
      nowFormatted = now.strftime('%Y-%m-%d %H:%M:%S')
      self.db.set('moveReminder', nowFormatted)

# She passed!
# class remindTest(commands.Cog):
#   def __init__(self, bot):
#     self.bot = bot
#     self.testReminder = datetime.datetime.now()
#     self.isActive = False
#     self.reminder.start()

#   @commands.Cog.listener()
#   async def on_message(self, message):
#       if not(message.author == self.bot.user or message.author.bot):
#         self.isActive = True

#   @tasks.loop(minutes=10)
#   async def reminder(self):
#     # if discord is active and it has been 5 hours since the last message
#     # then we will send another reminder
#     if self.isActive and datetime.datetime.now() >= self.testReminder:
#       self.testReminder = datetime.datetime.now() + datetime.timedelta(hours=5)
#       channel = self.bot.get_channel(866903190082682910)
#       await channel.send("<@!628081471785009162> Study for your test or you're gonna fail - Patrick")
#       self.isActive = False