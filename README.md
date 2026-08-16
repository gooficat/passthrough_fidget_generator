# Passthrough Fidget Generator

Generate interlocking passthrough fidgets from existing 3D models.

The generator takes an existing STL, OBJ, or PLY model and splits it into two interlocking pieces using a smooth curved interface. The resulting pieces can be printed separately and assembled into a passthrough fidget.

## Features

- Generate passthrough fidgets from existing 3D models
- Smooth mathematical curved interfaces
- Configurable clearance
- Configurable waves
- Configurable twists
- Configurable radial resolution
- Configurable height resolution
- STL output
- Command-line interface
- Python API

## Installation

Install from PyPI:

```bash
pip install passthrough-fidget-generator
```

## Command Line

Basic usage:

```bash
passthrough-fidget-generator model.stl
```

Specify an output directory:

```bash
passthrough-fidget-generator model.stl -o output
```

### Parameters

#### `--clearance`

Sets the gap between the two pieces.

```bash
--clearance 0.3
```

The value uses the same units as the input model.

#### `--waves`

Controls the number of waves along the height of the model.

```bash
--waves 1.5
```

#### `--twists`

Controls how many rotations the interface makes around the model.

```bash
--twists 2
```

#### `--radial-samples`

Controls the resolution around the curved interface.

```bash
--radial-samples 128
```

Higher values produce smoother surfaces but require more processing.

#### `--height-samples`

Controls the resolution along the height of the interface.

```bash
--height-samples 64
```

Higher values produce smoother surfaces but require more processing.

### Example

```bash
passthrough-fidget-generator model.stl \
    --clearance 0.3 \
    --waves 1.5 \
    --twists 2 \
    --radial-samples 128 \
    --height-samples 64 \
    -o output
```

## Python API

The generator can be used directly from Python:

```python
from passthrough_fidget_generator import generate_from_file

paths = generate_from_file(
    "model.stl",
    output="output",
    clearance=0.3,
    waves=1.5,
    twists=2,
    radial_samples=128,
    height_samples=64,
)
```

You can also work directly with a `trimesh.Trimesh` object:

```python
from passthrough_fidget_generator import generate

inner, outer = generate(
    mesh,
    clearance=0.3,
    waves=1.5,
    twists=2,
    radial_samples=128,
    height_samples=64,
)
```

## Input Models

The input should be a closed, watertight solid.

Supported formats depend on the underlying `trimesh` installation, including:

- STL
- OBJ
- PLY

Non-watertight or invalid meshes may fail during the boolean operations used to create the pieces.

## How It Works

The generator:

1. Loads the input mesh.
2. Creates a smooth mathematical interface through the model.
3. Uses boolean operations to divide the original model along that interface.
4. Applies the requested clearance.
5. Extracts the resulting inner and outer pieces.
6. Writes the generated meshes as STL files.

The interface is generated mathematically rather than using voxelization, allowing the resulting pieces to have smooth curved surfaces.

## Dependencies

The project uses:

- NumPy
- SciPy
- Trimesh
- Manifold3D
- scikit-image
- NetworkX

These dependencies are installed automatically when installing from PyPI.

## Development

Clone the repository:

```bash
git clone https://github.com/gooficat/passthrough_fidget_generator.git
cd passthrough_fidget_generator
```

Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the package in editable mode:

```bash
pip install -e .
```

Run the tests:

```bash
pytest
```

## Building

Build the package with:

```bash
python -m build
```

The distribution files will be created in:

```text
dist/
```
