import random
import json
from player import Player
from board import Board

class GameManager:
    def __init__(self, playerNames):
        self.players = [Player(name) for name in playerNames]
        self.board = Board()
        self.activePlayerIndex = 0

    def rollDice(self):
        die1 = random.randint(1, 6)
        die2 = random.randint(1, 6)
        return die1 + die2, die1 == die2

    def executeTurn(self):
        activePlayer = self.players[self.activePlayerIndex]
        rollTotal, isDouble = self.rollDice()
        
        print(f"\n{activePlayer.playerName} rolled a {rollTotal} {'(Doubles!)' if isDouble else ''}")
        self.resolveMovement(activePlayer, rollTotal)

        if not isDouble:
            self.activePlayerIndex = (self.activePlayerIndex + 1) % len(self.players)

    def resolveMovement(self, player, steps):
        player.moveSpaces(steps)
        landedTile = self.board.getTile(player.boardPosition)
        print(f"  -> Landed on: {landedTile.name} (Space {landedTile.index})")
        landedTile.onLand(player, self)

    def promptBuyDecision(self, player, propertyTile):
        if player.deductFunds(propertyTile.price):
            propertyTile.ownerId = player.playerName
            player.addProperty(propertyTile.index)
            print(f"  -> ACTION: {player.playerName} bought {propertyTile.name} for ${propertyTile.price}.")
        else:
            print(f"  -> ACTION: {player.playerName} cannot afford {propertyTile.name}.")

    def processRentPayment(self, payingPlayer, receivingPlayerId, amount):
        receivingPlayer = next(p for p in self.players if p.playerName == receivingPlayerId)
        if payingPlayer.deductFunds(amount):
            receivingPlayer.addFunds(amount)
            print(f"  -> TRANSACTION: {payingPlayer.playerName} paid ${amount} rent to {receivingPlayerId}.")
        else:
            print(f"  -> BANKRUPTCY: {payingPlayer.playerName} cannot afford ${amount} rent!")

    # --- NEW: Reward & Equity Math ---
    def calculateEquity(self, player):
        """Calculates total net worth: Cash + (Property Values)"""
        equity = player.cashBalance
        for propId in player.ownedProperties:
            equity += self.board.getTile(propId).price
        return equity

    def proposeTrade(self, initiatorId, targetId, offerData):
        initiator = next(p for p in self.players if p.playerName == initiatorId)
        target = next(p for p in self.players if p.playerName == targetId)
        
        # Translate IDs to readable names for the terminal
        giveNames = [self.board.getTile(pid).name for pid in offerData['giveProps']]
        recvNames = [self.board.getTile(pid).name for pid in offerData['receiveProps']]
        
        print(f"\n--- TRADE PROPOSAL ---")
        print(f"{initiator.playerName} offers {target.playerName}:")
        print(f"GIVING: ${offerData['giveCash']} and Properties: {giveNames}")
        print(f"FOR: ${offerData['receiveCash']} and Properties: {recvNames}")
        
        self.executeTrade(initiator, target, offerData)

    def executeTrade(self, initiator, target, offerData):
        # 1. Snapshot pre-trade equity (BATNA baseline)
        initiatorPreEquity = self.calculateEquity(initiator)
        targetPreEquity = self.calculateEquity(target)

        # 2. Execute Asset Swap
        initiator.deductFunds(offerData["giveCash"])
        target.addFunds(offerData["giveCash"])
        target.deductFunds(offerData["receiveCash"])
        initiator.addFunds(offerData["receiveCash"])
        
        for propId in offerData["giveProps"]:
            initiator.removeProperty(propId)
            target.addProperty(propId)
            self.board.getTile(propId).ownerId = target.playerName
            
        for propId in offerData["receiveProps"]:
            target.removeProperty(propId)
            initiator.addProperty(propId)
            self.board.getTile(propId).ownerId = initiator.playerName
            
        print("  -> ACTION: Trade Accepted and Executed.")

        # 3. Calculate post-trade equity and print the RL Reward shift
        initiatorPostEquity = self.calculateEquity(initiator)
        targetPostEquity = self.calculateEquity(target)
        
        print("\n  -> [BATNA EVALUATOR]:")
        print(f"     {initiator.playerName} Equity Shift: ${initiatorPreEquity} -> ${initiatorPostEquity} (Delta: ${initiatorPostEquity - initiatorPreEquity})")
        print(f"     {target.playerName} Equity Shift: ${targetPreEquity} -> ${targetPostEquity} (Delta: ${targetPostEquity - targetPreEquity})")

    def serializeGameState(self, activePlayer):
        def formatProperties(propertyIds):
            props = []
            for propId in propertyIds:
                tile = self.board.getTile(propId)
                props.append({
                    "id": tile.index,
                    "name": tile.name,
                    "colorGroup": tile.colorGroup,
                    "price": tile.price,
                    "currentRent": tile.calculateRent()
                })
            return props

        stateDict = {
            "myState": {
                "name": activePlayer.playerName,
                "cash": activePlayer.cashBalance,
                "position": self.board.getTile(activePlayer.boardPosition).name,
                "ownedProperties": formatProperties(activePlayer.ownedProperties)
            },
            "opponents": []
        }
        
        for player in self.players:
            if player.playerName != activePlayer.playerName:
                stateDict["opponents"].append({
                    "name": player.playerName,
                    "cash": player.cashBalance,
                    "ownedProperties": formatProperties(player.ownedProperties)
                })
                
        return json.dumps(stateDict, indent=2)