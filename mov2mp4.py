import subprocess
import sys
from pathlib import Path


def convert_mov(input_path: Path) -> None:
    output_path = input_path.with_suffix(".mp4")

    command = [
        "ffmpeg",
        "-y",
        "-i", str(input_path),
        "-c:v", "libx264",
        "-crf", "20",
        "-preset", "medium",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        str(output_path),
    ]

    print(f"Converting: {input_path.name}")
    subprocess.run(command, check=True)
    print(f"Created:    {output_path}")


def main():
    if len(sys.argv) != 2:
        print(f"Usage: python {Path(sys.argv[0]).name} <video.mov | folder>")
        sys.exit(1)

    path = Path(sys.argv[1]).expanduser().resolve()

    if not path.exists():
        print(f"Path not found: {path}")
        sys.exit(1)

    # Single MOV file
    if path.is_file():
        if path.suffix.lower() != ".mov":
            print("Input file must be a .mov file.")
            sys.exit(1)

        convert_mov(path)
        return

    # Folder containing MOV files
    if path.is_dir():
        mov_files = sorted(
            file
            for file in path.iterdir()
            if file.is_file() and file.suffix.lower() == ".mov"
        )

        if not mov_files:
            print(f"No .mov files found in: {path}")
            return

        print(f"Found {len(mov_files)} MOV file(s).\n")

        for i, mov_file in enumerate(mov_files, start=1):
            print(f"[{i}/{len(mov_files)}]")
            convert_mov(mov_file)
            print()

        print(f"Done. Converted {len(mov_files)} file(s).")


if __name__ == "__main__":
    main()