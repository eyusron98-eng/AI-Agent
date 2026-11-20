# Panduan Setup & Uji Coba Tim Konten Kreator AI (n8n Cloud + Google Gemini + Fonnte Skema A)

File workflow [`n8n_tim_konten_fonnte_motion.json`](./n8n_tim_konten_fonnte_motion.json) sudah disesuaikan khusus untuk pilihanmu:
- **Platform:** **n8n Cloud**
- **Otak AI:** **Google Gemini (`models/gemini-2.5-flash`)** via Google AI Studio
- **WhatsApp:** **Fonnte Skema A (2 Nomor WA — Nomor Khusus Bot)**, sehingga kamu **tidak perlu mengetik `/ai`** setiap kali mengirim perintah dari nomor WA pribadimu.
- **Google Sheets:** Sudah terhubung ke Spreadsheet ID `1-6ra-cPS3nDlSfbxpmO-jjJkBEhcjr6rbI1VCGLInN4` ([Database_Tim_Konten](https://docs.google.com/spreadsheets/d/1-6ra-cPS3nDlSfbxpmO-jjJkBEhcjr6rbI1VCGLInN4/edit)) lengkap dengan 6 tool (`Baca_Katalog_Produk`, `Baca_Bank_Ide`, `Simpan_Bank_Ide`, `Baca_Kalender_Konten`, `Simpan_Kalender_Konten`, dan `Baca_Performa_Konten`) serta penyimpanan otomatis `Link_File_Media` setelah video selesai dirender.

---

## Langkah 1: Isi Data Produk & Fakta Asli di Google Sheets (5 Menit)

Buka [Database_Tim_Konten](https://docs.google.com/spreadsheets/d/1-6ra-cPS3nDlSfbxpmO-jjJkBEhcjr6rbI1VCGLInN4/edit) → masuk ke tab **`Katalog_Produk_&_Fakta`**.

Ganti atau tambahkan baris produk/riset aslimu dengan format berikut:

| Kode | Pilar | Nama_Produk_atau_Riset | Bahan_dan_Fakta_Valid | Harga | Klaim_Terlarang |
|---|---|---|---|---|---|
| `P-01` | `Sabun` | *(Nama varian sabunmu)* | *(Komposisi minyak, proses cold process, masa curing 4 minggu, berat gram)* | *(Harga asli)* | `DILARANG klaim menyembuhkan eksim/jerawat medis, anti-bakteri medis, atau obat penyakit kulit` |
| `P-02` | `Koperasi` | *(Nama paket/layanan pasokan koperasi)* | *(Daftar bahan dapur yang dipasok, minimal order, jadwal kirim)* | *(Harga/skema)* | `DILARANG janji harga tetap selamanya atau stok tak terbatas` |
| `P-03` | `Dapur` | *(Nama menu/katering dapur)* | *(Bahan segar dari koperasi, tanpa pengawet, daya tahan)* | *(Harga per porsi/paket)* | `DILARANG klaim organik bersertifikat jika bahan belum bersertifikat organik` |
| `P-04` | `Riset` | *(Topik riset/formulasi yang sedang berjalan)* | *(Temuan valid atau edukasi ilmiah populer yang boleh dibagikan ke publik)* | `-` | `DILARANG menyimpulkan hasil klinis medis tanpa uji terverifikasi` |

> [!TIP]
> Kamu juga bisa menuliskan daftar produk, bahan, dan harga aslimu langsung di chat ini agar saya buatkan tabel/data siap tempel atau bantu update langsung ke Google Sheets.

---

## Langkah 2: Import Workflow ke n8n Cloud (2 Menit)

1. Masuk ke dashboard **n8n Cloud** milikmu → klik **Create Workflow**.
2. Klik ikon menu titik tiga (`...`) di pojok kanan atas → pilih **Import from File...**
3. Pilih file [`n8n_tim_konten_fonnte_motion.json`](./n8n_tim_konten_fonnte_motion.json) dari repositori ini.

---

## Langkah 3: Pasang 4 Kredensial & Nomor WA Pemilik (10 Menit)

### A. Google Gemini API Key (Google AI Studio)
1. Buka [Google AI Studio (aistudio.google.com/app/apikey)](https://aistudio.google.com/app/apikey) → klik **Create API Key** → salin kodenya.
2. Di n8n Cloud, klik dua kali node **`Google Gemini (Manajer)`** → pada bagian *Credential to connect with*, pilih **Create New Credential**.
3. Tempel API Key tersebut lalu klik **Save**.
4. Buka juga node **`Google Gemini (Motion)`** dan pilih credential Google Gemini yang sama.

### B. Akun Google Sheets (OAuth2)
1. Klik dua kali node **`Baca_Katalog_Produk`** → pada *Credential to connect with*, klik **Create New Credential** → klik tombol **Sign in with Google**.
2. Pilih akun Google yang memiliki file `Database_Tim_Konten` → klik **Allow**.
3. Pastikan ketujuh node Google Sheets (`Baca_Katalog_Produk`, `Baca_Bank_Ide`, `Simpan_Bank_Ide`, `Baca_Kalender_Konten`, `Simpan_Kalender_Konten`, `Baca_Performa_Konten`, `Ambil Data Konten dari Sheets`, dan `Simpan Link Video ke Sheets`) memakai credential Google Sheets tersebut.

### C. Whitelist Nomor WA Pribadimu (Skema A — 2 Nomor)
1. Klik dua kali node **`Filter Nomor Pemilik (Skema A)`**.
2. Pada kondisi kedua (`cond-sender-whitelist`), ganti angka **`6281234567890`** dengan **nomor WhatsApp pribadimu** yang akan kamu pakai untuk mengirim perintah ke nomor bot (wajib diawali `628...`, tanpa tanda `+`, spasi, atau strip).
3. *(Dengan filter ini, hanya pesan dari nomor WA pribadimu yang akan diproses oleh Manajer Konten AI).*

### D. Token Device Fonnte (Nomor Kedua / Nomor Bot)
1. Masuk ke dashboard **Fonnte** → menu **Device** → pastikan **Nomor Kedua (Nomor Bot AI)** sudah terhubung (status *Connected*).
2. Klik tombol **Token** pada device nomor bot tersebut → salin tokennya.
3. Di n8n Cloud, buka node **`Kirim Balasan Teks via Fonnte`** dan **`Kirim Video via Fonnte`** → pada bagian *Header Parameters* (`Authorization`), ganti `ISI_TOKEN_FONNTE_ANDA` dengan Token Fonnte tersebut.

### E. API Key JSON2Video (Untuk Render Video Motion `.mp4`)
1. Daftar/masuk ke [json2video.com](https://json2video.com) → ambil **API Key** dari dashboard.
2. Di n8n Cloud, buka node **`Render Video Motion (JSON2Video)`** dan **`Ambil URL Video MP4`** → pada *Header Parameters* (`x-api-key`), ganti `ISI_API_KEY_JSON2VIDEO_ANDA` dengan API Key JSON2Video milikmu.
*(Catatan: Kamu sudah bisa menguji fitur riset ide, pembuatan naskah, ACC, revisi, dan laporan mingguan meskipun API Key JSON2Video belum diisi).*

---

## Langkah 4: Hubungkan Webhook n8n Cloud ke Fonnte

1. Di n8n Cloud, klik dua kali node paling kiri: **`Webhook Fonnte Masuk`**.
2. Klik tab **Production URL**, lalu salin URL-nya (bentuknya: `https://<nama-workspace>.app.n8n.cloud/webhook/fonnte-tim-konten`).
3. Simpan workflow (`Ctrl+S`), lalu ubah tombol **Inactive** di kanan atas n8n Cloud menjadi **Active** (hijau).
4. Buka dashboard **Fonnte → Device** → klik **Edit** pada nomor bot AI → tempel Production URL tadi ke kolom **Webhook URL** → klik **Save**.

---

## Langkah 5: Checklist Uji Coba dari WhatsApp Pribadimu

Ambil HP dengan **nomor WA pribadimu**, lalu kirim pesan ke **nomor WA Bot AI** secara berurutan:

- [ ] **Tes 1 (Riset Ide 4 Pilar):** Kirim pesan:
  ```text
  Ide minggu ini
  ```
  *Hasil yang diharapkan:* Dalam 10–20 detik, bot membalas daftar ide konten baru di WhatsApp, dan baris baru (`R-04`, dst.) otomatis muncul di tab `Bank_Riset_Ide`.

- [ ] **Tes 2 (Buat Draft Naskah & Caption):** Kirim pesan:
  ```text
  Buatkan naskah dari R-01
  ```
  *Hasil yang diharapkan:* Bot menyusun Hook 3 detik, naskah 4–5 bagian, caption + hashtag + CTA yang mematuhi `Klaim_Terlarang`, menyimpannya ke tab `Kalender_Konten` dengan status `Menunggu ACC`, lalu mengirimkan draft-nya ke WA-mu.

- [ ] **Tes 3 (Revisi Naskah):** Kirim pesan:
  ```text
  Revisi K-01: Buat kalimat hook lebih singkat dan tambahkan ajakan pesan lewat WA di akhir caption
  ```
  *Hasil yang diharapkan:* Bot memperbarui baris `K-01` di `Kalender_Konten` dan mengirimkan versi revisinya ke WA.

- [ ] **Tes 4 (Render Video Motion 9:16 Otomatis):** Kirim pesan:
  ```text
  Video K-01
  ```
  *Hasil yang diharapkan:* Setelah ~35–45 detik, video `.mp4` (lengkap dengan voiceover Bahasa Indonesia `id-ID-GadisNeural` dan subtitle otomatis) masuk ke WhatsApp-mu, dan kolom `Link_File_Media` di `Kalender_Konten` terisi otomatis.

- [ ] **Tes 5 (Persetujuan Tayang):** Kirim pesan:
  ```text
  ACC K-01
  ```
  *Hasil yang diharapkan:* Status `K-01` di tab `Kalender_Konten` berubah menjadi **`Siap Tayang`**.
