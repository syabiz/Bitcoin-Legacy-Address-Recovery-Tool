#!/usr/bin/env python3
"""
Bitcoin Legacy Address Recovery Tool
Mencari Bitcoin address legacy (P2PKH) yang dimulai dengan '1'
Menggunakan multiprocessing untuk optimalisasi CPU
"""

import hashlib
import ecdsa
import base58
import random
import os
import time
import sys
from multiprocessing import Process, cpu_count, Value, Queue, Event

# ==================== KONSTANTA ====================
LOW_LIMIT  = 0x1
HIGH_LIMIT = 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff

# ==================== FUNGSI UTAMA ====================

def key_to_legacy_addr(hex_key):
    """
    Konversi private key hex ke Bitcoin legacy address (P2PKH)
    Hanya generate compressed public key (lebih umum digunakan)
    
    Args:
        hex_key (str): Private key dalam format hex (64 karakter)
    
    Returns:
        str atau None: Bitcoin address legacy, atau None jika error
    """
    try:
        # Validasi panjang key (harus 32 bytes = 64 karakter hex)
        key_bytes = bytes.fromhex(hex_key)
        if len(key_bytes) != 32:
            return None
        
        # Generate key pair menggunakan kurva SECP256k1
        sk = ecdsa.SigningKey.from_string(key_bytes, curve=ecdsa.SECP256k1)
        vk = sk.verifying_key
        
        # Compressed public key
        # - Awalan 0x02 jika y genap, 0x03 jika y ganjil
        # - Diikuti 32 bytes x coordinate
        prefix = b'\x02' if vk.to_string()[-1] % 2 == 0 else b'\x03'
        pub_compressed = prefix + vk.to_string()[:32]
        
        # Hash160: SHA256 + RIPEMD-160
        sha = hashlib.sha256(pub_compressed).digest()
        ripe = hashlib.new('ripemd160', sha).digest()
        
        # Tambahkan network byte (0x00 untuk mainnet)
        network_ripe = b'\x00' + ripe
        
        # Checksum: 4 bytes pertama dari double SHA256
        checksum = hashlib.sha256(hashlib.sha256(network_ripe).digest()).digest()[:4]
        
        # Base58 encode
        address = base58.b58encode(network_ripe + checksum).decode('utf-8')
        
        return address
        
    except (ValueError, ecdsa.BadDigestError, OverflowError) as e:
        # Logging minimal untuk menghindari spam
        if random.random() < 0.001:  # Log ~0.1% error saja
            print(f"[DEBUG] Error sample: {str(e)[:50]}...")
        return None


def check_weak_pattern(hex_key):
    """
    Deteksi pola-pola weak key yang mungkin digunakan di masa lalu
    
    Args:
        hex_key (str): Private key hex
    
    Returns:
        bool: True jika terdeteksi pola weak
    """
    patterns = []
    
    # 1. All zeros atau all ones
    if hex_key == '0' * 64:
        patterns.append("all_zeros")
    if hex_key == 'f' * 64:
        patterns.append("all_ones")
    
    # 2. Sequential (0123456789abcdef...)
    sequential = True
    for i in range(63):
        if int(hex_key[i], 16) != (int(hex_key[i+1], 16) - 1) % 16:
            sequential = False
            break
    if sequential:
        patterns.append("sequential")
    
    # 3. Low entropy (< 10 karakter unik)
    if len(set(hex_key)) < 10:
        patterns.append("low_entropy")
    
    # 4. Palindrome
    if hex_key == hex_key[::-1]:
        patterns.append("palindrome")
    
    # 5. Repeated pattern (deadbeef deadbeef ...)
    if len(hex_key) >= 16 and hex_key[:16] == hex_key[16:32] == hex_key[32:48] == hex_key[48:]:
        patterns.append("repeated")
    
    if patterns:
        print(f"\n[!] Weak pattern detected: {', '.join(patterns)}")
        print(f"    Key: {hex_key[:16]}...{hex_key[-16:]}")
        return True
    
    return False


def load_legacy_targets(filename):
    """
    Load dan validasi file target address
    Hanya address legacy valid (dimulai dengan '1', panjang 25-34 karakter) yang digunakan
    
    Args:
        filename (str): Nama file berisi daftar address
    
    Returns:
        set: Set address valid
    """
    if not os.path.exists(filename):
        print(f"[-] Error: File '{filename}' tidak ditemukan!")
        print("[*] Buat file dengan format satu address per baris")
        print("[*] Contoh: 1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")
        sys.exit(1)
    
    valid = set()
    invalid = 0
    total = 0
    
    print(f"[*] Membaca file {filename}...")
    
    with open(filename, 'r') as f:
        for line_num, line in enumerate(f, 1):
            addr = line.strip()
            if not addr:
                continue
                
            total += 1
            
            # Validasi address legacy P2PKH
            # - Harus dimulai dengan '1'
            # - Panjang antara 25-34 karakter
            if addr.startswith('1') and 25 <= len(addr) <= 34:
                valid.add(addr)
            else:
                invalid += 1
                if invalid <= 5:  # Tampilkan 5 contoh invalid pertama
                    print(f"[!] Baris {line_num}: '{addr}' bukan address legacy valid")
    
    print(f"\n[*] Total baris: {total}")
    print(f"[*] Address valid: {len(valid)}")
    if invalid > 0:
        print(f"[*] Address tidak valid (diabaikan): {invalid}")
    
    if not valid:
        print("[-] Error: Tidak ada address legacy valid!")
        sys.exit(1)
    
    return valid


