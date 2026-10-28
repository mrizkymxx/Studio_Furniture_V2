"""
Generator Master Studio Lifestyle 16:9 (D:\\Studio_Furniture_V2)
Menghasilkan 01_STUDIO/Studio_Lifestyle.blend secara headless.
Karakteristik:
- Ruangan matte off-white arsitektural (prosedural, 0 MB download)
- Cahaya netral PBR (RGB 1,1,1) menjaga warna kayu asli 100% akurat
- Bayangan kontak tajam & penumbra lembut
- 4 Kamera 16:9 (Hero, Straight-On, 2-Point Vertikal Lurus, Close-Up Detail)
- Khronos PBR Neutral -2.5 EV
"""

import bpy
import math
from pathlib import Path

def reset_scene():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    scene = bpy.context.scene
    scene.name = "Lifestyle Studio"
    return scene

def create_matte_offwhite_material():
    mat = bpy.data.materials.new(name="Lifestyle | Matte Off-White")
    mat.use_nodes = True
    nodes = mat.node_tree.nodes
    links = mat.node_tree.links
    nodes.clear()

    out_node = nodes.new(type="ShaderNodeOutputMaterial")
    out_node.location = (400, 0)

    bsdf = nodes.new(type="ShaderNodeBsdfPrincipled")
    bsdf.location = (100, 0)
    # Off-white matte: #EBE8E3 -> linear RGB ~ (0.81, 0.78, 0.74, 1.0)
    bsdf.inputs['Base Color'].default_value = (0.815, 0.788, 0.745, 1.0)
    bsdf.inputs['Roughness'].default_value = 0.88
    if 'Specular IOR Level' in bsdf.inputs:
        bsdf.inputs['Specular IOR Level'].default_value = 0.20
    elif 'Specular' in bsdf.inputs:
        bsdf.inputs['Specular'].default_value = 0.20

    # Subtle procedural micro-bump to prevent synthetic CGI plastic appearance
    noise = nodes.new(type="ShaderNodeTexNoise")
    noise.location = (-300, -100)
    noise.inputs['Scale'].default_value = 140.0
    noise.inputs['Detail'].default_value = 3.0
    noise.inputs['Roughness'].default_value = 0.5

    bump = nodes.new(type="ShaderNodeBump")
    bump.location = (-100, -100)
    bump.inputs['Strength'].default_value = 0.025
    bump.inputs['Distance'].default_value = 0.001

    links.new(noise.outputs['Fac'], bump.inputs['Height'])
    links.new(bump.outputs['Normal'], bsdf.inputs['Normal'])
    links.new(bsdf.outputs['BSDF'], out_node.inputs['Surface'])

    return mat

