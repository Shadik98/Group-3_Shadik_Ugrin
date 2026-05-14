#Assignment 03 - Slovenia Surface
#Author : Shadik & Ugrin
#Generate 3D surface with contour lines using the polynomial formula

import math
import cmath

try:
    import System
    import rhinoscriptsyntax as rs
    import scriptcontext as sc
    import Rhino
except ImportError:
    raise ImportError("This script must be run inside Rhino's Python environment.")


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
    t1 = cmath.exp(1j * 2 * math.pi * u / width)
    t2 = cmath.exp(1j * 2 * math.pi * v / height)
    return polynomial(x, t1, t2).real


def create_surface_mesh(width=200.0, height=120.0, rows=100, cols=200):
    """Create a NURBS surface from the heightfield."""
    points = []
    for row in range(rows):
        v = height * row / float(rows - 1) if rows > 1 else 0.0
        for col in range(cols):
            u = width * col / float(cols - 1) if cols > 1 else 0.0
            z = height_field_z(u, v, width, height)
            points.append(Rhino.Geometry.Point3d(u, v, z))

    surface = Rhino.Geometry.NurbsSurface.CreateThroughPoints(
        points, cols, rows, 3, 3, False, False
    )
    if surface:
        surface.SetDomain(0, Rhino.Geometry.Interval(0.0, width))
        surface.SetDomain(1, Rhino.Geometry.Interval(0.0, height))
    return surface


def create_contour_lines(width=200.0, height=120.0, num_contours=12, resolution=150):
    """Create contour lines as points close to level sets for z values."""
    contour_ids = []

    z_values = []
    for i in range(num_contours):
        u_sample = width * i / float(num_contours - 1) if num_contours > 1 else 0.0
        v_sample = height / 2.0
        z_values.append(height_field_z(u_sample, v_sample, width, height))

    if not z_values:
        return contour_ids

    z_min = min(z_values)
    z_max = max(z_values)
    delta = (z_max - z_min) / 50.0 if z_max != z_min else 1.0

    for contour_idx in range(num_contours):
        z_level = z_min + (z_max - z_min) * contour_idx / float(num_contours - 1) if num_contours > 1 else z_min
        contour_points = []

        for u_idx in range(resolution):
            u = width * u_idx / float(resolution - 1) if resolution > 1 else 0.0
            for v_idx in range(resolution):
                v = height * v_idx / float(resolution - 1) if resolution > 1 else 0.0
                z = height_field_z(u, v, width, height)
                if abs(z - z_level) < delta:
                    contour_points.append(Rhino.Geometry.Point3d(u, v, z_level))

        if contour_points:
            polyline = Rhino.Geometry.Polyline(contour_points)
            if polyline.IsValid:
                curve = polyline.ToNurbsCurve()
                curve_id = sc.doc.Objects.AddCurve(curve)
                if curve_id != System.Guid.Empty:
                    contour_ids.append(curve_id)

    return contour_ids


def create_slovenia_surface_3d(width=200.0, height=120.0, rows=100, cols=200, num_contours=12):
    """Create the 3D Slovenia surface and contour lines."""
    sc.doc = Rhino.RhinoDoc.ActiveDoc

    surface = create_surface_mesh(width, height, rows, cols)
    if surface is None:
        raise RuntimeError("Unable to create the Slovenia surface.")

    surface_id = sc.doc.Objects.AddSurface(surface)
    if surface_id == System.Guid.Empty:
        raise RuntimeError("Unable to add surface to Rhino.")

    contour_ids = create_contour_lines(width, height, num_contours)
    sc.doc.Views.Redraw()
    return surface_id, contour_ids


def main():
    try:
        surface_id, contour_ids = create_slovenia_surface_3d(
            width=200.0,
            height=120.0,
            rows=100,
            cols=200,
            num_contours=15,
        )
        print("Slovenia surface created with contour lines.")
        print("Surface ID:", surface_id)
        print("Contour curves created:", len(contour_ids))
    except Exception as exc:
        print("Error creating Slovenia surface:", exc)


if __name__ == "__main__":
    main()