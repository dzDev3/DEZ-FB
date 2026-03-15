import requests
import json
import time
import re
import sys
import os
import concurrent.futures
import base64

# --- KONFIGURASI STATIS ---
CLIENT_DOC_ID = "2904796126889595781480664706"
USER_AGENT_API = "[FBAN/FB4A;FBAV/548.1.0.51.64;FBBV/882676621;FBDM/{density=2.0,width=720,height=1184};FBLC/id_ID;FBRV/894237573;FBCR/XL;FBMF/unknown;FBBD/Android;FBPN/com.facebook.katana;FBDV/Phh-Treble vanilla;FBSV/10;FBOP/1;FBCA/arm64-v8a:;]"
COOKIE_FILE = "saved_cookie.txt"

# Variabel global untuk tracking
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
    
    headers = {
        "Cookie": cookie,
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "referer": "https://www.facebook.com/",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin"
    }
    
    try:
        print("[*] Mencoba lewat Ads Manager...")
        r1 = requests.get("https://www.facebook.com/adsmanager/manage/campaigns", headers=headers, timeout=15)
        token = re.search(r'accessToken\s*:\s*["\'](EAAB\w+)["\']', r1.text)
        if token:
            print(f"[+] Berhasil mendapatkan token EAAB dari Ads Manager!")
            return token.group(1)
        token = re.search(r'["\'](EAA\w+)["\']', r1.text)
        if token:
            print(f"[+] Berhasil mendapatkan token dari Ads Manager!")
            return token.group(1)
    except:
        pass

    endpoints = [
        "https://business.facebook.com/business_locations",
        "https://business.facebook.com/settings/people/"
    ]
    
    for url in endpoints:
        try:
            print(f"[*] Mencoba lewat {url.split('/')[2]}...")
            r2 = requests.get(url, headers=headers, timeout=15)
            token = re.search(r'(EAAG\w+|EAAI\w+|EAAAA\w+|EAAC\w+)', r2.text)
            if token:
                print(f"[+] Berhasil mendapatkan token dari {url.split('/')[2]}!")
                return token.group(1)
        except:
            continue
            
    try:
        r3 = requests.get("https://www.facebook.com/", headers=headers, timeout=10)
        token = re.search(r'["\']accessToken["\']\s*:\s*["\'](EAA\w+)["\']', r3.text)
        if token:
            print(f"[+] Berhasil menemukan token di halaman utama!")
            return token.group(1)
    except:
        pass
        
    print("[!] Semua metode otomatis gagal. Gunakan token manual jika perlu.")
    return None

def format_feedback_id(feedback_id, cookie=None):
    """
    Format feedback_id agar selalu sesuai dengan standar GraphQL (Base64).
    Jika input berupa Link/URL, skrip akan melacak ID aslinya.
    """
    # 1. Jika URL Facebook, lakukan ekstraksi dari HTML
    if "facebook.com" in feedback_id or "fb.watch" in feedback_id or "http" in feedback_id:
        extracted = get_feedback_id_from_url(feedback_id, cookie)
        if extracted:
            print(f"[+] Berhasil mendapatkan Feedback ID asli: {extracted[:15]}...")
            feedback_id = extracted
        else:
            print("[!] Peringatan: Gagal mengekstrak ID asli dari web FB. Mencoba fallback ke regex.")
            match = re.search(r'story_fbid=([^&]+)', feedback_id)
            if not match: match = re.search(r'fbid=([^&]+)', feedback_id)
            if not match: match = re.search(r'/posts/([^/?]+)', feedback_id)
            if match:
                feedback_id = match.group(1)
                
    # 2. Jika sudah format feedback:<angka> tapi belum encode Base64
    if feedback_id.startswith("feedback:"):
        return base64.b64encode(feedback_id.encode('utf-8')).decode('utf-8'), feedback_id.replace("feedback:", "")
        
    # 3. Jika sepertinya sudah base64 encode dari GraphQL (ZmV...) atau mengandung '=='
    if "==" in feedback_id or feedback_id.startswith("ZmVlZG"):
        return feedback_id, feedback_id[:15] # Berikan bagian depan base64 sbg penanda nama file
        
    # 4. Asumsi murni angka/ID, encode menjadi base64 (contoh: feedback:123456)
    formatted = f"feedback:{feedback_id}"
    return base64.b64encode(formatted.encode('utf-8')).decode('utf-8'), feedback_id


