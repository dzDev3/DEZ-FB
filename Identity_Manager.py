"""
Identity_Manager.py
====================
Tool OTOMATIS untuk menangkap identitas FB dari HP Android Anda (1 kali tangkap, 
auto-simpan ke identity.json, lalu dipakai terus oleh Konsep_Cracking_Dynamic.py).

CARA PAKAI:
1. Pastikan HP terhubung via USB + Frida Server berjalan di HP
2. Buka terminal: python Identity_Manager.py
3. Di HP, buka aplikasi Facebook dan coba LOGIN (meskipun salah password tidak apa)
4. Tekan ENTER di terminal untuk selesai dan menyimpan hasil
5. File identity.json akan dibuat otomatis
6. Konsep_Cracking_Dynamic.py akan membaca dari identity.json secara otomatis
"""

import frida
import sys
import time
import json
import os
import re
import threading

PACKAGE_NAME = "com.facebook.katana"
IDENTITY_FILE = "identity.json"

# Storage untuk menampung data yang ditangkap
captured = {
    "device_id": None,
    "family_device_id": None,
    "machine_id": None,
    "usdid": None,
    "zca": None,
    "attestation": None,
    "user_agent": None,
    "capture_time": None
}

def print_status():
    """Cetak status identitas yang sudah berhasil ditangkap."""
    print("\n" + "="*55)
    print("  STATUS IDENTITAS YANG BERHASIL DITANGKAP")
    print("="*55)
    status_items = {
        "device_id": "Device ID",
        "family_device_id": "Family Device ID",
        "machine_id": "Machine ID (x-fb-integrity-machine-id)",
        "usdid": "USDID (x-meta-usdid)",
        "zca": "ZCA (x-meta-zca)",
        "attestation": "Attestation Result",
        "user_agent": "User-Agent"
    }
    for key, label in status_items.items():
        val = captured[key]
        if val:
            short = str(val)[:50] + "..." if len(str(val)) > 50 else str(val)
            print(f"  [✓] {label}: {short}")
        else:
            print(f"  [✗] {label}: BELUM DITANGKAP")
    print("="*55 + "\n")

def on_message(message, data):
    """Callback ketika Frida mengirim pesan."""
    if message['type'] == 'send':
        payload = message['payload']
        print(f"[CAPTURE] {payload}")
        
        # Parsing: PREF-GET device_id
        if "[PREF-GET] Key: DEVICE_ID" in payload or "[PREF-GET] Key: device_id" in payload:
            m = re.search(r'Value:\s*([0-9a-f\-]{36})', payload)
            if m and not captured["device_id"]:
                captured["device_id"] = m.group(1)
                print(f"  >> [GOT] device_id = {captured['device_id']}")
        
        # Parsing: PREF-GET family_device_id
        if "family_device_id" in payload.lower() and "[PREF-GET]" in payload:
            m = re.search(r'Value:\s*([0-9a-f\-]{36})', payload)
            if m and not captured["family_device_id"]:
                captured["family_device_id"] = m.group(1)
                print(f"  >> [GOT] family_device_id = {captured['family_device_id']}")

        # Parsing: JSON-PUT device_id
        if "[JSON-PUT] Key: device_id" in payload:
            m = re.search(r'Value:\s*([0-9a-f\-]{36})', payload)
            if m and not captured["device_id"]:
                captured["device_id"] = m.group(1)
                print(f"  >> [GOT] device_id (JSON) = {captured['device_id']}")

        # Parsing: JSON-PUT family_device_id
        if "[JSON-PUT] Key: family_device_id" in payload:
            m = re.search(r'Value:\s*([0-9a-f\-]{36})', payload)
            if m and not captured["family_device_id"]:
                captured["family_device_id"] = m.group(1)
                print(f"  >> [GOT] family_device_id (JSON) = {captured['family_device_id']}")

        # Parsing: JSON-PUT attestation_result
        if "[JSON-PUT] Key: attestation_result" in payload or "[JSON-PUT] Key: attestation" in payload:
            m = re.search(r'Value:\s*(\{.*\})', payload)
            if m and not captured["attestation"]:
                try:
                    captured["attestation"] = json.loads(m.group(1))
                    print(f"  >> [GOT] attestation_result!")
                except:
                    captured["attestation"] = m.group(1)

        # Parsing: HEADER machine-id
        if "[HEADER-SEND] x-fb-integrity-machine-id" in payload:
            m = re.search(r'x-fb-integrity-machine-id:\s*(\S+)', payload, re.IGNORECASE)
            if m and not captured["machine_id"]:
                captured["machine_id"] = m.group(1)
                print(f"  >> [GOT] machine_id = {captured['machine_id']}")

        # Parsing: HEADER usdid
        if "[HEADER-SEND] x-meta-usdid" in payload:
            m = re.search(r'x-meta-usdid:\s*(\S+)', payload, re.IGNORECASE)
            if m and not captured["usdid"]:
                captured["usdid"] = m.group(1)
                print(f"  >> [GOT] usdid = {captured['usdid'][:30]}...")

        # Parsing: HEADER zca
        if "[HEADER-SEND] x-meta-zca" in payload:
            m = re.search(r'x-meta-zca:\s*(\S+)', payload, re.IGNORECASE)
            if m and not captured["zca"]:
                captured["zca"] = m.group(1)
                print(f"  >> [GOT] zca = {captured['zca'][:30]}...")

        # Parsing: User-Agent
        if "[HEADER-SEND] user-agent" in payload.lower():
            m = re.search(r'user-agent:\s*(FBAN.*?)$', payload, re.IGNORECASE)
            if m and not captured["user_agent"]:
                captured["user_agent"] = m.group(1)
                print(f"  >> [GOT] user_agent!")

