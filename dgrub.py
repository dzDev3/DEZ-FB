import requests
import json
import time
import re
import sys
import os
import concurrent.futures

# --- KONFIGURASI STATIS ---
CLIENT_DOC_ID = "3718233543435848979127405069"
USER_AGENT_API = "[FBAN/FB4A;FBAV/548.1.0.51.64;FBBV/882676621;FBDM/{density=2.0,width=720,height=1184};FBLC/id_ID;FBRV/894237573;FBCR/XL;FBMF/unknown;FBBD/Android;FBPN/com.facebook.katana;FBDV/Phh-Treble vanilla;FBSV/10;FBOP/1;FBCA/arm64-v8a:;]"
COOKIE_FILE = "saved_cookie.txt"

# Vairabel global untuk tracking
total_dumped = 0
is_finished = False

def save_cookie(cookie):
    """Menyimpan cookie ke file lokal."""
    try:
        with open(COOKIE_FILE, "w", encoding="utf-8") as f:
            f.write(cookie)
        print(f"[*] Cookie berhasil disimpan ke {COOKIE_FILE}")
    except Exception as e:
        print(f"[!] Gagal menyimpan cookie: {e}")

def load_cookie():
    """Memuat cookie dari file lokal jika ada."""
    if os.path.exists(COOKIE_FILE):
        try:
            with open(COOKIE_FILE, "r", encoding="utf-8") as f:
                cookie = f.read().strip()
            if cookie:
                print(f"[*] Menemukan cookie tersimpan: {cookie[:30]}...")
                return cookie
        except:
            pass
    return None

def get_access_token(cookie):
    """Mengekstrak access token dari berbagai endpoint (Ads Manager & Business Suite)."""
    print("[*] Sedang mencoba mendapatkan access token secara otomatis...")
    
    # Header yang lebih lengkap untuk meniru browser sungguhan
    headers = {
        "Cookie": cookie,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "referer": "https://www.facebook.com/",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin"
    }
    
    # 1. Coba lewat Ads Manager (Metode paling ampuh untuk token EAAB)
    try:
        print("[*] Mencoba lewat Ads Manager...")
        r1 = requests.get("https://www.facebook.com/adsmanager/manage/campaigns", headers=headers, timeout=15)
        # Cari token EAAB dalam source code
        token = re.search(r'accessToken\s*:\s*["\'](EAAB\w+)["\']', r1.text)
        if token:
            print(f"[+] Berhasil mendapatkan token EAAB dari Ads Manager!")
            return token.group(1)
            
        # Jika EAAB tidak ada, cari token lain (EAA...) dalam window object
        token = re.search(r'["\'](EAA\w+)["\']', r1.text)
        if token:
            print(f"[+] Berhasil mendapatkan token dari Ads Manager!")
            return token.group(1)
    except:
        pass

    # 2. Coba lewat Business Suite (EAAG/EAAI)
    endpoints = [
        "https://business.facebook.com/business_locations",
        "https://business.facebook.com/settings/people/"
    ]
    
    for url in endpoints:
        try:
            print(f"[*] Mencoba lewat {url.split('/')[2]}...")
            r2 = requests.get(url, headers=headers, timeout=15)
            # Cari token EAAG atau sejenisnya
            token = re.search(r'(EAAG\w+|EAAI\w+|EAAAA\w+|EAAC\w+)', r2.text)
            if token:
                print(f"[+] Berhasil mendapatkan token dari {url.split('/')[2]}!")
                return token.group(1)
        except:
            continue
            
    # 3. Terakhir, coba grab dari window.__accessToken di home (jika ada)
    try:
        r3 = requests.get("https://www.facebook.com/", headers=headers, timeout=10)
        token = re.search(r'["\']accessToken["\']\s*:\s*["\'](EAA\w+)["\']', r3.text)
        if token:
            print(f"[+] Berhasil menemukan token di halaman utama!")
            return token.group(1)
    except:
        pass
        
    print("[!] Semua metode otomatis gagal. Gunakan token dari Reqable secara manual.")
    return None

