from tile import SafeTile, PropertyTile, TaxTile, ActionTile

class Board:
    def __init__(self):
        self.tiles = self.initializeTiles()

    def initializeTiles(self):
        tiles: list = [None] * 40
        
        # Corners
        tiles[0] = SafeTile("Go", 0)
        tiles[10] = SafeTile("Jail (Just Visiting)", 10)
        tiles[20] = SafeTile("Free Parking", 20)
        tiles[30] = SafeTile("Go To Jail", 30)

        # Taxes
        tiles[4] = TaxTile("Income Tax", 4, 200)
        tiles[38] = TaxTile("Luxury Tax", 38, 100)

        # Action Tiles
        for idx in [2, 17, 33]: tiles[idx] = ActionTile("Community Chest", idx)
        for idx in [7, 22, 36]: tiles[idx] = ActionTile("Chance", idx)

        # Subset of Properties
        tiles[1] = PropertyTile("Mediterranean Avenue", 1, 60, [2, 10, 30, 90, 160, 250], "Brown")
        tiles[3] = PropertyTile("Baltic Avenue", 3, 60, [4, 20, 60, 180, 320, 450], "Brown")
        
        tiles[5] = PropertyTile("Reading Railroad", 5, 200, [25, 50, 100, 200], "Railroad")
        tiles[15] = PropertyTile("Pennsylvania Railroad", 15, 200, [25, 50, 100, 200], "Railroad")
        
        tiles[6] = PropertyTile("Oriental Avenue", 6, 100, [6, 30, 90, 270, 400, 550], "Light Blue")
        tiles[8] = PropertyTile("Vermont Avenue", 8, 100, [6, 30, 90, 270, 400, 550], "Light Blue")
        tiles[9] = PropertyTile("Connecticut Avenue", 9, 120, [8, 40, 100, 300, 450, 600], "Light Blue")

        # Fill the remaining slots with safe placeholders
        for i in range(40):
            if tiles[i] is None:
                tiles[i] = SafeTile(f"Placeholder {i}", i)
        
        return tiles

    def getTile(self, index):
        return self.tiles[index]