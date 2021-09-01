import redis
import json
from discord.ext import tasks, commands

class currency(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db
    
    @commands.command()
    async def register(self, ctx):
        if self.db.hexists('currency', ctx.author.id):
            await ctx.send("You are already registered!")
        else:
            # We create a dictionary that represents the users wallet
            # We serialize to json str so we can store the dictionary in the redis database
            # This makes it easy for use to come back and add more fields/complexity to the wallet (in theory)
            # We can also create a wallet object and serialize it to json so it can be stored in database
            wallet = json.dumps({'balance':100})
            self.db.hset('currency', ctx.author.id, wallet)
            await ctx.send("You have successfully registered!")
    
    @commands.command()
    async def balance(self, ctx):
        if self.db.hexists('currency', ctx.author.id):
            serialized = self.db.hget('currency', ctx.author.id)
            deserialized = json.loads(serialized)
            balance = deserialized['balance']
            await ctx.send(f'You currently have {balance} Moon Tokens')
        else:
            await ctx.send("You need to register using the '$register' command first")