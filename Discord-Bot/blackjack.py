import pydealer

class Game():
    class Player():
        # Represents a player in the game of blackjack
        def __init__(self):
            self.hand = None
            self.value = 0

        def calcValue(self):
        if not self.hand:
            return 0
        num_aces = 0
        total_value = 0
        for card in self.hand:
            if pydealer.const.DEFAULT_RANKS['values'][card.value] == 13:
                num_aces += 1
                total_value += 11
            elif pydealer.const.DEFAULT_RANKS['values'][card.value] >= 10:
                total_value += 10
            else:
                total_value += int(card.value)

        while num_aces > 0 and total_value > 21:
                total_value -= 10
                num_aces -= 1
        return total_value

    # Represents a game of blackjack
    def __init__(self):
        self.players = None
        self.deck = pydealer.Deck()
        self.dealer = None

    def start(self, players):
        self.dealer = players[0]
        self.players = players[1:]
        self.deck.shuffle()
        self.dealer.hand = self.deck.deal(1)
        for player in players:
            player.hand = self.deck.deal(2)
