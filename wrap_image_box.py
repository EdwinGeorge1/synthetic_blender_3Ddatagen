#!/usr/bin/env python3

import bpy
import sys
import os
import shutil
import argparse
import math

def parse_args():
    argv = sys.argv
    if "--" not in argv:
        print("Error: missing '--' separator")
        sys.exit(1)
    idx = argv.index("--")
    cli_args = argv[idx + 1:]

    p = argparse.ArgumentParser(description="Wrap an image onto the side face of a standing box.")
    p.add_argument("--image", "-i", type=str, required=True, help="Path to image file")
    p.add_argument("--outdir", "-o", type=str, required=True, help="Output directory")
    return p.parse_args(cli_args)

def clear_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)

def create_box(w, d, h):
    bpy.ops.mesh.primitive_cube_add(size=1)
    obj = bpy.context.active_object
    obj.scale = (w / 2, d / 2, h / 2)
    bpy.ops.object.transform_apply(scale=True)
    return obj

def make_dim_string(w, d, h):
    def fmt(val): return str(round(val, 4)).replace(".", "p")
    return f"{fmt(w)}x{fmt(d)}x{fmt(h)}"

def create_materials(obj, image_path):
    dm = bpy.data.materials.new("DefaultMat")
    dm.use_nodes = True
    nodes = dm.node_tree.nodes
    links = dm.node_tree.links
    for n in nodes: nodes.remove(n)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (1, 1, 1, 1)
    out = nodes.new("ShaderNodeOutputMaterial")
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    im = bpy.data.materials.new("ImageMat")
    im.use_nodes = True
    nodes = im.node_tree.nodes
    links = im.node_tree.links
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
    import bmesh
    if not obj.data.uv_layers:
        obj.data.uv_layers.new(name="UVMap")

    for poly in obj.data.polygons:
        poly.material_index = 1 if poly.normal.z > 0.9 else 0

    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bm = bmesh.from_edit_mesh(obj.data)
    uv_layer = bm.loops.layers.uv.active

    for face in bm.faces:
        if face.normal.z > 0.9:
            face.material_index = 1
            for loop in face.loops:
                vert = loop.vert.co
                u = (vert.x / obj.dimensions.x) + 0.5
                v = (vert.y / obj.dimensions.y) + 0.5
                loop[uv_layer].uv = (u, v)

    bmesh.update_edit_mesh(obj.data)
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
    outdir = os.path.abspath(args.outdir)
    os.makedirs(outdir, exist_ok=True)

    # Load image and get aspect ratio
    img = bpy.data.images.load(src_img)
    width_px, height_px = img.size
    aspect_y_by_x = height_px / width_px
    print(f"Image size: {width_px} x {height_px} px → aspect Y/X = {aspect_y_by_x:.3f}")

    # Get real-world box size
    x_cm = float(input("Enter box width (X) in cm: ").strip())
    z_cm = float(input("Enter box height (Z) in cm: ").strip())
    y_cm = x_cm * aspect_y_by_x  # calculated to preserve image proportion

    print(f"\n→ Box dimensions:")
    print(f"   Width  (X): {x_cm:.2f} cm")
    print(f"   Depth  (Y): {y_cm:.2f} cm (auto from image)")
    print(f"   Height (Z): {z_cm:.2f} cm")

    # Convert cm to meters
    w, d, h = x_cm / 100.0, y_cm / 100.0, z_cm / 100.0

    # File names
    dim_str = make_dim_string(w, d, h)
    ext = os.path.splitext(src_img)[1]
    tex_name = f"texture_{dim_str}{ext}"
    dae_name = f"box_{dim_str}.dae"
    tex_dest = os.path.join(outdir, tex_name)
    dae_dest = os.path.join(outdir, dae_name)
    shutil.copy(src_img, tex_dest)

    # Create box
    clear_scene()
    box = create_box(w, d, h)
    create_materials(box, tex_dest)
    assign_face_materials_and_uv(box)

    # Rotate the box to make the image appear on vertical side face
    box.rotation_euler = (math.radians(90), 0, 0)  # rotate 90° around X-axis
    bpy.context.view_layer.update()

    # Export
    export_collada(dae_dest)

    print(f"\n✅ Exported box:")
    print(f"   Texture: {tex_dest}")
    print(f"   Model  : {dae_dest}")

if __name__ == "__main__":
    main()
