# LVLE
Pygame level editor in python


Load the level in your game 

'''

import json


grid = {}
with open("level.json", "r") as f:
    data = json.load(f)
    for key, tid in data.items():
        x_str, y_str = key.split(",")
        grid[(int(x_str), int(y_str))] = tid

'''