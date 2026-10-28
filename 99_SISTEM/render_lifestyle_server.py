"""
Headless Batch Renderer Studio Lifestyle (D:\\Studio_Furniture_V2)
Digunakan oleh server render atau script batch lokal.
Menerima file .blend dan merender ke-4 angle 16:9 (1920x1080) secara otomatis.

Penggunaan:
  blender -b 01_STUDIO/Studio_Lifestyle.blend --python 99_SISTEM/render_lifestyle_server.py -- <file_sesi_atau_produk.blend> [--samples 128] [--uji]
"""

import bpy
import sys
import os
from pathlib import Path
from mathutils import Vector

# Import fungsi framing dari lifestyle_ui
sys.path.append(str(Path(__file__).parent))
from lifestyle_ui import get_product_bounds, frame_cameras_to_bounds

def parse_args():
    argv = sys.argv
    if "--" not in argv:
        return None, 128, False
    args = argv[argv.index("--") + 1:]
    if not args:
        return None, 128, False
    blend_path = args[0]
    samples = 128
    is_uji = "--uji" in args

    if "--samples" in args:
        idx = args.index("--samples")
        if idx + 1 < len(args):
            samples = int(args[idx + 1])

    if is_uji:
        samples = 32

    return blend_path, samples, is_uji

def main():
    blend_path, samples, is_uji = parse_args()
    if not blend_path or not os.path.exists(blend_path):
        print("ERROR: File .blend tidak ditemukan atau tidak disertakan.")
        sys.exit(1)

    root = Path(__file__).resolve().parents[1]
    prod_name = Path(blend_path).stem.replace("Sesi_Webapp_", "")
    out_dir = root / "04_HASIL_RENDER" / prod_name
    out_dir.mkdir(parents=True, exist_ok=True)

    scene = bpy.context.scene
    scene.render.resolution_x = 960 if is_uji else 1920
    scene.render.resolution_y = 540 if is_uji else 1080
    scene.cycles.samples = samples
    scene.cycles.use_denoising = True

    # Periksa apakah file yang dimasukkan sudah merupakan sesi (sudah ada PRODUK) atau file produk mentah
    has_product = "PRODUK" in bpy.data.collections
    if not has_product:
        new_coll = bpy.data.collections.new("PRODUK")
        scene.collection.children.link(new_coll)
        with bpy.data.libraries.load(blend_path, link=False) as (data_from, data_to):
            data_to.objects = [name for name in data_from.objects]
        imported_objects = []
        for obj in data_to.objects:
            if obj and obj.type not in {'LIGHT', 'CAMERA'}:
                new_coll.objects.link(obj)
                imported_objects.append(obj)

        bpy.context.view_layer.update()
        lo, hi = get_product_bounds(imported_objects)
        tops = [o for o in new_coll.objects if o.parent is None]
        off = Vector((-(lo.x + hi.x) / 2.0, -(lo.y + hi.y) / 2.0, -lo.z))
        for o in tops:
            o.location += off
        bpy.context.view_layer.update()
        new_lo, new_hi = get_product_bounds(imported_objects)
        frame_cameras_to_bounds(new_lo, new_hi, scene)
    else:
        # Sudah ada PRODUK di dalam sesi yang di-pack
        prod_coll = bpy.data.collections["PRODUK"]
        lo, hi = get_product_bounds(list(prod_coll.all_objects))
        frame_cameras_to_bounds(lo, hi, scene)

    # 4 Angle Kamera
    angles = [
        ("CAM LIFESTYLE | HERO", "HERO"),
        ("CAM LIFESTYLE | STRAIGHT", "STRAIGHT"),
        ("CAM LIFESTYLE | TWO_POINT", "TWO_POINT"),
        ("CAM LIFESTYLE | CLOSEUP", "CLOSEUP"),
    ]

    print(f"\n==================================================")
    print(f"Memulai Render Lifestyle: {prod_name}")
    print(f"Resolusi: {scene.render.resolution_x}x{scene.render.resolution_y} (16:9), Samples: {samples}")
    print(f"Output folder: {out_dir}")
    print(f"==================================================\n")

    for cam_name, suffix in angles:
        cam = bpy.data.objects.get(cam_name)
        if not cam:
            print(f"Peringatan: Kamera {cam_name} tidak ditemukan, lewati.")
            continue

        scene.camera = cam
        out_file = out_dir / f"{prod_name}_{suffix}.png"
        scene.render.filepath = str(out_file)

        print(f"Rendering [{suffix}] -> {out_file.name} ...")
        bpy.ops.render.render(write_still=True)
        print(f"Selesai [{suffix}]")

    print(f"\nSEMUA RENDER SELESAI: {out_dir}\n")

if __name__ == "__main__":
    main()
