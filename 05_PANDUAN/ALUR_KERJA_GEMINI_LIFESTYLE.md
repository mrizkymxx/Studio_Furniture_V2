# SOP & Master Prompt AI: Alur Kerja Studio Lifestyle 16:9

Dokumen ini adalah panduan standar bagi tim untuk menghasilkan foto thumbnail produk yang **100% konsisten** di Gemini / NanoBanana tanpa pergeseran latar belakang (zero background drift) dan tanpa distorsi detail produk.

---

## 1. Mengapa Background Dulu Sering Berubah?
Sebelumnya, tim mengunggah foto produk dan meminta Gemini "menciptakan ruangan/latar belakang" melalui instruksi teks. Model difusi AI (Gemini/NanoBanana) akan selalu menghaluinasi ruangan baru setiap kali generate, mengubah sudut kamera, tinggi pandang, dan warna dinding/lantai.

**Kunci Solusi (Blender-First + Gemini Polish):**
1. Blender merender seluruh ruangan fisik (dinding matte off-white, lantai, pencahayaan matahari netral, dan contact shadow di bawah kaki produk) dalam rasio 16:9 yang sudah pas.
2. Gemini **HANYA** bertugas melakukan *surface micro-texture polish* (menaikkan kesan fotorealistik tekstur), bukan mengarang ruangan dari nol.

---

## 2. Alur Kerja Langkah-demi-Langkah

```
[Langkah 1: Blender Lokal]
Buka MULAI_STUDIO.cmd -> Klik 'Pilih File Produk (.blend)' -> Cek 4 Angle -> Klik 'Simpan & Pack untuk Webapp'
                             │
                             ▼ (File .blend di folder 03_PROYEK)
[Langkah 2: Webapp Server Render]
Upload file .blend ke Webapp Server -> Server render 4 sudut (1920x1080 16:9 PNG)
                             │
                             ▼ (Hasil PNG Render 16:9)
[Langkah 3: Gemini / NanoBanana]
Upload hasil render PNG ke Gemini -> Set Image-to-Image (Denoise 0.28 - 0.33) -> Masukkan Master Prompt
                             │
                             ▼
[Langkah 4: Hasil Akhir Konsisten]
Thumbnail fotorealistik dengan latar belakang, warna kayu, dan sudut pandang yang 100% konsisten antar produk!
```

---

## 3. Pengaturan Wajib di Gemini / NanoBanana

Saat memasukkan gambar render 16:9 dari server ke Gemini:
- **Mode Kerja**: Gunakan mode `Image-to-Image` / `Edit` / `Variations` (JANGAN Text-to-Image).
- **Rasio Aspek**: `16:9` (sama persis dengan render input).
- **Denoising Strength / Image Weight (SANGAT KRUSIAL)**:
  - Nilai optimal: **`0.28 - 0.33`** (atau Image Influence **`~70%`**).
  - *Catatan:* Jika nilai denoise > 0.40, Gemini akan mulai menghaluinasi prop/ruangan baru. Jika nilai < 0.20, peningkatan fotorealisme kurang terasa.

---

## 4. Master Prompt Template (Copy-Paste)

Gunakan template di bawah ini. Ganti `{NAMA_PRODUK}`, `{TIPE_FURNITUR}` (contoh: *nightstand*, *tallboy dresser*, *bed frame*), dan `{JENIS_KAYU}` (contoh: *natural oak*, *walnut*, *mindi*):

```text
[TASK: IMAGE-TO-IMAGE PHOTOREALISTIC SURFACE ENHANCEMENT ONLY]
Input: 3D render plate of {NAMA_PRODUK} ({TIPE_FURNITUR}) inside a clean matte off-white architectural space.

CORE DIRECTIVE:
Refine realistic surface micro-texture, micro-pores, and subtle optical depth. Maintain 100% strict spatial fidelity to the input render. Treat input image as a locked base plate.

MANDATORY PRESERVATIONS (DO NOT ALTER):
1. CAMERA & PERSPECTIVE: Preserve exact 16:9 framing, camera height, focal length, vanishing lines, and horizon. Do NOT re-frame, tilt, pan, crop, or rotate camera.
2. PRODUCT GEOMETRY & DETAILS: Preserve exact furniture shape, leg taper, drawer reveal gaps, edge bevels, joints, and hardware handle positions. No added, missing, or warped parts.
3. WOOD MATERIAL & COLOR: Preserve natural {JENIS_KAYU} wood tone, grain pattern, and color temperature. Do NOT oversaturate, stain, or change the wood color.
4. ENVIRONMENT & LIGHTING: Preserve the clean matte off-white wall, floor texture, wall-floor baseline seam, and natural contact shadows under the furniture legs.

ENHANCEMENT TARGETS (POLISH ONLY):
- Add subtle organic micro-sheen on the floor surface under the sunlight.
- Refine realistic tactile wood pore depth without altering grain flow.
- Add subtle 35mm optical lens realism and gentle shadow penumbra falloff.

STRICT NEGATIVE CONSTRAINTS:
NO extra furniture, NO rugs, NO plants, NO wall frames, NO decorative clutter, NO humans, NO cartoon/CGI plastic look, NO color shifting, NO camera distortion, NO watermark.
```

---

## 5. QC Checklist Hasil Akhir

Sebelum gambar final dirilis ke katalog/website, pastikan:
- [ ] **Garis Vertikal**: Garis dinding dan tepi furnitur lurus rapi (tidak melengkung atau miring).
- [ ] **Warna Kayu**: Warna kayu pada thumbnail cocok dengan swatch/sampel fisik produk asli.
- [ ] **Handle & Hardware**: Bentuk dan posisi tarikan laci/handle sama persis dengan model 3D CAD.
- [ ] **Latar Belakang**: Latar matte off-white bersih seragam di seluruh thumbnail katalog.
