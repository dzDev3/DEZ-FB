import requests
import json
import re
from iden import BloksIdentityEngine, FacebookRSAEncrypter

def single_login_test(username, password):
    print(f"[*] Menjalankan test login untuk: {username}")
    
    # 1. Inisialisasi engine
    mesin = BloksIdentityEngine()
    encrypter = FacebookRSAEncrypter()
    
    # 2. Generate data
    password_encoded = encrypter.generate_pwd_enc(password)
    headers = mesin.get_headers()
    
    # Kita perlu menyisipkan username ke dalam payload
    # Di iden.py, contact_point ada di dalam client_input_params
    # Namun saat ini get_payload belum menerima username sebagai argumen
    # Mari kita modifikasi sedikit cara kita memanggilnya atau modifikasi iden.py nanti
    
    # Untuk test ini, kita akan buat payload manual atau modifikasi iden.py agar fleksibel
    # PENTING: Meneruskan username sebagai contact_point agar payload tidak kosong
    payload = mesin.get_payload(password_encoded, contact_point=username)
    
    # Sisipkan username ke dalam payload (karena di iden.py tadi contact_point dikosongkan)
    # Payload dalam format urlencoded, kita tambahkan manual atau replace
    if "contact_point=" in payload:
        # Ini agak tricky karena payload sudah di-encode dan di-json-dump berkali-kali di dalam variables
        # Lebih baik kita perbaiki iden.py agar get_payload menerima username
        pass

    # Debug info diringkas agar tidak berantakan
    print(f"[*] Request Payload : {len(payload)} bytes")
    print(f"[*] Password Format : {password_encoded.split(':')[0]}:{password_encoded.split(':')[1]}")

    print("[*] Mengirim request GraphQL ke b-graph.facebook.com ...")
    
    try:
        response = requests.post(
            "https://b-graph.facebook.com/graphql",
            headers=headers,
            data=payload,
            timeout=15
        )
        
        # Simpan ke file untuk debug bersih
        with open("last_response.json", "w", encoding="utf-8") as f:
            f.write(response.text)
        
        # Logika Parsing Status Login
        res_text = response.text
        
        if "access_token" in res_text:
            print("\n" + "*"*40)
            print(" [ LOGIN BERHASIL / SUCCESS ]")
            print("*"*40)
            try:
                # Cari Token EAAB
                token_match = re.search(r'access_token["\\ :]+(EAAB[A-Za-z0-9]+)', res_text)
                uid_match = re.search(r'uid["\\ :]+(\d+)', res_text)
                
                if uid_match:
                    print(f" [+] UID       : {uid_match.group(1)}")
                if token_match:
                    print(f" [+] Token     : {token_match.group(1)}")
                
                if "session_cookies" in res_text:
                    # Metoda Sakti: Normalisasi string (buang semua backslash)
                    # Ini membuat struktur JSON-like menjadi sangat mudah di-regex
                    norm_text = res_text.replace('\\', '')
                    
                    # Regex mencari pasangan name dan value yang berdekatan
                    cookie_data = re.findall(r'name":"([a-z_]+)","value":"([^"]+)"', norm_text)
                    
                    if cookie_data:
                        # Gabungkan semua cookie yang relevan
                        cookies_list = []
                        for name, value in cookie_data:
                            # Ambil semua cookie yang dikirim FB (biasanya: c_user, xs, fr, datr)
                            if name in ["c_user", "xs", "fr", "datr", "sb", "wd", "presence"]:
                                cookies_list.append(f"{name}={value}")
                        
                        if cookies_list:
                            print(f" [+] Cookies   : {'; '.join(cookies_list)};")
                        else:
                            print(" [+] Cookies   : Terdeteksi tapi gagal diurai.")
                    else:
                        print(" [+] Cookies   : Tidak ditemukan di dalam respons.")
                
            except Exception as e:
                print(f" [-] Gagal parsing detail: {e}")
            print("*"*40 + "\n")
                
        elif "checkpoint" in res_text.lower() or "checkpoint_url" in res_text.lower():
            print("\n[ CHECKPOINT / CP ]")
            print("  - Akun ini butuh verifikasi (Sesi/A2F/TTE).")
            
        elif "e53" in res_text.lower() or "error_message" in res_text.lower():
            print("\n[ FAILED / GAGAL ]")
            print("  - Password salah atau akun tidak ditemukan (Kode: e53).")
            
        else:
            print("\n[ UNKNOWN / RAW RESPONSE ]")
            print("  - Format respons tidak dikenali, silakan cek manual:")
            # Jika ada kode (eXX), tampilkan kodenya
            if "(" in res_text and ")" in res_text:
                try:
                    code = res_text.split('action":"')[1].split('"')[0]
                    print(f"  - Kemungkinan Kode Bloks: {code}")
                except:
                    pass
            print(res_text[:500] + "...")
            
    except Exception as e:
        print(f"[-] Terjadi kesalahan koneksi: {e}")

if __name__ == "__main__":
    # Input data dari terminal
    print("-" * 30)
    user_input = input("[?] Masukkan Target (Format UID|NAMA): ")
    pass_test = input("[?] Masukkan Password: ")
    print("-" * 30)
    
    if not user_input or not pass_test:
        print("[-] Error: Target dan Password tidak boleh kosong.")
    else:
        # Logika Smart Parsing: Ambil NAMA sebagai login target
        if "|" in user_input:
            parts = user_input.split("|")
            uid_test = parts[0]   # UID
            name_test = parts[1] if len(parts) > 1 else ""
            
            # KESALAHAN SEBELUMNYA: Menggunakan Nama ("Shizu Xcz") sebagai login id.
            # Server FB hanya menerima Email, Nomor HP, atau UID.
            # Jadi kita kembalikan email_test ke UID.
            email_test = uid_test 
            
            print(f"[*] Target Nama : {name_test}")
            print(f"[*] Login ID    : {email_test}")
        else:
            email_test = user_input
            
        single_login_test(email_test, pass_test)
