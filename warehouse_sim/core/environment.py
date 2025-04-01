"""
Environment grid layout, shelf/pallet placement, and occupancy tracking.
"""

import numpy as np
import random
from warehouse_sim import config

class Environment:
    def __init__(self, width_m, height_m, resolution):
        self.width_m = width_m
        self.height_m = height_m
        self.resolution = resolution
        self.grid_width = int(width_m / resolution)
        self.grid_height = int(height_m / resolution)
        self.occupancy = np.zeros((self.grid_width, self.grid_height), dtype=np.uint8)
        self.objects = []

    def is_free(self, x, y):
        return self.occupancy[x, y] == 0

    def place_object(self, width_m, height_m):
        gw = int(width_m / self.resolution)
        gh = int(height_m / self.resolution)
        for _ in range(1000):
            gx = random.randint(1, self.grid_width - gw - 1)
            gy = random.randint(1, self.grid_height - gh - 1)
            if np.all(self.occupancy[gx:gx+gw, gy:gy+gh] == 0):
                self.occupancy[gx:gx+gw, gy:gy+gh] = 1
                return gx, gy, gw, gh
        return None

    def place_shelves(self):
        shelf_gw = int(config.SHELF_SIZE[0] / self.resolution)
        shelf_gh = int(config.SHELF_SIZE[1] / self.resolution)
        aisle_spacing = shelf_gh + 4
        for row in range(2, self.grid_height - shelf_gh - 2, aisle_spacing):
            for _ in range(random.randint(3, 5)):
                gx = random.randint(1, self.grid_width - shelf_gw - 1)
                if np.all(self.occupancy[gx:gx+shelf_gw, row:row+shelf_gh] == 0):
                    self.occupancy[gx:gx+shelf_gw, row:row+shelf_gh] = 1
                    self.objects.append(("shelf", (gx, row, shelf_gw, shelf_gh)))

    def place_pallets(self, num):
        for _ in range(num):
            obj = self.place_object(*config.PALLET_SIZE)
            if obj:
                self.objects.append(("pallet", obj))

    def to_world_coords(self, gx, gy):
        return gx * self.resolution, gy * self.resolution

    def to_grid_coords(self, x, y):
        return int(x / self.resolution), int(y / self.resolution)
