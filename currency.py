import redis
import json
from discord.ext import tasks, commands

class currency(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db
    
    @commands.command()
    async def register(self, ctx):
        # If the authos id is already a field in the hashmap then they're registered
        if self.db.hexists('currency', ctx.author.id):
            await ctx.send("You are already registered!")
        else:
            # We create a dictionary that represents the users wallet
            # We serialize to json str so we can store the dictionary in the redis database
            # This makes it easy for use to come back and add more fields/complexity to the wallet (in theory)
            wallet = json.dumps({'balance':100})
            # We set the hashmap key to be 'currency', the authors id is the field, and the wallet is the value
            self.db.hset('currency', ctx.author.id, wallet)
            await ctx.send("You have successfully registered!")
    
    @commands.command()
    async def balance(self, ctx):
        # I opted to use one key in the database that stores hashmaps
        # The hashmaps use the user ids as keys and take the json serialized form of a python dictionary as values (these dictionaries represent the wallet)
        # The other option was to simply use multiple keys in the database, where each key was the user id, and the value was the wallet (idk which way is better)
        if self.db.hexists('currency', ctx.author.id):
            # We retrieve the serialized form of the wallet from the database
            serialized = self.db.hget('currency', ctx.author.id)
            # Deserialize it back into a python dictionary
            deserialized = json.loads(serialized)
            balance = deserialized['balance']
            await ctx.send(f'You currently have {balance} Moon Tokens')
        else:
            await ctx.send("You need to register using the '$register' command first")