import json
path_input = "config/setups/the_wall.json"
path_output = "config/setups/the_wall_fixed.json"

data = json.load(open(path_input, "r"))
for coord in data["coordinates"]:
    if len(coord) == 2:
        coord.append(0)
json.dump(data, open(path_output, "w"), indent=4)