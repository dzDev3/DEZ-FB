import json
import re

with open("last_response.json", "r", encoding="utf-8") as f:
    res_text = f.read()

print("--- Metoda 7: Deep JSON Parsing ---")
try:
    data = json.loads(res_text)
    # Navigasi ke Bloks Bundle
    bundle_str = data['data']['fb_bloks_action']['root_action']['action']['action_bundle']['bloks_bundle_action']
    bundle_data = json.loads(bundle_str)
    
    # Kadang ada di bloks_payload -> data
    payload = bundle_data.get('layout', {}).get('bloks_payload', {})
    items = payload.get('data', [])
    
    print(f"Items found: {len(items)}")
    
    # Namun cookies biasanya ada di dalam 'action' string yang berisi JSON ter-escape lagi
    # Mari kita cari string JSON di dalam respons mentah secara manual jika navigasi di atas buntu
    # Cara paling sakti: cari substring yang diapit [{"name" ... }]
    match = re.search(r'\[\{[^{}]*name[^{}]*value[^{}]*\}\]', res_text.replace('\\', ''))
    if match:
        print(f"Regex Match on cleaned string: {match.group(0)[:100]}...")
        # Coba parse segment tersebut
        print("Success finding array-like structure!")

except Exception as e:
    print(f"Error in deep parsing: {e}")

# KEMBALI KE REGEX TAPI LEBIH PINTAR
print("\n--- Metoda 8: The Ultimate Cookie Regex ---")
# Kita tangkap pair name dan value secara berdekatan
# Pola: name\": \"(.*?)\", \"value\": \"(.*?)\"
# Kita ignore semua backslash
normalized = res_text.replace('\\', '')
cookie_pairs = re.findall(r'name":"([a-z_]+)","value":"([^"]+)"', normalized)
for n, v in cookie_pairs:
    if n in ["c_user", "xs", "fr", "datr", "sb", "wd", "presence"]:
        print(f"Matched: {n}={v}")
