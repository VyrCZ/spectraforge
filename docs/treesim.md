# Tree Simulator documentation

look at effects/flashy.py for a simple example.

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
