#!/usr/bin/env python3
"""Build Phobos-owned fillType HUD DDS icons from source PNG artwork."""

from __future__ import annotations

import argparse
import struct
from pathlib import Path


def write_dds_bgra_mipmaps(image, output_path: Path) -> None:
    from PIL import Image

    width, height = image.size
    if width != height or width <= 0 or width & (width - 1) != 0:
        raise ValueError("DDS icon source must be square and power-of-two sized")

    levels = []
    current = image.convert("RGBA")
    while True:
        levels.append(current)
        if current.size == (1, 1):
            break
        next_size = (max(1, current.width // 2), max(1, current.height // 2))
        current = current.resize(next_size, resample=Image.Resampling.LANCZOS)

    pitch = width * 4
    flags = 0x1 | 0x2 | 0x4 | 0x1000 | 0x20000 | 0x80000
    caps = 0x1000 | 0x8 | 0x400000
    pixel_format = struct.pack(
        "<8I",
        32,
        0x1 | 0x40,
        0,
        32,
        0x00FF0000,
        0x0000FF00,
        0x000000FF,
        0xFF000000,
    )
    header = struct.pack(
        "<7I44s",
        124,
        flags,
        height,
        width,
        pitch,
        0,
        len(levels),
        b"\0" * 44,
    )
    caps_data = struct.pack("<5I", caps, 0, 0, 0, 0)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as handle:
        handle.write(b"DDS ")
        handle.write(header)
        handle.write(pixel_format)
        handle.write(caps_data)
        for level in levels:
            rgba = level.tobytes()
            bgra = bytearray(len(rgba))
            bgra[0::4] = rgba[2::4]
            bgra[1::4] = rgba[1::4]
            bgra[2::4] = rgba[0::4]
            bgra[3::4] = rgba[3::4]
            handle.write(bgra)


def build_icon(source_path: Path, output_path: Path, size: int) -> None:
    from PIL import Image

    source = Image.open(source_path).convert("RGBA")
    icon = source.resize((size, size), resample=Image.Resampling.LANCZOS)
    write_dds_bgra_mipmaps(icon, output_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Phobos fillType HUD DDS icons")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--size", type=int, default=256, help="Output icon size in pixels")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    icons = [
        (
            repo_root / "assets/source/fillTypes/hud_fill_phbWetBiomassMash.png",
            repo_root / "mod/hud/fillTypes/hud_fill_phbWetBiomassMash.dds",
        )
    ]

    for source_path, output_path in icons:
        if not source_path.is_file():
            raise FileNotFoundError(f"Missing source icon: {source_path}")
        build_icon(source_path, output_path, args.size)
        print(f"Wrote {output_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
