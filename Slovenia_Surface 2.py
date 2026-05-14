import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import cmath

def coeff_t1(t1):
    """Coefficient for x^6 term: -50i t1^6 + 50 t1^5 + 50 t1^4 - 50i t1^3 - 50i t1^2 - 50 t1 - 50i"""
    return (
        -50j * t1**6
        + 50 * t1**5
        + 50 * t1**4
        - 50j * t1**3
        - 50j * t1**2
        - 50 * t1
        - 50j
    )

def polynomial(x, t1, t2):
    """Evaluate p(x) = x^14 - x^13 + (50i t2 - 50i) x^9 + coeff(t1) x^6 - 0.5 x + 0.5"""
    c9 = 50j * t2 - 50j
    c6 = coeff_t1(t1)
    return x**14 - x**13 + c9 * x**9 + c6 * x**6 - 0.5 * x + 0.5

def height_field_z(u, v, width, height):
    """Height z = Re(p(u + i*v, t1(u), t2(v)))"""
    x = u + 1j * v
    t1 = cmath.exp(1j * 2 * np.pi * u / width)
    t2 = cmath.exp(1j * 2 * np.pi * v / height)
    return polynomial(x, t1, t2).real

# Parameters
width = 200.0
height = 120.0
rows = 100  # Resolution for u
cols = 100  # Resolution for v
num_contours = 12

# Create grid
u = np.linspace(0, width, cols)
v = np.linspace(0, height, rows)
U, V = np.meshgrid(u, v)

# Compute z values
Z = np.zeros_like(U)
for i in range(rows):
    for j in range(cols):
        Z[i, j] = height_field_z(U[i, j], V[i, j], width, height)

# Plot the 3D surface
fig = plt.figure(figsize=(12, 8))
ax = fig.add_subplot(111, projection='3d')
surf = ax.plot_surface(U, V, Z, cmap='viridis', edgecolor='none', alpha=0.8)
ax.set_xlabel('u')
ax.set_ylabel('v')
ax.set_zlabel('z (Real part)')
ax.set_title('Slovenia Surface: 3D Height Field')
fig.colorbar(surf, ax=ax, shrink=0.5, aspect=5)

# Add contour lines on the surface
contours = ax.contour(U, V, Z, levels=num_contours, cmap='coolwarm', linewidths=2)
ax.clabel(contours, inline=True, fontsize=8)

plt.show()