def build_room(mat):
    coll = bpy.data.collections.new("Lifestyle_Room")
    bpy.context.scene.collection.children.link(coll)

    # 1. Floor (Lantai) 24m x 24m at Z=0
    bpy.ops.mesh.primitive_plane_add(size=24.0, location=(0, 0, 0))
    floor = bpy.context.active_object
    floor.name = "Lifestyle / Lantai"
    floor.data.materials.append(mat)
    coll.objects.link(floor)
    bpy.context.scene.collection.objects.unlink(floor)

    # 2. Back Wall (Dinding Belakang) 24m x 8m at Y=6.0m
    bpy.ops.mesh.primitive_plane_add(size=24.0, location=(0, 6.0, 4.0))
    bwall = bpy.context.active_object
    bwall.name = "Lifestyle / Dinding belakang"
    bwall.rotation_euler = (math.radians(90), 0, 0)
    bwall.scale = (1.0, 0.333, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    bwall.data.materials.append(mat)
    coll.objects.link(bwall)
    bpy.context.scene.collection.objects.unlink(bwall)

    # 3. Left Wall (Dinding Kiri) 24m x 8m at X=-6.0m
    bpy.ops.mesh.primitive_plane_add(size=24.0, location=(-6.0, 0, 4.0))
    lwall = bpy.context.active_object
    lwall.name = "Lifestyle / Dinding kiri"
    lwall.rotation_euler = (0, math.radians(90), 0)
    lwall.scale = (0.333, 1.0, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    lwall.data.materials.append(mat)
    coll.objects.link(lwall)
    bpy.context.scene.collection.objects.unlink(lwall)

    # 4. Ceiling Bounce (Plafon GI bounce, invisible to camera) at Z=8.0m
    bpy.ops.mesh.primitive_plane_add(size=24.0, location=(0, 0, 8.0))
    ceiling = bpy.context.active_object
    ceiling.name = "Lifestyle / Plafon"
    ceiling.data.materials.append(mat)
    ceiling.visible_camera = False
    ceiling.visible_shadow = False
    coll.objects.link(ceiling)
    bpy.context.scene.collection.objects.unlink(ceiling)

    return coll

def setup_lights():
    coll = bpy.data.collections.new("Lifestyle_Lights")
    bpy.context.scene.collection.children.link(coll)

    # 1. Key Sun: Pure neutral 1,1,1 for true material fidelity, 6° angle for sharp contact + soft penumbra
    key_data = bpy.data.lights.new(name="Lifestyle_KeySun", type='SUN')
    key_data.energy = 22.0
    key_data.color = (1.0, 1.0, 1.0)
    key_data.angle = math.radians(6.0)

    key_obj = bpy.data.objects.new(name="Lifestyle / Key Sun", object_data=key_data)
    # Sun coming from front-left at ~45 deg
    key_obj.rotation_euler = (math.radians(45.0), math.radians(15.0), math.radians(-50.0))
    coll.objects.link(key_obj)

    # 2. Sky Fill: Pure neutral 1,1,1, high angle (80°) for ultra-soft shadow lift in deep cavities
    fill_data = bpy.data.lights.new(name="Lifestyle_SkyFill", type='SUN')
    fill_data.energy = 6.0
    fill_data.color = (1.0, 1.0, 1.0)
    fill_data.angle = math.radians(80.0)

    fill_obj = bpy.data.objects.new(name="Lifestyle / Sky Fill", object_data=fill_data)
    fill_obj.rotation_euler = (math.radians(60.0), math.radians(-20.0), math.radians(60.0))
    coll.objects.link(fill_obj)

    return coll

def setup_cameras():
    coll = bpy.data.collections.new("Lifestyle_Cameras")
    bpy.context.scene.collection.children.link(coll)

    # Standard 16:9 Camera specs
    cam_configs = [
        {
            "name": "CAM LIFESTYLE | HERO",
            "lens": 55.0,
            "fstop": 8.0,
            "loc": (1.45, -2.15, 0.78),
            "rot": (math.radians(76.0), 0, math.radians(34.0)),
            "shift_y": 0.05
        },
        {
            "name": "CAM LIFESTYLE | STRAIGHT",
            "lens": 50.0,
            "fstop": 11.0,
            "loc": (0.0, -2.50, 0.55),
            "rot": (math.radians(86.0), 0, 0),
            "shift_y": 0.08
        },
        {
            "name": "CAM LIFESTYLE | TWO_POINT",
            # True 2-Point Architectural Perspective: Pitch is exactly 90 deg vertical, Zero keystone distortion
            "lens": 50.0,
            "fstop": 8.0,
            "loc": (1.20, -2.20, 0.55),
            "rot": (math.radians(90.0), 0, math.radians(28.0)),
            "shift_y": 0.22  # Uses vertical lens shift to center product while keeping lines vertical
        },
        {
            "name": "CAM LIFESTYLE | CLOSEUP",
            "lens": 65.0,
            "fstop": 4.5,
            "loc": (0.75, -1.25, 0.65),
            "rot": (math.radians(72.0), 0, math.radians(31.0)),
            "shift_y": 0.02
        }
    ]

    cams = {}
    for cfg in cam_configs:
        cam_data = bpy.data.cameras.new(name=cfg["name"])
        cam_data.lens = cfg["lens"]
        cam_data.sensor_width = 36.0
        cam_data.sensor_height = 20.25  # 16:9
        cam_data.sensor_fit = 'AUTO'
        cam_data.shift_y = cfg["shift_y"]
        cam_data.dof.use_dof = True
        cam_data.dof.aperture_fstop = cfg["fstop"]

        cam_obj = bpy.data.objects.new(name=cfg["name"], object_data=cam_data)
        cam_obj.location = cfg["loc"]
        cam_obj.rotation_euler = cfg["rot"]
        coll.objects.link(cam_obj)
        cams[cfg["name"]] = cam_obj

    return cams

def setup_render_and_world(scene, hero_cam):
    # World setup: neutral clean ambient
    world = bpy.data.worlds.new("Lifestyle_World")
    world.use_nodes = True
    bg_node = world.node_tree.nodes.get("Background")
    if bg_node:
        bg_node.inputs['Color'].default_value = (0.5, 0.5, 0.5, 1.0)
        bg_node.inputs['Strength'].default_value = 0.15
    scene.world = world

    # Render settings: 16:9 1920x1080
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    scene.render.pixel_aspect_x = 1.0
    scene.render.pixel_aspect_y = 1.0
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGB'
    scene.render.image_settings.color_depth = '8'

    # Cycles & Color Management: Khronos PBR Neutral, -2.5 EV
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'GPU'
    scene.cycles.samples = 128
    scene.cycles.preview_samples = 32
    scene.cycles.use_denoising = True

    scene.view_settings.view_transform = 'Khronos PBR Neutral'
    scene.view_settings.exposure = -2.50
    scene.view_settings.look = 'None'

    # Default active camera
    scene.camera = hero_cam

    # Set default viewport shading to MATERIAL (Material Preview / EEVEE) so scanned PBR textures are immediately visible
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces.active.shading.type = 'MATERIAL'
                area.spaces.active.shading.use_scene_lights = True
                area.spaces.active.shading.use_scene_world = True

def main():
    root = Path(__file__).resolve().parents[1]
    out_dir = root / "01_STUDIO"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / "Studio_Lifestyle.blend"

    print("[1/5] Menginisialisasi scene kosong...")
    scene = reset_scene()

    print("[2/5] Membangun material & ruangan matte off-white...")
    mat = create_matte_offwhite_material()
    build_room(mat)

    print("[3/5] Mengatur pencahayaan netral PBR...")
    setup_lights()

    print("[4/5] Memasang 4 kamera 16:9 profesional...")
    cams = setup_cameras()
    hero_cam = cams["CAM LIFESTYLE | HERO"]

    print("[5/5] Konfigurasi render Cycles & Khronos PBR Neutral...")
    setup_render_and_world(scene, hero_cam)

    # Save file
    bpy.ops.wm.save_as_mainfile(filepath=str(out_file))
    print(f"BERHASIL: Master Studio Lifestyle tersimpan di: {out_file}")

if __name__ == "__main__":
    main()
