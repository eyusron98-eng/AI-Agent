# Panduan Setup 100% GRATIS di VPS Biznet (Ubuntu 26 + n8n Self-Host + Mesin Video Motion Lokal + Gemini + Fonnte)

Dengan memasang sistem ini di **VPS Biznet Ubuntu** milikmu, kamu mendapatkan:
1. **n8n Self-Host (Community Edition):** **Rp 0 / Gratis selamanya** tanpa batas workflow & eksekusi.
2. **Mesin Render Video Motion 9:16 (`motion-renderer`):** **Rp 0 / Gratis selamanya** di dalam VPS-mu sendiri (memakai `FFmpeg` + `Pillow` + Voiceover Bahasa Indonesia `id-ID-GadisNeural` dari `edge-tts`), **tanpa perlu bayar JSON2Video**.
3. **Otak AI Google Gemini (`gemini-2.5-flash`):** **Rp 0 / Gratis** memakai kuota Free Tier dari Google AI Studio.
4. **SSL / HTTPS Otomatis (`Caddy` + `sslip.io`):** **Rp 0 / Gratis**, bahkan jika kamu belum punya domain sendiri!

---

## Langkah 1: Pastikan Firewall / Security Group di Portal Biznet Terbuka (1 Menit)

Di panel **Biznet Gio / NEO Cloud**:
1. Buka menu **Security Group / Firewall** untuk VPS Ubuntu kamu.
2. Pastikan **Inbound Rules** mengizinkan trafik masuk untuk port:
   - **TCP `22`** (SSH)
   - **TCP `80`** (HTTP untuk verifikasi sertifikat SSL gratis)
   - **TCP `443`** (HTTPS untuk Dashboard n8n, Webhook Fonnte, & link download video `.mp4`)
   - **TCP `5678`** *(opsional, akses cadangan langsung via IP)*

---

## Langkah 2: Install Otomatis di VPS Biznet (Cukup Copy-Paste 1 Perintah)

Masuk (SSH) ke VPS Ubuntu 26 kamu, lalu jalankan perintah berikut:

```bash
git clone https://github.com/eyusron98-eng/AI-Agent.git ~/AI-Agent && cd ~/AI-Agent/vps && sudo bash install.sh
```

*(Jika folder `~/AI-Agent` sudah ada sebelumnya, jalankan: `cd ~/AI-Agent && git pull && cd vps && sudo bash install.sh`)*

### Apa yang dilakukan `install.sh` secara otomatis?
1. Memasang **Docker** dan **Docker Compose** jika belum ada di Ubuntu 26.
2. Mendeteksi IP Publik VPS Biznet kamu (misal `103.x.x.x`), lalu menanyakan domain:
   - Jika kamu **belum punya domain**, cukup **tekan `ENTER`** → script otomatis membuat alamat HTTPS gratis `https://103-x-x-x.sslip.io`.
   - Jika kamu **punya subdomain** (misal `n8n.domainmu.com` yang A record-nya sudah diarahkan ke IP VPS), ketik subdomain tersebut lalu tekan `ENTER`.
3. Membangun dan menyalakan 3 layanan sekaligus:
   - **`n8n`** (Otak otomasi & AI Agent)
   - **`motion-renderer`** (Mesin pembuat video `.mp4` 9:16 + suara Bahasa Indonesia)
   - **`caddy`** (Pengatur HTTPS otomatis & penyedia link `/videos/*.mp4`)

Setelah instalasi selesai (~1–3 menit), buka URL `https://<IP-ANDA>.sslip.io` yang muncul di layar terminal dan buat akun Admin n8n lokalmu.

---

## Langkah 3: Import Workflow Gratis ke n8n VPS (1 Menit)

1. Di dashboard n8n VPS kamu, klik **Add Workflow**.
2. Klik menu titik tiga (`...`) di pojok kanan atas → pilih **Import from File...**
3. Pilih file [`n8n_tim_konten_fonnte_motion.json`](./n8n_tim_konten_fonnte_motion.json).
   *(Perhatikan: Di workflow terbaru ini, node video sudah otomatis diarahkan ke `http://motion-renderer:8000/render` di dalam VPS-mu, jadi kamu **tidak butuh akun/API key JSON2Video lagi**!)*

