"""
Addon UI Studio Lifestyle 16:9 (D:\\Studio_Furniture_V2)
Fitur Utama:
1. Muat Produk: Impor non-destruktif (tekstur asli 100% terjaga), pusatkan di Z=0.
2. Kamera Adaptif Pinhole Frustum: Framing presisi 16:9 untuk 4 angle profesional (Hero, Straight, 2-Point, Close-Up).
3. Otomatis Mode Tekstur: Mengaktifkan Material Preview agar serat kayu asli langsung terlihat jelas.
4. Simpan & Pack: Mengunci seluruh tekstur ke dalam .blend siap upload ke Webapp Server.
"""

import bpy
import os
import math
from pathlib import Path
from datetime import datetime
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty
from mathutils import Vector

bl_info = {
    "name": "Lifestyle Studio Tools V2",
    "author": "Tala Living",
    "version": (2, 3, 0),
    "blender": (5, 2, 0),
    "location": "View3D > Sidebar > Lifestyle Studio",
    "description": "Alat minimalis persiapan sesi render 16:9 untuk webapp server",
    "category": "3D View"
}

def get_product_bounds(objects):
    """Menghitung bounding box global yang akurat dari seluruh mesh produk."""
    dg = bpy.context.evaluated_depsgraph_get()
    pts = []
    for o in objects:
        if o.type == 'MESH' and not o.hide_render:
            eval_obj = o.evaluated_get(dg)
            pts.extend([eval_obj.matrix_world @ Vector(v) for v in eval_obj.bound_box])

    if not pts:
        return Vector((-0.25, -0.20, 0.0)), Vector((0.25, 0.20, 0.55))

    lo = Vector([min(p[i] for p in pts) for i in range(3)])
    hi = Vector([max(p[i] for p in pts) for i in range(3)])
    return lo, hi

