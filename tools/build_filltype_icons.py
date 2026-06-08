#!/usr/bin/env python3
"""Build GBW-owned fillType HUD DDS icons from source PNG artwork."""

from __future__ import annotations

import argparse
import struct
from pathlib import Path


def rgb_to_565(red: int, green: int, blue: int) -> int:
    return ((red & 0xF8) << 8) | ((green & 0xFC) << 3) | (blue >> 3)


def rgb_from_565(value: int) -> tuple[int, int, int]:
    red = ((value >> 11) & 0x1F) * 255 // 31
    green = ((value >> 5) & 0x3F) * 255 // 63
    blue = (value & 0x1F) * 255 // 31
    return red, green, blue


def alpha_palette(alpha0: int, alpha1: int) -> list[int]:
    if alpha0 > alpha1:
        return [
            alpha0,
            alpha1,
            (6 * alpha0 + alpha1) // 7,
            (5 * alpha0 + 2 * alpha1) // 7,
            (4 * alpha0 + 3 * alpha1) // 7,
            (3 * alpha0 + 4 * alpha1) // 7,
            (2 * alpha0 + 5 * alpha1) // 7,
            (alpha0 + 6 * alpha1) // 7,
        ]
    return [
        alpha0,
        alpha1,
        (4 * alpha0 + alpha1) // 5,
        (3 * alpha0 + 2 * alpha1) // 5,
        (2 * alpha0 + 3 * alpha1) // 5,
        (alpha0 + 4 * alpha1) // 5,
        0,
        255,
    ]


def encode_alpha_block(pixels: list[tuple[int, int, int, int]]) -> bytes:
    alphas = [pixel[3] for pixel in pixels]
    low, high = min(alphas), max(alphas)
    candidates = [(high, low), (low, high)]
    best_error: int | None = None
    best_block = b""

    for alpha0, alpha1 in candidates:
        palette = alpha_palette(alpha0, alpha1)
        bits = 0
        error = 0
        for index, alpha in enumerate(alphas):
            best_index = min(range(8), key=lambda item: (palette[item] - alpha) ** 2)
            error += (palette[best_index] - alpha) ** 2
            bits |= best_index << (index * 3)
        block = bytes([alpha0, alpha1]) + bits.to_bytes(6, "little")
        if best_error is None or error < best_error:
            best_error = error
            best_block = block

    return best_block


def choose_color_endpoints(pixels: list[tuple[int, int, int, int]]) -> tuple[int, int]:
    color_pixels = [pixel[:3] for pixel in pixels if pixel[3] > 8] or [pixel[:3] for pixel in pixels]
    if len(set(color_pixels)) <= 1:
        red, green, blue = color_pixels[0]
        color = rgb_to_565(red, green, blue)
        return color, color

    best_pair = (color_pixels[0], color_pixels[1])
    best_distance = -1
    for left in color_pixels:
        for right in color_pixels:
            distance = sum((left[channel] - right[channel]) ** 2 for channel in range(3))
            if distance > best_distance:
                best_distance = distance
                best_pair = (left, right)

    color0 = rgb_to_565(*best_pair[0])
    color1 = rgb_to_565(*best_pair[1])
    if color0 < color1:
        color0, color1 = color1, color0
    return color0, color1


def encode_color_block(pixels: list[tuple[int, int, int, int]]) -> bytes:
    color0, color1 = choose_color_endpoints(pixels)
    rgb0 = rgb_from_565(color0)
    rgb1 = rgb_from_565(color1)

    if color0 == color1:
        palette = [rgb0, rgb1, rgb0, rgb1]
    else:
        palette = [
            rgb0,
            rgb1,
            tuple((2 * rgb0[channel] + rgb1[channel]) // 3 for channel in range(3)),
            tuple((rgb0[channel] + 2 * rgb1[channel]) // 3 for channel in range(3)),
        ]

    bits = 0
    for index, pixel in enumerate(pixels):
        rgb = pixel[:3]
        best_index = min(
            range(4),
            key=lambda item: sum((palette[item][channel] - rgb[channel]) ** 2 for channel in range(3)),
        )
        bits |= best_index << (index * 2)

    return struct.pack("<HHI", color0, color1, bits)


def encode_dxt5_level(image) -> bytes:
    width, height = image.size
    if hasattr(image, "get_flattened_data"):
        source = list(image.get_flattened_data())
    else:
        source = list(image.getdata())
    output = bytearray()

    for block_y in range(0, height, 4):
        for block_x in range(0, width, 4):
            pixels: list[tuple[int, int, int, int]] = []
            for offset_y in range(4):
                for offset_x in range(4):
                    x = min(block_x + offset_x, width - 1)
                    y = min(block_y + offset_y, height - 1)
                    pixels.append(source[y * width + x])
            output.extend(encode_alpha_block(pixels))
            output.extend(encode_color_block(pixels))

    return bytes(output)


def write_dds_dxt5(image, output_path: Path) -> None:
    width, height = image.size
    if width != height or width <= 0 or width & (width - 1) != 0:
        raise ValueError("DDS icon source must be square and power-of-two sized")
    if width % 4 != 0 or height % 4 != 0:
        raise ValueError("DXT5 DDS icon dimensions must be divisible by 4")

    compressed = encode_dxt5_level(image.convert("RGBA"))
    flags = 0x1 | 0x2 | 0x4 | 0x1000 | 0x20000 | 0x80000
    linear_size = len(compressed)
    pixel_format = struct.pack(
        "<8I",
        32,
        0x4,
        int.from_bytes(b"DXT5", "little"),
        0,
        0,
        0,
        0,
        0,
    )
    header = struct.pack(
        "<7I44s",
        124,
        flags,
        height,
        width,
        linear_size,
        0,
        1,
        b"\0" * 44,
    )
    caps_data = struct.pack("<5I", 0x1000, 0, 0, 0, 0)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("wb") as handle:
        handle.write(b"DDS ")
        handle.write(header)
        handle.write(pixel_format)
        handle.write(caps_data)
        handle.write(compressed)


def build_icon(source_path: Path, output_path: Path, size: int) -> None:
    from PIL import Image

    source = Image.open(source_path).convert("RGBA")
    icon = source.resize((size, size), resample=Image.Resampling.LANCZOS)
    write_dds_dxt5(icon, output_path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build GBW fillType HUD DDS icons")
    parser.add_argument("--repo-root", default=".", help="Repository root")
    parser.add_argument("--size", type=int, default=256, help="Output icon size in pixels")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    icons = [
        (
            repo_root / "assets/source/fillTypes/hud_fill_gbwSweetMash.png",
            repo_root / "mod/hud/fillTypes/hud_fill_gbwSweetMash.dds",
        ),
        (
            repo_root / "assets/source/fillTypes/hud_fill_gbwRootMash.png",
            repo_root / "mod/hud/fillTypes/hud_fill_gbwRootMash.dds",
        ),
        (
            repo_root / "assets/source/fillTypes/hud_fill_gbwGreenMash.png",
            repo_root / "mod/hud/fillTypes/hud_fill_gbwGreenMash.dds",
        ),
        (
            repo_root / "assets/source/fillTypes/hud_fill_gbwResidueMash.png",
            repo_root / "mod/hud/fillTypes/hud_fill_gbwResidueMash.dds",
        ),
    ]

    for source_path, output_path in icons:
        if not source_path.is_file():
            raise FileNotFoundError(f"Missing source icon: {source_path}")
        build_icon(source_path, output_path, args.size)
        print(f"Wrote {output_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
