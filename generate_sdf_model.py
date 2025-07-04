#!/usr/bin/env python3
import os
import shutil
import argparse
import yaml

CONFIG_DIR = os.path.join(os.path.dirname(__file__), "configs")

def load_config(shape):
    path = os.path.join(CONFIG_DIR, f"{shape}.yaml")
    if not os.path.exists(path):
        raise FileNotFoundError(f"No config for shape '{shape}'")
    with open(path) as f:
        return yaml.safe_load(f)

def main():
    p = argparse.ArgumentParser(
        description="Generate an SDF model from a shape config"
    )
    p.add_argument("--shape",
        choices=[fn[:-5] for fn in os.listdir(CONFIG_DIR) if fn.endswith(".yaml")],
        default="box",
        help="Which shape config to use"
    )
    # mesh‐based args
    p.add_argument("--dae",     help="Path to .dae file (only for mesh shapes)")
    p.add_argument("--texture", help="Path to texture (only for mesh shapes)")
    # cylinder‐based args
    p.add_argument("--radius",  type=float, help="Cylinder radius")
    p.add_argument("--length",  type=float, help="Cylinder length")
    p.add_argument("--output",  required=True, help="Output model folder")
    args = p.parse_args()

    cfg = load_config(args.shape)
    model_name = os.path.basename(args.output)
    outdir     = os.path.abspath(args.output)
    os.makedirs(outdir, exist_ok=True)

    # prep context from placeholders
    ctx = dict(cfg.get("placeholders", {}), model_name=model_name)

    # if using mesh, copy files & set dae_filename
    if "{dae_filename}" in cfg["template"]:
        if not args.dae or not args.texture:
            raise ValueError("Mesh shapes require --dae and --texture")
        mesh_dir = os.path.join(outdir, "meshes")
        os.makedirs(mesh_dir, exist_ok=True)
        dae_fn = os.path.basename(args.dae)
        tex_fn = os.path.basename(args.texture)
        shutil.copy(args.dae,     os.path.join(mesh_dir, dae_fn))
        shutil.copy(args.texture, os.path.join(mesh_dir, tex_fn))
        ctx["dae_filename"] = dae_fn

    # if using cylinder placeholders
    if "{radius}" in cfg["template"]:
        if args.radius is None or args.length is None:
            raise ValueError("Cylinder shapes require --radius and --length")
        ctx["radius"] = args.radius
        ctx["length"] = args.length

    # render template
    sdf_xml = cfg["template"].format(**ctx)
    with open(os.path.join(outdir, "model.sdf"), "w") as f:
        f.write(sdf_xml)

    # identical model.config for all shapes
    model_config = f"""<?xml version="1.0"?>
<model>
  <name>{model_name}</name>
  <version>1.0</version>
  <sdf version="1.7">model.sdf</sdf>
  <author><name>Generated</name><email>noreply@example.com</email></author>
  <description>Auto-generated model.</description>
</model>
"""
    with open(os.path.join(outdir, "model.config"), "w") as f:
        f.write(model_config)

    print(f"✅ Gazebo model created in: {outdir}")

if __name__=="__main__":
    main()
