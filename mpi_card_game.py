from mpi4py import MPI
import random
import time

# Task 1: Game Setup - Yatharth
def create_deck():
    deck = []
    # ChatGPT example code I was using to test, can base off of it to make your code work with mine, can delete after or just delete if not using
    # ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
    # suits = ['H', 'D', 'C', 'S']
    # deck = [(r, s) for r in ranks for s in suits]
    # random.shuffle(deck)
    # return deck

# Task 2: Dealer logic - Miyuki
class Dealer:
    def __init__(self, num_players, deck):
        self.num_players = num_players
        self.deck = deck
        self.current_card = None
        self.player = 1

    # deal 4 cards from deck to each player
    def deal_hands(self, comm):
        for p in range(1, self.num_players + 1):
            hand = [self.deck.pop() for _ in range(4)]
            comm.send(hand, dest=p)
    
    # draw a new board card from deck
    def draw_board_card(self):
        self.current_card = self.deck.pop()
        print(f"[Dealer] Board card: {self.current_card}")
    
    # simulate game round
    def play_round(self, comm):
        self.draw_board_card()

        # run through all player turns
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

            # player has no more cards
            elif status == "win":
                for i in range(1, self.num_players + 1):
                    comm.send("win", dest=i)
                return True

        # No winner, tell all players to continue
        for active in range(1, self.num_players + 1):
            comm.send("continue", dest=active)

        return False

# Task 3: Player Logic - Jayna
class Player:
    def __init__(self, rank):
        self.rank = rank
        self.hand = []

    # ChatGPT example code I was using to test, can base off of it to make your code work with mine, can delete after or just delete if not using
    # def take_turn(self, board_card):
    #     for card in self.hand:
    #         if card[0] == board_card[0]:
    #             self.hand.remove(card)
    #             if len(self.hand) == 0:
    #                 return card, "win"
    #             return card, "play"
    #     return board_card, "pass"

# Task 4: Ensure Deadlock Prevention and MPI Termination - Yatharth
def main():
    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()

    if rank == 0:
        # create/initialize dealer for rank 0
        deck = create_deck()
        dealer = Dealer(size -1, deck)
        dealer.deal_hands(comm)

        # dealer game loop
        game_over = False
        while not game_over:
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

            if msg == "win":
                break

            if msg == "continue":
                continue

            # play only on players turn
            if msg["active"]:
                played_card, status = player.take_turn(msg["board"])
                comm.send((played_card, status), dest=0)

main()