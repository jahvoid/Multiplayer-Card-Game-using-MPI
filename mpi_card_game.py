from mpi4py import MPI
import random


#Initializing MPI communicator for all process
comm = MPI.COMM_WORLD

rank = comm.Get_rank() 


"""
    Searches the player's hand for a card that matches
    the rank of the current board card.

    Parameters:
    hand (list): list of cards held by the player
    board_card (tuple): current card on the board (rank, suit)

    Returns:
    tuple: matching card if found
    None: if no matching card exists
    """
    
def find_matching_card(hand, board_card):
    board_rank = board_card[0]

    #Checks for each card in player's hand
    for card in hand:
        if card[0] == board_rank:
            return card
    return None

#Player logic for task 3 and 5
def player_logic():

    """
    Implements behavior for all player processes (rank != 0).

    Player responsibilities:
    - Receive initial hand from dealer
    - Wait for turn signal from dealer
    - Play matching card if possible
    - Request card from dealer if no match
    - Send game status back to dealer
    - Terminate when dealer signals game end
    """


    #Dealer send message containing player's starting cards
    data = comm.recv(source=0)

    if data['type'] != "init":
        return 
    
    hand = data["hand"]
    print(f"Player {rank} received hand: {hand}")


    #Player continuous awaits dealer instructions
    while True:
        message = comm.recv(source=0)


        # Terminiation logic
        if message["type"] == "terminate" :
            print(f"Player {rank} terminating.")
            break

        if message["type"] == "turn": 

            #Dealer sends the current board card
            board_card = message["board"]
            print(f"Player {rank} turn. Board card: {board_card}")

            #Find matching card in player's hand
            match = find_matching_card(hand, board_card)

        #Play card if match exists
            if match:
                #Removes card from player's hand
                hand.remove(match)

                print(f"Player {rank} plays {match}")

        #Checks if player wins
                if len(hand) == 0:
                    #Notify dealer that player has won
                    comm.send({"status": "wins", "card" : match}, dest=0)
                    print(f"Player {rank}  !!!WINS!!!")
                    break
                
                #Send played card to dealer
                comm.send({"status": "played", "card": match}, dest=0)


        #Logic is no matching card is found, player should draw from deck
        else: 
            print(f"Player {rank} cannot play. ")
            print("Requesting card....")

            # Inform dealer that player cannot play
            # Dealer will respond with a card from deck
            comm.send({"status": "pass"}, dest=0)

    #Recieve drawn card from dealer
            draw_msg = comm.recv(source=0)

            # Dealer sends card using message type "draw_card"
            if draw_msg["type"] == "draw_card":
                drawn_card = draw_msg["card"]

            # Add card to hand if deck is not empty
                if drawn_card is not None:
                    hand.append(drawn_card)
                    print("Player {rank} drew {drawn_card}")

                else:
                    print(f"Player {rank} cannot draw, the deck is empty.")
            # End turn after drawing 
            comm.send({"status":"pass"}, dest=0)


def main():
    if rank == 0:
        pass

    else:
        player_logic()


if __name__ == "__main__":
    main()
   