def frame_cameras_to_bounds(lo, hi, scene):
    """Menghitung jarak & sudut 4 kamera 16:9 adaptif berdasarkan frustum pinhole."""
    size = hi - lo
    ctr = (lo + hi) / 2.0
    asp = scene.render.resolution_x / scene.render.resolution_y

    # 1. Posisikan dinding ruangan adaptif agar tidak menabrak produk besar
    max_span = max(size.x, size.y)
    gap = 0.95 + 0.35 * max_span
    bwall = bpy.data.objects.get("Lifestyle / Dinding belakang")
    if bwall:
        bwall.location.y = hi.y + gap
    lwall = bpy.data.objects.get("Lifestyle / Dinding kiri")
    if lwall:
        lwall.location.x = lo.x - gap * 1.5

    corners = [Vector((x, y, z)) for x in (lo.x, hi.x) for y in (lo.y, hi.y) for z in (lo.z, hi.z)]

    # 1. HERO (3/4 depan kanan, eye level duduk ~0.75m)
    cam_hero = bpy.data.objects.get("CAM LIFESTYLE | HERO")
    if cam_hero:
        cd = cam_hero.data
        cd.lens = 55.0
        cd.sensor_width = 36.0
        cd.sensor_fit = 'AUTO'
        tx = cd.sensor_width / (2.0 * cd.lens); ty = tx / asp
        tgt = Vector((ctr.x, ctr.y, lo.z + size.z * 0.45))
        d = Vector((0.65, -1.0, 0.38)).normalized()
        cam_hero.location = tgt + d
        cam_hero.rotation_euler = (tgt - cam_hero.location).to_track_quat('-Z', 'Y').to_euler()
        inv = cam_hero.rotation_euler.to_matrix().transposed()
        dist = 0.05
        for c in corners:
            p = inv @ (c - tgt)
            dist = max(dist, p.z + abs(p.x) / tx * 1.18, p.z + abs(p.y) / ty * 1.18)
        cam_hero.location = tgt + d * dist
        cam_hero.rotation_euler = (tgt - cam_hero.location).to_track_quat('-Z', 'Y').to_euler()
        cd.shift_x = 0.0
        cd.shift_y = 0.0
        cd.dof.use_dof = True
        cd.dof.focus_distance = dist
        cd.dof.aperture_fstop = 8.0

    # 2. STRAIGHT (Tampak depan lurus sejajar tengah)
    cam_str = bpy.data.objects.get("CAM LIFESTYLE | STRAIGHT")
    if cam_str:
        cd = cam_str.data
        cd.lens = 50.0
        cd.sensor_width = 36.0
        cd.sensor_fit = 'AUTO'
        tx = cd.sensor_width / (2.0 * cd.lens); ty = tx / asp
        tgt = Vector((ctr.x, ctr.y, lo.z + size.z * 0.50))
        d = Vector((0.0, -1.0, 0.08)).normalized()
        cam_str.location = tgt + d
        cam_str.rotation_euler = (tgt - cam_str.location).to_track_quat('-Z', 'Y').to_euler()
        inv = cam_str.rotation_euler.to_matrix().transposed()
        dist = 0.05
        for c in corners:
            p = inv @ (c - tgt)
            dist = max(dist, p.z + abs(p.x) / tx * 1.25, p.z + abs(p.y) / ty * 1.25)
        cam_str.location = tgt + d * dist
        cam_str.rotation_euler = (tgt - cam_str.location).to_track_quat('-Z', 'Y').to_euler()
        cd.shift_x = 0.0
        cd.shift_y = -0.02
        cd.dof.use_dof = True
        cd.dof.focus_distance = dist
        cd.dof.aperture_fstop = 11.0

    # 3. TWO_POINT (Perspektif arsitektural vertikal 100% tegak lurus)
    cam_tp = bpy.data.objects.get("CAM LIFESTYLE | TWO_POINT")
    if cam_tp:
        cd = cam_tp.data
        cd.lens = 50.0
        cd.sensor_width = 36.0
        cd.sensor_fit = 'AUTO'
        tx = cd.sensor_width / (2.0 * cd.lens); ty = tx / asp
        tgt = Vector((ctr.x, ctr.y, lo.z + size.z * 0.50))
        d = Vector((0.60, -1.0, 0.0)).normalized() # Pitch strictly horizontal
        cam_z = max(lo.z + size.z * 0.70, 0.70)
        dist = 0.05
        for c in corners:
            dist = max(dist, abs(c.x - tgt.x) / tx * 1.20, abs(c.y - tgt.y) / ty * 1.20)
        dist = max(dist * 1.35, 2.0)
        cam_tp.location = Vector((tgt.x + d.x * dist, tgt.y + d.y * dist, cam_z))
        horiz_dir = Vector((tgt.x - cam_tp.location.x, tgt.y - cam_tp.location.y, 0.0))
        cam_tp.rotation_euler = horiz_dir.to_track_quat('-Z', 'Y').to_euler()
        cd.shift_x = 0.0
        cd.shift_y = -0.20
        cd.dof.use_dof = True
        cd.dof.focus_distance = dist
        cd.dof.aperture_fstop = 8.0

    # 4. CLOSEUP (Macro detail menyorot handle, sambungan & serat kayu)
    cam_cu = bpy.data.objects.get("CAM LIFESTYLE | CLOSEUP")
    if cam_cu:
        cd = cam_cu.data
        cd.lens = 85.0
        cd.sensor_width = 36.0
        cd.sensor_fit = 'AUTO'
        tgt = Vector((ctr.x, lo.y, lo.z + size.z * 0.65))
        d = Vector((0.45, -1.0, 0.25)).normalized()
        dist = max(1.25, max_span * 1.35)
        cam_cu.location = tgt + d * dist
        cam_cu.rotation_euler = (tgt - cam_cu.location).to_track_quat('-Z', 'Y').to_euler()
        cd.shift_x = 0.0
        cd.shift_y = 0.0
        cd.dof.use_dof = True
        cd.dof.focus_distance = dist
        cd.dof.aperture_fstop = 3.5

    bpy.context.view_layer.update()

def set_viewport_shading(shading_type='MATERIAL'):
    """Mengatur shading viewport 3D ke Material Preview atau Rendered."""
    for screen in bpy.data.screens:
        for area in screen.areas:
            if area.type == 'VIEW_3D':
                space = area.spaces.active
                space.shading.type = shading_type
                if shading_type == 'MATERIAL':
                    space.shading.use_scene_lights = True
                    space.shading.use_scene_world = True
                elif shading_type == 'SOLID':
                    space.shading.color_type = 'TEXTURE'
                area.tag_redraw()

