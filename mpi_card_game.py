from mpi4py import MPI
import random

# Task 1: Game Setup - Yatharth
def create_deck():
    deck = []

    # Temporary
    return [random.randint(1, 13) for _ in range(52)]

# Task 2: Dealer logic - Miyuki
class Dealer:
    def __init__(self, num_players, deck):
        self.num_players = num_players
        self.deck = deck
        self.current_card = None
        self.player = 1

    def deal_hands(self, comm):
        for p in range(1, self.num_players + 1):
            hand = [self.deck.pop() for _ in range(4)]
            comm.send(hand, dest=p)
    
    def draw_board_card(self, comm):
        self.current_card = self.deck.pop()
    
    def play_round(self, comm):
        self.draw_board_card()

        for p in range(1, self.num_players, + 1):
            # Send turn
            comm.send(self.current_card, dest=p)

            # Recieve response
            played_card, status = comm.recv(source=p)

            if status == "pass":
                self.current_card = played_card
            elif status == "win":
                # Notify all players
                for p in range(1, self.num_players + 1):
                    comm.send("win", dest=p)
                return True
        return False

# Task 3: Player Logic - Jayna
class Player:
    def __init__(self, rank):
        self.rank = rank
        self.hand = []

# Task 4: Ensure Deadlock Prevention and MPI Termination - Yatharth
def main():
    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()

    deck = create_deck()

    if rank == 0:
        dealer = Dealer(size -1, deck)
        dealer.deal_hands(comm)

        game_over = False
        while not game_over:
            game_over = dealer.play_round(comm)
        
    else:
        player = Player(rank)
        player.hand = comm.recv(source=0)

        while True:
            board_card = comm.recv(source=0)
            played_card, status = player.take_turn(board_card)
            comm.send((played_card, status), dest=0)

            if status == "win":
                break

            result = comm.recv(source=0)
            if result == "win":
                break

    #dealer = comm.bcast(dealer, root=0)
    #card = dealer.broadcast_card(comm)
    
    #print(f"Process {rank}: received {card}")

main()