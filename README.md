# Passthrough Toy Generator

A Python generator for creating interlocking passthrough toys from existing 3D models.

The generator takes a watertight STL/OBJ/PLY model and creates two separate meshes:

* `inner.stl` — the inner/interlocking piece
* `outer.stl` — the surrounding piece
* `combined.stl` — both pieces together for inspection

The interlocking boundary is generated from a mathematical curved surface rather than voxelizing the model.

## Requirements

* Python 3.10+
* NumPy
* Trimesh
* Manifold3D

Install the dependencies with:

```bash
pip install numpy trimesh manifold3d
```

## Usage

Basic example:

```bash
python main.py model.stl
```

This creates:

```text
output/
├── inner.stl
├── outer.stl
└── combined.stl
```

### Example

```bash
python main.py "xyz-10mm-calibration-cube (1).stl" \
    --clearance 0.3 \
    --waves 1.5 \
    --twists 2 \
    --radial-samples 128 \
    --height-samples 64 \
    -o output
```

## Options

### `--clearance`

Controls the gap between the two pieces.

```bash
--clearance 0.3
```

The value uses the same units as the input model. For an STL in millimetres, this is 0.3 mm.

Typical starting values:

```text
0.2 mm  Tight
0.3 mm  Normal
0.4 mm  Loose
0.5 mm  Very loose
```

The correct value depends on the printer and material.

### `--waves`

Controls the number of waves along the height of the model.

```bash
--waves 1.5
```

Higher values produce more interlocking sections.

### `--twists`

Controls how much the wave rotates around the object.

```bash
--twists 2
```

Higher values create more twisting between the inner and outer pieces.

### `--amplitude`

Controls how far the curved interface moves from its base radius.

```bash
--amplitude 1.0
```

If omitted or set to `0`, the generator chooses an amplitude automatically.

### `--radius`

Controls the base radius of the curved interface.

```bash
--radius 2.5
```

If set to `0`, the radius is calculated automatically from the input model.

### `--radial-samples`

Controls the number of points around the curved surface.

```bash
--radial-samples 256
```

Higher values produce a smoother circular direction but increase processing time and STL size.

### `--height-samples`

Controls the number of points along the height of the curved surface.

```bash
--height-samples 128
```

Higher values produce a smoother vertical curve.

## Recommended Resolution

For testing:

```bash
--radial-samples 128 --height-samples 64
```

For a smoother final model:

```bash
--radial-samples 256 --height-samples 128
```

For very smooth surfaces:

```bash
--radial-samples 512 --height-samples 256
```

Higher resolutions create significantly more triangles.

## How It Works

The interlocking surface is based on a mathematical function:

```text
r(θ,z) = R + A sin(kz + nθ)
```

where:

* `R` is the base radius
* `A` is the wave amplitude
* `k` controls the vertical waves
* `n` controls the angular twisting

The surface is sampled directly and converted into a triangle mesh.

This is different from voxel-based generation.

### Voxel approach

```text
Model
  ↓
Voxel grid
  ↓
Marching cubes
  ↓
STL
```

This can produce stepped or blocky surfaces depending on voxel resolution.

### This approach

```text
Mathematical surface
  ↓
Direct surface sampling
  ↓
Triangle mesh
  ↓
STL
```

The underlying interface is therefore a continuous mathematical curve, with the STL triangles only approximating that curve.

## Input Models

The input should preferably be:

* Watertight
* A single solid
* A reasonably clean mesh
* Suitable for boolean operations

For example:

```text
model.stl
```

or:

```text
model.obj
```

A model containing holes, self-intersections, or disconnected geometry may produce incorrect results.

## Output

`inner.stl` contains the inner piece.

`outer.stl` contains the outer piece.

`combined.stl` contains both meshes in their generated positions and is useful for checking the result in a slicer or mesh viewer.

The two individual STLs should normally be exported separately for printing.

## Printing

The generated parts are intended to be printed as separate pieces.

The most important setting is clearance. A printer with poorer dimensional accuracy may require a larger clearance.

A reasonable first test is:

```text
Clearance: 0.3 mm
```

If the pieces are too tight:

```text
0.4–0.5 mm
```

If they are excessively loose:

```text
0.2–0.25 mm
```

## Current Limitations

The current generator uses a cylindrical/radial mathematical interface. It therefore works best with models that have a reasonably continuous body around their central axis.

It does not yet automatically adapt the curved interface to every arbitrary model shape.

Future improvements could include:

* Automatically fitting the curved surface to the input model
* Supporting different axes
* Better handling of irregular models
* Automatic wall-thickness checks
* Collision/intersection validation
* Automatic printer-clearance compensation
* Preview rendering
* GUI
* Direct slicer integration
