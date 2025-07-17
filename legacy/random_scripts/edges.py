import numpy as np
import matplotlib.pyplot as plt

# 1) Generate or load your point cloud:
#    Here we'll make a noisy grid for demonstration.
xg = np.linspace(0, 10, 30)
yg = np.linspace(0, 5, 15)
xx, yy = np.meshgrid(xg, yg)
pts = np.vstack([xx.ravel(), yy.ravel()]).T
pts += 0.2*np.random.randn(*pts.shape)

# 2) Compute convex hull via Andrew’s monotone chain:
def convex_hull(points):
    # sort lexicographically
    pts = sorted(map(tuple, points))
    if len(pts) <= 1: 
        return pts
    def half_chain(pts):
        chain = []
        for p in pts:
            while len(chain) >= 2 and ((chain[-1][0]-chain[-2][0])*(p[1]-chain[-2][1])
                                     - (chain[-1][1]-chain[-2][1])*(p[0]-chain[-2][0])) <= 0:
                chain.pop()
            chain.append(p)
        return chain

    lower = half_chain(pts)
    upper = half_chain(reversed(pts))
    # omit last point of each (it's repeated)
    return lower[:-1] + upper[:-1]

hull_pts = np.array(convex_hull(pts))

# 4) Plot both
fig, ax = plt.subplots(figsize=(8, 4))
ax.scatter(pts[:,0], pts[:,1], s=10, cmap='rainbow', c=pts[:,0]+pts[:,1])
hull_closed = np.vstack([hull_pts, hull_pts[0]])
ax.plot(hull_closed[:,0], hull_closed[:,1], 'w--', lw=2, zorder=10, label='Convex hull', color="green")
ax.set_aspect('equal', 'box')
ax.legend()
ax.set_title("Convex vs. Concave Hull of a 2D Point Cloud")
plt.show()
