#!/usr/bin/env python3
import argparse
import os
import shutil
import subprocess
import sys

def find_blender(path):
    return path or os.environ.get("BLENDER_PATH", "blender")

def run_pipeline(image_path, output_dir, primitive, blender_exec):
    """Wrap one image and generate its SDF model."""
    scratch = os.path.abspath("output_tmp")
    if os.path.exists(scratch):
        shutil.rmtree(scratch)
    os.makedirs(scratch)

    # 1) Blender wrap step
    subprocess.run([
        blender_exec,
        "--background", "--python", "wrap_image_box.py", "--",
        "--primitive", primitive,
        "--image",    os.path.abspath(image_path),
        "--outdir",   scratch
    ], check=True)

    # 2) Locate the generated .dae and texture_*
    files = os.listdir(scratch)
    dae_file = next(f for f in files if f.endswith(".dae"))
    tex_file = next(f for f in files if f.startswith("texture_"))
    dae_path = os.path.join(scratch, dae_file)
    tex_path = os.path.join(scratch, tex_file)

    # 3) SDF generation
    subprocess.run([
        sys.executable,
        "generate_sdf_model.py",
        "--dae",     dae_path,
        "--texture", tex_path,
        "--output",  os.path.abspath(output_dir)
    ], check=True)

    print(f"✅ Model created: {output_dir}")

def main():
    p = argparse.ArgumentParser(
        description="Wrap→SDF pipeline; single image or batch"
    )
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--image", "-i",
        help="Single image file to process"
    )
    group.add_argument(
        "--batch-dir", "-b",
        help="Directory of images to process in batch"
    )
    p.add_argument(
        "--output", "-o",
        required=True,
        help="Output root folder (single) or parent folder (batch)"
    )
    p.add_argument(
        "--primitive", "-p",
        choices=["box", "cylinder"],
        default="box",
        help="Which primitive to wrap"
    )
    p.add_argument(
        "--blender",
        help="Path to Blender executable (or set $BLENDER_PATH)"
    )
    args = p.parse_args()

    blender_exec = find_blender(args.blender)

    if args.batch_dir:
        # process every image in the folder
        imgs = sorted(
            f for f in os.listdir(args.batch_dir)
            if f.lower().endswith((".png", ".jpg", ".jpeg"))
        )
        if not imgs:
            print(f"No images found in {args.batch_dir}")
            sys.exit(1)
        for img in imgs:
            img_path = os.path.join(args.batch_dir, img)
            name     = os.path.splitext(img)[0]
            out_dir  = os.path.join(args.output, name)
            print(f"\n--- Processing {img} → {out_dir} ---")
            run_pipeline(img_path, out_dir, args.primitive, blender_exec)
    else:
        # single image mode
        run_pipeline(args.image, args.output, args.primitive, blender_exec)

    print("\n🎉 All tasks complete.")

if __name__ == "__main__":
    main()
