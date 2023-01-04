import discord
import redis
import json
import os
from parseTranslations import parseTranslations
from functools import reduce
from discord.ext import tasks, commands
from PIL import (
    Image,
    ImageFont,
    ImageDraw,
)


class bang(commands.Cog):
    def __init__(self, bot, db):
        self.bot = bot
        self.db = db
        self.players = None

    # players = {userID: [[options], choice], userID: [[options], choice], ...}

    # TODO - implement better data structure for players
    # players = {userID: {options: ["Index1", "Index2", ...], choice: "Index"}, userID: {options: ["Index1", "Index2", ...], choice: "Index"}, ...}

    @commands.command()
    async def loadDB(self, ctx):
        if ctx.author.id == 387855771355840512:
            headers, body = parseTranslations()
            for i in range(len(headers)):
                toJSON = json.dumps(body[i])
                self.db.hset("bang", headers[i].split(" ")[0], toJSON)
            await ctx.send("Done")

            # remove all images in cache
            path = "imageCache/"
            for _, _, files in os.walk(path):
                for file in files:
                    os.remove(f'{path}{file}')

        else:
            await ctx.send("Only Jason can use this command.")

    @tasks.loop(seconds=5.0)
    async def autoBangBoard(self):
        if self.havePicked():
            mentionsAndIndexes = [(self.bot.get_user(k).name, v[1])
                                  for k, v in self.players.items()]
            descriptions = [json.loads(self.db.hget(
                "bang", mentionsAndIndexes[i][1])) for i in range(len(mentionsAndIndexes))]

            imgFraction = 1
            fontFamily = "test.ttf"
            finalString = self.formatDescription(
                mentionsAndIndexes, descriptions)

            img = Image.new('RGB', (10000, 4000), (255, 255, 255))
            d = ImageDraw.Draw(img)
            fontSize = self.find_font_size(
                finalString, fontFamily, img, imgFraction)
            font = ImageFont.truetype(fontFamily, fontSize)

            d.text((10, 10), finalString, fill=(0, 0, 0), font=font)
            img.save("bangBoard.png")
            file = discord.File("bangBoard.png")
            channel = self.bot.get_channel(892268475211456532)
            await channel.send(file=file)
            os.remove("bangBoard.png")
            self.autoBangBoard.stop()

    @commands.command()
    async def bang(self, ctx, *args):
        if (self.players != None):
            await ctx.send(embed=self.createEmbed('Error', f'There is already a game in progress!'), delete_after=30)
            return
        if len(args) >= 1:
            if self.areMentions(args):
                self.players = {
                    int((mention.replace("@", "").replace("!", "")[1:-1])): [] for mention in args}
                newline = "\n"  # Escape characters are not allowed in f string embedded expressions
                self.autoBangBoard.start()
                await ctx.send(embed=self.createEmbed('Success', f'Game started! Players are:\n{newline.join(self.bot.get_user(playerID).mention for playerID in self.players.keys())}'))
                return
            else:
                await ctx.send(embed=self.createEmbed('Error', f'Incorrect formatting, must only include mentions!'), delete_after=30)
                return
        else:
            await ctx.send(embed=self.createEmbed('Error', f'You need at least 4 players to start a game!'), delete_after=30)
            return

    @commands.command()
    async def getPlayers(self, ctx):
        print(
            f'Here are the players for the current game {self.players.keys()}')
        return

    @commands.command()
    async def getPlayerVals(self, ctx):
        print(
            f'Here are the players values for the current game {self.players.values()}')
        return

    @commands.command()
    async def endBang(self, ctx):
        self.players = None
        await ctx.send(embed=self.createEmbed('Success', f'Game has ended!'), delete_after=30)
        return

    @commands.command()
    async def find(self, ctx, *args):
        if len(self.players[ctx.author.id]) > 1:
            await ctx.send(embed=self.createEmbed('Error', f'You have already picked a card!'), delete_after=30)
            return

        if len(args) > 0:
            if self.areIndexes(args):

                if len(self.players[ctx.author.id]) == 1:
                    self.players[ctx.author.id][0] = []
                else:
                    self.players[ctx.author.id].append([])

                if self.areUnique(args):
                    for index in args:

                        path = f'imageCache/{index}.png'
                        if os.path.isfile(path):
                            file = discord.File(path)
                            await ctx.author.send(file=file)
                            self.players[ctx.author.id][0].append(index)
                            continue

                        self.players[ctx.author.id][0].append(index)
                        description = json.loads(
                            self.db.hget("bang", index))

                        imgFraction = 0.95
                        fontFamily = "test.ttf"
                        finalString = self.formatDescription(
                            [("Placeholder", index)], [description])

                        img = Image.new(
                            'RGB', (1000, 1200), (255, 255, 255))
                        d = ImageDraw.Draw(img)
                        fontSize = self.find_font_size(
                            finalString, fontFamily, img, imgFraction)
                        font = ImageFont.truetype(fontFamily, fontSize)

                        d.text((10, 10), finalString,
                               fill=(0, 0, 0), font=font)
                        img.save(path)
                        file = discord.File(path)
                        await ctx.author.send(file=file)
                    return
                else:
                    await ctx.send(embed=self.createEmbed('Error', f'One or more of these indexes have been claimed by another player!'), delete_after=30)
                    return
            else:
                await ctx.send(embed=self.createEmbed('Error', f'There is one or more invalid index!'), delete_after=30)
                return
        else:
            await ctx.send(embed=self.createEmbed('Error', f'You need to provide at least 1 index!'), delete_after=30)
            return

    @commands.command()
    async def check(self, ctx, *args):
        if len(args) > 0:
            if self.areIndexes(args):
                for index in args:

                    path = f'imageCache/{index}.png'
                    if os.path.isfile(path):
                        file = discord.File(path)
                        await ctx.author.send(file=file)
                        return

                    description = json.loads(self.db.hget("bang", index))

                    imgFraction = 0.95
                    fontFamily = "test.ttf"
                    finalString = self.formatDescription(
                        [("Placeholder", index)], [description])

                    img = Image.new('RGB', (1000, 1200), (255, 255, 255))
                    d = ImageDraw.Draw(img)
                    fontSize = self.find_font_size(
                        finalString, fontFamily, img, imgFraction)
                    font = ImageFont.truetype(fontFamily, fontSize)

                    d.text((10, 10), finalString, fill=(0, 0, 0), font=font)
                    img.save(path)
                    file = discord.File(path)
                    await ctx.author.send(file=file)
                return
            else:
                await ctx.send(embed=self.createEmbed('Error', f'There is one or more invalid index!'), delete_after=30)
                return
        else:
            await ctx.send(embed=self.createEmbed('Error', f'You need to provide at least 1 index!'), delete_after=30)
            return

    @commands.command()
    async def pick(self, ctx, index):
        if self.areIndexes([index]):
            if len(self.players[ctx.author.id]) == 1:
                choices = self.players[ctx.author.id][0]
                if index in choices:
                    self.players[ctx.author.id].append(index)
                    await ctx.send(embed=self.createEmbed('Success', f'Your card has been assigned!'), delete_after=30)
                    return
                else:
                    await ctx.send(embed=self.createEmbed('Error', f'Given index is not one of your choices!'), delete_after=30)
                    return
            else:
                await ctx.send(embed=self.createEmbed('Error', f'Either you have not entered your choices using "$find", or you have already picked your card!'), delete_after=30)
                return
        else:
            await ctx.send(embed=self.createEmbed('Error', f'Invalid Index!'), delete_after=30)
            return

    @commands.command()
    async def bangBoard(self, ctx):
        if self.havePicked():
            mentionsAndIndexes = [(self.bot.get_user(k).name, v[1])
                                  for k, v in self.players.items()]
            descriptions = [json.loads(self.db.hget(
                "bang", mentionsAndIndexes[i][1])) for i in range(len(mentionsAndIndexes))]

            imgFraction = 1
            fontFamily = "test.ttf"
            finalString = self.formatDescription(
                mentionsAndIndexes, descriptions)

            img = Image.new('RGB', (10000, 4000), (255, 255, 255))
            d = ImageDraw.Draw(img)
            fontSize = self.find_font_size(
                finalString, fontFamily, img, imgFraction)
            font = ImageFont.truetype(fontFamily, fontSize)

            d.text((10, 10), finalString, fill=(0, 0, 0), font=font)
            img.save("bangBoard.png")
            file = discord.File("bangBoard.png")
            await ctx.send(file=file)
            os.remove("bangBoard.png")
            return
        else:
            await ctx.send(embed=self.createEmbed('Error', f'Not every played has picker their card!'), delete_after=30)
            return

    def havePicked(self):
        for v in self.players.values():
            if len(v) == 2:
                continue
            else:
                return False
        return True

    def areMentions(self, iter):
        # Only works correctly when input has at least one element
        # Input must be iterable containing subscriptable types
        return reduce(lambda x, y: x and (y[0] == '<' and y[-1] == '>'), iter, True)

    def areIndexes(self, iter):
        for index in iter:
            if self.db.hexists("bang", index):
                continue
            else:
                return False
        return True

    def areUnique(self, iter):
        for index in iter:
            for v in self.players.values():
                if len(v) >= 1:
                    for existingIndex in v[0]:
                        if index == existingIndex:
                            return False
        return True

    def createEmbed(self, header, content):
        embed = discord.Embed()
        embed.add_field(name=header, value=content, inline=False)
        return embed

    def formatDescription(self, headers, descriptions):
        # Headers is a list of tuples [(Name:str, Index:str), ...]
        # Descriptions is a list of lists, where each inner list is a descriptive text
        #   that has been split on every space [["Hello", "World!"], ["This", "is", "a", "test"], ...]
        characterLimit = 50
        spacing = 60
        cols = 4
        string = ""
        while descriptions:
            if len(descriptions) >= cols:
                for i in range(cols):
                    string += headers[i][0].ljust(spacing)
                string += "\n"
                for i in range(cols):
                    string += headers[i][1].ljust(spacing)
                string += "\n\n"
                headers = headers[cols:]
                while True:
                    # newDescriptions is smaller than descriptions every iteration so this should always terminate
                    newDescriptions, fmtLine = self.formatDescLine(
                        cols, characterLimit, spacing, descriptions)
                    descriptions = newDescriptions
                    string += fmtLine + "\n"
                    if reduce(lambda x, y: x and y == [], descriptions[0:cols], True):
                        descriptions = descriptions[cols:]
                        string += "\n\n"
                        break
            else:
                length = len(descriptions)
                for i in range(length):
                    string += headers[i][0].ljust(spacing)
                string += "\n"
                for i in range(length):
                    string += headers[i][1].ljust(spacing)
                string += "\n\n"
                headers = headers[length:]
                while True:
                    # newDescriptions is smaller than descriptions every iteration so this should always terminate
                    newDescriptions, fmtLine = self.formatDescLine(
                        length, characterLimit, spacing, descriptions)
                    descriptions = newDescriptions
                    string += fmtLine + "\n"
                    if reduce(lambda x, y: x and y == [], descriptions[0:length], True):
                        descriptions = descriptions[length:]
                        string += "\n\n\n"
                        break
        return string

    def formatDescLine(self, cols, characterLimit, spacing, descriptions):
        returnStr = ""
        for i, description in enumerate(descriptions):
            tempString = ""
            if i == cols:
                break
            if description == []:
                returnStr += tempString.ljust(spacing)
            else:
                counter = 0
                wordIndex = 0
                for word in description:
                    if len(word) + counter + 1 <= characterLimit:
                        # The various if statements represent how I chose to parse the descriptions given to me
                        # They handle cases such as ability names, bullet points, and empty lines for formatting
                        # If only a simple block of text is to be parsed these if statements are not needed
                        if "@" in word:  # the @ is used to indicate that the word is an ability name/header
                            if counter == 0:
                                tempString += "|" + \
                                    word.replace("@", "").strip() + "|"
                                wordIndex += 1
                                break
                            else:
                                break
                        if "^" in word:  # the ^ indicates that an empty line should be inserted between the previous word and the next word
                            if counter == 0:
                                wordIndex += 1
                                break
                            else:
                                break
                        if "â€¢" in word or "•" in word:  # the â€¢ is a .doc representation of a bullet point, this case handles these specific bullet points
                            if counter == 0:
                                word = "•"
                            else:
                                break
                        tempString += word.strip() + " "
                        counter += len(word) + 1
                        wordIndex += 1
                    else:
                        break
                if wordIndex < len(description):
                    descriptions[i] = description[wordIndex:]
                else:
                    descriptions[i] = []
                returnStr += tempString.ljust(spacing)
        return descriptions, returnStr

    # Credit to jinnlao for the two functions below
    # https://stackoverflow.com/users/6185694/jinnlao
    # https://stackoverflow.com/questions/4902198/pil-how-to-scale-text-size-in-relation-to-the-size-of-the-image

    def find_font_size(self, text, font, image, target_width_ratio):
        tested_font_size = 100
        tested_font = ImageFont.truetype(font, tested_font_size)
        observed_width, observed_height = self.get_text_size(
            text, image, tested_font)
        estimated_font_size_width = tested_font_size / \
            (observed_width / image.width) * target_width_ratio
        estimated_font_size_height = tested_font_size / \
            (observed_height / image.height) * target_width_ratio
        return min(round(estimated_font_size_width), round(estimated_font_size_height))

    def get_text_size(self, text, image, font):
        im = Image.new('RGB', (image.width, image.height))
        draw = ImageDraw.Draw(im)
        return draw.textsize(text, font)
