#!/usr/bin/env python3

import os
import shutil
import argparse

def make_sdf(model_name, dae_filename):
    return f"""<?xml version='1.0'?>
<sdf version='1.7'>
  <model name='{model_name}'>
    <link name='link_0'>
      <inertial>
        <mass>1</mass>
        <inertia>
          <ixx>0.166667</ixx>
          <ixy>0</ixy>
          <ixz>0</ixz>
          <iyy>0.166667</iyy>
          <iyz>0</iyz>
          <izz>0.166667</izz>
        </inertia>
        <pose>0 0 0 0 -0 0</pose>
      </inertial>
      <pose>0 0 0 0 -0 0</pose>
      <gravity>1</gravity>
      <self_collide>0</self_collide>
      <kinematic>0</kinematic>
      <enable_wind>0</enable_wind>
      <visual name='visual'>
        <pose>0 0 0 0 -0 0</pose>
        <geometry>
          <mesh>
            <uri>model://{model_name}/meshes/{dae_filename}</uri>
            <scale>1 1 1</scale>
          </mesh>
        </geometry>
        <material>
          <shader type='pixel'>
            <normal_map>__default__</normal_map>
          </shader>
          <emissive>0 0 0 1</emissive>
        </material>
        <transparency>0</transparency>
        <cast_shadows>1</cast_shadows>
      </visual>
      <collision name='collision'>
        <laser_retro>0</laser_retro>
        <max_contacts>10</max_contacts>
        <pose>0 0 0 0 -0 0</pose>
        <geometry>
          <mesh>
            <uri>model://{model_name}/meshes/{dae_filename}</uri>
            <scale>1 1 1</scale>
          </mesh>
        </geometry>
        <surface>
          <friction>
            <ode>
              <mu>1</mu>
              <mu2>1</mu2>
              <fdir1>0 0 0</fdir1>
              <slip1>0</slip1>
              <slip2>0</slip2>
            </ode>
            <torsional>
              <coefficient>1</coefficient>
              <patch_radius>0</patch_radius>
              <surface_radius>0</surface_radius>
              <use_patch_radius>1</use_patch_radius>
              <ode>
                <slip>0</slip>
              </ode>
            </torsional>
          </friction>
          <bounce>
            <restitution_coefficient>0</restitution_coefficient>
            <threshold>1e+06</threshold>
          </bounce>
          <contact>
            <collide_without_contact>0</collide_without_contact>
            <collide_without_contact_bitmask>1</collide_without_contact_bitmask>
            <collide_bitmask>1</collide_bitmask>
            <ode>
              <soft_cfm>0</soft_cfm>
              <soft_erp>0.2</soft_erp>
              <kp>1e+13</kp>
              <kd>1</kd>
              <max_vel>0.01</max_vel>
              <min_depth>0</min_depth>
            </ode>
            <bullet>
              <split_impulse>1</split_impulse>
              <split_impulse_penetration_threshold>-0.01</split_impulse_penetration_threshold>
              <soft_cfm>0</soft_cfm>
              <soft_erp>0.2</soft_erp>
              <kp>1e+13</kp>
              <kd>1</kd>
            </bullet>
          </contact>
        </surface>
      </collision>
    </link>
    <static>0</static>
    <allow_auto_disable>1</allow_auto_disable>
  </model>
</sdf>
"""

def make_model_config(model_name):
    return f"""<?xml version="1.0"?>
<model>
  <name>{model_name}</name>
  <version>1.0</version>
  <sdf version="1.7">model.sdf</sdf>
  <author>
    <name>Generated</name>
    <email>noreply@example.com</email>
  </author>
  <description>
    Auto-generated model.
  </description>
</model>
"""

def main():
    parser = argparse.ArgumentParser(description="Generate SDF and model.config from DAE and texture.")
    parser.add_argument("--dae", required=True, help="Path to .dae file")
    parser.add_argument("--texture", required=True, help="Path to .jpeg or .png texture file")
    parser.add_argument("--output", required=True, help="Output folder (model name)")
    args = parser.parse_args()

    dae_path = os.path.abspath(args.dae)
    texture_path = os.path.abspath(args.texture)
    model_name = os.path.basename(args.output)
    output_dir = os.path.abspath(args.output)
    mesh_dir = os.path.join(output_dir, "meshes")

    os.makedirs(mesh_dir, exist_ok=True)

    # Copy mesh and texture
    dae_filename = os.path.basename(dae_path)
    tex_filename = os.path.basename(texture_path)
    shutil.copy(dae_path, os.path.join(mesh_dir, dae_filename))
    shutil.copy(texture_path, os.path.join(mesh_dir, tex_filename))

    # Write model.sdf
    sdf_path = os.path.join(output_dir, "model.sdf")
    with open(sdf_path, "w") as f:
        f.write(make_sdf(model_name, dae_filename))

    # Write model.config
    config_path = os.path.join(output_dir, "model.config")
    with open(config_path, "w") as f:
        f.write(make_model_config(model_name))

    print(f"\n✅ Gazebo model created in: {output_dir}")
    print(f"├── model.config")
    print(f"├── model.sdf")
    print(f"└── meshes/")
    print(f"    ├── {dae_filename}")
    print(f"    └── {tex_filename}")

if __name__ == "__main__":
    main()
