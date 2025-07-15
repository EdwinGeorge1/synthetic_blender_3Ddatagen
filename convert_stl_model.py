#!/usr/bin/env python3
import os, sys, shutil, argparse
try:
    import trimesh
    from trimesh import repair
except ImportError:
    print("Please install trimesh: pip install trimesh", file=sys.stderr)
    sys.exit(1)

def compute_props(mesh, density):
    if not mesh.is_watertight:
        repair.fill_holes(mesh)
    mesh.density = density
    mp = mesh.mass_properties
    m = mp["mass"]
    I = mp["inertia"]
    return m, (I[0,0], I[1,1], I[2,2])

def main():
    p = argparse.ArgumentParser(__doc__)
    p.add_argument("--stl",   required=True, help="Input STL file")
    p.add_argument("--output",required=True, help="Destination Gazebo model dir")
    p.add_argument("--scale", type=float, default=1.0, help="Unit→meter scale")
    p.add_argument("--density", type=float, help="Density kg/m³ (prompt if omitted)")
    args = p.parse_args()

    # load & scale
    raw = trimesh.load(args.stl, force="mesh")
    if not raw.is_watertight:
        repair.fill_holes(raw)
    mesh = raw.copy()
    mesh.apply_scale(args.scale)

    # density
    dens = args.density if args.density is not None else float(input("Density [1000]: ") or 1000.0)
    mass, inertia = compute_props(mesh, dens)
    print(f"Mass={mass:.4f} kg, inertia={inertia}")

    # prepare folders
    model = os.path.basename(args.output.rstrip("/"))
    odir  = os.path.abspath(args.output)
    mdir  = os.path.join(odir, "meshes")
    os.makedirs(mdir, exist_ok=True)

    # export visual STL
    vis = f"{model}.stl"
    mesh.export(os.path.join(mdir, vis))

    # export convex‐hull collision STL
    hull = mesh.convex_hull
    col  = f"{model}_col.stl"
    hull.export(os.path.join(mdir, col))

    # write model.sdf with hard-coded anti-wiggle settings
    sdf = f"""<?xml version='1.0'?>
<sdf version='1.7'>
  <model name='{model}'>
    <static>0</static>
    <link name='link'>
      <inertial>
        <mass>{mass:.6f}</mass>
        <inertia>
          <ixx>{inertia[0]:.6f}</ixx><ixy>0</ixy><ixz>0</ixz>
          <iyy>{inertia[1]:.6f}</iyy><iyz>0</iyz><izz>{inertia[2]:.6f}</izz>
        </inertia>
        <pose>0 0 0 0 0 0</pose>
      </inertial>

      <!-- Strong damping -->
      <velocity_decay><linear>2.0</linear><angular>2.0</angular></velocity_decay>

      <visual name='vis'>
        <geometry>
          <mesh><uri>model://{model}/meshes/{vis}</uri><scale>1 1 1</scale></mesh>
        </geometry>
      </visual>

      <collision name='coll'>
        <geometry>
          <mesh><uri>model://{model}/meshes/{col}</uri><scale>1 1 1</scale></mesh>
        </geometry>
        <surface>
          <friction><ode><mu>10</mu><mu2>10</mu2><slip1>5</slip1><slip2>5</slip2></ode></friction>
          <bounce><restitution_coefficient>0</restitution_coefficient><threshold>1e6</threshold></bounce>
          <contact>
            <ode>
              <kp>1e6</kp><kd>1e3</kd>
              <soft_cfm>0.01</soft_cfm><soft_erp>0.95</soft_erp>
            </ode>
          </contact>
        </surface>
      </collision>
    </link>
  </model>
</sdf>
"""
    with open(os.path.join(odir, "model.sdf"), "w") as f: f.write(sdf)

    # write model.config
    cfg = f"""<?xml version="1.0"?>
<model>
  <name>{model}</name>
  <version>1.0</version>
  <sdf version="1.7">model.sdf</sdf>
  <author><name>AutoGen</name><email>noreply@example.com</email></author>
  <description>Convex‐hull + heavy damping to eliminate wiggle</description>
</model>
"""
    with open(os.path.join(odir, "model.config"), "w") as f: f.write(cfg)

    print(f"\n✅ Model ready: {odir}")
    print("├ model.config")
    print("├ model.sdf")
    print("└ meshes/")
    print(f"   ├ {vis}")
    print(f"   └ {col}")

if __name__=="__main__":
    main()
