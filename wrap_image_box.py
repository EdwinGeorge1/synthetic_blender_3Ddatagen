#!/usr/bin/env python3

import bpy
import sys
import os
import shutil
import argparse
from fractions import Fraction

def parse_args():
    """
    Parse command-line args after the '--' separator.
    Now only requires:
      --image /path/to/image.png
      --outdir /path/to/output_folder
    """
    argv = sys.argv
    if "--" not in argv:
        print("Error: missing '--' separator")
        sys.exit(1)
    idx = argv.index("--")
    cli_args = argv[idx+1:]

    p = argparse.ArgumentParser(
        description="Wrap an image onto the top face of a box and export as COLLADA (.dae)."
    )
    p.add_argument("--image",  "-i", type=str, required=True, help="Path to source image")
    p.add_argument("--outdir", "-o", type=str, required=True, help="Output folder for texture+dae")
    return p.parse_args(cli_args)

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def create_box(w, d, h):
    bpy.ops.mesh.primitive_cube_add(size=1)
    obj = bpy.context.active_object
    obj.scale = (w/2, d/2, h/2)
    bpy.ops.object.transform_apply(scale=True)
    return obj

def make_dim_string(w, d, h):
    # e.g. 0.4 → "0p4"
    def fmt(val): return str(val).replace(".", "p")
    return f"{fmt(w)}x{fmt(d)}x{fmt(h)}"

def create_materials(obj, image_path):
    # 1) Default white mat (slot 0)
    dm = bpy.data.materials.new("DefaultMat")
    dm.use_nodes = True
    nodes, links = dm.node_tree.nodes, dm.node_tree.links
    for n in nodes: nodes.remove(n)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (1,1,1,1)
    out = nodes.new("ShaderNodeOutputMaterial")
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    # 2) Image mat (slot 1)
    im = bpy.data.materials.new("ImageMat")
    im.use_nodes = True
    nodes, links = im.node_tree.nodes, im.node_tree.links
    for n in nodes: nodes.remove(n)
    tex = nodes.new("ShaderNodeTexImage")
    tex.image = bpy.data.images.load(os.path.abspath(image_path))
    bsdf2 = nodes.new("ShaderNodeBsdfPrincipled")
    out2 = nodes.new("ShaderNodeOutputMaterial")
    links.new(tex.outputs["Color"], bsdf2.inputs["Base Color"])
    links.new(bsdf2.outputs["BSDF"], out2.inputs["Surface"])

    obj.data.materials.append(dm)
    obj.data.materials.append(im)

def assign_face_materials_and_uv(obj):
    if not obj.data.uv_layers:
        obj.data.uv_layers.new(name="UVMap")

    # assign mat slots per face (top face: normal.z > 0.9)
    for poly in obj.data.polygons:
        poly.material_index = 1 if poly.normal.z > 0.9 else 0

    # UV-unwrap only the image face
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_mode(type="FACE")
    bpy.ops.mesh.select_all(action="DESELECT")
    bpy.ops.object.mode_set(mode="OBJECT")

    for poly in obj.data.polygons:
        poly.select = (poly.material_index == 1)

    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.uv.unwrap(method="ANGLE_BASED", margin=0.001)
    bpy.ops.object.mode_set(mode="OBJECT")

def export_collada(path):
    bpy.ops.wm.collada_export(
        filepath=os.path.abspath(path),
        apply_modifiers=True,
        export_mesh_type_selection="view",
        selected=False
    )

def main():
    args = parse_args()
    src_img = os.path.abspath(args.image)
    outdir  = os.path.abspath(args.outdir)

    # 1) make output folder
    os.makedirs(outdir, exist_ok=True)

    # 2) load image to get pixel dimensions & compute X:Y ratio
    img = bpy.data.images.load(src_img)
    px_w, px_h = img.size[0], img.size[1]
    frac = Fraction(px_w, px_h).limit_denominator()
    rx, ry = frac.numerator, frac.denominator
    print(f"Detected image aspect ratio: {rx}:{ry}")

    # 3) prompt for real-world X (cm), compute Y; then prompt for Z (height)
    x_cm = float(input(f"Enter desired length for the {rx}-part (in cm): ").strip())
    y_cm = x_cm * ry / rx
    print(f" → computed other side (Y): {y_cm:.2f} cm")
    z_cm = float(input("Enter desired third dimension (height, Z axis) in cm: ").strip())

    # 4) convert all to meters
    w = x_cm / 100.0
    d = y_cm / 100.0
    h = z_cm / 100.0

    # 5) build names
    dim      = make_dim_string(w, d, h)
    ext      = os.path.splitext(src_img)[1]  # keep .png/.jpg
    tex_name = f"texture_{dim}{ext}"
    dae_name = f"box_{dim}.dae"

    tex_dest = os.path.join(outdir, tex_name)
    dae_dest = os.path.join(outdir, dae_name)

    # 6) copy image into folder
    shutil.copy(src_img, tex_dest)

    # 7) build scene & export
    clear_scene()
    box = create_box(w, d, h)
    create_materials(box, tex_dest)
    assign_face_materials_and_uv(box)
    export_collada(dae_dest)

    print(f"Done.  Texture → {tex_dest}\n      Model   → {dae_dest}")

if __name__ == "__main__":
    main()
