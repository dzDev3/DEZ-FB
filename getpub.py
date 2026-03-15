import requests

session = requests.Session()
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "id,en-US;q=0.7,en;q=0.3",
}

# Halaman login Facebook pasti memuat Public Key RSA terbaru
r = session.get("https://www.facebook.com/login/", headers=headers, timeout=10)

# Cari blok "publicKey" (persis di dalam tag <script> halaman FB)
if "publicKey" in r.text:
    idx = r.text.find('"publicKey":"') + 13
    pub_key = r.text[idx:r.text.find('"', idx)]
    
    idx2 = r.text.find('"keyId":') + 8
    key_id = r.text[idx2:r.text.find(',', idx2)]
    
    print(f"[KEY ID]    : {key_id}")
    print(f"[PUBLIC KEY]: {pub_key[:80]}...")  # tampilkan 80 karakter pertama
else:
    print("Tidak ditemukan - coba pakai proxy atau User-Agent berbeda")
