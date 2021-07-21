boardRef = [
         0 , 1 , 2 , 3 , 4 , 5  , 6,
         7 , 8 , 9 , 10, 11, 12, 13,
         14, 15, 16, 17, 18, 19, 20,
         21, 22, 23, 24, 25 ,26, 27,
         28, 29 ,30, 31, 32, 33, 34,
         35, 36, 37, 38, 39, 40, 41
         ]
col1 = [0, 7 , 14 ,21 ,28 ,35]
col2 = [1, 8 , 15, 22, 29, 36]
col3 = [2, 9 , 16, 23, 30, 37]
col4 = [3, 10, 17, 24, 31, 38]
col5 = [4, 11, 18, 25, 32, 39]
col6 = [5, 12, 19 ,26, 33, 40]
col7 = [6, 13, 20, 27, 34, 41]

class Board:
  # Don't ask me why I made classes, I don't even know why I did
    class Node:
        def __init__(self, colour=None):
            # colour can be either 'r', 'y', or None
            self.colour = colour

        def getColour(self):
            return self.colour

        def setColour(self, colour):
            if colour == 'r':
                self.colour = ":red_circle:"
            elif colour == 'y':
                self.colour = ":yellow_circle:"
            else:
                return

    def __init__(self):
        self.board = [self.Node() for i in range(42)]

    def makeMove(self, player, col):
        try:
            moveIndex = self.place_piece(player, col)
            if self.hasWon(moveIndex):
                return True
            else:
                return False
        except:
            raise Exception()

    def hasWon(self, moveIndex):
        c = self.checkColumn(moveIndex)
        r = self.checkRow(moveIndex)
        d = self.checkDiagonals(moveIndex)
        if c or r or d:
            return True
        else:
            return False

    def checkColumn(self, index):
        colour = self.board[index].getColour()
        upIndex = index + 7
        streak = 1
        while upIndex >= 0 and upIndex < 42:
            if self.board[upIndex].getColour() == colour:
                streak += 1
                if streak >= 4:
                    return True
            else:
                break
            upIndex += 7
        downIndex = index - 7
        streak = 1
        while downIndex >= 0 and downIndex < 42:
            if self.board[downIndex].getColour() == colour:
                streak += 1
                if streak >= 4:
                    return True
            else:
                break
            downIndex -= 7
        return False

    def checkRow(self, index):
        colour = self.board[index].getColour()
        row = index // 7
        low = row * 7
        high = low + 6
        rIndex = index + 1
        streak = 1
        while rIndex >= low and rIndex <= high:
            if self.board[rIndex].getColour() == colour:
                streak += 1
                if streak >= 4:
                    return True
            else:
                break
            rIndex += 1
        lIndex = index - 1
        streak = 1
        while lIndex >= low and lIndex <= high:
            if self.board[lIndex].getColour() == colour:
                streak += 1
                if streak >= 4:
                    return True
            else:
                break
            lIndex -= 1
        lIndex = index + -1
        rIndex = index + 1
        streak = 1
        # Jank solution can be incorporated into earlier checks lol xD haha
        while lIndex >= low and rIndex >= low and lIndex <= high and rIndex <= high:
            if self.board[rIndex].getColour() == colour:
                streak +=1
                if streak >= 4:
                    return True
            if self.board[lIndex].getColour() == colour:
                streak += 1
                if streak >= 4:
                    return True
            else:
                break
            lIndex -= 1
            rIndex += 1
        return False

    def checkDiagonals(self, index):
        colour = self.board[index].getColour()
        ulIndex = index - 8
        streak = 1
        while ulIndex >= 0 and ulIndex < 42:
            if self.board[ulIndex].getColour() == colour:
                streak += 1
                if streak >= 4:
                    return True
            else:
                break
            ulIndex -= 8
        urIndex = index - 6
        streak = 1
        while urIndex >= 0 and urIndex < 42:
            if self.board[urIndex].getColour() == colour:
                streak += 1
                if streak >= 4:
                    return True
            else:
                break
            urIndex -= 6
        brIndex = index + 8
        streak = 1
        while brIndex >= 0 and brIndex < 42:
            if self.board[brIndex].getColour() == colour:
                streak += 1
                if streak >= 4:
                    return True
            else:
                break
            brIndex += 8
        blIndex = index + 6
        streak = 1
        while blIndex >= 0 and blIndex < 42:
            if self.board[blIndex].getColour() == colour:
                streak += 1
                if streak >= 4:
                    return True
            else:
                break
            blIndex += 6
        return False

    def place_piece(self, player, col):
        # player is an integer, either 1(Yellow) or 2(Red)
        # col is the column the player wants to drop the piece
        # Future Jason here - IDK why I did this
        if player == 1 and self.isValid(col):
            index = self.place('y', col)
            return index
        elif player == 2 and self.isValid(col):
            index = self.place('r', col)
            return index
        else:
            raise Exception()

    def isValid(self, col):
        return self.board[col - 1].getColour() == None

    def place(self, colour, col):
        column = self.getColumn(col)
        for i in range(-1, -7, -1):
            index = column[i]
            if self.board[index].getColour() == None:
                self.board[index].setColour(colour)
                return index

    def getColumn(self, col):
        if col == 1:
            return col1
        elif col == 2:
            return col2
        elif col == 3:
            return col3
        elif col == 4:
            return col4
        elif col == 5:
            return col5
        elif col == 6:
            return col6
        else:
            return col7

    def print_board(self):
      # Pain in the ass to create
        result = ''
        i = 0
        for node in self.board:
            if node.getColour() == None:
                nodeString = ':white_circle:'
            else:
                nodeString = node.getColour()
            if i%7 == 0 and i != 0:
                result += '\n═════════════════════════\n'
                result += '│' + nodeString + '│'
            else:
                result += '│' + nodeString + '│'
            i += 1
        return result

def play(b, player, col):
  # I literally don't even use this, why is this here?
    try:
        isOver = b.makeMove(player, col)
        boardState = b.print_board()
    except:
        return -1
    return (b, boardState, isOver)