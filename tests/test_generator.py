from passthrough_fidget_generator import generate
import trimesh


def test_generate():
    mesh = trimesh.creation.box(
        extents=[10, 10, 10]
    )

    inner, outer = generate(
        mesh,
        clearance=0.3,
        radial_samples=32,
        height_samples=16,
    )

    assert len(inner.vertices) > 0
    assert len(outer.vertices) > 0
