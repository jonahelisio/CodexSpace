from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Iterable

from field_engine import FieldSample


def write_field_csv(samples: Iterable[FieldSample], path: str | Path) -> None:
    destination = Path(path)
    with destination.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["x", "y", "z", "value", "region"])
        for sample in samples:
            writer.writerow([sample.x, sample.y, sample.z, sample.value, sample.region])


def write_slice_csv(samples: Iterable[FieldSample], path: str | Path, axis_name: str) -> None:
    destination = Path(path)
    with destination.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["x", "y", "z", "value", "region", "slice_axis"])
        for sample in samples:
            writer.writerow([sample.x, sample.y, sample.z, sample.value, sample.region, axis_name])


def write_summary_json(summary: dict[str, float], path: str | Path) -> None:
    destination = Path(path)
    with destination.open("w") as handle:
        json.dump(summary, handle, indent=2)
        handle.write("\n")


def write_xyz(samples: Iterable[FieldSample], path: str | Path) -> None:
    destination = Path(path)
    with destination.open("w") as handle:
        for sample in samples:
            handle.write(f"{sample.x} {sample.y} {sample.z}\n")


def write_obj(samples: Iterable[FieldSample], path: str | Path) -> None:
    destination = Path(path)
    with destination.open("w") as handle:
        for sample in samples:
            handle.write(f"v {sample.x} {sample.y} {sample.z}\n")


def write_ply(samples: list[FieldSample], path: str | Path) -> None:
    destination = Path(path)
    with destination.open("w") as handle:
        handle.write("ply\n")
        handle.write("format ascii 1.0\n")
        handle.write(f"element vertex {len(samples)}\n")
        handle.write("property float x\n")
        handle.write("property float y\n")
        handle.write("property float z\n")
        handle.write("property float value\n")
        handle.write("end_header\n")
        for sample in samples:
            handle.write(f"{sample.x} {sample.y} {sample.z} {sample.value}\n")


REGION_COLORS: dict[str, tuple[int, int, int]] = {
    "negative": (40, 120, 220),
    "surface": (240, 90, 40),
    "positive": (240, 210, 70),
}


def write_region_color_ply(samples: list[FieldSample], path: str | Path) -> None:
    destination = Path(path)
    with destination.open("w") as handle:
        handle.write("ply\n")
        handle.write("format ascii 1.0\n")
        handle.write(f"element vertex {len(samples)}\n")
        handle.write("property float x\n")
        handle.write("property float y\n")
        handle.write("property float z\n")
        handle.write("property float value\n")
        handle.write("property uchar red\n")
        handle.write("property uchar green\n")
        handle.write("property uchar blue\n")
        handle.write("end_header\n")
        for sample in samples:
            red, green, blue = REGION_COLORS.get(sample.region, (180, 180, 180))
            handle.write(
                f"{sample.x} {sample.y} {sample.z} {sample.value} "
                f"{red} {green} {blue}\n"
            )
