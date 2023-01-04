class Game:
  class Node:
    def __init__(self, player=0):
      #Represents the player that controls the node
      #Player=0 means no one controls the node
      self.player = player

    def getPlayer(self):
      return self.player

    def setPlayer(self, player):
      self.player = player

  def __init__(self, height, width):
    #Initializes an empty board with the given dimensions
    #Regular connect four is on a 6x7 (row x column) board
    self.height = height
    self.width = width
    self.board = [[self.Node() for j in range(self.height)] for i in range(self.width)]

  def nextBoard(self, player, col):
    #Updates the board given a player and its move
    for node in self.board[col]:
      if node.getPlayer() == 0:
        node.setPlayer(player)
        return

  def isValid(self, col):
    #checks if the given move is valid
    return self.board[col][-1].getPlayer() == 0

  def hasWon(self, player):
    #checks if the given player has won

    #check rows
    for j in range(self.height):
        for i in range(self.width - 3):
            if self.board[i][j].getPlayer() == player and self.board[i+1][j].getPlayer() == player and self.board[i+2][j].getPlayer() == player and self.board[i+3][j].getPlayer() == player:
              return True

    #check columns
    for i in range(self.width):
        for j in range(self.height - 3):
            if self.board[i][j].getPlayer() == player and self.board[i][j+1].getPlayer() == player and self.board[i][j+2].getPlayer() == player and self.board[i][j+3].getPlayer() == player:
              return True

    #check increasing diagonals
    for i in range(3, self.width):
        for j in range(self.height - 3):
            if self.board[i][j].getPlayer() == player and self.board[i-1][j+1].getPlayer() == player and self.board[i-2][j+2].getPlayer() == player and self.board[i-3][j+3].getPlayer() == player:
              return True

    #check decreasing diagonals
    for i in range(3, self.width):
        for j in range(3, self.height):
            if self.board[i][j].getPlayer() == player and self.board[i-1][j-1].getPlayer() == player and self.board[i-2][j-2].getPlayer() == player and self.board[i-3][j-3].getPlayer() == player:
              return True

    return False

  def printBoard(self):
    #Returns a string representation of the current board
    result = ''
    for j in range(-1, ((self.height + 1) * -1), -1):
      for i in range(self.width):
        nodeString = self.playerToColour(self.board[i][j].getPlayer())
        if i == self.width - 1:
          result += '│' + nodeString + '│' + '\n═════════════════════════\n'
        else:
          result += '│' + nodeString + '│'
    return result

  def playerToColour(self, id):
    #Converts the player's nodes to an image
    #Player 1 is yellow, Player 2 red, and Empty node is white
    if id == 0:
      return ':white_circle:'
    elif id == 1:
      return ":yellow_circle:"
    else:
      return ":red_circle:"

#Code below is used to play the game in the terminal (useful for testing)

#If testing in terminal replace:
#':white_circle:' with '⚪'
#':yellow_circle:' with '🟡'
#':red_circle:' with '🔴'

# def play(board):
#     isOver = False
#     i = 0
#     print(board.printBoard())
#     while isOver == False:
#         if i%2 == 0:
#             player = 1
#         else:
#             player = 2
#         i += 1
#         col = int(input("Enter column: ")) - 1
#         board.nextBoard(player, col)
#         isOver = board.hasWon(player)
#         print(board.printBoard())

# if __name__ == '__main__':
#     b = Game(6, 7)
#     play(b)


    