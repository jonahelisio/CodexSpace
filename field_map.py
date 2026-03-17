from __future__ import annotations

import argparse
from pathlib import Path

from exports import (
    write_field_csv,
    write_obj,
    write_ply,
    write_region_color_ply,
    write_slice_csv,
    write_summary_json,
    write_xyz,
)
from field_engine import FORMULA_LIBRARY, GridSpec, FieldSample, collect_samples, summarize_samples


def select_slice(samples: list[FieldSample], axis_name: str, coordinate: float, tolerance: float) -> list[FieldSample]:
    selected: list[FieldSample] = []
    for sample in samples:
        axis_value = getattr(sample, axis_name)
        if abs(axis_value - coordinate) <= tolerance:
            selected.append(sample)
    return selected


def main() -> int:
    parser = argparse.ArgumentParser(description="Sample and classify a scalar field on a regular grid.")
    parser.add_argument("--formula", help="Formula string such as 'x**2 + y**2 + z**2 - 1'")
    parser.add_argument("--preset", choices=sorted(FORMULA_LIBRARY.keys()), help="Use a built-in formula preset")
    parser.add_argument("--bound", type=float, default=2.0, help="Half-width of the sampled cube")
    parser.add_argument("--resolution", type=int, default=30, help="Samples per axis")
    parser.add_argument("--epsilon", type=float, default=0.1, help="Surface band threshold")
    parser.add_argument("--outdir", default="outputs", help="Destination directory")
    parser.add_argument("--slice-axis", choices=["x", "y", "z"], default="z", help="Axis used for slice export")
    parser.add_argument("--slice-coordinate", type=float, default=0.0, help="Slice plane coordinate")
    parser.add_argument("--slice-tolerance", type=float, default=None, help="Slice inclusion tolerance")
    parser.add_argument(
        "--surface-export",
        choices=["none", "xyz", "obj", "ply"],
        default="ply",
        help="Optional surface-band point export",
    )
    parser.add_argument(
        "--region-exports",
        choices=["none", "xyz", "ply"],
        default="ply",
        help="Optional per-region layer exports for negative, surface, and positive samples",
    )
    parser.add_argument(
        "--color-ply",
        action="store_true",
        help="Write a single PLY with all samples color-coded by region",
    )
    args = parser.parse_args()

    formula = args.formula or FORMULA_LIBRARY.get(args.preset or "", "")
    if not formula:
        parser.error("Provide either --formula or --preset")

    grid = GridSpec(bound=args.bound, resolution=args.resolution)
    outdir = Path(args.outdir)
    outdir.mkdir(parents=True, exist_ok=True)

    samples = collect_samples(formula=formula, grid=grid, epsilon=args.epsilon)
    summary = summarize_samples(samples)
    tolerance = args.slice_tolerance if args.slice_tolerance is not None else grid.step / 2.0
    slice_samples = select_slice(samples, args.slice_axis, args.slice_coordinate, tolerance)
    surface_samples = [sample for sample in samples if sample.region == "surface"]
    negative_samples = [sample for sample in samples if sample.region == "negative"]
    positive_samples = [sample for sample in samples if sample.region == "positive"]

    write_field_csv(samples, outdir / "field_samples.csv")
    write_slice_csv(slice_samples, outdir / f"slice_{args.slice_axis}_{args.slice_coordinate:g}.csv", args.slice_axis)
    write_summary_json(
        {
            **summary,
            "formula": formula,
            "bound": args.bound,
            "resolution": args.resolution,
            "epsilon": args.epsilon,
            "slice_axis": args.slice_axis,
            "slice_coordinate": args.slice_coordinate,
            "slice_tolerance": tolerance,
        },
        outdir / "field_summary.json",
    )

    if args.surface_export == "xyz":
        write_xyz(surface_samples, outdir / "surface_points.xyz")
    elif args.surface_export == "obj":
        write_obj(surface_samples, outdir / "surface_points.obj")
    elif args.surface_export == "ply":
        write_ply(surface_samples, outdir / "surface_points.ply")

    if args.region_exports != "none":
        region_sets = {
            "negative": negative_samples,
            "surface": surface_samples,
            "positive": positive_samples,
        }
        for region_name, region_samples in region_sets.items():
            if args.region_exports == "xyz":
                write_xyz(region_samples, outdir / f"{region_name}_points.xyz")
            elif args.region_exports == "ply":
                write_ply(region_samples, outdir / f"{region_name}_points.ply")

    if args.color_ply:
        write_region_color_ply(samples, outdir / "field_regions_color.ply")

    print(f"Formula: {formula}")
    print(f"Samples: {summary['total']}")
    print(
        "Regions: "
        f"negative={summary['negative']} "
        f"surface={summary['surface']} "
        f"positive={summary['positive']}"
    )
    print(f"Value range: {summary['min_value']} to {summary['max_value']}")
    print(f"Outputs written to: {outdir.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