def estimate_time(speed, num_targets):
    """
    Estimasi waktu berdasarkan probabilitas matematis
    
    Args:
        speed (float): Kecepatan dalam keys/second
        num_targets (int): Jumlah address target
    """
    # Ruang kunci address: 2^160 (hash160)
    # Probabilitas per key: num_targets / 2^160
    probability_per_key = num_targets / (2 ** 160)
    
    if probability_per_key <= 0:
        return
    
    expected_keys = 1 / probability_per_key
    
    # Waktu yang dibutuhkan
    seconds_needed = expected_keys / speed
    years_needed = seconds_needed / (365 * 24 * 3600)
    
    print("\n" + "="*60)
    print("📊 ESTIMASI STATISTIK")
    print("="*60)
    print(f"[*] Kecepatan: {speed:,.0f} keys/second")
    print(f"[*] Jumlah target: {num_targets:,} address")
    print(f"[*] Probabilitas per key: {probability_per_key:.2e}")
    print(f"[*] Expected keys untuk menemukan 1 address: {expected_keys:.2e}")
    print(f"\n⏱️  Estimasi waktu:")
    
    if years_needed < 1:
        if seconds_needed < 60:
            print(f"   {seconds_needed:.1f} detik")
        elif seconds_needed < 3600:
            print(f"   {seconds_needed/60:.1f} menit")
        elif seconds_needed < 86400:
            print(f"   {seconds_needed/3600:.1f} jam")
        else:
            print(f"   {seconds_needed/86400:.1f} hari")
    elif years_needed < 100:
        print(f"   {years_needed:.1f} tahun")
    else:
        print(f"   {years_needed:.2e} tahun (sangat tidak realistis)")
    
    print("\n💡 SARAN:")
    print("   • Fokus pada range yang terbatas (puzzle transactions)")
    print("   • Cek database known weak keys (brain wallets)")
    print("   • Gunakan GPU computing untuk percepatan 100-1000x")
    print("="*60)


def worker(worker_id, mode, shared_counter, targets, stats_queue, stop_event):
    """
    Proses worker untuk generate dan cek private key
    Menggunakan batch processing untuk efisiensi
    
    Args:
        worker_id (int): ID worker
        mode (str): '1' sequential, '2' random
        shared_counter: Counter bersama untuk mode sequential
        targets (set): Set address target
        stats_queue: Queue untuk update statistik
        stop_event: Event untuk signal berhenti
    """
    local_count = 0
    error_count = 0
    max_errors = 1000
    batch_size = 100
    weak_check_interval = 10000
    
    # Konversi targets ke set untuk O(1) lookup
    targets_set = set(targets)
    
    # Untuk logging error
    error_log_interval = 100
    
    while not stop_event.is_set():
        # Generate batch values
        values = []
        for _ in range(batch_size):
            if mode == '1':
                with shared_counter.get_lock():
                    shared_counter.value += 1
                    val = shared_counter.value
                    # Wrap around jika mencapai batas
                    if val > HIGH_LIMIT:
                        shared_counter.value = LOW_LIMIT
                        val = LOW_LIMIT
            else:
                val = random.randint(LOW_LIMIT, HIGH_LIMIT)
            values.append(val)
        
        # Proses batch
        for val in values:
            hex_key = format(val, '064x')
            
            # Generate address
            addr = key_to_legacy_addr(hex_key)
            
            if addr is None:
                error_count += 1
                if error_count % error_log_interval == 0:
                    # Log setiap 100 error
                    pass
                if error_count >= max_errors:
                    print(f"\n[!] Worker {worker_id}: Terlalu banyak error ({error_count}), berhenti.")
                    stats_queue.put(local_count)
                    return
                continue
            
            local_count += 1
            
            # Cek weak pattern secara periodik
            if local_count % weak_check_interval == 0:
                if check_weak_pattern(hex_key):
                    # Simpan ke file untuk analisis
                    try:
                        with open("weak_patterns.log", "a") as f:
                            f.write(f"{hex_key}\n")
                    except:
                        pass
            
            # Cek apakah address ditemukan di target
            if addr in targets_set:
                # Format hasil
                result = (
                    f"\n{'='*60}\n"
                    f"[!!!] FOUND BY WORKER {worker_id}!\n"
                    f"{'='*60}\n"
                    f"Private Key (hex): {hex_key}\n"
                    f"Private Key (dec): {val}\n"
                    f"Address: {addr}\n"
                    f"Keys checked by this worker: {local_count}\n"
                    f"Total errors: {error_count}\n"
                    f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"{'='*60}\n"
                )
                
                # Simpan ke file
                try:
                    with open("FOUND.txt", "a") as f:
                        f.write(result)
                except:
                    print("\n[!] Gagal menulis ke file FOUND.txt")
                
                print(result)
                stop_event.set()
                return
            
            # Progress reporting
            if local_count >= 5000:
                stats_queue.put(local_count)
                local_count = 0
        
        # Cek error rate per batch
        if error_count > max_errors:
            print(f"\n[!] Worker {worker_id}: Error limit exceeded ({error_count})")
            stats_queue.put(local_count)
            return


