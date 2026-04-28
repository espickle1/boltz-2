#!/usr/bin/env python3
"""
Batch Boltz-2 prediction runner on Modal (remote GPU).

Usage:
    modal run boltz_predict_modal.py --input-dir <input_dir> [--out-dir <output_dir>]

Finds all .yaml/.yml files in <input_dir>, ships each to a Modal GPU container
running `boltz predict`, and writes the resulting zip back into <output_dir>.

Auth / setup (one-time):
    pip install modal
    modal token new
"""

import sys
from pathlib import Path

import modal

# ---------------------------------------------------------------------------
# Modal app + image
# ---------------------------------------------------------------------------

# GPU choice. T4 ~16GB matches the Colab notebook; A10G ~24GB is faster and
# handles larger complexes. Override with --gpu on the CLI.
DEFAULT_GPU = "A10G"
DEFAULT_TIMEOUT = 60 * 60  # 1h per prediction

image = (
    modal.Image.debian_slim(python_version="3.11")
    .apt_install("git", "wget")
    .pip_install(
        "boltz[cuda]",
        extra_index_url="https://download.pytorch.org/whl/cu121",
    )
)

app = modal.App("boltz-predict")

# Cache Boltz model weights across invocations (boltz downloads to ~/.boltz on
# first run; without this the weights are re-fetched every cold start).
weights_vol = modal.Volume.from_name("boltz-weights", create_if_missing=True)


# ---------------------------------------------------------------------------
# Remote prediction function
# ---------------------------------------------------------------------------

def _build_predict_fn(gpu: str, timeout: int):
    """Build a Modal Function bound to the chosen GPU/timeout at call time."""

    @app.function(
        image=image,
        gpu=gpu,
        timeout=timeout,
        volumes={"/root/.boltz": weights_vol},
    )
    def predict_one(params: dict) -> dict:
        """Run `boltz predict` on a single YAML inside the container.

        params keys: yaml_name, yaml_text, recycling_steps, sampling_steps,
        diffusion_samples, step_scale, sampling_steps_affinity,
        diffusion_samples_affinity, use_msa_server.

        Returns {name, zip_bytes, rc, log}.
        """
        import io
        import shutil
        import subprocess
        import tempfile
        import zipfile

        # CUDA preflight — fail loudly if the GPU did not come up.
        import torch
        if not torch.cuda.is_available():
            return {
                "name": params["yaml_name"],
                "zip_bytes": b"",
                "rc": 2,
                "log": "ERROR: torch.cuda.is_available() is False inside Modal container.",
            }
        print(
            f"CUDA OK: {torch.cuda.device_count()} device(s), "
            f"{torch.cuda.get_device_name(0)} (torch {torch.__version__})",
            flush=True,
        )

        work = Path(tempfile.mkdtemp(prefix="boltz_"))
        yaml_path = work / params["yaml_name"]
        yaml_path.write_text(params["yaml_text"])
        out_dir = work / "out"
        out_dir.mkdir()

        cmd = [
            "boltz", "predict",
            str(yaml_path),
            "--out_dir", str(out_dir),
            "--recycling_steps", str(params["recycling_steps"]),
            "--sampling_steps", str(params["sampling_steps"]),
            "--diffusion_samples", str(params["diffusion_samples"]),
            "--step_scale", str(params["step_scale"]),
            "--sampling_steps_affinity", str(params["sampling_steps_affinity"]),
            "--diffusion_samples_affinity", str(params["diffusion_samples_affinity"]),
            "--accelerator", "gpu",
            "--devices", "1",
        ]
        if params.get("use_msa_server", True):
            cmd.append("--use_msa_server")

        print("$", " ".join(cmd), flush=True)
        proc = subprocess.run(cmd, capture_output=True, text=True)
        log = (proc.stdout or "") + (proc.stderr or "")
        print(log, flush=True)

        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in out_dir.rglob("*"):
                if f.is_file():
                    zf.write(f, f.relative_to(out_dir))

        shutil.rmtree(work, ignore_errors=True)
        return {
            "name": params["yaml_name"],
            "zip_bytes": buf.getvalue(),
            "rc": proc.returncode,
            "log": log,
        }

    return predict_one


# Default function (used when invoked via `modal run`). The CLI entrypoint
# below picks GPU/timeout from args and calls this same function reference.
predict_one = _build_predict_fn(DEFAULT_GPU, DEFAULT_TIMEOUT)


# ---------------------------------------------------------------------------
# Local entrypoint
# ---------------------------------------------------------------------------

@app.local_entrypoint()
def main(
    input_dir: str,
    out_dir: str = "boltz_results",
    recycling_steps: int = 8,
    sampling_steps: int = 64,
    diffusion_samples: int = 5,
    step_scale: float = 1.7,
    sampling_steps_affinity: int = 64,
    diffusion_samples_affinity: int = 4,
    no_msa_server: bool = False,
    parallel: bool = False,
):
    """Dispatch every YAML in input_dir to a Modal GPU container.

    --parallel fans the jobs out concurrently (one container per YAML); the
    default is sequential so logs stay readable.
    """
    in_dir = Path(input_dir)
    yaml_files = sorted(
        f for f in in_dir.iterdir() if f.suffix in (".yaml", ".yml")
    )
    if not yaml_files:
        print(f"No .yaml/.yml files found in {in_dir}")
        sys.exit(1)

    out_root = Path(out_dir)
    out_root.mkdir(parents=True, exist_ok=True)
    print(
        f"Found {len(yaml_files)} YAML file(s); "
        f"dispatching to Modal on {DEFAULT_GPU} "
        f"({'parallel' if parallel else 'sequential'})"
    )

    def make_params(yaml_path: Path) -> dict:
        return {
            "yaml_name": yaml_path.name,
            "yaml_text": yaml_path.read_text(),
            "recycling_steps": recycling_steps,
            "sampling_steps": sampling_steps,
            "diffusion_samples": diffusion_samples,
            "step_scale": step_scale,
            "sampling_steps_affinity": sampling_steps_affinity,
            "diffusion_samples_affinity": diffusion_samples_affinity,
            "use_msa_server": not no_msa_server,
        }

    succeeded, failed = [], []

    def handle_result(result: dict):
        name = result["name"]
        stem = Path(name).stem
        zip_path = out_root / f"{stem}.zip"
        if result["zip_bytes"]:
            zip_path.write_bytes(result["zip_bytes"])
        if result["rc"] != 0:
            print(f"FAILED: {name} (rc={result['rc']})")
            log_path = out_root / f"{stem}.log"
            log_path.write_text(result["log"])
            print(f"  log -> {log_path}")
            failed.append(name)
        else:
            print(f"OK: {name} -> {zip_path}")
            succeeded.append(name)

    if parallel:
        params_list = [make_params(f) for f in yaml_files]
        for result in predict_one.map(params_list):
            handle_result(result)
    else:
        for i, yaml_path in enumerate(yaml_files, 1):
            print(f"\n{'='*60}")
            print(f"[{i}/{len(yaml_files)}] {yaml_path.name}")
            print(f"{'='*60}")
            handle_result(predict_one.remote(make_params(yaml_path)))

    print(f"\n{'='*60}")
    print(
        f"DONE: {len(succeeded)} succeeded, "
        f"{len(failed)} failed out of {len(yaml_files)}"
    )
    if failed:
        print(f"Failed: {', '.join(failed)}")
        sys.exit(1)
