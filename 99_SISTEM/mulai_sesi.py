"""
Script Startup Sesi Studio Lifestyle (D:\\Studio_Furniture_V2)
Dijalankan otomatis oleh buka_studio.ps1 saat Blender terbuka.
"""

import bpy
import sys
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ui_script = ROOT / "99_SISTEM" / "lifestyle_ui.py"

# Muat dan daftarkan addon UI
spec = importlib.util.spec_from_file_location("lifestyle_ui", str(ui_script))
mod = importlib.util.module_from_spec(spec)
sys.modules["lifestyle_ui"] = mod
spec.loader.exec_module(mod)
mod.register()

# Konfigurasi viewport agar langsung menampilkan sudut kamera & Material Preview
for window in bpy.context.window_manager.windows:
    for area in window.screen.areas:
        if area.type == 'VIEW_3D':
            area.spaces.active.show_region_ui = True
            area.spaces.active.region_3d.view_perspective = 'CAMERA'
            area.spaces.active.shading.type = 'MATERIAL'
            area.spaces.active.shading.use_scene_lights = True
            area.spaces.active.shading.use_scene_world = True

def activate_lifestyle_panel():
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.spaces.active.shading.type = 'MATERIAL'
                area.spaces.active.shading.use_scene_lights = True
                area.spaces.active.shading.use_scene_world = True
                for region in area.regions:
                    if region.type == 'UI':
                        try:
                            region.active_panel_category = 'Lifestyle Studio'
                        except Exception:
                            pass
    return None

bpy.app.timers.register(activate_lifestyle_panel, first_interval=0.5)
print("STUDIO_LIFESTYLE_V2_READY")
