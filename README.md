# 3D Synthetic Data Generation with Blender

A lightweight Blender pipeline to wrap arbitrary 2D images onto the **side face** of rectangular boxes and automatically generate a complete Gazebo model (SDF + textures).

## Features
- Automatic aspect‐ratio detection
- Interactive prompts for X/Z dimensions
- Consistent naming conventions
- One‐stop `main.py` to run Blender + SDF generator
- Headless/batch operation

## Prerequisites
- **Blender 4.2.1** (or newer)
- **Python 3.x**
- `wrap_image_box.py`, `generate_sdf_model.py`, and `main.py` all located in your project root

## Installation & Setup

1. **Download & extract Blender**  
   ```bash
   cd ~
   wget https://download.blender.org/release/Blender4.2/blender-4.2.1-linux-x64.tar.xz
   tar -xf blender-4.2.1-linux-x64.tar.xz
   ```

2. **Make Blender executable**  
   ```bash
   chmod +x ~/blender-4.2.1-linux-x64/blender
   ```

3. **(Optional) Add Blender to your PATH**  
   ```bash
   echo 'export BLENDER_PATH=~/blender-4.2.1-linux-x64/blender' >> ~/.bashrc
   source ~/.bashrc
   ```

4. **Clone or copy this repository**  
   ```bash
   git clone <your-repo-url> project-root
   cd project-root
   ```

5. **Make scripts executable**  
   ```bash
   chmod +x wrap_image_box.py generate_sdf_model.py main.py
   ```

## Directory Structure

```
project-root/
├── wrap_image_box.py
├── generate_sdf_model.py
├── main.py
├── images/
│   └── pics_crop/
├── output_tmp/        # Auto-created scratch directory
└── README.md
```

## Usage

From **project root**, run:

```bash
./main.py   --image ./images/pics_crop/<your-image>.jpeg   --output ~/.gazebo/models/<model_name>
```

- **Prompts** (unchanged from before):
  ```
  Enter box width (X) in cm:   # your desired width in cm
  Enter box height (Z) in cm:  # your desired height in cm
  ```
- **On completion**:
  ```
  ✅ All done! Gazebo model ready in:
      /home/you/.gazebo/models/<model_name>
  ```

## Batch Generation

Automate multiple images:

```bash
for img in images/pics_crop/*.{png,jpeg,jpg}; do
  base=$(basename "$img" | sed 's/\.[^.]*$//')
  ./main.py --image "$img" --output ~/.gazebo/models/"$base"
done
```

## Cleaning Up

To remove the temporary working directory:

```bash
rm -rf output_tmp/
```

## Contributing

Pull requests welcome! Feel free to adjust UV margins, material settings, or add new features.

## License

MIT License. See [LICENSE](LICENSE).