# Tree Simulator documentation

The tree simulator is built as a replacement for the Effect class, which all effects have to inherit from. This new class handles the simulation, displaying and generating sample coordinates for the tree. Note that these coordinates are completely random and will look different than physical placement of lights in a ring formation. They are also not ordered like the physical lights, so any effects that rely on running along the line of lights will not work as expected.

## class Simulation

### values:

- `(list[[x,y,z]]) points` - list of 3D coordinates of the points
- `(list[[r,g,b]]) colors` - list of RGB colors of the points (in range 0-255)
- `(float) height` - height of the tree (defaults to 2.4)
- `(float) diameter` - diameter of the base of the tree (defaults to 1.5)
- `(float) num_points` - amount of points on the tree (defaults to 200)

### pyvista values (do not override these, used for the simulation):
- plotter
- cloud
- actor

### functions:
- `__init__()` - displays the tree
- `update_colors()` - updates the lights