class LIFESTYLE_OT_SetShading(bpy.types.Operator):
    """Ubah mode tampilan viewport 3D"""
    bl_idname = "lifestyle.set_shading"
    bl_label = "Ubah Tampilan Shading"
    bl_options = {'REGISTER'}

    shading_type: StringProperty(default="MATERIAL")

    def execute(self, context):
        set_viewport_shading(self.shading_type)
        return {'FINISHED'}

class LIFESTYLE_OT_LoadProduct(bpy.types.Operator, ImportHelper):
    """Pilih dan muat file produk (.blend) ke dalam studio"""
    bl_idname = "lifestyle.load_product"
    bl_label = "Pilih File Produk (.blend)"
    bl_options = {'REGISTER', 'UNDO'}

    filter_glob: StringProperty(default="*.blend", options={'HIDDEN'})

    def execute(self, context):
        filepath = self.filepath
        if not os.path.exists(filepath):
            self.report({'ERROR'}, "File tidak ditemukan.")
            return {'CANCELLED'}

        prod_name = Path(filepath).stem

        # 1. Bersihkan koleksi produk lama jika ada
        old_coll = bpy.data.collections.get("PRODUK")
        if old_coll:
            for obj in list(old_coll.all_objects):
                bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.collections.remove(old_coll)

        new_coll = bpy.data.collections.new("PRODUK")
        context.scene.collection.children.link(new_coll)

        # 2. Append objek dari file produk .blend (link=False membawa datablock material & image asli)
        imported_objects = []
        with bpy.data.libraries.load(filepath, link=False) as (data_from, data_to):
            data_to.objects = [name for name in data_from.objects]

        for obj in data_to.objects:
            if obj:
                if obj.type in {'LIGHT', 'CAMERA'}:
                    continue
                new_coll.objects.link(obj)
                imported_objects.append(obj)

        if not imported_objects:
            self.report({'WARNING'}, "Tidak ada objek 3D yang berhasil dimuat.")
            return {'CANCELLED'}

        context.view_layer.update()

        # 3. Hitung bounding box awal
        lo, hi = get_product_bounds(imported_objects)

        # 4. Pusatkan secara horizontal di (0,0) dan tempatkan dasar produk tepat di Z=0
        tops = [o for o in new_coll.objects if o.parent is None]
        off = Vector((-(lo.x + hi.x) / 2.0, -(lo.y + hi.y) / 2.0, -lo.z))
        for o in tops:
            o.location += off

        context.view_layer.update()

        # 5. Hitung bounding box akhir yang sudah terpusat
        new_lo, new_hi = get_product_bounds(imported_objects)

        # 6. Adaptif sesuaikan ke-4 kamera 16:9 dan posisi dinding
        frame_cameras_to_bounds(new_lo, new_hi, context.scene)

        # 7. Set viewport ke kamera Hero dan aktifkan Material Preview agar tekstur asli langsung terlihat
        context.scene.camera = bpy.data.objects.get("CAM LIFESTYLE | HERO")
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces.active.region_3d.view_perspective = 'CAMERA'

        set_viewport_shading('MATERIAL')

        context.scene["lifestyle_loaded_product"] = prod_name
        self.report({'INFO'}, f"Produk '{prod_name}' berhasil dimuat, dipusatkan, dan diframing.")
        return {'FINISHED'}

class LIFESTYLE_OT_SetAngle(bpy.types.Operator):
    """Pilih sudut kamera 16:9 untuk pratinjau"""
    bl_idname = "lifestyle.set_angle"
    bl_label = "Pilih Sudut Kamera"
    bl_options = {'REGISTER'}

    camera_name: StringProperty(name="Camera Name")

    def execute(self, context):
        cam = bpy.data.objects.get(self.camera_name)
        if not cam:
            self.report({'ERROR'}, f"Kamera {self.camera_name} tidak ditemukan.")
            return {'CANCELLED'}

        context.scene.camera = cam

        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces.active.region_3d.view_perspective = 'CAMERA'

        return {'FINISHED'}

