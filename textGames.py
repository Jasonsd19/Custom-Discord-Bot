import connectFour
import discord
import asyncio
from discord.ext import tasks, commands

class connectFourText(commands.Cog):
  def __init__(self, bot):
    self.bot = bot

    #Vars for interacting with game
    self.game = None
    self.isOver = False

    #Vars for interacting with discord
    self.isPlaying = False
    self.gameMessage = None
    self.player1 = None
    self.player2 = None
    self.currentPlayer = None

    #Emojis used for interacting (should never be changed)
    self.reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣']

  def nextBoard(self, player, move):
    #The next board state given a player and a move
    self.game.nextBoard(player, move)

  def hasWon(self, player):
    #Returns whether a player has won or not
    return self.game.hasWon(player)

  def isValid(self, move):
    #Returns whether a move is valid or not
    return self.game.isValid(move)

  def printBoard(self):
    #Returns a string representation of the current board state
    return self.game.printBoard()

  def play(self, player, move):
    if self.isValid(move):
      self.nextBoard(player, move)
      self.isOver = self.hasWon(player)
    else:
      raise Exception("Invalid move!")

  def createEmbed(self, content):
    #This creates the embed that visually displays the state of the game, the content passed in should be a string rep of the board state
    embed = discord.Embed()
    #Name is the header text of the embed, value is the body of the embed
    embed.add_field(name='Connect Four - Player ' + str(self.currentPlayer[0]) + ' it is your turn', value=content ,inline=False)
    return embed

  def getColumn(self, emoji):
    #Takes in an emoji and returns an integer representing the column it's associated with
    i = 0
    for reaction in self.reactions:
      if emoji == reaction:
        return i
      else:
        i += 1

  def nextPlayer(self):
    #Cycle between players every move
    if self.currentPlayer == self.player1:
      self.currentPlayer = self.player2
    else:
      self.currentPlayer = self.player1

  def cleanupGame(self):
    #Reset all the variables associated with the game
    self.game = None
    self.isOver = False
    self.isPlaying = False
    self.gameMessage = None
    self.player1 = None
    self.player2 = None
    self.currentPlayer = None

  @commands.command()
  async def c4(self, ctx, mention1: str, mention2: str):
    #Checks if the arguments are mentions and if no games are currently occuring
    if (mention1[0] == '<' and mention1[-1] == '>' and mention2[0] == '<' and mention2[-1] == '>' and self.isPlaying == False):
      #Initialise a new connect four board
      self.game = connectFour.Game(6, 7)
      #Discord mentions are inconsistent, some include '!' others do not
      #So we store both possibilities as a tuple alongside the player ID
      self.player1 = (1, mention1, mention1.replace('!', ''))
      self.player2 = (2, mention2, mention2.replace('!', ''))
      #We start the game with player 1
      self.currentPlayer = self.player1
      #Create embed used by the bot to display the board
      embed = self.createEmbed(self.printBoard())
      #Grab the message object so we can interact and edit the message later
      self.gameMessage = await ctx.send(embed=embed)
      #Add reactions to the message as a proxy for player interaction
      for reaction in self.reactions:
        await self.gameMessage.add_reaction(reaction)
        await asyncio.sleep(0.5)
      #Prevents other games from being Initialised
      self.isPlaying = True
    else:
      #Bot command was formatted incorrectly
      await ctx.send("Invalid format")

  @commands.Cog.listener('on_reaction_add')
  async def getNextMove(self, reaction, user):
    if self.isPlaying == True:
      #check reaction is for the relevant message (our game embed) and if the
      #user reacting is the user who's turn it currently is
      if reaction.message == self.gameMessage and (user.mention == self.currentPlayer[1] or user.mention == self.currentPlayer[2]):
        #convert emoji react into column index
        col = self.getColumn(reaction.emoji)
        try:
          #Perform next move and switch turn to next player
          self.play(self.currentPlayer[0], col)
          self.nextPlayer()
        except:
          #Invalid move, player can try again, board doesn't change
          await reaction.message.channel.send("Invalid move!")
        embed = self.createEmbed(self.printBoard())
        #Update the board display
        await self.gameMessage.edit(embed=embed)

      if self.isOver:
        #We cycle back to the player that made the winning move
        self.nextPlayer()
        await reaction.message.channel.send(self.currentPlayer[1] + " Congratulations you win!")
        #Reset class variables/attributes for next game
        self.cleanupGame()
      
      #Remove the reaction applied by the user, so they can react again
      await reaction.remove(user)
      return
    return

  @commands.command()
  async def killGame(self, ctx):
    #Terminates a game session
    self.cleanupGame()
    await ctx.send("Game has been stopped.")
  