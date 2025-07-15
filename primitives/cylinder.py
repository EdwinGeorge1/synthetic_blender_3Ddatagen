# primitives/cylinder.py

import os, math, shutil, bpy, bmesh
from .base import PrimitiveWrapper

class CylinderWrapper(PrimitiveWrapper):
    def run(self, image_path: str, outdir: str):
        # 1) Setup output dir
        os.makedirs(outdir, exist_ok=True)

        # 2) Load image & get aspect ratio W/H
        img = bpy.data.images.load(os.path.abspath(image_path))
        w_px, h_px = img.size
        ratio = w_px / h_px
        print(f"Image size: {w_px}×{h_px}px → aspect W/H = {ratio:.3f}")

        # 3) Prompt for height (cm), then compute circumference → radius
        H_cm = float(input("Enter cylinder height (H) in cm: ").strip())
        C_cm = H_cm * ratio
        R_cm = C_cm / (2 * math.pi)
        print(f"→ Height: {H_cm:.2f}cm, Circumference: {C_cm:.2f}cm → Radius: {R_cm:.2f}cm")

        # 4) Convert to meters
        H = H_cm / 100.0
        R = R_cm / 100.0

        # 5) Filenames
        def fmt(x): return str(round(x,4)).replace('.', 'p')
        dim = f"{fmt(R)}x{fmt(H)}"
        ext = os.path.splitext(image_path)[1]
        tex_fn = f"texture_{dim}{ext}"
        dae_fn = f"cylinder_{dim}.dae"
        tex_dst = os.path.join(outdir, tex_fn)
        dae_dst = os.path.join(outdir, dae_fn)
        shutil.copy(image_path, tex_dst)

        # 6) Clear scene & create cylinder
        bpy.ops.wm.read_factory_settings(use_empty=True)
        bpy.ops.mesh.primitive_cylinder_add(
            radius=R, depth=H, vertices=64, enter_editmode=False
        )
        obj = bpy.context.active_object

        # 7) Create Default + Image materials
        def make_mat(name, use_tex=False):
            m = bpy.data.materials.new(name)
            m.use_nodes = True
            nodes = m.node_tree.nodes; links = m.node_tree.links
            for n in nodes: nodes.remove(n)
            bsdf = nodes.new("ShaderNodeBsdfPrincipled")
            out = nodes.new("ShaderNodeOutputMaterial")
            if use_tex:
                tex = nodes.new("ShaderNodeTexImage")
                tex.image = bpy.data.images.load(tex_dst)
                tex.extension = 'CLIP'
                links.new(tex.outputs["Color"], bsdf.inputs["Base Color"])
            else:
                bsdf.inputs["Base Color"].default_value = (1,1,1,1)
            links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
            return m

        m_def = make_mat("DefaultMat", use_tex=False)
        m_img = make_mat("ImageMat",   use_tex=True)
        obj.data.materials.clear()
        obj.data.materials.append(m_def)
        obj.data.materials.append(m_img)

        # 8) Manual UV unwrap of side faces
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.mode_set(mode="EDIT")
        bm = bmesh.from_edit_mesh(obj.data)
        uv_layer = bm.loops.layers.uv.verify()

        # Side faces: normals roughly horizontal
        for face in bm.faces:
            if abs(face.normal.z) < 0.9:
                face.material_index = 1
                for loop in face.loops:
                    co = loop.vert.co
                    # U = normalized angle around Z
                    angle = math.atan2(co.y, co.x)
                    u = (angle / (2*math.pi)) + 0.5
                    # V = normalized height
                    v = (co.z / H) + 0.5
                    loop[uv_layer].uv = (u, v)
            else:
                face.material_index = 0

        bmesh.update_edit_mesh(obj.data)
        bpy.ops.object.mode_set(mode="OBJECT")

        # 9) Export as COLLADA
        bpy.ops.wm.collada_export(
            filepath=os.path.abspath(dae_dst),
            apply_modifiers=True,
            export_mesh_type_selection="view",
            selected=False
        )

        print(f"\n✅ Exported cylinder:\n   Texture: {tex_dst}\n   Model:   {dae_dst}")
