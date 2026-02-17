# 🚀 Bitcoin Legacy Address Recovery Tool

[![Python Version](https://img.shields.io/badge/python-3.6%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)
[![Dependencies](https://img.shields.io/badge/dependencies-ecdsa%2C%20base58-orange)](requirements.txt)

**Tool untuk mencari Bitcoin address legacy (P2PKH) yang mungkin terlupakan atau hilang.**  
Program ini dioptimalkan khusus untuk address yang dimulai dengan `1` (format legacy) dan menggunakan multiprocessing untuk memaksimalkan penggunaan CPU.

---

## 📋 Daftar Isi
- [Fitur Utama](#fitur-utama)
- [Cara Kerja](#cara-kerja)
- [Instalasi](#instalasi)
- [Persiapan File Target](#persiapan-file-target)
- [Cara Penggunaan](#cara-penggunaan)
- [Contoh Output](#contoh-output)
- [Penjelasan Kode](#penjelasan-kode)
- [Optimasi & Tips](#optimasi--tips)
- [Batasan & Peringatan](#batasan--peringatan)
- [Pengembangan Lanjutan](#pengembangan-lanjutan)
- [Lisensi](#lisensi)
- [Kontribusi](#kontribusi)
- [Donasi](#donasi)

---

## ✨ Fitur Utama

| Fitur | Deskripsi |
|-------|-----------|
| **Multiprocessing** | Menggunakan semua core CPU untuk percepatan maksimal |
| **Optimasi Legacy** | Hanya generate compressed public key (lebih umum) |
| **Pre-processing Target** | Validasi otomatis format address, filter yang tidak valid |
| **Batch Processing** | Proses ribuan key dalam batch untuk efisiensi |
| **Weak Key Detection** | Deteksi pola-pola weak key (brain wallet, low entropy) |
| **Estimasi Realistis** | Perhitungan probabilitas dan estimasi waktu |
| **Error Handling** | Robust error handling dengan auto-stop jika terlalu banyak error |
| **Live Progress** | Tampilan kecepatan, total cek, dan waktu berjalan |

---

## 🎯 Cara Kerja

```mermaid
graph TD
    A[File Target: Rich_P2PKH.txt] --> B[Validasi & Filter]
    B --> C[Set Address Valid]
    D[Generate Private Key] --> E[Convert ke Public Key]
    E --> F[Hash160 + Base58]
    F --> G[Bitcoin Address]
    G --> H{Cek di Set Target?}
    H -->|Ya| I[Simpan di FOUND.txt]
    H -->|Tidak| D
    J[Multiprocessing] --> D