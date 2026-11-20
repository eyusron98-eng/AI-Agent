# Tim AI Agent — Ekosistem Koperasi, Sabun, Dapur, Riset & Konten Kreator

Repositori ini berisi rancangan sistem **Tim AI Agent tanpa coding** untuk mengelola operasional usaha, riset, dan produksi konten dalam satu kendali lewat **WhatsApp**.

## 1. Gambaran Besar Ekosistem

Di atas semua tim terdapat **Manajer AI** yang menerima perintah pemilik dan memantau **3 tim utama**:

1. **Tim Usaha** — mencakup 3 unit:
   - **Koperasi:** pesanan & stok bahan dapur, pembelian/supplier, keuangan & anggota
   - **Sabun (rintisan):** formulasi & jadwal curing, legalitas & label, penjualan & marketplace
   - **Dapur:** menu & HPP, inventaris belanja (terhubung ke koperasi), keamanan pangan
2. **Tim Peneliti** — pencari literatur, analis data, penulis ilmiah, pemantau hibah/event (sekaligus mendukung R&D formulasi sabun).
3. **Tim Konten Kreator *(Prioritas Pertama)*** — menangani 4 pilar konten (**Koperasi**, **Sabun**, **Dapur**, **Riset**) dengan 5 peran spesialis:
   - Spesialis Riset & Ide
   - Spesialis Strategi & Copywriting
   - Spesialis Desain Visual
   - Spesialis Video Maker (**Full-Otomatis Video Motion 9:16**)
   - Admin Jadwal & Analis

## 2. Keputusan Arsitektur & Tech Stack (Tanpa Coding)

- **Antarmuka Chat:** **WhatsApp via Fonnte**
  - **Skema A (2 Nomor):** Nomor kedua dipasangkan ke Fonnte khusus sebagai nomor Manajer AI.
  - **Skema B (1 Nomor Eksisting):** Memakai nomor WA yang sudah aktif di Fonnte dengan filter di n8n (hanya membalas pesan dari nomor terizinkan yang diawali `/ai`).
- **Otak Otomasi:** **n8n**
- **Database Bersama:** **Google Sheets** (`Database_Tim_Konten`) dengan 4 tab:
  1. `Kalender_Konten`
  2. `Bank_Riset_Ide`
  3. `Katalog_Produk_&_Fakta` *(termasuk kolom `Klaim_Terlarang` untuk kepatuhan BPOM/PIRT)*
  4. `Performa_Konten`
- **Video Maker:** **Full-Otomatis Video Motion (9:16 Reels/TikTok/WA Status)** memakai **JSON2Video** (atau **Creatomate**) untuk merender scene, animasi teks, voiceover, dan subtitle otomatis menjadi `.mp4` lalu dikirim ke WhatsApp via Fonnte untuk persetujuan (`ACC <ID>`).

## 3. Database Google Sheets yang Sudah Aktif

- **Nama File:** `Database_Tim_Konten`
- **Tautan:** [Buka Google Sheets Database_Tim_Konten](https://docs.google.com/spreadsheets/d/1-6ra-cPS3nDlSfbxpmO-jjJkBEhcjr6rbI1VCGLInN4/edit)
- **Spreadsheet ID:** `1-6ra-cPS3nDlSfbxpmO-jjJkBEhcjr6rbI1VCGLInN4`

*(Ganti baris contoh di tab `Katalog_Produk_&_Fakta` dengan data produk, harga, dan batasan klaim aslimu sebelum workflow dijalankan.)*

## 4. Daftar File di Repositori

| File | Fungsi |
|---|---|
| [`blueprint_tim_ai_agent.md`](./blueprint_tim_ai_agent.md) | Blueprint menyeluruh Manajer AI dan 3 tim besar (Usaha, Peneliti, Konten), pilihan platform, tahapan, dan aturan keamanan. |
| [`desain_tim_konten_kreator.md`](./desain_tim_konten_kreator.md) | Desain utuh Tim Konten Kreator: arsitektur, skema 1 vs 2 nomor Fonnte, peran 5 spesialis, struktur 4 tab Sheets, kamus perintah WA, dan 3 system prompt siap salin. |
| [`n8n_tim_konten_fonnte_motion.json`](./n8n_tim_konten_fonnte_motion.json) | Template workflow **n8n 100% Gratis di VPS** dengan **Google Gemini (`gemini-2.5-flash`)**, **Fonnte Skema A (2 Nomor)**, 6 tool Google Sheets (`$fromAI`), dan **Mesin Render Video Motion Lokal (`http://motion-renderer:8000/render`)**. |
| [`panduan_setup_vps_biznet_gratis.md`](./panduan_setup_vps_biznet_gratis.md) | **Panduan Utama (100% Gratis):** Instalasi 1 perintah di **VPS Biznet (Ubuntu 26)** lengkap dengan n8n Self-Host, Mesin Video Motion 9:16 + TTS Bahasa Indonesia gratis, SSL/HTTPS otomatis (`sslip.io`), dan Google Service Account. |
| [`vps/`](./vps) | Paket Docker Compose (`n8n` + `motion-renderer` FastAPI/FFmpeg/edge-tts + `Caddy` HTTPS otomatis) dan script [`vps/install.sh`](./vps/install.sh). |
| [`data/sheets_batch_template.json`](./data/sheets_batch_template.json) | Struktur JSON kolom dan contoh data awal untuk 4 tab Google Sheets. |

## 5. Cara Install 100% Gratis di VPS Biznet (Ubuntu 26)

Jalankan 1 baris perintah ini di terminal SSH VPS Ubuntu kamu:

```bash
git clone https://github.com/eyusron98-eng/AI-Agent.git ~/AI-Agent && cd ~/AI-Agent/vps && sudo bash install.sh
```

Ikuti panduan lengkap langkah demi langkah di [`panduan_setup_vps_biznet_gratis.md`](./panduan_setup_vps_biznet_gratis.md).
