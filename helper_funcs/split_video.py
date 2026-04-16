#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import asyncio
import logging
import math
import os

from hachoir.metadata import extractMetadata
from hachoir.parser import createParser

logger = logging.getLogger(__name__)

# 1.95 GB — safely under the 2 GB Telegram bot upload limit
SPLIT_SIZE_BYTES = int(1.95 * 1024 * 1024 * 1024)


def _get_duration_seconds(file_path: str) -> float:
    """Return duration in seconds using hachoir, or 0 on failure."""
    try:
        metadata = extractMetadata(createParser(file_path))
        if metadata is not None and metadata.has("duration"):
            return metadata.get("duration").seconds
    except Exception as exc:
        logger.warning("hachoir could not read duration: %s", exc)
    return 0


async def split_video(input_file: str, output_dir: str) -> list:
    """
    Split *input_file* into multiple parts, each under SPLIT_SIZE_BYTES.

    Uses a byte-rate estimate to calculate segment duration so no re-encode
    is needed (stream copy is instant and lossless).

    Returns a sorted list of absolute paths to the part files.
    Raises RuntimeError if splitting fails.
    """
    file_size = os.path.getsize(input_file)
    duration = _get_duration_seconds(input_file)

    if duration <= 0:
        # Fallback: binary split (non-video files, eg. zip/rar)
        return await _binary_split(input_file, output_dir)

    # Estimate how many seconds fit inside SPLIT_SIZE_BYTES
    bytes_per_second = file_size / duration
    segment_duration = math.floor(SPLIT_SIZE_BYTES / bytes_per_second)
    if segment_duration <= 0:
        segment_duration = 600  # 10-minute safety fallback

    base_name = os.path.splitext(os.path.basename(input_file))[0]
    ext = os.path.splitext(input_file)[1] or ".mp4"
    output_pattern = os.path.join(output_dir, f"{base_name}_part%03d{ext}")

    cmd = [
        "ffmpeg",
        "-i", input_file,
        "-c", "copy",                   # stream-copy — no re-encode, very fast
        "-map", "0",
        "-segment_time", str(segment_duration),
        "-f", "segment",
        "-reset_timestamps", "1",
        "-y",
        output_pattern,
    ]

    logger.info("Splitting video with command: %s", " ".join(cmd))
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        err = stderr.decode().strip()
        logger.error("ffmpeg split failed: %s", err)
        raise RuntimeError(f"ffmpeg split error: {err}")

    # Collect all generated part files in sorted order
    parts = sorted(
        os.path.join(output_dir, f)
        for f in os.listdir(output_dir)
        if f.startswith(f"{base_name}_part") and f.endswith(ext)
    )

    if not parts:
        raise RuntimeError("ffmpeg ran but produced no output files.")

    logger.info("Split produced %d parts: %s", len(parts), parts)
    return parts


async def _binary_split(input_file: str, output_dir: str) -> list:
    """
    Raw binary split for non-video files that ffmpeg cannot segment.
    Each chunk is SPLIT_SIZE_BYTES. Parts are named <base>.part001, .part002 …
    """
    base_name = os.path.basename(input_file)
    parts = []
    part_index = 1

    with open(input_file, "rb") as src:
        while True:
            chunk = src.read(SPLIT_SIZE_BYTES)
            if not chunk:
                break
            part_path = os.path.join(output_dir, f"{base_name}.part{part_index:03d}")
            with open(part_path, "wb") as dst:
                dst.write(chunk)
            parts.append(part_path)
            part_index += 1

    logger.info("Binary split produced %d parts.", len(parts))
    return parts
