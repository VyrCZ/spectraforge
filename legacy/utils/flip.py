# script made to flip the y and z coordinates in a file named "coordinates.txt"

# Open the file in read mode
with open("coordinates.txt", "r") as file:
    # Read each line of the file
    lines = file.readlines()

# Open the file in write mode
with open("coordinates.txt", "w") as file:
    # Iterate over the lines
    for line in lines:
        # Split the line by comma
        x, y, z = line.strip().split(",")

        # Flip the y and z coordinates
        flipped_coordinates = f"{x},{z},{y}"

        # Write the modified coordinates to the file
        file.write(flipped_coordinates + "\n")
