import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Load coordinates from file
with open("coordinates.txt", "r") as file:
    lines = file.readlines()

# Parse coordinates
x_coords = []
y_coords = []
z_coords = []

for line in lines:
    coords = line.strip().split(",")
    x_coords.append(float(coords[0]))
    y_coords.append(float(coords[1]))
    z_coords.append(float(coords[2]))

# Create 3D plot
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

# Plot coordinates
ax.scatter(x_coords, y_coords, z_coords)

# Set labels and title
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('3D Coordinate Plot')

# Show the plot
plt.show()
