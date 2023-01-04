import redis
import json
import discord
import datetime
import discord
from discord.ext import tasks, commands


class currency(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db
        #self.moonTokensMax = 10600

    @commands.command()
    async def register(self, ctx):
        # If the authos id is already a field in the hashmap then they're registered
        if self.db.hexists('currency', ctx.author.id):
            await ctx.send("You are already registered!")
        else:
            # We create a dictionary that represents the users wallet
            # We serialize to json str so we can store the dictionary in the redis database
            # This makes it easy for use to come back and add more fields/complexity to the wallet (in theory)
            wallet = json.dumps({'balance': 0})
            # We set the hashmap key to be 'currency', the authors id is the field, and the wallet is the value
            self.db.hset('currency', ctx.author.id, wallet)
            # Now we give the new user 100 Moon Tokens from the reserve, if the reserve is low (< 100) then they get none
            code = self.updateWallet(self.bot.user.id, ctx.author.id, 100)
            if code == 1:
                await ctx.send("You have successfully registered and received 100 Moon Tokens!")
            else:
                await ctx.send("You have successfully registered, but the reserves are low so you do not get any Moon Tokens :frowning2:")

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

    @commands.command()
    async def reserve(self, ctx):
        if self.db.hexists('currency', self.bot.user.id):
            # We retrieve the serialized form of the wallet from the database
            serialized = self.db.hget('currency', self.bot.user.id)
            # Deserialize it back into a python dictionary
            deserialized = json.loads(serialized)
            balance = deserialized['balance']
            await ctx.send(f'There are currently {balance} Moon Tokens in the reserve out of the 10600 Moon Tokens that exist.')
        else:
            await ctx.send("The bot is not registered, it has no reserves!")

    @commands.command()
    async def give(self, ctx, mention, amount):
        # *TODO* Split function into give and tip, give is specifically used to give money from bot, tip for everyone else ***
        # This function allows users to tip other users currency

        # If I (Jason) am using the command then the amount is subtracted from the bot's wallet (I'm not registered)
        if ctx.author.id == 387855771355840512:
            authorID = self.bot.user.id
        else:
            authorID = ctx.author.id

        # Scuffed check to make sure the author actually mentioned someone
        if mention[0] == '<' and mention[-1] == '>':
            try:
                # Cast input to int
                amount = int(amount)
                if amount < 0:
                    await ctx.send(embed=self.createEmbed('Error', "Amount transferred must be positive"), delete_after=30)
                    return
                # Extract user discord id from mention
                mentionID = int(mention.replace(
                    "@", "").replace("!", "")[1:-1])
                # Update wallets and return code indicating if it's successfull or not
                code = self.updateWallet(authorID, mentionID, amount)
                if code == 1:
                    await ctx.send(embed=self.createEmbed('Success', f'{self.bot.get_user(authorID).mention} has transferred {amount} Moon Tokens to {mention}!'))
                    return
                elif code == 2:
                    await ctx.send(embed=self.createEmbed('Error', f'{self.bot.get_user(authorID).mention} you do not have enough Moon Tokens!'), delete_after=30)
                    return
                elif code == 3:
                    await ctx.send(embed=self.createEmbed('Error', f'{mention} please register for Moon Tokens using "$register"'), delete_after=30)
                    return
                elif code == 4:
                    await ctx.send(embed=self.createEmbed('Error', f'{self.bot.get_user(authorID).mention} please register for Moon Tokens using "$register"'), delete_after=30)
                    return
                else:
                    await ctx.send(embed=self.createEmbed('Error', f'Stop playing with yourself :wink:'), delete_after=30)
                    return
            except ValueError:
                # Input was not an int
                await ctx.send(embed=self.createEmbed('Error', "Invalid command format"), delete_after=30)
                return
        else:
            # The author did not actually mention someone
            await ctx.send(embed=self.createEmbed('Error', "Invalid command format"), delete_after=30)
            return

    @commands.command()
    async def yoink(self, ctx, mention, amount):
        # Only I can use the command :)
        if ctx.author.id == 387855771355840512:
            if mention[0] == '<' and mention[-1] == '>':
                try:
                    # Cast input to int
                    amount = int(amount)
                    if amount < 0:
                        await ctx.send(embed=self.createEmbed('Error', "Amount transferred must be positive"), delete_after=30)
                        return
                    # Extract user discord id from mention
                    mentionID = int(mention.replace(
                        "@", "").replace("!", "")[1:-1])
                    # Update wallets and return code indicating if it's successfull or not
                    code = self.updateWallet(
                        mentionID, self.bot.user.id, amount)
                    if code == 1:
                        await ctx.send(embed=self.createEmbed('Success', f'{self.bot.get_user(mentionID).mention} has transferred {amount} Moon Tokens to {self.bot.user.mention}!'))
                        return
                    elif code == 2:
                        await ctx.send(embed=self.createEmbed('Error', f'{self.bot.get_user(mentionID).mention} you do not have enough Moon Tokens!'), delete_after=30)
                        return
                    elif code == 3:
                        await ctx.send(embed=self.createEmbed('Error', f'{self.bot.user.mention} please register for Moon Tokens using "$register"'), delete_after=30)
                        return
                    elif code == 4:
                        await ctx.send(embed=self.createEmbed('Error', f'{self.bot.get_user(mentionID).mention} please register for Moon Tokens using "$register"'), delete_after=30)
                        return
                    else:
                        await ctx.send(embed=self.createEmbed('Error', f'Stop playing with yourself :wink:'), delete_after=30)
                        return
                except ValueError:
                    # Input was not an int
                    await ctx.send(embed=self.createEmbed('Error', "Invalid command format"), delete_after=30)
                    return
                return
            # The author did not actually mention someone
            await ctx.send(embed=self.createEmbed('Error', "Invalid command format"), delete_after=30)
            return
        else:
            await ctx.send(embed=self.createEmbed('Beta Detected', "Only chads can use this command :sunglasses:"), delete_after=30)
            return

    @commands.command()
    async def moonBoard(self, ctx):
        stored = self.db.hgetall("currency")
        nonFmt = []
        for k, v in stored.items():
            userName = self.bot.get_user(int(k)).name
            # nonFmt.append(userName)
            # nonFmt.append(v[12:-1])
            nonFmt.append((userName, v[12:-1]))
        fmt = self.fmtcols(nonFmt)
        await ctx.send(embed=self.createEmbed("Current Moon Token Leaderboards", f"```{fmt}```"))
        return

    @commands.command()
    async def ledger(self, ctx):
        await ctx.send("Here is the ledger:", file=discord.File("ledger.txt"))

    @commands.Cog.listener('on_message')
    async def rewardC4Win(self, message):
        if message.author == self.bot.user and "Congratulations you won the connect four game!" in message.content:
            split = message.content.split(" ")
            # Grab the winner's discord mention and id
            winnerMention = split[0]
            winnerID = int(winnerMention.replace(
                "@", "").replace("!", "")[1:-1])
            # Grab the loser's discord mention and id
            loserMention = split[9]
            loserID = int(loserMention.replace("@", "").replace("!", "")[1:-1])
            amount = 10
            # Give the winner the specified amount of tokens (from the loser's wallet)
            code = self.updateWallet(loserID, winnerID, amount)
            # I don't like how this block of code is the same from the give function, however the listener does not have context so I can't invoke
            # the give command from within this function, there must be some way to remove this redundant code
            if code == 1:
                await message.channel.send(embed=self.createEmbed('Success', f'{loserMention} has transferred {amount} Moon Tokens to {winnerMention}!'))
                return
            elif code == 2:
                await message.channel.send(embed=self.createEmbed('Error', f'{loserMention} you do not have enough Moon Tokens!'), delete_after=30)
                return
            elif code == 3:
                await message.channel.send(embed=self.createEmbed('Error', f'{winnerMention} please register for Moon Tokens using "$register"'), delete_after=30)
                return
            elif code == 4:
                await message.channel.send(embed=self.createEmbed('Error', f'{loserMention} please register for Moon Tokens using "$register"'), delete_after=30)
                return
            else:
                await message.channel.send(embed=self.createEmbed('Error', f'Stop playing with yourself :wink:'), delete_after=30)
                return

    def updateWallet(self, giver, receiver, amount):
        # Hotfix for infinite moon token bug
        if giver == receiver:
            return 5
        # Check the giver is registered in database
        if self.db.hexists('currency', giver):
            # Deserialize json str representing wallet to python dictoinary
            authorWallet = json.loads(self.db.hget('currency', giver))
            # Check the receiver is registered in database
            if self.db.hexists('currency', receiver):
                # Deserialize json str representing wallet to python dictoinary
                mentionWallet = json.loads(self.db.hget('currency', receiver))
                # Check that the giver actually has enough tokens to pay receiver
                if authorWallet['balance'] >= amount:
                    # Update both the giver's and receiver's wallets
                    authorWallet['balance'] -= amount
                    mentionWallet['balance'] += amount
                    # Serialize updated wallets to a json str and put into database
                    self.db.hset('currency', giver, json.dumps(authorWallet))
                    self.db.hset('currency', receiver,
                                 json.dumps(mentionWallet))
                    # Write transaction to ledger
                    ledger = open('ledger.txt', 'a')
                    ledger.write(
                        f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}, {str(giver)}, {str(receiver)}, {amount}\n')
                    ledger.close()
                    return 1
                else:
                    return 2
            else:
                return 3
        else:
            return 4

    def createEmbed(self, header, content):
        embed = discord.Embed()
        embed.add_field(name=header, value=content, inline=False)
        return embed

    def fmtcols(self, mylist):
        # credit to S.Lott - https://stackoverflow.com/users/10661/s-lott
        # modified the function slightly
        maxwidth = max(list(map(lambda x: len(x[0]), mylist)))
        justifyList = list(
            map(lambda x: (x[0].ljust(maxwidth), x[1].ljust(maxwidth)), mylist))
        justifyList.sort(reverse=True, key=lambda x: int(x[1]))
        lines = (' '.join(justifyList[i])
                 for i in range(0, len(justifyList)))
        return "\n".join(lines)
