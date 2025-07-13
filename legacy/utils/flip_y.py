# Invert the Y axis, make the highest point the lowest and vice versa
import json

file = "config/setups/the_wall.json"
with open(file, "r") as f:
    data = json.load(f)

minY = min(coord[1] for coord in data["coordinates"])
maxY = max(coord[1] for coord in data["coordinates"])
normalized_Y = []
height = maxY - minY
# Normalize the Y coordinates to a range of 0 to 1
for coord in data["coordinates"]:
    new_y = (coord[1] - minY) / height
    normalized_Y.append(new_y)

for i, coord in enumerate(data["coordinates"]):
    # invert | round because float
    coord[1] = int(round((1 - normalized_Y[i]) * height))

# Save the modified data back to the file
with open(file, "w") as f:
    json.dump(data, f, indent=4)