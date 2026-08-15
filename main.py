import argparse
import os

import numpy as np
import trimesh


def load_mesh(path):
    mesh = trimesh.load_mesh(path)

    if isinstance(mesh, trimesh.Scene):
        if not mesh.geometry:
            raise RuntimeError("No geometry found")

        mesh = trimesh.util.concatenate(
            tuple(mesh.geometry.values())
        )

    if not isinstance(mesh, trimesh.Trimesh):
        raise RuntimeError("Input is not a triangle mesh")

    mesh.remove_unreferenced_vertices()
    mesh.merge_vertices()

    if not mesh.is_watertight:
        print("WARNING: input mesh is not watertight")

    return mesh


def make_curved_solid(
    center,
    radius,
    amplitude,
    height,
    waves,
    twists,
    clearance,
    radial_samples,
    height_samples
):
    zmin = center[2] - height / 2
    zmax = center[2] + height / 2

    theta = np.linspace(
        0,
        2 * np.pi,
        radial_samples,
        endpoint=False
    )

    z = np.linspace(
        zmin,
        zmax,
        height_samples
    )

    theta_grid, z_grid = np.meshgrid(
        theta,
        z
    )

    phase = (
        waves * np.pi *
        ((z_grid - center[2]) / (height / 2))
        +
        twists * theta_grid
    )

    r = (
        radius
        + amplitude * np.sin(phase)
        + clearance
    )

    x = center[0] + r * np.cos(theta_grid)
    y = center[1] + r * np.sin(theta_grid)

    vertices = np.column_stack((
        x.ravel(),
        y.ravel(),
        z_grid.ravel()
    ))

    faces = []

    # Main curved surface.
    for z_index in range(height_samples - 1):
        for t_index in range(radial_samples):
            a = (
                z_index * radial_samples
                + t_index
            )

            b = (
                z_index * radial_samples
                + (t_index + 1) % radial_samples
            )

            c = (
                (z_index + 1) * radial_samples
                + (t_index + 1) % radial_samples
            )

            d = (
                (z_index + 1) * radial_samples
                + t_index
            )

            faces.append([a, b, c])
            faces.append([a, c, d])

    # Bottom cap.
    bottom_center = len(vertices)
    vertices = np.vstack((
        vertices,
        [[center[0], center[1], zmin]]
    ))

    for t_index in range(radial_samples):
        a = t_index
        b = (t_index + 1) % radial_samples

        faces.append([
            bottom_center,
            b,
            a
        ])

    # Top cap.
    top_center = len(vertices)
    vertices = np.vstack((
        vertices,
        [[center[0], center[1], zmax]]
    ))

    top_start = (
        (height_samples - 1)
        * radial_samples
    )

    for t_index in range(radial_samples):
        a = top_start + t_index
        b = (
            top_start
            + (t_index + 1) % radial_samples
        )

        faces.append([
            top_center,
            a,
            b
        ])

    mesh = trimesh.Trimesh(
        vertices=vertices,
        faces=np.asarray(faces),
        process=True
    )

    mesh.remove_unreferenced_vertices()

    if not mesh.is_watertight:
        raise RuntimeError(
            "Generated curved cutter is not watertight"
        )

    return mesh


def boolean_intersection(a, b):
    result = trimesh.boolean.intersection(
        [a, b],
        engine="manifold"
    )

    if result is None:
        raise RuntimeError(
            "Boolean intersection failed"
        )

    return result


def boolean_difference(a, b):
    result = trimesh.boolean.difference(
        [a, b],
        engine="manifold"
    )

    if result is None:
        raise RuntimeError(
            "Boolean difference failed"
        )

    return result


def largest_component(mesh):
    parts = mesh.split(
        only_watertight=True
    )

    if not parts:
        return mesh

    return max(
        parts,
        key=lambda x: x.volume
    )


