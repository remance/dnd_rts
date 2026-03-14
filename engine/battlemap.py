from pygame.sprite import Sprite
from pygame.surface import Surface
from pygame.rect import Rect

class BattleMap(Sprite):
    battle = None

    def __init__(self):
        Sprite.__init__(self)
        self.grids = {}
        self.terrains = {}
        self.heights = {}
        self.image = Surface((0, 0))
        self.rect = self.image.get_rect(topleft=(0, 0))

    def create_map(self, map_data):
        self.grids = {}
        self.terrains = {}
        self.heights = {}
        self.image = Surface((len(map_data), len(map_data[0])))
        self.rect = self.image.get_rect(topleft=(0, 0))
        for x in map_data:
            if x not in self.grids:
                self.grids[x] = {}
                self.terrains[x] = {}
                self.heights[x] = {}
            for y in map_data:
                self.grids[x][y] =
                self.terrains[x][y] = map_data[x][y]["terrain"]
                self.heights[x][y] = map_data[x][y]["height"]
