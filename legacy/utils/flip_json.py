import json

file = "config/setups/tree_2024.json"
with open(file, "r") as f:
    data = json.load(f)

# Flip the y and z coordinates in the JSON data
for coord in data["coordinates"]:
    coord[1], coord[2] = coord[2], coord[1]

# Save the modified data back to the file
with open(file, "w") as f:
    json.dump(data, f, indent=4)