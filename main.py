#!/usr/bin/env python3
import argparse, os, shutil, subprocess, sys

def find_blender(path):
    return path or os.environ.get("BLENDER_PATH","blender")

def main():
    p = argparse.ArgumentParser(
        description="Full pipeline: wrap → generate SDF"
    )
    p.add_argument("-i","--image", required=True)
    p.add_argument("-o","--output", required=True)
    p.add_argument("--primitive", default="box",
                   choices=["box","cylinder"])
    p.add_argument("--blender", default=None)
    args = p.parse_args()

    scratch = os.path.abspath("output_tmp")
    if os.path.exists(scratch): shutil.rmtree(scratch)
    os.makedirs(scratch)

    # 1) Blender
    subprocess.run([
        find_blender(args.blender),
        "--background","--python","wrap_image_box.py","--",
        "--primitive", args.primitive,
        "--image",    os.path.abspath(args.image),
        "--outdir",   scratch
    ], check=True)

    # 2) pick .dae & texture
    dae   = next(f for f in os.listdir(scratch) if f.endswith(".dae"))
    tex   = next(f for f in os.listdir(scratch) if f.startswith("texture_"))
    dae_p = os.path.join(scratch, dae)
    tex_p = os.path.join(scratch, tex)

    # 3) SDF
    subprocess.run([
        sys.executable,
        "generate_sdf_model.py",
        "--dae",     dae_p,
        "--texture", tex_p,
        "--output",  os.path.abspath(args.output)
    ], check=True)

    print(f"✅ All done! Model in {args.output}")

if __name__=="__main__":
    main()
