import requests
import random
import asyncio
from discord.ext import tasks, commands

def add_call_api(original_class):
  def call_api(self, endpoint):
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
      print(f"fam if you reached this stage just die. Endpoint: {endpoint}")
    return r
  original_class._call_api = call_api
  return original_class

@add_call_api
class WallStreetBetsApi(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    return

  @commands.command(description='See what is trending on WSB.',
             help='Displays the 10 most popular tickers from the WallStreetBets subreddit.')
  async def wsb(ctx):
    await ctx.send(self.topTickers())
    return
  
  def topTickers():
    url = "https://apewisdom.io/api/v1.0/filter/wallstreetbets"
    r = self._call_api(url)
    json = r.json()
    result = "Top 10 tickers in WSB:\n"
    for i in range(10):
      result += "#{0} {1}\n".format(i+1, json['results'][i]['ticker'])
    return result

@add_call_api
class MemeApi(commands.Cog):
  def __init__(self, bot):
    self.bot = bot
    self.memeReminder = datetime.datetime.now()
    return
  
  @commands.command()
  async def meme(ctx):
    await ctx.send(self.getMeme())
    return
  
  @commands.command()
  async def animalPic(ctx):
    await ctx.send(self.getAnimalPic())
    return
  
  @commands.command()
  async def catFact(ctx):
    await ctx.send(self.getCatFact())
    return
  
  @tasks.loop(minutes=10)
  async def factAndPicAndMeme():
    # if it has been  hours 8 since the last fact/pic/meme then send another
    if datetime.datetime.now() >= self.memeReminder:
      self.memeReminder = datetime.datetime.now() + datetime.timedelta(hours=8)

      for channel in self.bot.get_all_channels():
        channel_name = lower(channel.name)
        isMemeChannel = 'meme' in channel_name
        isAnimalChannel = 'animal' in channel_name or 'pet' in channel_name or 'cat' in channel_name or 'dog' in channel_name
        if lower(channel.type.name) == 'text' and isMemeChannel:
            await memeChannel.send(getMeme())
            await asyncio.sleep(2)
        elif lower(channel.type.name) == 'text' and isAnimalChannel:
            await animChannel.send(getCatFact())
            await animChannel.send("Now enjoy a picture of a random animal.")
            await asyncio.sleep(2)
            await animChannel.send(getAnimalPic())
            await asyncio.sleep(2)

  def getMeme():
    url = 'https://meme-api.herokuapp.com/gimme'
    r = self._call_api(url)
    return r.json()['url']
  
  def getAnimalPic():
    i = random.randint(1, 99)
    if i > 66:
      url = 'https://aws.random.cat/meow?ref=apilist.fun'
      r = self._call_api(url)
      return r.json()['file']
    elif i > 33:
      url = 'https://random.dog/woof.json?ref=apilist.fun'
      r = self._call_api(url)
      return r.json()['url']
    else:
      url = 'https://randomfox.ca/floof/'
      r = self._call_api(url)
      return r.json()['image']

  def getCatFact():
    url = 'https://catfact.ninja/fact?max_length=500'
    r = self._call_api(url)
    json = r.json()
    return json['fact']