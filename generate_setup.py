import random
import os
import json

dir = "config/setups"

width = 60
height = 34

data = {
    "type": "2D",
    "coordinates": []
}

for x in range(width):
    for y in range(height):
        data["coordinates"].append(
            [
                x * 10 + random.randint(-2, 2),
                y * 10 + random.randint(-2, 2),
                0
            ]
        )

file_name = f"{width}x{height}.json"
with open(os.path.join(dir, file_name), "w+", encoding="utf-8") as file:
    json.dump(data, file, indent=4)
