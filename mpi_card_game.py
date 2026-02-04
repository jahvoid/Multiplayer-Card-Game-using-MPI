from mpi4py import MPI
import random

# Task 1: Game Setup - Yatharth
def createDeck():
    deck = []

    # Temporary
    return [random.randint(1, 13) for _ in range(52)]

# Task 2: Dealer logic - Miyuki
class Dealer:
    def __init__(self, player_num, deck):
        self.rank = 0
        self.player_num = player_num
        self.deck = deck
        self.current_card = None

    def deal_hands(self, comm):
        for i in range(1,self.player_num + 1):
            hand = random.sample(self.deck, 4)
            comm.send(hand, dest=i)
    
    def broadcast_card(self, comm):
        card = random.randint(1, 13)
        self.current_card = card
        return comm.bcast(card, root=self.rank)

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

    deck = createDeck()

    if rank == 0:
        dealer = Dealer(size -1, deck)
        card = dealer.current_card
        dealer.deal_hands(comm)
        
    else:
        player = Player(rank)
        dealer = None
        card = None
        player.hand = comm.recv(source=0)
        print(player.hand)

    dealer = comm.bcast(dealer, root=0)
    card = dealer.broadcast_card(comm)
    
    print(f"Process {rank}: received {card}")


main()