import requests
import random
import asyncio
import datetime
from bs4 import BeautifulSoup
from discord.ext import tasks, commands
import redis

# A decorator that implements the callApi function for all the classes below
def addCallApi(original_class):
  def callApi(self, endpoint, endpointHeaders={}):
    try:
      r = requests.get(endpoint, headers=endpointHeaders)
      r.raise_for_status()
    except requests.ConnectionError:
      #possible internet issue
      print(f"connection error, endpoint: {endpoint}")
    except requests.exceptions.Timeout:
      print(f"requests timedout, endpoint: {endpoint}")
    except requests.exceptions.HTTPError as err:
      print(err, f"endpoint: {endpoint}")
    except requests.exceptions.TooManyRedirects:
      print(f"too many redirects bad url {endpoint}")
    except requests.exceptions.RequestException as e:
      # all other exceptions
      print(e, f"fam if you reached this stage just die. Endpoint: {endpoint}")
    return r
  original_class._callApi = callApi
  return original_class

@addCallApi
class WallStreetBetsApi(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    return

  @commands.command(description='See what is trending on WSB.',
             help='Displays the 10 most popular tickers from the WallStreetBets subreddit.')
  async def wsb(self, ctx):
    await ctx.send(self.topTickers())
    return

  def topTickers(self):
    url = "https://apewisdom.io/api/v1.0/filter/wallstreetbets"
    r = self._callApi(url)
    json = r.json()
    result = "Top 10 tickers in WSB:\n"
    for i in range(10):
      result += "#{0} {1}\n".format(i+1, json['results'][i]['ticker'])
    return result

@addCallApi
class MemeApi(commands.Cog):
  def __init__(self, bot, key):
    self.bot = bot
    # Need an API key for the cat API (is there a better way to pass this in?)
    self.key = key
    self.memeReminder = datetime.datetime.now()
    # Start the loop
    self.factAndPicAndMeme.start()
    return

  @commands.command()
  async def meme(self, ctx):
    await ctx.send(self.getMeme())
    return

  @commands.command()
  async def animalPic(self, ctx):
    await ctx.send(self.getAnimalPic())
    return

  @commands.command()
  async def catFact(self, ctx):
    await ctx.send(self.getCatFact())
    return

  @tasks.loop(minutes=10)
  async def factAndPicAndMeme(self):
    # if it has been  hours 8 since the last fact/pic/meme then send another **Need to move this functionality over to database
    if datetime.datetime.now() >= self.memeReminder:
      self.memeReminder = datetime.datetime.now() + datetime.timedelta(hours=8)

      # Find all the channels we want to utilise and send the corresponding message
      for channel in self.bot.get_all_channels():
        channel_name = channel.name.lower()
        isMemeChannel = 'meme' in channel_name
        isAnimalChannel = 'animal' in channel_name or 'pet' in channel_name or 'cat' in channel_name or 'dog' in channel_name
        if channel.type.name.lower() == 'text' and isMemeChannel:
            await channel.send(self.getMeme())
            await asyncio.sleep(2)
        elif channel.type.name.lower() == 'text' and isAnimalChannel:
            await channel.send(self.getCatFact())
            await channel.send("Now enjoy a picture (or gif!) of a random animal.")
            await asyncio.sleep(2)
            await channel.send(self.getAnimalPic())
            await asyncio.sleep(2)

  def getMeme(self):
    url = 'https://meme-api.herokuapp.com/gimme'
    r = self._callApi(url)
    return r.json()['url']


  def getAnimalPic(self):
    i = random.randint(1, 99)
    if i > 66:
      url = 'https://api.thecatapi.com/v1/images/search'
      r = self._callApi(url, {"x-api-key":self.key})
      return r.json()[0]['url']
    elif i > 33:
      url = 'https://random.dog/woof.json?ref=apilist.fun'
      r = self._callApi(url)
      return r.json()['url']
    else:
      url = 'https://randomfox.ca/floof/'
      r = self._callApi(url)
      return r.json()['image']

  def getCatFact(self):
    url = 'https://catfact.ninja/fact?max_length=500'
    r = self._callApi(url)
    json = r.json()
    return json['fact']

@addCallApi
class coinflipAPI(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def flip(self, ctx):
    # It's not actually an API I just scrape the image from the website lol
    url = 'https://www.random.org/coins/?num=1&cur=60-cad.0100c'
    r = self._callApi(url)
    soup = BeautifulSoup(r.text, 'html.parser')
    for link in soup.find_all('img'):
      img = link.get('src')
    await ctx.send('https://www.random.org/coins/' + img)

@addCallApi
class diceAPI(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def roll(self, ctx, dice: str):
    # It's not actually an API I just scrape the image from the website lol
    url = 'http://roll.diceapi.com/html/' + dice
    try:
      r = self._callApi(url)
      text = r.text
      imgLink = text.split('\"')[1]
      await ctx.send(imgLink)
    except:
      # Either we have a connection error or the input was invalid
      # Should make the error handeling more specific, might do it later, might not
      await ctx.send("Invalid format! We can only roll 'd6' or 'd20'")

@addCallApi
class insultApi(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def insultMe(self, ctx):
    # Here we grab the author's mention, to be used by the bot in its response
    user = ctx.author.mention
    # If the person being insulted is me, then don't insult them ;)
    if ctx.author.id == 387855771355840512:
      await ctx.send("I would never insult my creator.")
    else:
      # Do insult all the other plebs
      await ctx.send(user + self.getInsult())

  @commands.command()
  async def insult(self, ctx, mention: str):
    try:
      # Scuffed check to make sure the author actually mentioned someone
      if mention[0] == '<' and mention[-1] == '>':
        # If someone tries to insult me, insult them instead
        if mention == '<@!387855771355840512>':
          await ctx.send("I would never insult my creator, but I would insult you\n" + ctx.author.mention + self.getInsult())
        else:
          # If it's not me then just insult the person lol
          await ctx.send(mention + ' ' + self.getInsult())
      else:
        # The author did not actually mention someone
        raise Exception("Incorrect format")
    except:
      # I put this here to catch the cases where the author input something other than a string (is that even possible?)
      # Also need to make error handeling more specific
      await ctx.send("Incorrect format")

  def getInsult(self):
    url = 'https://evilinsult.com/generate_insult.php?lang=en&type=text'
    r = self._callApi(url)
    string = r.text
    return string

@addCallApi
class magic8BallApi(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def ask(self, ctx, *args):
    # If there is a space between words after the $ask command, they are taken to be seperate arguments for the function
    # So here we take in an arbitrary number of arguments and create a string out of them (with spaces inbetween)
    question = ' '.join(args)
    url = 'https://8ball.delegator.com/magic/JSON/' + question
    r = self._callApi(url)
    responseJSON = r.json()
    await ctx.send('The magic 8-Ball says: ' + responseJSON['magic']['answer'])

@addCallApi
class complimentApi(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def complimentMe(self, ctx):
    # Grab author's mention
    user = ctx.author.mention
    compliment = self.getCompliment()
    await ctx.send(f"Hey {user}, {compliment}")

  @commands.command()
  async def compliment(self, ctx, mention: str):
    try:
      # Scuffed check to make sure the author actually mentioned someone
      if mention[0] == '<' and mention[-1] == '>':
        compliment = self.getCompliment()
        await ctx.send(f"Hey {mention}, {compliment}")
      else:
        # The author did not actually mention someone
        raise Exception("Incorrect format")
    except:
      # I put this here to catch the cases where the author input something other than a string (is that even possible?)
      # Also need to make error handeling more specific
      await ctx.send("Incorrect format")

  def getCompliment(self):
    url = 'https://complimentr.com/api'
    r = self._callApi(url)
    json = r.json()
    compliment = json['compliment']
    return compliment

@addCallApi
class excuseApi(commands.Cog):
 def __init__(self, bot, db):
   self.bot = bot
   self.db = db
   
 @commands.command()
 async def excuse(self, ctx):
   # Check if the excuses key exists in the database
    if self.db.exists('excuses'):
      # If it exists we grab a random excuse from the set
      excuse = self.db.srandmember('excuses')
      await ctx.send(excuse)
    else:
      # If it doesn't exist we prompt the users to add excuses
      await ctx.send("No excuses recorded, add one youself by using $addExcuse")

 @commands.command()
 async def addExcuse(self, ctx, *args):
   excuse = ' '.join(args)
   # Here we add the exuse to the database, and create the key if it doesn't exist (eg. it's the first excuse to be added)
   self.db.sadd('excuses', excuse)
   await ctx.send("Excuse has been recorded!")