def fetch_reactions_page(cookie, token, formatted_feedback_id, reaction_id, after_cursor, file_lock, f):
    """Mengambil satu halaman reaktor dan menyimpannya (menggunakan thread)."""
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
        "feedback_id": formatted_feedback_id,
        "fetch_invitable_reactor_count": True,
        "reaction_id": reaction_id, # Optional. Jika None/kosong, ambil semua
        "reactors_profile_image_size": 80,
        "reactors_connection_first": 25, # Mengikuti batas payload asli
        "profile_pic_media_type": "image/x-auto",
        "should_use_consolidated_button": True,
        "social_context_render_location": "PROFILE_LIKERS_LIST"
    }

    # Jika pagination (kursor berikutnya)
    if after_cursor:
        variables["reactors_connection_after"] = after_cursor
        
    # Jika tidak mencari spesifik reaksi (semua reaksi)
    if not reaction_id:
        variables.pop("reaction_id", None)
    
    payload = {
        "method": "post",
        "pretty": "false",
        "format": "json",
        "server_timestamps": "true",
        "locale": "id_ID",
        "fb_api_req_friendly_name": "FeedbackReactorsGraphService",
        "fb_api_caller_class": "graphservice",
        "client_doc_id": CLIENT_DOC_ID,
        "fb_api_client_context": '{"is_background":false}',
        "variables": json.dumps(variables)
    }
    
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=20)
        response.raise_for_status()
        data = response.json()
        
        # Sesuai data structure dr Reqable user
        feedback_node = data.get("data", {})
        if feedback_node is None:
            print("\n[!] Error: data.node dari respons kosong (None). Mungkin ID Feedback salah/terhapus, atau akun terlimit.")
            is_finished = True
            return None
            
        node = feedback_node.get("node", {})
        if node is None:
            print("\n[!] Error: Tidak menemukan struktur 'node' di dalam data JSON. ID mungkin salah format.")
            is_finished = True
            return None

        reactors_data = node.get("reactors", {})
        if reactors_data is None:
            # Reaktor dikunci, postingan tidak ada reaksi, atau bukan tipe postingan yang valid
            print("\n[*] Tidak ada data reaktor. Mungkin postingan ini tidak bisa dilohat reaksinya atau 0 reaksi.")
            is_finished = True
            return None

        edges = reactors_data.get("edges", [])
        
        if not edges:
            is_finished = True
            return None
        
        local_count = 0
        with file_lock:
            for edge in edges:
                reactor_node = edge.get("node", {})
                uid = reactor_node.get("id")
                name = reactor_node.get("name")
                if uid and name:
                    f.write(f"{uid}|{name}\n")
                    local_count += 1
            f.flush()
            total_dumped += local_count
            sys.stdout.write(f"\r[+] Berhasil dump {total_dumped} reaktor... ")
            sys.stdout.flush()
            
        page_info = reactors_data.get("page_info", {})
        if not page_info.get("has_next_page"):
            is_finished = True
            return None
            
        return page_info.get("end_cursor")
        
    except Exception as e:
        print(f"\n[!] Error saat mengambil data (limit/error parse): {e}")
        time.sleep(2)
        return None

def main():
    global total_dumped, is_finished
    print("="*50)
    print("   FACEBOOK POST REACTION DUMPER (THREADS)   ")
    print("="*50)
    
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
        save_cookie(cookie)
        
    print("\n[?] Feedback ID bisa berupa deretan Base64 panjang yg didapat dr Reqable,")
    print("    Atau bisa langsung numerik ID Postingan FB biasa.")
    feedback_id = input("[?] Masukkan Feedback ID / Post ID FB: ").strip()
    if not feedback_id:
        print("[!] Feedback ID tidak boleh kosong!")
        return
        
    formatted_res = format_feedback_id(feedback_id, cookie)
    if isinstance(formatted_res, tuple):
        formatted_feedback_id, filename_safe_id = formatted_res
    else:
        formatted_feedback_id = formatted_res
        filename_safe_id = feedback_id.split("=")[0] if "==" in feedback_id else feedback_id

    print("\n[*] Tipe Reaksi (Opsional):")
    print("    1 = Like, 2 = Love, 3 = Wow, 4 = Haha, 7 = Sad, 8 = Angry, 16 = Care")
    print("    (Kosongkan dan tekan Enter untuk mengambil SEMUA Reaksi)")
    
    reaction_input = input("[?] Masukkan ID Reaksi (Opsional): ").strip()
    
    token = get_access_token(cookie)
    if not token:
        token = input("[?] (Fallback) Masukkan Access Token (EAA...) manual: ").strip()
        if not token:
            print("[!] Token diperlukan untuk melanjutkan.")
            return
            
    try:
        max_threads = int(input("\n[?] Masukkan jumlah thread (rekomendasi: 5-10): ").strip() or "5")
    except:
        max_threads = 5
        print("[*] Menggunakan default 5 thread.")

    # Menghilangkan karakter-karakter yang tidak valid untuk nama file Windows/Linux
    filename_safe_id = re.sub(r'[\\/*?:"<>|]', "", filename_safe_id)
    filename = f"reaktor_dump_{filename_safe_id[:30]}.txt"
    print(f"\n[*] Memulai dump reaktor untuk Posting/Feedback tersebut dengan {max_threads} thread")
    
    try:
        import threading
        file_lock = threading.Lock()
        
        with open(filename, "a", encoding="utf-8") as f:
            current_cursor = None
            
            with concurrent.futures.ThreadPoolExecutor(max_workers=max_threads) as executor:
                while not is_finished:
                    future = executor.submit(fetch_reactions_page, cookie, token, formatted_feedback_id, reaction_input, current_cursor, file_lock, f)
                    next_cursor = future.result() 
                    
                    if next_cursor:
                        current_cursor = next_cursor
                    else:
                        break
                        
    except KeyboardInterrupt:
        print("\n\n[!] Dihentikan oleh pengguna.")
        is_finished = True
    except Exception as e:
        print(f"\n[!] Error utama: {e}")

    print(f"\n[*] Selesai. Total ID yang di-dump: {total_dumped}")
    print(f"[*] Hasil tersimpan di: {filename}")

if __name__ == "__main__":
    main()