def generate(
    mesh,
    clearance,
    waves,
    twists,
    amplitude,
    radial_samples,
    height_samples,
    radius
):
    center = mesh.bounding_box.centroid
    extents = mesh.bounding_box.extents

    height = extents[2] + clearance * 4

    if radius <= 0:
        radius = min(
            extents[0],
            extents[1]
        ) * 0.25

    if amplitude <= 0:
        amplitude = min(
            extents[0],
            extents[1]
        ) * 0.12

    print("Creating smooth curved surface...")

    cutter = make_curved_solid(
        center=center,
        radius=radius,
        amplitude=amplitude,
        height=height,
        waves=waves,
        twists=twists,
        clearance=0,
        radial_samples=radial_samples,
        height_samples=height_samples
    )

    print(
        f"Cutter: "
        f"{len(cutter.vertices):,} vertices, "
        f"{len(cutter.faces):,} triangles"
    )

    # This is the inner piece.
    print("Creating inner piece...")

    inner = boolean_intersection(
        mesh,
        cutter
    )

    # Create a slightly larger version of the curved surface.
    # This gives the outer piece its clearance from the inner piece.
    print("Creating clearance cutter...")

    clearance_cutter = make_curved_solid(
        center=center,
        radius=radius,
        amplitude=amplitude,
        height=height,
        waves=waves,
        twists=twists,
        clearance=clearance,
        radial_samples=radial_samples,
        height_samples=height_samples
    )

    print("Creating outer piece...")

    outer = boolean_difference(
        mesh,
        clearance_cutter
    )

    inner = largest_component(inner)
    outer = largest_component(outer)

    return inner, outer


def main():
    parser = argparse.ArgumentParser(
        description="Generate a smooth curved passthrough fidget."
    )

    parser.add_argument(
        "input",
        help="Input STL/OBJ/PLY"
    )

    parser.add_argument(
        "-o",
        "--output",
        default="output"
    )

    parser.add_argument(
        "--clearance",
        type=float,
        default=0.3,
        help="Gap between inner and outer pieces"
    )

    parser.add_argument(
        "--waves",
        type=float,
        default=2.0,
        help="Number of vertical waves"
    )

    parser.add_argument(
        "--twists",
        type=float,
        default=2.0,
        help="Angular twist"
    )

    parser.add_argument(
        "--amplitude",
        type=float,
        default=0.0,
        help="Wave amplitude; 0 = automatic"
    )

    parser.add_argument(
        "--radius",
        type=float,
        default=0.0,
        help="Base radius; 0 = automatic"
    )

    parser.add_argument(
        "--radial-samples",
        type=int,
        default=256,
        help="Samples around curved surface"
    )

    parser.add_argument(
        "--height-samples",
        type=int,
        default=128,
        help="Samples along curved surface"
    )

    args = parser.parse_args()

    if args.clearance <= 0:
        raise ValueError(
            "--clearance must be positive"
        )

    if args.radial_samples < 16:
        raise ValueError(
            "--radial-samples is too low"
        )

    if args.height_samples < 4:
        raise ValueError(
            "--height-samples is too low"
        )

    os.makedirs(
        args.output,
        exist_ok=True
    )

    print("Loading model...")

    mesh = load_mesh(
        args.input
    )

    print(
        "Model size:",
        mesh.bounding_box.extents
    )

    inner, outer = generate(
        mesh,
        args.clearance,
        args.waves,
        args.twists,
        args.amplitude,
        args.radial_samples,
        args.height_samples,
        args.radius
    )

    inner_path = os.path.join(
        args.output,
        "inner.stl"
    )

    outer_path = os.path.join(
        args.output,
        "outer.stl"
    )

    combined_path = os.path.join(
        args.output,
        "combined.stl"
    )

    print("Writing inner.stl...")
    inner.export(inner_path)

    print("Writing outer.stl...")
    outer.export(outer_path)

    print("Writing combined.stl...")

    combined = trimesh.util.concatenate([
        inner,
        outer
    ])

    combined.export(combined_path)

    print()
    print("Finished.")
    print(f"Inner:    {inner_path}")
    print(f"Outer:    {outer_path}")
    print(f"Combined: {combined_path}")


if __name__ == "__main__":
    main()
