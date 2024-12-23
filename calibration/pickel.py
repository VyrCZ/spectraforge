import pickle
import os

# Step 1: Import necessary modules

# Step 2: Open and load the pickle file
with open('coordinates.pkl', 'rb') as file:
    coordinates = pickle.load(file)

# Step 3: Open the "coords.txt" file in write mode
with open('coords.txt', 'w') as file:
    # Step 4: Write each coordinate on a new line
    for coordinate in coordinates:
        file.write(f"{coordinate[0]},{coordinate[1]}\n")

# Step 5: Close the files
file.close()
