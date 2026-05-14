# Slovenia Surface Grasshopper Component
# Inputs: num_contours (int)
# Outputs: surface (NURBS surface), contours (list)
# Plan

import math
import cmath
import Rhino.Geometry as rg

# Fixed domain and mesh settings in mm
width = 10000.0  # 10m in mm
height = 10000.0  # 10m in mm
rows = 80
cols = 80
z_scale = 0.01

# Default input for Grasshopper
if 'num_contours' not in globals():
    num_contours = 12
num_contours = int(num_contours)


def coeff_t1(t1):
    """Compute the x^6 coefficient from t1."""
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
    """Evaluate the complex polynomial for the height field."""
    c9 = 50j * t2 - 50j
    c6 = coeff_t1(t1)
    return x**14 - x**13 + c9 * x**9 + c6 * x**6 - 0.5 * x + 0.5


def height_field_z(u, v):
    """Return the surface height for the point (u, v)."""
    u_norm = (u / width) * 2.0
    v_norm = (v / height) * 2.0
    x = u_norm + 1j * v_norm
    t1 = cmath.exp(1j * 2.0 * math.pi * u / width)
    t2 = cmath.exp(1j * 2.0 * math.pi * v / height)
    return polynomial(x, t1, t2).real * z_scale


# Build point grid
points = []
for row in range(rows):
    v = height * row / float(rows - 1)
    for col in range(cols):
        u = width * col / float(cols - 1)
        z = height_field_z(u, v)
        points.append(rg.Point3d(u, v, z))

surface = rg.NurbsSurface.CreateThroughPoints(points, cols, rows, 3, 3, False, False)
if surface:
    surface.SetDomain(0, rg.Interval(0.0, width))
    surface.SetDomain(1, rg.Interval(0.0, height))

# Simple contour output placeholder
contours = []

# Output variables
# surface = surface
# contours = contours
## we make flate area 10m by 10m
## bulit grid of points and for each point calculate height using the polynomial function
## it turnes grid of points into a NURBS surface