def save_identity():
    """Simpan identitas yang sudah ditangkap ke identity.json."""
    captured["capture_time"] = int(time.time())
    
    # Hitung kelengkapan
    required = ["device_id", "family_device_id", "machine_id", "usdid", "attestation"]
    ok = [k for k in required if captured[k]]
    
    with open(IDENTITY_FILE, "w") as f:
        json.dump(captured, f, indent=2)
    
    print(f"\n[+] Identitas disimpan ke: {IDENTITY_FILE}")
    print(f"[+] Kelengkapan data: {len(ok)}/{len(required)} item kritikal tertangkap")
    
    missing = [k for k in required if not captured[k]]
    if missing:
        print(f"[!] Data berikut BELUM tertangkap: {', '.join(missing)}")
        print(f"[!] Tip: Pastikan Anda menekan tombol LOGIN di FB saat capture berjalan!")
    else:
        print(f"[+] SEMUA DATA KRITIKAL BERHASIL DITANGKAP! Siap digunakan.")

def main():
    print("=" * 60)
    print("  IDENTITY MANAGER - FB Auto Capture Tool")
    print("=" * 60)
    print()
    
    # Cek status identity.json yang sudah ada
    if os.path.exists(IDENTITY_FILE):
        with open(IDENTITY_FILE) as f:
            existing = json.load(f)
        cap_time = existing.get("capture_time", 0)
        age_hours = (time.time() - cap_time) / 3600
        print(f"[!] File {IDENTITY_FILE} sudah ada (Umur: {age_hours:.1f} jam)")
        print(f"    Machine ID: {existing.get('machine_id', 'N/A')}")
        print(f"    USDID: {str(existing.get('usdid', 'N/A'))[:30]}...")
        print()
        jawab = input("Apakah Anda ingin ULANG TANGKAP identitas baru? (y/n): ").strip().lower()
        if jawab != 'y':
            print("[*] Menggunakan identitas lama. Selesai!")
            print_status()
            return
    
    # --- PILIH MODE KONEKSI ---
    print("Pilih metode koneksi ke HP (sama seperti yg biasa Anda pakai):")
    print("  1. USB langsung (kabel USB)")
    print("  2. TCP/Socket - localhost (via adb forward atau adb connect)")
    print("  3. TCP/Socket - IP lain (misal WiFi / IP HP langsung)")
    mode = input("Pilih (1/2/3) [default=2]: ").strip() or "2"

    device = None
    
    if mode == "1":
        try:
            device = frida.get_usb_device()
            print(f"[+] HP Terdeteksi (USB): {device.name}")
        except Exception as e:
            print(f"[x] Gagal USB: {e}")
            print("[!] Coba pilih mode 2 jika HP pakai ADB forward atau adb connect")
            return
            
    elif mode == "2":
        # Mode TCP via localhost (adb forward tcp:27042 tcp:27042)
        port = input("Masukan PORT frida-server (default: 27042): ").strip() or "27042"
        host = f"127.0.0.1:{port}"
        try:
            dm = frida.get_device_manager()
            device = dm.add_remote_device(host)
            print(f"[+] Terhubung via TCP localhost: {device.name}")
        except Exception as e:
            print(f"[x] Gagal TCP localhost:{port}: {e}")
            print(f"    Jalankan di PC: adb forward tcp:{port} tcp:{port}")
            return
            
    elif mode == "3":
        host = input("Masukan IP:PORT HP (contoh: 192.168.1.100:27042): ").strip()
        if not host:
            host = "192.168.1.100:27042"
        try:
            dm = frida.get_device_manager()
            device = dm.add_remote_device(host)
            print(f"[+] Terhubung via TCP {host}: {device.name}")
        except Exception as e:
            print(f"[x] Gagal TCP {host}: {e}")
            print("    Pastikan frida-server berjalan di HP dan di network yang sama")
            return

    if device is None:
        print("[x] Tidak berhasil terhubung ke HP!")
        return

    print("[*] Menghubungkan ke aplikasi Facebook...")
    session = None
    try:
        # Mencoba ATTACH terlebih dahulu (jika aplikasi sudah terbuka di layar)
        print(f"[*] Mencoba menempel (attaching) ke {PACKAGE_NAME}...")
        session = device.attach(PACKAGE_NAME)
        print("[+] Berhasil menempel ke proses yang berjalan.")
    except frida.ProcessNotFoundError:
        # Jika tidak ada, baru coba SPAWN
        print(f"[*] Aplikasi tidak ditemukan berjalan, mencoba men-spawn...")
        try:
            pid = device.spawn([PACKAGE_NAME])
            session = device.attach(pid)
            device.resume(pid)
            print("[+] Berhasil men-spawn aplikasi.")
        except Exception as e:
            print(f"[x] Gagal spawn FB: {e}")
            print("[!] Tips: Buka aplikasi Facebook di HP Anda secara MANUAL, lalu jalankan script ini lagi.")
            return
    except Exception as e:
        print(f"[x] Gagal attach/spawn: {e}")
        return

    if not session:
        print("[x] Gagal mendapatkan session Frida.")
        return

    script_code = """
    Java.perform(function() {
        console.log("=== IDENTITY CAPTURE AKTIF ===");

        // Hook SharedPreferences (membaca ID lokal)
        var SharedPreferencesImpl = Java.use('android.app.SharedPreferencesImpl');
        SharedPreferencesImpl.getString.implementation = function(key, defValue) {
            var res = this.getString(key, defValue);
            if (key) {
                var k = key.toLowerCase();
                if (k.indexOf('device_id') !== -1 || k.indexOf('family_device') !== -1 ||
                    k.indexOf('usdid') !== -1 || k.indexOf('machine') !== -1) {
                    send("[PREF-GET] Key: " + key + " | Value: " + res);
                }
            }
            return res;
        };

        // Hook JSONObject (merakit JSON payload)
        var JSONObject = Java.use('org.json.JSONObject');
        JSONObject.put.overload('java.lang.String', 'java.lang.Object').implementation = function(key, value) {
            if (key) {
                var k = key.toLowerCase();
                if (k.indexOf('device_id') !== -1 || k.indexOf('family_device') !== -1 ||
                    k.indexOf('attest') !== -1 || k.indexOf('usdid') !== -1) {
                    var v = (value !== null) ? value.toString() : "null";
                    send("[JSON-PUT] Key: " + key + " | Value: " + v);
                }
            }
            return this.put(key, value);
        };

        // Hook OkHttp3 Headers (saat REQUEST dikirim ke server FB)
        try {
            var Builder = Java.use('okhttp3.Request$Builder');
            Builder.addHeader.implementation = function(name, value) {
                var n = name.toLowerCase();
                if (n.indexOf('usdid') !== -1 || n.indexOf('zca') !== -1 ||
                    n.indexOf('machine-id') !== -1 || n.indexOf('machine_id') !== -1 ||
                    n === 'user-agent') {
                    send("[HEADER-SEND] " + name + ": " + value);
                }
                return this.addHeader(name, value);
            };
        } catch(e) { console.log("OkHttp3 hook error: " + e); }

        // SSL Bypass
        try {
            var TrustManagerImpl = Java.use('com.android.org.conscrypt.TrustManagerImpl');
            TrustManagerImpl.checkTrustedRecursive.implementation = function() {
                return Java.use("java.util.ArrayList").$new();
            };
        } catch(e) {}

        console.log("[!] APP JALAN. Silakan buka dan LOGIN di FB di HP Anda...");
    });
    """

    try:
        script = session.create_script(script_code)
        script.on('message', on_message)
        script.load()
        device.resume(pid)
    except Exception as e:
        print(f"[x] Gagal memuat script Frida: {e}")
        return

    print()
    print("[!] ===== INSTRUKSI UNTUK ANDA =====")
    print("    1. Di HP Anda, BUKA aplikasi Facebook")
    print("    2. Masukkan email/no HP dan password, lalu TEKAN TOMBOL LOGIN")
    print("    3. Tunggu sampai proses login selesai (berhasil atau gagal tidak apa)")
    print("    4. Kembali ke terminal ini dan tekan ENTER untuk SIMPAN identitas")
    print("=" * 60)
    print("[*] Menunggu data identitas dari HP... (Tekan ENTER untuk simpan dan keluar)")
    print()
    
    input()  # Tunggu user tekan ENTER
    
    print_status()
    save_identity()
    print(f"\n[+] Sekarang Konsep_Cracking_Dynamic.py akan otomatis membaca dari {IDENTITY_FILE}")
    print(f"[+] Jalankan: python Konsep_Cracking_Dynamic.py")

if __name__ == "__main__":
    main()
