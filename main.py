#!/usr/bin/env python3
import argparse
import os
import shutil
import subprocess
import sys

def find_blender(exec_path):
    # allow override via --blender, fallback to $BLENDER_PATH or just "blender"
    return exec_path or os.environ.get("BLENDER_PATH", "blender")

def main():
    p = argparse.ArgumentParser(
        description="Full pipeline: wrap image in Blender → generate Gazebo model"
    )
    p.add_argument(
        "-i","--image", required=True,
        help="Path to source image"
    )
    p.add_argument(
        "-o","--output", required=True,
        help="Gazebo-model install folder (e.g. ~/.gazebo/models/med_box)"
    )
    p.add_argument(
        "--blender", default=None,
        help="Path to Blender executable (fallback: $BLENDER_PATH or in $PATH)"
    )
    args = p.parse_args()

    img = os.path.abspath(args.image)
    model_out = os.path.abspath(args.output)

    # 1) Blender step → output_tmp/
    scratch = os.path.join(os.getcwd(), "output_tmp")
    if os.path.exists(scratch):
        shutil.rmtree(scratch)
    os.makedirs(scratch)

    blender_exec = find_blender(args.blender)
    subprocess.run([
        blender_exec,
        "--background",
        "--python", "wrap_image_box.py",
        "--", "--image", img, "--outdir", scratch
    ], check=True)

    # 2) pick up the generated .dae & texture
    dae_file   = next(f for f in os.listdir(scratch) if f.endswith(".dae"))
    tex_file   = next(f for f in os.listdir(scratch) if f.startswith("texture_"))
    dae_path   = os.path.join(scratch, dae_file)
    texture    = os.path.join(scratch, tex_file)

    # 3) SDF step → final Gazebo models folder
    subprocess.run([
        sys.executable,
        "generate_sdf_model.py",
        "--dae", dae_path,
        "--texture", texture,
        "--output", model_out
    ], check=True)

    print(f"\n✅ All done! Gazebo model ready in:\n    {model_out}")

if __name__ == "__main__":
    main()
