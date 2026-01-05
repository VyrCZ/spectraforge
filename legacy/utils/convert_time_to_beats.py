import argparse
import json
from pathlib import Path
import sys

def quantize_beats(beats: float, subdivision: int) -> float:
    unit = 1.0 / subdivision
    q = round(beats / unit) * unit
    return round(q, 6)

def convert_file(input_path: Path, output_path: Path, bpm_override: float | None, subdivision: int):
    with input_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    bpm = bpm_override or data.get("bpm") or 120.0
    try:
        bpm = float(bpm)
    except Exception:
        print("Invalid BPM value, defaulting to 120", file=sys.stderr)
        bpm = 120.0
    if bpm == 0:
        print("BPM is 0, defaulting to 120", file=sys.stderr)
        bpm = 120.0

    timeline = data.get("timeline", [])
    if not isinstance(timeline, list):
        print("No timeline array found in input file.", file=sys.stderr)
        return 1

    for item in timeline:
        # only convert numeric start/end if present
        if "start" in item and item["start"] is not None:
            try:
                seconds = float(item["start"])
                beats = seconds * (bpm / 60.0)
                item["start"] = quantize_beats(beats, subdivision)
            except Exception:
                print(f"Warning: could not convert start for item {item}", file=sys.stderr)
        if "end" in item and item["end"] is not None:
            try:
                seconds = float(item["end"])
                beats = seconds * (bpm / 60.0)
                item["end"] = quantize_beats(beats, subdivision)
            except Exception:
                print(f"Warning: could not convert end for item {item}", file=sys.stderr)

    # set/update bpm field so downstream tooling knows beats are used
    data["bpm"] = bpm

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Converted {input_path} -> {output_path} (bpm={bpm}, subdivision=1/{subdivision})")
    return 0

def main():
    parser = argparse.ArgumentParser(description="Convert absolute-time (seconds) lightshow JSON to beat-based (beats), quantized.")
    parser.add_argument("input", help="Input JSON lightshow file (start/end in seconds).")
    parser.add_argument("-o", "--output", help="Output file path. Defaults to input_beats.json")
    parser.add_argument("--bpm", type=float, help="Optional BPM override. If omitted, uses file bpm or 120.")
    parser.add_argument("--subdivision", type=int, default=16, help="Quantize to 1/N beats (default: 16 -> 1/16).")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        print("Input file does not exist.", file=sys.stderr)
        sys.exit(1)
    output_path = Path(args.output) if args.output else input_path.with_name(input_path.stem + "_beats" + input_path.suffix)

    rc = convert_file(input_path, output_path, args.bpm, args.subdivision)
    sys.exit(rc)

if __name__ == "__main__":
    main()
