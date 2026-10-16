from gameManager import GameManager

def main():
    print("--- Booting Monopoly Playground Engine ---")
    game = GameManager(["Agent A", "Agent B"])
    
    # Run a few turns to seed the board
    for turn in range(1, 11):
        game.executeTurn()

    # Create a mock offer: Agent A offers $50 and Reading Railroad (ID 5) for Baltic Ave (ID 3)
    offer = {
        "giveCash": 50,
        "giveProps": [5],
        "receiveCash": 0,
        "receiveProps": [3]
    }
    
    game.proposeTrade("Agent A", "Agent B", offer)

    print("\n--- Enriched Serialized State (Post-Trade) ---")
    agentA = game.players[0] 
    jsonPrompt = game.serializeGameState(agentA)
    print(jsonPrompt)

if __name__ == "__main__":
    main()