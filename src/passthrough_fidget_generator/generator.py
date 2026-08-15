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
        print("Warning: input mesh is not watertight")

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
    height_samples,
):
    zmin = center[2] - height / 2
    zmax = center[2] + height / 2

    theta = np.linspace(
        0,
        2 * np.pi,
        radial_samples,
        endpoint=False,
    )

    z = np.linspace(
        zmin,
        zmax,
        height_samples,
    )

    theta_grid, z_grid = np.meshgrid(
        theta,
        z,
    )

    phase = (
        waves
        * np.pi
        * ((z_grid - center[2]) / (height / 2))
        + twists * theta_grid
    )

    r = (
        radius
        + amplitude * np.sin(phase)
        + clearance
    )

    x = center[0] + r * np.cos(theta_grid)
    y = center[1] + r * np.sin(theta_grid)

    vertices = np.column_stack(
        (
            x.ravel(),
            y.ravel(),
            z_grid.ravel(),
        )
    )

    faces = []

    for z_index in range(height_samples - 1):
        for theta_index in range(radial_samples):
            a = (
                z_index * radial_samples
                + theta_index
            )

            b = (
                z_index * radial_samples
                + (theta_index + 1) % radial_samples
            )

            c = (
                (z_index + 1) * radial_samples
                + (theta_index + 1) % radial_samples
            )

            d = (
                (z_index + 1) * radial_samples
                + theta_index
            )

            faces.append([a, b, c])
            faces.append([a, c, d])

    bottom_center = len(vertices)

    vertices = np.vstack(
        (
            vertices,
            [[center[0], center[1], zmin]],
        )
    )

    for theta_index in range(radial_samples):
        a = theta_index
        b = (theta_index + 1) % radial_samples

        faces.append(
            [
                bottom_center,
                b,
                a,
            ]
        )

    top_center = len(vertices)

    vertices = np.vstack(
        (
            vertices,
            [[center[0], center[1], zmax]],
        )
    )

    top_start = (
        (height_samples - 1)
        * radial_samples
    )

    for theta_index in range(radial_samples):
        a = top_start + theta_index

        b = (
            top_start
            + (theta_index + 1) % radial_samples
        )

        faces.append(
            [
                top_center,
                a,
                b,
            ]
        )

    mesh = trimesh.Trimesh(
        vertices=vertices,
        faces=np.asarray(faces),
        process=True,
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
        engine="manifold",
    )

    if result is None:
        raise RuntimeError(
            "Boolean intersection failed"
        )

    return result


def boolean_difference(a, b):
    result = trimesh.boolean.difference(
        [a, b],
        engine="manifold",
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
        key=lambda part: part.volume,
    )


def generate(
    mesh,
    clearance=0.3,
    waves=2.0,
    twists=2.0,
    amplitude=0.0,
    radial_samples=256,
    height_samples=128,
    radius=0.0,
):
    center = mesh.bounding_box.centroid
    extents = mesh.bounding_box.extents

    height = extents[2] + clearance * 4

    if radius <= 0:
        radius = (
            min(extents[0], extents[1])
            * 0.25
        )

    if amplitude <= 0:
        amplitude = (
            min(extents[0], extents[1])
            * 0.12
        )

    cutter = make_curved_solid(
        center=center,
        radius=radius,
        amplitude=amplitude,
        height=height,
        waves=waves,
        twists=twists,
        clearance=0,
        radial_samples=radial_samples,
        height_samples=height_samples,
    )

    print("Generating inner piece...")

    inner = boolean_intersection(
        mesh,
        cutter,
    )

    clearance_cutter = make_curved_solid(
        center=center,
        radius=radius,
        amplitude=amplitude,
        height=height,
        waves=waves,
        twists=twists,
        clearance=clearance,
        radial_samples=radial_samples,
        height_samples=height_samples,
    )

    print("Generating outer piece...")

    outer = boolean_difference(
        mesh,
        clearance_cutter,
    )

    inner = largest_component(inner)
    outer = largest_component(outer)

    return inner, outer


def generate_from_file(
    input_path,
    output_dir="output",
    **kwargs,
):
    mesh = load_mesh(input_path)

    print(
        "Model size:",
        mesh.bounding_box.extents,
    )

    inner, outer = generate(
        mesh,
        **kwargs,
    )

    os.makedirs(
        output_dir,
        exist_ok=True,
    )

    inner_path = os.path.join(
        output_dir,
        "inner.stl",
    )

    outer_path = os.path.join(
        output_dir,
        "outer.stl",
    )

    combined_path = os.path.join(
        output_dir,
        "combined.stl",
    )

    print("Writing inner.stl...")
    inner.export(inner_path)

    print("Writing outer.stl...")
    outer.export(outer_path)

    print("Writing combined.stl...")

    combined = trimesh.util.concatenate(
        [
            inner,
            outer,
        ]
    )

    combined.export(combined_path)

    return (
        inner_path,
        outer_path,
        combined_path,
    )
