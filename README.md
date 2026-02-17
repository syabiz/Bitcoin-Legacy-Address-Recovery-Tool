# Bitcoin Legacy Address Recovery Tool

[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Dependencies](https://img.shields.io/badge/dependencies-ecdsa%2C%20base58-orange)](requirements.txt)

**Sebuah tool untuk memahami cara kerja Bitcoin address generation dan melakukan pencarian address legacy (P2PKH) yang mungkin terlupakan.** Program ini menggunakan multiprocessing dan dilengkapi berbagai fitur optimasi.

---

## DAFTAR ISI

- [Tentang Project](#tentang-project)
- [Fitur Utama](#fitur-utama)
- [Cara Kerja Program](#cara-kerja-program)
- [Instalasi](#instalasi)
- [Persiapan File Target](#persiapan-file-target)
- [Panduan Penggunaan](#panduan-penggunaan)
- [Contoh Output](#contoh-output)
- [Penjelasan Fungsi](#penjelasan-fungsi)
- [Optimasi Kinerja](#optimasi-kinerja)
- [Batasan](#batasan)
- [Peringatan Penting](#peringatan-penting)
- [Skenario Penggunaan](#skenario-penggunaan)
- [Pengembangan Lanjutan](#pengembangan-lanjutan)
- [Lisensi](#lisensi)
- [Donasi](#donasi)
- [Kontak](#kontak)
- [Ucapan Terima Kasih](#ucapan-terima-kasih)

---

## TENTANG PROJECT

### Latar Belakang

Bitcoin menggunakan sistem kriptografi kurva elliptic (Elliptic Curve Cryptography) untuk mengamankan transaksi. Setiap Bitcoin address adalah representasi dari public key yang diturunkan dari private key. Address legacy (P2PKH) adalah format address Bitcoin pertama yang digunakan, dimulai dengan angka `1`.

### Tujuan Project

1. **Edukasi**: Memahami bagaimana private key dikonversi menjadi Bitcoin address
2. **Eksperimen**: Mempelajari teknik multiprocessing dan optimasi Python
3. **Recovery**: Membantu pemulihan address yang terlupakan (dengan range terbatas)

### Untuk Siapa Tool Ini?

- **Developer** yang ingin belajar kriptografi Bitcoin
- **Peneliti keamanan** yang mempelajari weak keys
- **Pemilik Bitcoin** yang lupa private key (dengan range terbatas)
- **Peserta puzzle/challenge** Bitcoin

---

## FITUR UTAMA

### 1. Multiprocessing dengan Batch Processing
- Membagi pekerjaan ke beberapa proses paralel
- Memanfaatkan semua core CPU untuk percepatan linear
- Batch size 100 key untuk mengurangi overhead komunikasi
- Progress reporting setiap 5000 key

### 2. Optimasi Khusus Address Legacy
- Hanya generate compressed public key (lebih umum digunakan >95%)
- Validasi format address otomatis
- Set data structure untuk O(1) lookup time

### 3. Pre-processing Target Address
- Validasi otomatis format address (harus mulai `1`, panjang 25-34)
- Filter address tidak valid untuk hemat memory
- Tampilkan sample address untuk verifikasi

### 4. Weak Key Detection

| Pola | Deskripsi | Contoh |
|------|-----------|--------|
| All zeros | Private key semua 0 | `0000...0000` |
| All ones | Private key semua f | `ffff...ffff` |
| Sequential | Berurutan 0-9-a-f | `0123456789abcdef...` |
| Low entropy | < 10 karakter unik | `1111...1111` |
| Palindrome | Sama jika dibalik | `abcd...dcba` |
| Repeated | Pola berulang | `deadbeefdeadbeef...` |

### 5. Error Handling Robust
- Specific exceptions (`ValueError`, `BadDigestError`, `OverflowError`)
- Error counting dengan auto-stop jika >1000 error
- Sampling log hanya 0.1% error untuk hindari spam

### 6. Estimasi Probabilitas Real-time
- Ruang kunci 2^160 (address space)
- Probabilitas = target_count / 2^160
- Expected keys = 1 / probabilitas
- Konversi ke waktu (detik/menit/jam/hari/tahun)

---

## CARA KERJA PROGRAM

### Flowchart

```
START
│
├─► Load file target (Rich_P2PKH.txt)
│   ├─► Validasi setiap address
│   └─► Simpan address valid ke SET
│
├─► Tanya jumlah core CPU
│   └─► Bagi pekerjaan ke N worker
│
├─► Tanya mode pencarian
│   ├─► Sequential: mulai dari 1 increment
│   └─► Random: acak di seluruh range
│
├─► Setiap worker melakukan LOOP:
│   ├─► Generate 100 private key (batch)
│   ├─► Untuk setiap key:
│   │   ├─► bytes.fromhex() konversi ke bytes
│   │   ├─► ecdsa.SigningKey.from_string() buat key pair
│   │   ├─► Ambil verifying_key (public key)
│   │   ├─► Buat compressed public key
│   │   ├─► SHA256(public key)
│   │   ├─► RIPEMD-160(hasil SHA256) → hash160
│   │   ├─► Tambah network byte 0x00
│   │   ├─► Double SHA256 untuk checksum
│   │   ├─► Base58Encode → address
│   │   └─► Cek apakah address ada di SET target
│   │       ├─► Jika YA → simpan dan STOP
│   │       └─► Jika TIDAK → lanjut
│   │
│   └─► Setiap 5000 key → kirim update ke main process
│
├─► Main process menerima update
│   ├─► Hitung kecepatan (keys/second)
│   ├─► Tampilkan progress setiap 1 detik
│   └─► Setiap 30 detik → tampilkan estimasi
│
└─► Jika STOP (ketemu atau Ctrl+C)
    ├─► Terminate semua worker
    └─► Tampilkan statistik final
```

### Diagram Sederhana

```
[MAIN PROCESS]
│
├── [WORKER 1] → Generate keys 1-100   → Check → Update stats
├── [WORKER 2] → Generate keys 101-200 → Check → Update stats
├── [WORKER 3] → Generate keys 201-300 → Check → Update stats
└── [WORKER 4] → Generate keys 301-400 → Check → Update stats
                                               │
                                               ▼
             Display Progress: "Checked: 1.234.567 | Speed: 45.678 keys/s"
```

---

## INSTALASI

### Prasyarat Sistem

| Komponen | Minimum | Rekomendasi |
|----------|---------|-------------|
| CPU | 2 core | 8+ core |
| RAM | 1 GB | 4+ GB |
| Storage | 100 MB | 1 GB |
| OS | Windows/Linux/macOS | Linux |
| Python | 3.6 | 3.9+ |

### Langkah Instalasi

#### Windows:
```bash
# 1. Buka Command Prompt atau PowerShell

# 2. Download atau clone repository
git clone https://github.com/username/bitcoin-legacy-recovery.git
cd bitcoin-legacy-recovery

# 3. Buat virtual environment (opsional)
python -m venv venv
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt
```

#### Linux/macOS:
```bash
# 1. Buka terminal

# 2. Clone repository
git clone https://github.com/username/bitcoin-legacy-recovery.git
cd bitcoin-legacy-recovery

# 3. Buat virtual environment
python3 -m venv venv
source venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt
```

#### File `requirements.txt`
```
ecdsa==0.18.0     # Library kurva elliptic SECP256k1
base58==2.1.1     # Encoding/decoding Base58Check
```

#### Verifikasi Instalasi
```bash
python -c "import ecdsa, base58; print('Instalasi sukses!')"
# Output: Instalasi sukses!
```

---

## PERSIAPAN FILE TARGET

### Format File yang Benar

Buat file `Rich_P2PKH.txt` dengan format:

```
# File target Bitcoin address legacy
# Format: SATU ADDRESS PER BARIS
# Karakter # untuk komentar (akan diabaikan)

# Address genesis block
1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa

# Address pizza transaction (10,000 BTC)
1HLoD9E4SDFFPDiYfNYnkBLQ85Y51J3Zb1

# Address lain
1F1tAaz5x1HUXrCNLbtMDqcw6o5GNn4xqX
1JCe8z4jJVNXSjohjM4i9Hh813dLC4xr7p
```

### Validasi Address Legacy

Ciri-ciri address legacy valid:
- Dimulai dengan angka `1`
- Panjang antara 25–34 karakter
- Hanya karakter Base58 (1-9, A-Z, a-z tanpa I, O, l)
- Memiliki checksum valid

**Contoh valid:**
- `1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa` (33 karakter)
- `1HLoD9E4SDFFPDiYfNYnkBLQ85Y51J3Zb1` (34 karakter)

**Contoh TIDAK valid:**
- `3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy` (P2SH, mulai `3`)
- `bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq` (Bech32, mulai `bc1`)
- `1A1zP1e` (terlalu pendek)

### Memory Usage

| Jumlah Address | Estimasi RAM |
|----------------|-------------|
| 100.000 | ~5–6 MB |
| 1.000.000 | ~50–60 MB |
| 10.000.000 | ~500–600 MB |

---

## PANDUAN PENGGUNAAN

### 1. Menjalankan Program

```bash
# Pastikan virtual environment aktif
python main.py
```

### 2. Step-by-Step

**Step 1: Load File Target**
```
============================================================
🚀 BITCOIN LEGACY ADDRESS RECOVERY TOOL
============================================================
Mencari address P2PKH (dimulai dengan '1')
Versi: 1.0.0
============================================================

[*] Memuat file target: Rich_P2PKH.txt
[*] Membaca file Rich_P2PKH.txt...
```

**Step 2: Validasi dan Statistik**
```
[*] Total baris: 1500
[*] Address valid: 1495
[*] Address tidak valid (diabaikan): 5

[*] Sample target addresses:
    1. 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
    2. 1HLoD9E4SDFFPDiYfNYnkBLQ85Y51J3Zb1
    3. 1F1tAaz5x1HUXrCNLbtMDqcw6o5GNn4xqX
    4. 1JCe8z4jJVNXSjohjM4i9Hh813dLC4xr7p
    5. 1L9jGHTR9jG6LpLQv5yWzXq7vP1qQzZx9k
    ... dan 1490 lainnya
```

**Step 3: Konfigurasi CPU**
```
[*] Detected 8 CPU cores
[?] Jumlah core yang digunakan (1-8):
```

Tips memilih core:
- `8 core (max)` → Kecepatan maksimal, CPU 100%
- `6-7 core` → Sisakan untuk OS
- `4 core` → Seimbang untuk multitasking
- `1-2 core` → Minimal, hemat baterai

**Step 4: Pilih Mode**
```
[?] Mode [1] Sequential [2] Random:
```

- **Mode Sequential (1):** Mulai dari `0x1`, increment 1 setiap kali. Cocok untuk range kecil berurutan.
- **Mode Random (2):** Memilih acak di seluruh range. Distribusi probabilitas merata.

**Step 5: Program Berjalan**
```
[*] Starting with 8 cores...
[*] Mode: RANDOM
[*] Press Ctrl+C to stop
[*] Worker 0 started
[*] Worker 1 started
...
```

### 3. Selama Program Berjalan

**Progress Bar**
```
[14:30:45] Checked: 1,234,567 | Speed: 45,678 keys/s | Cores: 8 | Time: 27s
```

| Komponen | Keterangan |
|----------|-----------|
| `[14:30:45]` | Waktu sekarang |
| `Checked: 1,234,567` | Total key dicek |
| `Speed: 45,678 keys/s` | Kecepatan rata-rata |
| `Cores: 8` | Jumlah core aktif |
| `Time: 27s` | Waktu berjalan |

**Deteksi Weak Pattern**
```
[!] Weak pattern detected: low_entropy
    Key: 1111111111111111...1111111111111111
```

**Estimasi Periodik (setiap 30 detik)**
```
============================================================
📊 ESTIMASI STATISTIK
============================================================
[*] Kecepatan: 45,678 keys/second
[*] Jumlah target: 1,495 address
[*] Probabilitas per key: 8.02e-46
[*] Expected keys: 1.25e+45

⏱️  Estimasi waktu: 1.25e+36 tahun

💡 SARAN:
   • Fokus pada range terbatas (puzzle transactions)
   • Cek database known weak keys
   • Gunakan GPU untuk percepatan 100-1000x
============================================================
```

### 4. Jika Menemukan Address

```
============================================================
[!!!] FOUND BY WORKER 3!
============================================================
Private Key (hex): 0000000000000000000000000000000000000000000000000000000000000001
Private Key (dec): 1
Address: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa
Keys checked by this worker: 12345
Timestamp: 2025-01-01 12:34:56
============================================================
```

### 5. Jika Menghentikan Program (Ctrl+C)

```
^C
[!] Stopping workers...

============================================================
📊 FINAL STATISTICS
============================================================
[*] Total keys checked: 1,234,567
[*] Total waktu: 27.45 detik
[*] Rata-rata kecepatan: 44,987 keys/s
[*] Target addresses: 1,495

❌ Tidak menemukan address
============================================================
```

---

## CONTOH OUTPUT

### Startup Normal
```
============================================================
🚀 BITCOIN LEGACY ADDRESS RECOVERY TOOL
============================================================

[*] Memuat file target: Rich_P2PKH.txt
[*] Total baris: 1000
[*] Address valid: 995
[*] Address tidak valid: 5

[*] Detected 8 CPU cores
[?] Jumlah core: 8
[?] Mode: 2

[*] Starting with 8 cores...
[*] Mode: RANDOM
[*] Worker 0 started
...
```

### Progress Normal
```
[14:30:45] Checked: 1,234,567 | Speed: 45,678 keys/s | Cores: 8 | Time: 27s
[14:30:46] Checked: 1,280,123 | Speed: 45,712 keys/s | Cores: 8 | Time: 28s
[14:30:47] Checked: 1,325,678 | Speed: 45,689 keys/s | Cores: 8 | Time: 29s
```

### Dengan Weak Pattern
```
[14:30:45] Checked: 1,234,567 | Speed: 45,678 keys/s | Cores: 8 | Time: 27s
[!] Weak pattern detected: low_entropy
    Key: 1111111111111111...1111111111111111
[14:30:46] Checked: 1,280,123 | Speed: 45,712 keys/s | Cores: 8 | Time: 28s
```

### Final Stats
```
============================================================
📊 FINAL STATISTICS
============================================================
[*] Total keys checked: 10,234,567
[*] Total waktu: 227.45 detik (3 menit 47 detik)
[*] Rata-rata kecepatan: 45,012 keys/s
[*] Target addresses: 1,495
[*] Weak patterns found: 3 (lihat weak_patterns.log)
============================================================
```

---

## PENJELASAN FUNGSI

### 1. `key_to_legacy_addr(hex_key)`

**Tujuan:** Mengubah private key hex menjadi Bitcoin address legacy

| Parameter | Tipe | Keterangan |
|-----------|------|-----------|
| `hex_key` | string | Private key 64 karakter hex |

**Return:** `address` (string) atau `None`

**Proses:**
1. Konversi hex ke bytes
2. Validasi panjang (harus 32 bytes)
3. Buat `SigningKey` (private key)
4. Dapatkan `VerifyingKey` (public key)
5. Buat compressed public key
6. Hash160 (SHA256 + RIPEMD160)
7. Tambah network byte `0x00`
8. Hitung checksum (double SHA256)
9. Base58 encode

---

### 2. `check_weak_pattern(hex_key)`

**Tujuan:** Deteksi private key dengan pola lemah

| Parameter | Tipe | Keterangan |
|-----------|------|-----------|
| `hex_key` | string | Private key 64 karakter hex |

**Return:** `True` jika weak pattern terdeteksi

**Pola yang dideteksi:** All zeros, All ones, Sequential, Low entropy, Palindrome, Repeated pattern

---

### 3. `load_legacy_targets(filename)`

**Tujuan:** Load dan validasi file target

| Parameter | Tipe | Keterangan |
|-----------|------|-----------|
| `filename` | string | Nama/path file target |

**Return:** `set` berisi address valid

**Proses:** Cek file exists → Baca baris per baris → Validasi format → Simpan ke set → Tampilkan statistik

---

### 4. `estimate_time(speed, num_targets)`

**Tujuan:** Estimasi waktu berdasarkan probabilitas matematis

| Parameter | Tipe | Keterangan |
|-----------|------|-----------|
| `speed` | float | Keys per second |
| `num_targets` | int | Jumlah address target |

**Rumus:**
```
Probabilitas    = num_targets / 2^160
Expected keys   = 1 / probabilitas
Waktu           = expected_keys / speed
```

---

### 5. `worker(worker_id, mode, shared_counter, targets, stats_queue, stop_event)`

**Tujuan:** Proses worker paralel

| Parameter | Keterangan |
|-----------|-----------|
| `worker_id` | ID unik worker |
| `mode` | `'1'` sequential, `'2'` random |
| `shared_counter` | Counter bersama antar proses |
| `targets` | Set address target |
| `stats_queue` | Queue komunikasi ke main |
| `stop_event` | Sinyal berhenti |

**Alur:** Generate batch → Konversi ke address → Cek di target set → Update progress → Handle error

---

## OPTIMASI KINERJA

### Tips Meningkatkan Kecepatan

1. **Gunakan semua core CPU** — Percepatan hampir linear dengan jumlah core
2. **Linux > Windows** — Linux memiliki overhead multiprocessing lebih rendah
3. **Kurangi target** — Lebih sedikit address = lookup lebih cepat
4. **SSD storage** — Untuk penulisan log `FOUND.txt` lebih cepat
5. **Tutup aplikasi lain** — Bebaskan resource CPU

### Perbandingan Kecepatan (Estimasi)

| Hardware | Keys/second |
|----------|------------|
| 1 core (modern CPU) | ~5.000–8.000 |
| 4 core | ~20.000–30.000 |
| 8 core | ~40.000–60.000 |
| GPU (dengan modifikasi) | ~1.000.000+ |

### Bottleneck Utama

Program ini dibatasi oleh komputasi ECDSA (kurva elliptic), bukan I/O. Untuk peningkatan signifikan, pertimbangkan implementasi GPU menggunakan CUDA atau OpenCL.

---

## BATASAN

- **Kecepatan terbatas** — Python + CPU jauh lebih lambat dari GPU
- **Probabilitas sangat kecil** — Untuk address acak, kemungkinan menemukan hampir nol
- **Tidak ada uncompressed key** — Hanya generate compressed public key
- **Sequential mode shared** — Semua worker berbagi counter, ada locking overhead
- **Memory** — Set besar (jutaan address) butuh RAM lebih

---

## PERINGATAN PENTING

> ⚠️ **DISCLAIMER HUKUM**
>
> Tool ini dibuat **SEMATA-MATA untuk tujuan edukasi dan penelitian**. Penggunaan tool ini untuk mengakses wallet Bitcoin milik orang lain tanpa izin adalah **ILEGAL** dan merupakan tindak pidana di sebagian besar yurisdiksi.
>
> Penulis **tidak bertanggung jawab** atas segala penyalahgunaan tool ini. Gunakan hanya untuk:
> - Memulihkan wallet **milik Anda sendiri**
> - Penelitian akademis dan keamanan
> - Edukasi dan pembelajaran kriptografi
> - Berpartisipasi dalam Bitcoin puzzle/challenge yang sah

---

## SKENARIO PENGGUNAAN

### Skenario 1: Bitcoin Puzzle Transactions

Bitcoin puzzle adalah challenge resmi di mana seseorang menyembunyikan private key dalam range tertentu. Contoh: **Bitcoin puzzle 1–160** dengan hadiah ratusan BTC.

```bash
# Modifikasi LOW_LIMIT dan HIGH_LIMIT di kode
LOW_LIMIT  = 0x1
HIGH_LIMIT = 0xff  # Untuk puzzle #8 (8-bit range)
```

### Skenario 2: Brain Wallet Recovery

Brain wallet adalah private key yang dibuat dari passphrase. Jika Anda lupa passphrase tetapi ingat pola tertentu, gunakan mode sequential dengan range terbatas.

### Skenario 3: Penelitian Weak Keys

Mengidentifikasi dan mendokumentasikan private key dengan entropi rendah yang mungkin rentan, untuk tujuan penelitian keamanan.

---

## PENGEMBANGAN LANJUTAN

### Fitur yang Dapat Ditambahkan

- [ ] **GPU Support** — Implementasi CUDA/OpenCL untuk kecepatan 100-1000x
- [ ] **Uncompressed Key** — Support public key tidak terkompresi
- [ ] **WIF Format** — Export private key dalam format Wallet Import Format
- [ ] **Database Integration** — Simpan progress ke SQLite untuk resume
- [ ] **API Integration** — Cek saldo address secara real-time
- [ ] **Web Interface** — Dashboard monitoring berbasis web
- [ ] **Distributed Computing** — Jalankan di banyak mesin sekaligus

### Kontribusi

Pull request dan issue sangat diterima! Silakan fork repository ini dan buat branch baru untuk setiap fitur atau perbaikan.

```bash
git checkout -b feature/nama-fitur
git commit -m "Tambah fitur: nama-fitur"
git push origin feature/nama-fitur
```

---

## LISENSI

Distributed under the MIT License. See `LICENSE` for more information.

```
MIT License

Copyright (c) 2026 Bitcoin Legacy Recovery Tool

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## DONASI

Jika tool ini bermanfaat untuk edukasi dan pembelajaran Anda, donasi sangat dihargai:

**Bitcoin (BTC):** `bc1qn6t8hy8memjfzp4y3sh6fvadjdtqj64vfvlx58`

**Ethereum (ETH):** `0x512936ca43829C8f71017aE47460820Fe703CAea`

**PayPal:** `syabiz@yandex.com`

Donasi akan digunakan untuk pengembangan fitur baru, maintenance server, dan dokumentasi.

---

## KONTAK

- **GitHub Issues:** https://github.com/username/bitcoin-legacy-recovery/issues
- **Email:** syabiz@yandex.com
- **Twitter:** @syabiz

---

## UCAPAN TERIMA KASIH

- **Komunitas Bitcoin** — Untuk dokumentasi dan spesifikasi teknis
- **Pengembang ecdsa** — Library kriptografi yang luar biasa
- **Pengembang base58** — Encoding/decoding yang efisien
- **Semua kontributor** — Yang membantu meningkatkan tool ini
- **Para pengguna** — Untuk feedback dan saran berharga

---

Terima kasih telah menggunakan Bitcoin Legacy Address Recovery Tool! 🚀

*Dibuat dengan ❤️ untuk edukasi dan pembelajaran Bitcoin*

*Selamat mencoba! Semoga beruntung menemukan address yang dicari!* 🍀

---

*Terakhir diperbarui: 18 Februari 2026*
