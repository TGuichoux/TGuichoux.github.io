import subprocess
import sys
from pathlib import Path


TARGET_LUFS = -16.0
TRUE_PEAK = -1.5
LOUDNESS_RANGE = 11.0


def normalize_wav(input_path: Path) -> None:
    output_path = input_path.with_name(
        f"{input_path.stem}_normalized.wav"
    )

    command = [
        "ffmpeg",
        "-y",
        "-i", str(input_path),
        "-af",
        f"loudnorm=I={TARGET_LUFS}:TP={TRUE_PEAK}:LRA={LOUDNESS_RANGE}",
        "-c:a", "pcm_s24le",
        str(output_path),
    ]

    print(f"Normalizing: {input_path.name}")
    subprocess.run(command, check=True)
    print(f"Created:     {output_path}")


def main():
    if len(sys.argv) != 2:
        print(f"Usage: python {Path(sys.argv[0]).name} <audio.wav | folder>")
        sys.exit(1)

    path = Path(sys.argv[1]).expanduser().resolve()

    if not path.exists():
        print(f"Path not found: {path}")
        sys.exit(1)

    # Single WAV file
    if path.is_file():
        if path.suffix.lower() != ".wav":
            print("Input file must be a .wav file.")
            sys.exit(1)

        normalize_wav(path)
        return

    # Folder containing WAV files
    if path.is_dir():
        wav_files = sorted(
            file
            for file in path.iterdir()
            if (
                file.is_file()
                and file.suffix.lower() == ".wav"
                and not file.stem.endswith("_normalized")
            )
        )

        if not wav_files:
            print(f"No WAV files found in: {path}")
            return

        print(f"Found {len(wav_files)} WAV file(s).\n")

        for i, wav_file in enumerate(wav_files, start=1):
            print(f"[{i}/{len(wav_files)}]")
            normalize_wav(wav_file)
            print()

        print(f"Done. Normalized {len(wav_files)} file(s).")


if __name__ == "__main__":
    main()