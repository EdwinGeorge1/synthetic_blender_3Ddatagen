# 3D Synthetic Data Generation

A lightweight Blender pipeline to wrap arbitrary 2D images onto the **top face** of rectangular boxes and export them as COLLADA (`.dae`) models—ideal for creating synthetic datasets for computer vision, robotics or AR/VR.

---

## 📋 Features

- **Automatic aspect-ratio detection** of your source image.  
- **Interactive prompts** to specify one dimension (X) in cm, auto-computes the second (Y) to preserve ratio, then prompts for height (Z).  
- **Consistent naming convention** for textures and models:  
  - Texture: `texture_<W>x<D>x<H>.<ext>`  
  - Model:   `box_<W>x<D>x<H>.dae`  
- **Runs headless** in Blender (`--background`) for easy batch scripting.

---

## 🚀 Prerequisites

- **Blender 4.2.1** (Linux x64)  
- **Python 3.x** (bundled with Blender)  
- The `wrap_image_box.py` script (this repo)

---

## 🛠️ Installation & Blender Setup

1. **Download & extract Blender**  
   ```bash
   cd ~
   wget https://download.blender.org/release/Blender4.2/blender-4.2.1-linux-x64.tar.xz
   tar -xf blender-4.2.1-linux-x64.tar.xz
````

2. **Make the binary executable** (if needed)

   ```bash
   chmod +x ~/blender-4.2.1-linux-x64/blender
   ```

3. **Place `wrap_image_box.py`** in your project folder, e.g.:

   ```
   project-root/
   ├── wrap_image_box.py
   ├── images/
   └── output/
   ```

---

## 📂 Directory Structure

```
project-root/
├── wrap_image_box.py
├── images/                    # your source .png/.jpg files
├── output/                    # root for all generated samples
│   └── <R>_<X>cmx<Y>cmx<Z>cm/
│       ├── texture_<WxDxH>.<ext>
│       └── box_<WxDxH>.dae
└── README.md
```

* **`<R>`** = detected aspect ratio, e.g. `4-3` (for 4:3)
* **`<X>cmx<Y>cmx<Z>cm`** = real-world dimensions you choose
* **`<WxDxH>`** = same dims in meters with “p” instead of “.” (e.g. `1p0x0p75x0p25`)

---

## ▶️ Usage

Run from your project root:

```bash
~/blender-4.2.1-linux-x64/blender \
  --background --python wrap_image_box.py -- \
    --image ./images/1.png \
    --outdir ./output/4-3_100cmx75cmx25cm
```

1. **Aspect detection**

   ```
   Detected image aspect ratio: 4:3
   ```
2. **Prompt 1 (X):**

   ```
   Enter desired length for the 4-part (in cm): 100
   → computed other side (Y): 75.00 cm
   ```
3. **Prompt 2 (Z):**

   ```
   Enter desired third dimension (height, Z axis) in cm: 25
   ```
4. **Output**

   ```
   Done.  Texture → ./output/4-3_100cmx75cmx25cm/texture_1p0x0p75x0p25.png
         Model   → ./output/4-3_100cmx75cmx25cm/box_1p0x0p75x0p25.dae
   ```

---

## 🧩 Batch Generation

To generate dozens or hundreds of samples:

1. Write a simple shell or Python loop over your images & desired X/Z values.
2. In each iteration compute your `<R>` and `<X>cmx<Y>cmx<Z>cm` folder name.
3. Call the same Blender command above.

---

## 📝 Contributing

* Feel free to tweak the UV-unwrap margin or material settings in `wrap_image_box.py`.
* Pull requests welcome for new features (e.g. side-face support, network-driven batch configs).

---

## 📄 License

This project is released under the **MIT License**. See [LICENSE](LICENSE) for details.

---