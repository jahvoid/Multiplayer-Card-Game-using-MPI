from mpi4py import MPI

# Task 1: Game Setup - Yatharth
def createDeck():
    deck = []

# Task 2: Dealer logic - Miyuki
class Dealer:
    def __init__(self):
        self.rank = 0

# Task 3: Player Logic - Jayna
class Player:
    def __init__(self, rank):
        self.rank = rank

# Task 4: Ensure Deadlock Prevention and MPI Termination - Yatharth
def main():
    comm = MPI.COMM_WORLD
    size = comm.Get_size()
    rank = comm.Get_rank()

