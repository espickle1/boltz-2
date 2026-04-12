#!/usr/bin/env python3
"""
Batch Boltz-2 prediction runner.

Usage:
    python boltz_predict.py <input_dir> [--out_dir <output_dir>]

Finds all .yaml/.yml files in <input_dir> and runs `boltz predict` on each.
Results are saved to <output_dir>/<yaml_stem>/ and zipped automatically.
"""

import argparse
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path


def stream_cmd(cmd_list):
    """Run a command and stream stdout+stderr line-by-line. Returns the exit code."""
    proc = subprocess.Popen(
        cmd_list,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
    )
    for line in proc.stdout:
        print(line, end="")
        sys.stdout.flush()
    return proc.wait()


def zip_results(run_dir: Path):
    """Zip the run_dir and return the zip path."""
    zip_path = shutil.make_archive(str(run_dir), "zip", root_dir=str(run_dir))
    print(f"\nZipped results -> {zip_path}")
    return zip_path


def main():
    parser = argparse.ArgumentParser(description="Batch Boltz-2 prediction runner")
    parser.add_argument("input_dir", type=Path, help="Directory containing YAML input files")
    parser.add_argument("--out_dir", type=Path, default=Path("boltz_results"),
                        help="Base output directory (default: ./boltz_results)")
    parser.add_argument("--recycling_steps", type=int, default=8)
    parser.add_argument("--sampling_steps", type=int, default=64)
    parser.add_argument("--diffusion_samples", type=int, default=5)
    parser.add_argument("--step_scale", type=float, default=1.7)
    parser.add_argument("--sampling_steps_affinity", type=int, default=64)
    parser.add_argument("--diffusion_samples_affinity", type=int, default=4)
    parser.add_argument("--no_msa_server", action="store_true",
                        help="Disable --use_msa_server flag")
    args = parser.parse_args()

    # Collect YAML files
    yaml_files = sorted(
        f for f in args.input_dir.iterdir()
        if f.suffix in (".yaml", ".yml")
    )
    if not yaml_files:
        print(f"No .yaml/.yml files found in {args.input_dir}")
        sys.exit(1)

    print(f"Found {len(yaml_files)} YAML file(s) in {args.input_dir}")
    args.out_dir.mkdir(parents=True, exist_ok=True)

    succeeded, failed = [], []

    for i, yaml_path in enumerate(yaml_files, 1):
        run_dir = args.out_dir / yaml_path.stem
        run_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n{'='*60}")
        print(f"[{i}/{len(yaml_files)}] {yaml_path.name}")
        print(f"{'='*60}")

        cmd = [
            "boltz", "predict",
            str(yaml_path.resolve()),
            "--out_dir", str(run_dir),
            "--recycling_steps", str(args.recycling_steps),
            "--sampling_steps", str(args.sampling_steps),
            "--diffusion_samples", str(args.diffusion_samples),
            "--step_scale", str(args.step_scale),
            "--sampling_steps_affinity", str(args.sampling_steps_affinity),
            "--diffusion_samples_affinity", str(args.diffusion_samples_affinity),
        ]
        if not args.no_msa_server:
            cmd.append("--use_msa_server")

        print("$", " ".join(shlex.quote(x) for x in cmd))

        rc = stream_cmd(cmd)
        print(f"\n[boltz exited with code {rc}]")

        if rc != 0:
            print(f"FAILED: {yaml_path.name}")
            failed.append(yaml_path.name)
            continue

        succeeded.append(yaml_path.name)
        time.sleep(0.5)
        zip_results(run_dir)

    # Summary
    print(f"\n{'='*60}")
    print(f"DONE: {len(succeeded)} succeeded, {len(failed)} failed out of {len(yaml_files)}")
    if failed:
        print(f"Failed: {', '.join(failed)}")


if __name__ == "__main__":
    main()
