# project-root/primitives/box.py

import os
import shutil
import math
import bpy
import bmesh
from .base import PrimitiveWrapper

def create_box(w, d, h):
    """Create a box of size (w,d,h) in meters, centered at origin."""
    bpy.ops.mesh.primitive_cube_add(size=1)
    obj = bpy.context.active_object
    obj.scale = (w/2, d/2, h/2)
    bpy.ops.object.transform_apply(scale=True)
    return obj

def create_materials(obj, image_path):
    """Set up a default material + an image‐texture material on the box."""
    # Default (uninfluenced) material
    dm = bpy.data.materials.new("DefaultMat")
    dm.use_nodes = True
    nodes = dm.node_tree.nodes
    links = dm.node_tree.links
    for n in nodes: nodes.remove(n)
    bsdf = nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (1,1,1,1)
    out = nodes.new("ShaderNodeOutputMaterial")
    links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])

    # Image material
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

    obj.data.materials.clear()
    obj.data.materials.append(dm)
    obj.data.materials.append(im)

def assign_face_materials_and_uv(obj):
    """
    Assign the image material (index=1) to the face whose normal.z>0.9,
    unwrap that face to cover full image, leave others as default.
    """
    # ensure UV map exists
    if not obj.data.uv_layers:
        obj.data.uv_layers.new(name="UVMap")

    # switch to edit mode
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bm = bmesh.from_edit_mesh(obj.data)
    uv_layer = bm.loops.layers.uv.active

    for face in bm.faces:
        # top face has normal pointing up (after rotation it'll be the side face)
        if face.normal.z > 0.9:
            face.material_index = 1
            for loop in face.loops:
                # map vertex coords (x,y) to (u,v)
                vert = loop.vert.co
                u = (vert.x / obj.dimensions.x) + 0.5
                v = (vert.y / obj.dimensions.y) + 0.5
                loop[uv_layer].uv = (u, v)
        else:
            face.material_index = 0

    # back to object mode
    bmesh.update_edit_mesh(obj.data)
    bpy.ops.object.mode_set(mode="OBJECT")

class BoxWrapper(PrimitiveWrapper):
    def run(self, image_path: str, outdir: str):
        # 1) ensure output folder exists
        os.makedirs(outdir, exist_ok=True)

        # 2) load image to get aspect ratio
        img = bpy.data.images.load(os.path.abspath(image_path))
        width_px, height_px = img.size
        aspect = height_px / width_px
        print(f"Image size: {width_px} x {height_px} px → aspect Y/X = {aspect:.3f}")

        # 3) prompt exactly as before
        x_cm = float(input("Enter box width (X) in cm: ").strip())
        z_cm = float(input("Enter box height (Z) in cm: ").strip())
        y_cm = x_cm * aspect
        print(f"\n→ Box dimensions:\n   Width (X): {x_cm:.2f} cm\n   Depth (Y): {y_cm:.2f} cm (auto)\n   Height(Z): {z_cm:.2f} cm")

        # 4) convert to meters
        w, d, h = x_cm/100.0, y_cm/100.0, z_cm/100.0

        # 5) prepare filenames
        def fmt(val): return str(round(val,4)).replace(".", "p")
        dimstr = f"{fmt(w)}x{fmt(d)}x{fmt(h)}"
        ext    = os.path.splitext(image_path)[1]
        tex_name = f"texture_{dimstr}{ext}"
        dae_name = f"box_{dimstr}.dae"
        tex_dest = os.path.join(outdir, tex_name)
        dae_dest = os.path.join(outdir, dae_name)

        # 6) copy texture into outdir
        shutil.copy(image_path, tex_dest)

        # 7) clear scene & create box
        bpy.ops.wm.read_factory_settings(use_empty=True)
        box = create_box(w, d, h)

        # 8) assign materials and UV to the top face
        create_materials(box, tex_dest)
        assign_face_materials_and_uv(box)

        # 9) rotate so that the textured face is vertical
        box.rotation_euler = (math.radians(90), 0, 0)
        bpy.context.view_layer.update()

        # 10) export Collada
        bpy.ops.wm.collada_export(
            filepath=os.path.abspath(dae_dest),
            apply_modifiers=True,
            export_mesh_type_selection="view",
            selected=False
        )

        print(f"\n✅ Exported box:\n   Texture: {tex_dest}\n   Model:   {dae_dest}")
