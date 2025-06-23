import json

input = "coordinates.txt"
output = "coordinates.json"

with open(input, "r") as f:
    coords_str = f.readlines()

coords = []
for coord in coords_str:
    coord = coord.split(",")
    coords.append([int(value) for value in coord])

with open(output, "w") as f:
    json.dump(coords, f, indent=4)