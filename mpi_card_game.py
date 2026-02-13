from mpi4py import MPI
import random
import time

# Task 1: Game Setup - Yatharth
def create_deck():
    """
    Creates a standard 52-card deck.
    Each card is represented as a tuple: (rank, suit).
    The deck is shuffled before being returned.
    """
    
    ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']

    deck = []

    # Manually building the card deck
    for suit in suits:
        for rank in ranks:
            deck.append((rank, suit))

    random.shuffle(deck)

    return deck

# Task 2: Dealer logic - Miyuki
class Dealer:
    def __init__(self, num_players, deck):
        self.num_players = num_players
        self.deck = deck
        self.current_card = None
        self.player = 1

    # deal 4 cards from deck to each player
    def deal_hands(self, comm, cards_per_player=4):
        
        # Check if there are enough cards to deal to all players - Added to prevent deadlock - yatharth
        required = self.num_players * cards_per_player

        # If not enough cards, end game immediately by sending "end" message to all players
        if len(self.deck) < required:
            print(f"[Dealer] Not enough cards to deal: need {required}, have {len(self.deck)}. Ending.")
            for p in range(1, self.num_players + 1):
                comm.send("end", dest=p)
            return False

        # Deal cards to each player
        for p in range(1, self.num_players + 1):
            # Previous version could crash if the deck ran out (pop from empty list),
            # which would leave other ranks blocked on recv(). Added deck-size check to terminate cleanly.
            # Previous code -> hand = [self.deck.pop() for _ in range(4)]

            hand = [self.deck.pop() for _ in range(cards_per_player)]
            comm.send(hand, dest=p)
        return True
    
    # draw a new board card from deck
    def draw_board_card(self):
        # Added to prevent deadlock - yatharth
        if not self.deck:
            self.current_card = None
            print("[Dealer] Deck empty. Ending game.")
            return False
        self.current_card = self.deck.pop()
        print(f"[Dealer] New Board card: {self.current_card}")
        return True
    
    # simulate game round
    def play_round(self, comm):
        # If deck is empty and no one has won, end game
        if self.current_card is None:
            for p in range(1, self.num_players + 1):
                comm.send("end", dest=p)
            return True

        new_card = False
        # run through all player turns
        # Dealer sends one turn message to every player.
        # Only the active player replies (exactly one send), matching recv(source=active) below.

        for active in range(1, self.num_players + 1):

            # Send turn info to ALL players
            for p in range(1, self.num_players + 1):
                comm.send(
                    {
                        "active": (p == active),
                        "board": self.current_card
                    },
                    dest=p
                )

            # Recieve player turn response
            played_card, status = comm.recv(source=active)
            print(f"[Dealer] Player {active} status: {status}", flush=True)
            time.sleep(0.1)

            # player card matched, set new board card
            if status == "play":
                self.current_card = played_card
                print(f"[Dealer] Updated Board card: {self.current_card}")
                new_card = True

            # player has no more cards
            elif status == "win":
                for i in range(1, self.num_players + 1):
                    comm.send("win", dest=i)
                return True

        # No winner, tell all players to continue
        for active in range(1, self.num_players + 1):
            comm.send("continue", dest=active)

        # if no one has played a card in the round, a new card is drawn from the deck
        # Added to prevent deadlock - yatharth
        if not new_card:
            ok = self.draw_board_card()
            if not ok:
                for p in range(1, self.num_players + 1):
                    comm.send("end", dest=p)
                return True 

        return False

# Task 3: Player Logic - Jayna
class Player:
    def __init__(self, rank):
        self.rank = rank
        self.hand = []

    def take_turn(self, board_card):
        board_rank = board_card[0]

        # Find the first matching rank card
        for card in self.hand:
            if card[0] == board_rank:
                self.hand.remove(card)

                # If hand empty after playing, player wins
                if len(self.hand) == 0:
                    return card, "win"

                return card, "play"

        # No match
        return board_card, "pass"


# Task 4: Ensure Deadlock Prevention and MPI Termination - Yatharth
def main():
    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()

    if rank == 0:
        # create/initialize dealer for rank 0
        deck = create_deck()
        dealer = Dealer(size -1, deck)
        
        #Previous code caused deadlock due to multiple pops from the deck - yatharth
        # Previous code -> dealer.deal_hands(comm)
        # Previous code -> dealer.draw_board_card()

        # Added checks so dealer never crashes on empty deck; dealer broadcasts "end" to release players.
        ok = dealer.deal_hands(comm)
        if not ok:
            print("Game Over!")
            return

        ok = dealer.draw_board_card()
        if not ok:
            for p in range(1, dealer.num_players + 1):
                comm.send("end", dest=p)
            print("Game Over!")
            return


        # dealer game loop
        game_over = False
        while not game_over:
            # check if deck is empty and end game if so - added to prevent deadlock - yatharth
            game_over = dealer.play_round(comm)
        print("Game Over!")
        
    else:
        # create player for all other ranks
        player = Player(rank)
        player.hand = comm.recv(source=0)
        print (f"[Player {rank}] Hand recieved: {player.hand}", flush=True)

        # player game loop
        while True:
            msg = comm.recv(source=0)

            if msg in ("win", "end"):
                break


            if msg == "continue":
                continue

            # play only on players turn
            if msg["active"]:
                played_card, status = player.take_turn(msg["board"])
                comm.send((played_card, status), dest=0)

main()