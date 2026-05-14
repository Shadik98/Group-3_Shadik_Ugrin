#A perforated metal screen on a curved surface. Map a sine-wave function to the aperture size. Constraint: Keep the grid UV coordinates 
#locked on the plane and only translate the aperture points along the surface normal.

import math

try:
    import System
    import rhinoscriptsyntax as rs
    import scriptcontext as sc
    import Rhino
except ImportError:
    raise ImportError("This script must be run inside Rhino's Python environment.")


def height_field_z(u, v, width, height, curve_strength, wavelength):
    """Height function for the curved surface."""
    return (
        curve_strength
        * math.sin(math.pi * u / width * wavelength)
        * math.cos(math.pi * v / height * wavelength)
    )


def surface_normal(u, v, width, height, curve_strength, wavelength):
    """Compute the normal for a heightfield surface z = f(u,v)."""
    du = math.pi * wavelength / width
    dv = math.pi * wavelength / height

    dz_du = curve_strength * math.cos(math.pi * u / width * wavelength) * math.cos(math.pi * v / height * wavelength) * du
    dz_dv = -curve_strength * math.sin(math.pi * u / width * wavelength) * math.sin(math.pi * v / height * wavelength) * dv

    normal = Rhino.Geometry.Vector3d(-dz_du, -dz_dv, 1.0)
    normal.Unitize()
    return normal


def aperture_radius(u, v, width, height, base_radius, amplitude, frequency_u, frequency_v, phase_u=0.0, phase_v=0.0):
    """Return a sine-mapped aperture radius using locked planar UV coordinates."""
    value_u = math.sin(2.0 * math.pi * frequency_u * u / width + phase_u)
    value_v = math.sin(2.0 * math.pi * frequency_v * v / height + phase_v)
    radius = base_radius + amplitude * value_u * value_v
    return max(0.5, radius)


def create_heightfield_surface(width, height, rows, cols, curve_strength, wavelength):
    """Create a curved surface from a planar UV grid using a heightfield function."""
    points = []
    for row in range(rows):
        v = height * row / float(rows - 1)
        for col in range(cols):
            u = width * col / float(cols - 1)
            z = height_field_z(u, v, width, height, curve_strength, wavelength)
            points.append(Rhino.Geometry.Point3d(u, v, z))

    surface = Rhino.Geometry.NurbsSurface.CreateThroughPoints(
        points, cols, rows, 3, 3, False, False
    )
    if surface:
        surface.SetDomain(0, Rhino.Geometry.Interval(0.0, width))
        surface.SetDomain(1, Rhino.Geometry.Interval(0.0, height))
    return surface


def create_perforated_screen(
    width=200.0,
    height=120.0,
    rows=12,
    cols=24,
    base_radius=2.5,
    amplitude=1.8,
    frequency_u=3.0,
    frequency_v=2.0,
    normal_offset=1.5,
    curve_strength=12.0,
    wavelength=2.0,
):
    """Generate a perforated curved metal screen with fixed planar UV grid coordinates."""
    sc.doc = Rhino.RhinoDoc.ActiveDoc

    # Create the curved surface.
    surface = create_heightfield_surface(
        width, height, rows, cols, curve_strength, wavelength
    )
    if surface is None:
        raise RuntimeError("Unable to generate the curved surface.")

    surface_id = sc.doc.Objects.AddSurface(surface)
    if surface_id == System.Guid.Empty:
        raise RuntimeError("Unable to add the surface to the Rhino document.")

    hole_curve_ids = []

    # Create each aperture center from the locked planar UV grid,
    # then move it only along the surface normal.
    for row in range(rows):
        v = height * row / float(rows - 1)
        for col in range(cols):
            u = width * col / float(cols - 1)

            radius = aperture_radius(
                u,
                v,
                width,
                height,
                base_radius,
                amplitude,
                frequency_u,
                frequency_v,
            )

            point_on_surface = surface.PointAt(u, v)
            normal = surface_normal(u, v, width, height, curve_strength, wavelength)
            aperture_center = point_on_surface + normal * normal_offset

            plane = Rhino.Geometry.Plane(aperture_center, normal)
            circle = Rhino.Geometry.Circle(plane, radius)
            curve_id = sc.doc.Objects.AddCircle(circle)
            if curve_id != System.Guid.Empty:
                hole_curve_ids.append(curve_id)

    sc.doc.Views.Redraw()
    return surface_id, hole_curve_ids


def main():
    """Entry point for the script."""
    try:
        create_perforated_screen()
        print("Perforated curved screen created successfully.")
    except Exception as exc:
        print("Error creating perforated screen:", exc)


if __name__ == "__main__":
    main()