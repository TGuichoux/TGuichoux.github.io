#!/usr/bin/env python3

import argparse
import subprocess
from pathlib import Path


def extract_first_frame(video_path: Path, output_path: Path) -> None:
    """
    Extract the first video frame as a JPEG image.
    """
    command = [
        "ffmpeg",
        "-y",
        "-i", str(video_path),
        "-vf", "select=eq(n\\,0)",
        "-frames:v", "1",
        "-q:v", "2",
        str(output_path),
    ]

    subprocess.run(
        command,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Extract the first frame of every MP4 file as a JPEG poster."
    )

    parser.add_argument(
        "video_dir",
        type=Path,
        help="Directory containing the MP4 files",
    )

    parser.add_argument(
        "output_dir",
        type=Path,
        help="Directory where poster JPEGs will be written",
    )

    args = parser.parse_args()

    video_dir = args.video_dir.expanduser().resolve()
    output_dir = args.output_dir.expanduser().resolve()

    if not video_dir.exists():
        raise FileNotFoundError(f"Video directory does not exist: {video_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)

    videos = sorted(video_dir.glob("*.mp4"))

    if not videos:
        print(f"No MP4 files found in {video_dir}")
        return

    print(f"Found {len(videos)} MP4 files.\n")

    for video_path in videos:
        output_path = output_dir / f"{video_path.stem}.jpg"

        print(f"{video_path.name} -> {output_path.name}")

        try:
            extract_first_frame(video_path, output_path)
        except subprocess.CalledProcessError:
            print(f"ERROR extracting frame from {video_path.name}")

    print("\nDone.")


if __name__ == "__main__":
    main()