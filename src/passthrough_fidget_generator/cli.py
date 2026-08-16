import argparse

from .generator import generate_from_file


def main():
    parser = argparse.ArgumentParser(
        description="Generate a passthrough fidget from a 3D model."
    )

    parser.add_argument(
        "input",
        help="Input STL, OBJ, or PLY file"
    )

    parser.add_argument(
        "-o",
        "--output",
        default="output",
        help="Output directory (default: output)"
    )

    parser.add_argument(
        "--clearance",
        type=float,
        default=0.3,
        help="Clearance between the pieces (default: 0.3)"
    )

    parser.add_argument(
        "--waves",
        type=float,
        default=2.0,
        help="Number of vertical waves (default: 2)"
    )

    parser.add_argument(
        "--twists",
        type=float,
        default=2.0,
        help="Amount of angular twisting (default: 2)"
    )

    parser.add_argument(
        "--amplitude",
        type=float,
        default=0.0,
        help="Wave amplitude; 0 uses automatic sizing"
    )

    parser.add_argument(
        "--radius",
        type=float,
        default=0.0,
        help="Base radius; 0 uses automatic sizing"
    )

    parser.add_argument(
        "--radius-scale",
        type=float,
        default=0.35,
        help="Fraction of the model's smaller XY extent used for the spiral cutout radius (default: 0.35)"
    )

    parser.add_argument(
        "--radial-samples",
        type=int,
        default=256,
        help="Surface resolution around the object (default: 256)"
    )

    parser.add_argument(
        "--height-samples",
        type=int,
        default=128,
        help="Surface resolution along the height (default: 128)"
    )

    args = parser.parse_args()

    if args.clearance <= 0:
        parser.error("--clearance must be positive")

    if args.radial_samples < 16:
        parser.error("--radial-samples must be at least 16")

    if args.height_samples < 4:
        parser.error("--height-samples must be at least 4")

    print(f"Loading: {args.input}")

    paths = generate_from_file(
        args.input,
        output_dir=args.output,
        clearance=args.clearance,
        waves=args.waves,
        twists=args.twists,
        amplitude=args.amplitude,
        radius=args.radius,
        radial_samples=args.radial_samples,
        height_samples=args.height_samples,
        radius_scale=args.radius_scale,
    )

    print()
    print("Generated:")
    print(f"  Inner:    {paths[0]}")
    print(f"  Outer:    {paths[1]}")
    print(f"  Combined: {paths[2]}")


if __name__ == "__main__":
    main()
