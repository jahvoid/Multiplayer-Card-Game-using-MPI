from mpi4py import MPI
import random

comm = MPI.COMM_WORLD
rank = comm.Get_rank() 


    
def find_matching_card(hand, board_card):
    board_rank = board_card[0]

    for card in hand:
        if card[0] == board_rank:
            return card
    return None

def player_logic():

    #Receiving hand from dealer
    data = comm.recv(source=0)

    if data['type'] != "init":
        return 
    
    hand = data["hand"]
    print(f"Player {rank} received hand: {hand}")

    while True:
        message = comm.recv(source=0)

        if message["type"] == "terminate" :
            print(f"Player {rank} terminating.")
            break

        if message["type"] == "turn": 
            board_card = message["board"]
            print(f"Player {rank} turn. Board card: {board_card}")

            #Find matching card
            match = find_matching_card(hand, board_card)

        #Play card if match
            if match:
                hand.remove(match)

                print(f"Player {rank} plays {match}")

        #Checks if players wins
                if len(hand) == 0:
                    comm.send({"status": "wins", "card" : match}, dest=0)
                    print(f"Player {rank}  !!!WINS!!!")
                    break
                
                #Send played card to dealer
                comm.send({"status": "played", "card": match}, dest=0)

        else: 
            print(f"Player {rank} passes")
            comm.send({"status": "pass"}, dest=0)


def main():
    if rank == 0:
        pass

    else:
        player_logic()


if __name__ == "__main__":
    main()
   

