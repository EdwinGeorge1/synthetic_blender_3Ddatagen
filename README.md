# 3D Synthetic Data Generation with Blender

A lightweight Blender pipeline to wrap arbitrary 2D images onto the **top face** of rectangular boxes and export them as COLLADA (`.dae`) models—ideal for creating synthetic datasets for computer vision, robotics, or AR/VR.

## Features

- **Automatic Aspect-Ratio Detection**  
- **Interactive Prompts** for X → auto-compute Y → then prompt for Z  
- **Consistent Naming Convention**  
  - Texture: `texture_<W>x<D>x<H>.<ext>`  
  - Model:   `box_<W>x<D>x<H>.dae`  
- **Headless Operation** via `--background` for batch processing

## Prerequisites

- Blender 4.2.1  
- Python 3.x (bundled with Blender)

## Installation & Setup

1. **Download Blender**  
   ```bash
   cd ~
   wget https://download.blender.org/release/Blender4.2/blender-4.2.1-linux-x64.tar.xz
   tar -xf blender-4.2.1-linux-x64.tar.xz
   ```  
2. **Make Executable**  
   ```bash
   chmod +x ~/blender-4.2.1-linux-x64/blender
   ```  
3. **Project Layout**  
   ```
   project-root/
   ├── wrap_image_box.py
   ├── images/
   └── output/
   ```

## Directory Structure

```
project-root/
├── wrap_image_box.py
├── images/
├── output/
│   └── <R>_<X>cmx<Y>cmx<Z>cm/
│       ├── texture_<WxDxH>.<ext>
│       └── box_<WxDxH>.dae
└── README.md
```

- `<R>` = aspect ratio (e.g., `4-3`)  
- `<X>cmx<Y>cmx<Z>cm` = chosen dimensions  
- `<WxDxH>` = dims in meters (dots → `p`)

## Usage

```bash
~/blender-4.2.1-linux-x64/blender   --background --python wrap_image_box.py --     --image ./images/1.png     --outdir ./output/4-3_100cmx75cmx25cm
```

1. Detects ratio:
   ```
   Detected image aspect ratio: 4:3
   ```
2. Prompt X:
   ```
   Enter desired length for the 4-part (in cm): 100
   → computed other side (Y): 75.00 cm
   ```
3. Prompt Z:
   ```
   Enter desired third dimension (height, Z axis) in cm: 25
   ```
4. Generates:
   ```
   Done.  Texture → ./output/4-3_100cmx75cmx25cm/texture_1p0x0p75x0p25.png
         Model   → ./output/4-3_100cmx75cmx25cm/box_1p0x0p75x0p25.dae
   ```

```bash
python3 generate_sdf_model.py   --dae box_0p08x0p2043x0p05.dae   --texture texture_0p08x0p2043x0p05.jpeg   --output /home/edwin/.gazebo/models/med_10
```

## Batch Generation

Loop over images & dimensions, compute folder names, and call the Blender command.

## Contributing

Pull requests welcome. Adjust UV margin or material settings as needed.

## License

MIT License. See [LICENSE](LICENSE).

---