class LIFESTYLE_OT_PackAndSave(bpy.types.Operator):
    """Pack seluruh tekstur dan simpan sesi .blend siap upload ke Webapp Server"""
    bl_idname = "lifestyle.pack_and_save"
    bl_label = "Simpan & Pack Sesi untuk Webapp"
    bl_options = {'REGISTER'}

    def execute(self, context):
        prod_name = context.scene.get("lifestyle_loaded_product", "Produk")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"Sesi_Webapp_{prod_name}_{timestamp}.blend"

        studio_root = Path(bpy.data.filepath).parents[1] if bpy.data.filepath else Path("D:/Studio_Furniture_V2")
        proyek_dir = studio_root / "03_PROYEK"
        proyek_dir.mkdir(parents=True, exist_ok=True)
        save_path = proyek_dir / filename

        try:
            bpy.ops.file.pack_all()
        except Exception as e:
            print("Pack warning:", e)

        bpy.ops.wm.save_as_mainfile(filepath=str(save_path), copy=True)

        try:
            os.startfile(str(proyek_dir))
        except Exception:
            pass

        msg = f"Sesi berhasil di-pack & disimpan:\n{filename}\n\nFile siap di-upload ke Webapp Server!"
        self.report({'INFO'}, msg)
        return {'FINISHED'}

class LIFESTYLE_PT_Panel(bpy.types.Panel):
    """Panel N di Viewport 3D untuk Studio Lifestyle"""
    bl_label = "Lifestyle Studio 16:9"
    bl_idname = "LIFESTYLE_PT_Panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'Lifestyle Studio'

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # Status Box
        box = layout.box()
        prod = scene.get("lifestyle_loaded_product", "Belum ada produk")
        box.label(text=f"Produk: {prod}", icon='OBJECT_DATA')

        # Mode Tampilan Tekstur Viewport
        layout.label(text="Tampilan Viewport:", icon='SHADING_TEXTURE')
        row = layout.row(align=True)
        btn1 = row.operator("lifestyle.set_shading", text="Tekstur Asli", icon='MATERIAL')
        btn1.shading_type = 'MATERIAL'
        btn2 = row.operator("lifestyle.set_shading", text="Cycles", icon='RENDER_RESULT')
        btn2.shading_type = 'RENDERED'
        btn3 = row.operator("lifestyle.set_shading", text="Clay", icon='SHADING_SOLID')
        btn3.shading_type = 'SOLID'

        # Langkah 1: Muat Produk
        layout.separator()
        layout.label(text="1. Impor & Posisikan Produk:", icon='IMPORT')
        row = layout.row(align=True)
        row.scale_y = 1.4
        row.operator("lifestyle.load_product", text="Pilih File Produk (.blend)", icon='FILE_FOLDER')

        # Langkah 2: Pilihan Angle Kamera
        layout.separator()
        layout.label(text="2. Cek Sudut Kamera 16:9:", icon='CAMERA_DATA')
        col = layout.column(align=True)

        angles = [
            ("CAM LIFESTYLE | HERO", "1. Hero 3/4 (Eye-Level)", 'CAMERA_DATA'),
            ("CAM LIFESTYLE | STRAIGHT", "2. Tampak Depan", 'ORIENTATION_VIEW'),
            ("CAM LIFESTYLE | TWO_POINT", "3. 2-Point Vertikal Lurus", 'VIEW_PERSPECTIVE'),
            ("CAM LIFESTYLE | CLOSEUP", "4. Close-Up Detail", 'ZOOM_SELECTED'),
        ]

        for cam_id, label, icon in angles:
            btn = col.operator("lifestyle.set_angle", text=label, icon=icon)
            btn.camera_name = cam_id

        # Langkah 3: Simpan untuk Webapp Server
        layout.separator()
        layout.label(text="3. Siapkan untuk Server Render:", icon='EXPORT')
        row = layout.row(align=True)
        row.scale_y = 1.5
        row.operator("lifestyle.pack_and_save", text="Simpan & Pack untuk Webapp", icon='PACKAGE')

classes = (
    LIFESTYLE_OT_SetShading,
    LIFESTYLE_OT_LoadProduct,
    LIFESTYLE_OT_SetAngle,
    LIFESTYLE_OT_PackAndSave,
    LIFESTYLE_PT_Panel,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