---

## Langkah 4: Pasang 3 Kredensial Gratis di n8n

### 1. Google Gemini API Key (Gratis dari Google AI Studio)
1. Buka [aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey) → klik **Create API Key** → salin kodenya.
2. Di n8n, buka node **`Google Gemini (Manajer)`** → *Create New Credential* → tempel API Key → klik **Save**.
3. Buka node **`Google Gemini (Motion)`** → pilih credential Google Gemini yang sama.

### 2. Google Sheets (Pilih Cara Service Account agar Paling Mudah di Self-Host VPS)
Karena kamu memakai n8n Self-Host di VPS, cara paling cepat dan stabil tanpa ribet verifikasi OAuth adalah memakai **Google Service Account**:
1. Buka [Google Cloud Console](https://console.cloud.google.com/) → buat/pilih Project.
2. Masuk ke **APIs & Services → Library** → cari **Google Sheets API** → klik **Enable**.
3. Masuk ke **IAM & Admin → Service Accounts** → klik **Create Service Account** (beri nama bebas, misal `n8n-bot`) → klik **Done**.
4. Klik Service Account yang baru dibuat → tab **Keys** → **Add Key → Create new key → JSON** → file `.json` akan terunduh ke komputermu.
5. Buka file `.json` tersebut dengan Notepad/Text Editor:
   - Salin nilai **`client_email`** (contoh: `n8n-bot@project-id.iam.gserviceaccount.com`).
   - Buka Google Sheets [Database_Tim_Konten](https://docs.google.com/spreadsheets/d/1-6ra-cPS3nDlSfbxpmO-jjJkBEhcjr6rbI1VCGLInN4/edit) → klik tombol **Share (Bagikan)** di pojok kanan atas → tempel `client_email` tadi sebagai **Editor** → klik **Send/Share**.
6. Kembali ke n8n → buka node **`Baca_Katalog_Produk`**:
   - Pada *Authentication*, ubah dari *OAuth2* menjadi **Service Account**.
   - Klik *Create New Credential* → isi **Email** dengan `client_email` dan **Private Key** dengan isi `private_key` dari file JSON tadi → klik **Save**.
   - Pilih credential Service Account tersebut pada semua node Google Sheets di workflow.

### 3. Whitelist Nomor WA Pribadi & Token Fonnte (Skema A — 2 Nomor)
1. Buka node **`Filter Nomor Pemilik (Skema A)`** → ganti `6281234567890` dengan **nomor WA pribadimu** (format `628...`).
2. Buka node **`Kirim Balasan Teks via Fonnte`** dan **`Kirim Video via Fonnte`** → ganti `ISI_TOKEN_FONNTE_ANDA` dengan **Device Token nomor bot** dari dashboard Fonnte.

---

## Langkah 5: Aktifkan Webhook & Tes Render Video Gratis!

1. Buka node **`Webhook Fonnte Masuk`** di n8n → salin **Production URL** (`https://<HOST-VPS>/webhook/fonnte-tim-konten`).
2. Klik toggle **Active** di kanan atas n8n.
3. Tempel Production URL tadi ke **Dashboard Fonnte → Device (Nomor Bot) → Webhook URL** → klik **Save**.
4. Sekarang ambil HP dengan nomor WA pribadimu dan kirim pesan ke nomor WA Bot:
   - `Ide minggu ini` → Bot meriset ide & menyimpannya ke Google Sheets.
   - `Draft K-01` → Bot menyusun naskah & menyimpannya ke `Kalender_Konten`.
   - `Video K-01` → VPS Biznet kamu merender video motion `.mp4` 9:16 lengkap dengan suara Bahasa Indonesia (`id-ID-GadisNeural`) dan subtitle dalam ~10–15 detik, menyimpannya ke Google Sheets, lalu mengirimkan videonya langsung ke WhatsApp-mu!
