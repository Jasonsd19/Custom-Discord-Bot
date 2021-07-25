import requests
import random
import asyncio
import datetime
from bs4 import BeautifulSoup
from discord.ext import tasks, commands

def addCallApi(original_class):
  def callApi(self, endpoint):
    try:
      r = requests.get(endpoint)
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
      #all other exceptions
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
  def __init__(self, bot):
    self.bot = bot
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
    # if it has been  hours 8 since the last fact/pic/meme then send another
    if datetime.datetime.now() >= self.memeReminder:
      self.memeReminder = datetime.datetime.now() + datetime.timedelta(hours=8)

      for channel in self.bot.get_all_channels():
        channel_name = channel.name.lower()
        isMemeChannel = 'meme' in channel_name
        isAnimalChannel = 'animal' in channel_name or 'pet' in channel_name or 'cat' in channel_name or 'dog' in channel_name
        if channel.type.name.lower() == 'text' and isMemeChannel:
            await channel.send(self.getMeme())
            await asyncio.sleep(2)
        elif channel.type.name.lower() == 'text' and isAnimalChannel:
            await channel.send(self.getCatFact())
            await channel.send("Now enjoy a picture of a random animal.")
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
      url = 'https://aws.random.cat/meow?ref=apilist.fun'
      r = self._callApi(url)
      return r.json()['file']
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
    url = 'http://roll.diceapi.com/html/' + dice
    try:
      r = self._callApi(url)
      text = r.text
      imgLink = text.split('\"')[1]
      await ctx.send(imgLink)
    except:
      # Either we have a connection error or the input was invalid
      # unsure about this try block
      await ctx.send("Invalid format! We can only roll 'd6' or 'd20'")

@addCallApi
class insultApi(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

  @commands.command()
  async def insultMe(self, ctx):
    user = ctx.author.mention
    if ctx.author.id == 387855771355840512:
      await ctx.send("I would never insult my creator.")
    else:
      await ctx.send(user + self.getInsult())

  @commands.command()
  async def insult(self, ctx, mention: str):
    try:
      if mention[0] == '<' and mention[-1] == '>':
        if mention == '<@!387855771355840512>':
          await ctx.send("I would never insult my creator, but I would insult you\n" + ctx.author.mention + self.getInsult())
        else:
          await ctx.send(mention + ' ' + self.getInsult())
      else:
        raise Exception("Incorrect format")
    except:
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
    question = ' '.join(args)
    url = 'https://8ball.delegator.com/magic/JSON/' + question
    r = self._callApi(url)
    responseJSON = r.json()
    await ctx.send('The magic 8-Ball says: ' + responseJSON['magic']['answer'])