def fetch_members_page(cookie, token, group_id, after_cursor, file_lock, f):
    """Mengambil satu halaman dan menyimpannya (untuk digunakan oleh thread)."""
    global total_dumped, is_finished
    
    if is_finished:
        return None
        
    url = "https://graph.facebook.com/graphql"
    
    headers = {
        "Authorization": f"OAuth {token}",
        "User-Agent": USER_AGENT_API,
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Cookie": cookie
    }
    
    variables = {
        "include_member_list_addon": True,
        "fetch_view_only_members": True,
        "group_member_profiles_connection_after_cursor": after_cursor,
        "group_view_only_members_pagination_at_stream_initial_count": 1,
        "paginationPK": group_id,
        "group_member_profiles_connection_at_stream_use_customized_batch": False,
        "should_use_consolidated_button": True,
        "group_member_profiles_connection_first": 200, # Maksimalkan per halaman jika didukung
        "profile_image_size": 128,
        "group_view_only_members_pagination_at_stream_use_customized_batch": False,
        "group_view_only_members_pagination_at_stream_enabled": False,
        "group_id": group_id
    }
    
    payload = {
        "method": "post",
        "pretty": "false",
        "format": "json",
        "server_timestamps": "true",
        "locale": "id_ID",
        "purpose": "fetch",
        "fb_api_req_friendly_name": "FetchGroupMemberListRecentlyJoined_At_Connection_Pagination_Group_group_member_profiles_connection",
        "fb_api_caller_class": "AtConnection",
        "client_doc_id": CLIENT_DOC_ID,
        "variables": json.dumps(variables)
    }
    
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=20)
        response.raise_for_status()
        data = response.json()
        
        group_data = data.get("data", {}).get("fetch__Group", {})
        member_profiles = group_data.get("group_member_profiles", {})
        edges = member_profiles.get("edges", [])
        
        if not edges:
            is_finished = True
            return None
        
        local_count = 0
        with file_lock:
            for edge in edges:
                node = edge.get("node", {})
                uid = node.get("id")
                name = node.get("name")
                if uid and name:
                    f.write(f"{uid}|{name}\n")
                    local_count += 1
            f.flush()
            total_dumped += local_count
            sys.stdout.write(f"\r[+] Berhasil dump {total_dumped} anggota... ")
            sys.stdout.flush()
            
        page_info = member_profiles.get("page_info", {})
        if not page_info.get("has_next_page"):
            is_finished = True
            return None
            
        return page_info.get("end_cursor")
        
    except Exception as e:
        print(f"\n[!] Error saat mengambil data (mungkin limit): {e}")
        # Jika error, beri sedikit jeda sebelum thread lain mencoba
        time.sleep(2)
        return None

def main():
    global total_dumped, is_finished
    print("="*40)
    print("   FACEBOOK GROUP ID DUMPER (THREADS)   ")
    print("="*40)
    
    # Auto-load cookie
    saved_cookie = load_cookie()
    cookie = ""
    
    if saved_cookie:
        use_saved = input(f"[?] Gunakan cookie tersimpan? (y/n) [y]: ").strip().lower()
        if use_saved != 'n':
            cookie = saved_cookie
            
    if not cookie:
        cookie = input("[?] Masukkan Cookie Facebook: ").strip()
        if not cookie:
            print("[!] Cookie tidak boleh kosong!")
            return
        # Save new cookie
        save_cookie(cookie)
        
    group_id = input("[?] Masukkan ID Grup FB: ").strip()
    if not group_id:
        print("[!] ID Grup tidak boleh kosong!")
        return

    # Ambil token otomatis
    token = get_access_token(cookie)
    if not token:
        token = input("[?] (Fallback) Masukkan Access Token (EAA...) manual: ").strip()
        if not token:
            print("[!] Token diperlukan untuk melanjutkan.")
            return
            
    try:
        max_threads = int(input("[?] Masukkan jumlah thread (rekomendasi: 5-10): ").strip() or "5")
    except:
        max_threads = 5
        print("[*] Menggunakan default 5 thread.")

    print(f"\n[*] Memulai dump untuk Grup ID: {group_id} dengan {max_threads} thread")
    filename = f"dump_{group_id}.txt"
    
    # Karena API berbasis kursor sequential, kita tidak bisa request halaman acak.
    # Namun kita bisa mempercepat proses fetching halaman berikutnya segera setelah
    # kursor halaman saat ini didapatkan, overlap request.
    
    try:
        import threading
        file_lock = threading.Lock()
        
        with open(filename, "a", encoding="utf-8") as f:
            current_cursor = None
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
                # Loop utama untuk mensubmit tugas
                while not is_finished:
                    # Jalankan request, tapi kita butuh cursor berurutan
                    # Ini sedikit tricky dengan cursor-based pagination
                    # Pendekatan: Fetch cursor, submit task berikutnya
                    
                    # Fetching (ini akan blocking sampai satu page selesai jika kita butuh cursornya)
                    # Karena GraphQL FB *sangat* butuh 'after' cursor, parallel murni sulit.
                    # Kita modifikasi: submit satu persatu, eksekusi dalam thread
                    
                    future = executor.submit(fetch_members_page, cookie, token, group_id, current_cursor, file_lock, f)
                    next_cursor = future.result() # Wait for cursor
                    
                    if next_cursor:
                        current_cursor = next_cursor
                    else:
                        break # is_finished true or error
                        
                    # Note: murni parallel fetching GraphQL butuh offset (first:200, skip:400)
                    # tapi FB pakai start_cursor/end_cursor.
                    # Penggunaan thread di sini lebih mengurangi bottleneck I/O saat file writing/parsing.
                        
    except KeyboardInterrupt:
        print("\n[!] Dihentikan oleh pengguna.")
        is_finished = True
    except Exception as e:
        print(f"\n[!] Error utama: {e}")

    print(f"\n[*] Selesai. Total ID yang di-dump: {total_dumped}")
    print(f"[*] Hasil tersimpan di: {filename}")

if __name__ == "__main__":
    main()