def main():
    """Fungsi utama program"""
    print("\n" + "="*60)
    print("🚀 BITCOIN LEGACY ADDRESS RECOVERY TOOL")
    print("="*60)
    print("Mencari address P2PKH (dimulai dengan '1')")
    print("Versi: 1.0.0")
    print("="*60 + "\n")
    
    # Load dan validasi target
    target_file = "Rich_P2PKH.txt"
    print(f"[*] Memuat file target: {target_file}")
    target_set = load_legacy_targets(target_file)
    
    # Tampilkan sample target
    print("\n[*] Sample target addresses:")
    for i, addr in enumerate(list(target_set)[:5]):
        print(f"    {i+1}. {addr}")
    if len(target_set) > 5:
        print(f"    ... dan {len(target_set)-5} lainnya")
    
    # Konfigurasi CPU
    total_cpu = cpu_count()
    print(f"\n[*] Detected {total_cpu} CPU cores")
    
    while True:
        try:
            use_cores = int(input(f"[?] Jumlah core yang digunakan (1-{total_cpu}): ").strip())
            if 1 <= use_cores <= total_cpu:
                break
            print(f"[-] Masukkan angka antara 1-{total_cpu}")
        except (ValueError, KeyboardInterrupt):
            print("\n[!] Input tidak valid, menggunakan 1 core")
            use_cores = 1
            break
    
    # Pilih mode
    while True:
        mode = input("[?] Mode [1] Sequential [2] Random: ").strip()
        if mode in ('1', '2'):
            break
        print("[-] Pilih 1 atau 2!")
    
    print(f"\n[*] Starting with {use_cores} cores...")
    print(f"[*] Mode: {'SEQUENTIAL' if mode == '1' else 'RANDOM'}")
    print("[*] Press Ctrl+C to stop\n")
    
    # Shared resources
    shared_val = Value('q', LOW_LIMIT)
    stats_queue = Queue()
    stop_event = Event()
    
    # Start workers
    processes = []
    for i in range(use_cores):
        p = Process(
            target=worker,
            args=(i, mode, shared_val, target_set, stats_queue, stop_event)
        )
        p.daemon = True
        p.start()
        processes.append(p)
        print(f"[*] Worker {i} started")
    
    # Tracking statistics
    total_checked = 0
    start_time = time.time()
    last_estimate_time = time.time()
    estimate_interval = 30  # Tampilkan estimasi setiap 30 detik
    
    try:
        while not stop_event.is_set():
            # Update stats
            while not stats_queue.empty():
                try:
                    total_checked += stats_queue.get_nowait()
                except:
                    break
            
            # Calculate speed
            elapsed = time.time() - start_time
            speed = total_checked / elapsed if elapsed > 0 else 0
            
            # Tampilkan progress
            print(
                f"\r[{time.strftime('%H:%M:%S')}] "
                f"Checked: {total_checked:,} | "
                f"Speed: {speed:,.0f} keys/s | "
                f"Cores: {use_cores} | "
                f"Time: {elapsed:.0f}s",
                end=""
            )
            
            # Tampilkan estimasi setiap interval
            if time.time() - last_estimate_time > estimate_interval:
                last_estimate_time = time.time()
                estimate_time(speed, len(target_set))
            
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n[!] Stopping workers...")
        stop_event.set()
    
    # Cleanup
    print("[*] Menunggu worker berhenti...")
    for p in processes:
        p.join(timeout=2)
        if p.is_alive():
            p.terminate()
    
    # Final stats
    elapsed = time.time() - start_time
    speed = total_checked / elapsed if elapsed > 0 else 0
    
    print("\n" + "="*60)
    print("📊 FINAL STATISTICS")
    print("="*60)
    print(f"[*] Total keys checked: {total_checked:,}")
    print(f"[*] Total waktu: {elapsed:.2f} detik")
    print(f"[*] Rata-rata kecepatan: {speed:,.0f} keys/s")
    print(f"[*] Target addresses: {len(target_set):,}")
    
    if os.path.exists("FOUND.txt"):
        print("\n✅ File FOUND.txt telah dibuat")
    else:
        print("\n❌ Tidak menemukan address (belum beruntung)")
    
    print("="*60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Program dihentikan oleh user")
        sys.exit(0)
    except Exception as e:
        print(f"\n[!] Error tidak terduga: {e}")
        sys.exit(1)