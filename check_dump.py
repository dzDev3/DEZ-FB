import json
import urllib.parse

# String variables dari dump v544 (decoded)
encoded_vars = "params%7B%22params%22%3A%7B%22params%22%3A%22%7B%5C%22params%5C%22%3A%5C%22%7B%5C%5C%5C%22server_params%5C%5C%5C%22%3A%7B%5C%5C%5C%22device_id%5C%5C%5C%22%3A%5C%5C%5C%22983256cd-997b-4374-bcc3-c92bf8bdaa60%5C%5C%5C%22%2C%5C%5C%5C%22server_login_source%5C%5C%5C%22%3A%5C%5C%5C%22login%5C%5C%5C%22%2C%5C%5C%5C%22waterfall_id%5C%5C%5C%22%3A%5C%5C%5C%225cfef83a-25a0-4e92-a681-d874e7dd1cbe%5C%5C%5C%22%2C%5C%5C%5C%22attestation_result%5C%5C%5C%22%3A%7B%5C%5C%5C%22errorMessage%5C%5C%5C%22%3A%5C%5C%5C%22KeyAttestationException%3A+No+key+found!%5C%5C%5C%22%7D%2C%5C%5C%5C%22machine_id%5C%5C%5C%22%3A%5C%5C%5C%22%5C%5C%5C%22%2C%5C%5C%5C%22from_native_screen%5C%5C%5C%22%3Atrue%2C%5C%5C%5C%22credential_type%5C%5C%5C%22%3A%5C%5C%5C%22password%5C%5C%5C%22%2C%5C%5C%5C%22password%5C%5C%5C%22%3A%5C%5C%5C%22%23PWD_ENC...%5C%5C%5C%22%2C%5C%5C%5C%22try_num%5C%5C%5C%22%3A%5C%5C%5C%221%5C%5C%5C%22%2C%5C%5C%5C%22family_device_id%5C%5C%5C%22%3A%5C%5C%5C%2211ce8f7e-a894-4264-89e6-6b9b5c183622%5C%5C%5C%22%2C%5C%5C%5C%22event_flow%5C%5C%5C%22%3A%5C%5C%5C%22login_manual%5C%5C%5C%22%2C%5C%5C%5C%22event_step%5C%5C%5C%22%3A%5C%5C%5C%22home_page%5C%5C%5C%22%2C%5C%5C%5C%22is_from_logged_in_switcher%5C%5C%5C%22%3Afalse%2C%5C%5C%5C%22contact_point%5C%5C%5C%22%3A%5C%5C%5C%22saputrax410%40gmail.com%5C%5C%5C%22%7D%7D%5C%22%7D%22%2C%22bloks_versioning_id%22%3A%226dcff2f1522756669e85e348a541dcfcb9a4478ef7ce18b4132a7ebb177a99f1%22%2C%22app_id%22%3A%22com.bloks.www.bloks.caa.login.async.send_login_request%22%7D%2C%22scale%22%3A%222%22%2C%22nt_context%22%3A%7B%22using_white_navbar%22%3Atrue%2C%22styles_id%22%3A%2256749ebea2452a6119a9d01ce0f1bd9e%22%2C%22pixel_ratio%22%3A2%2C%22is_push_on%22%3Atrue%2C%22debug_tooling_metadata_token%22%3Anull%2C%22is_flipper_enabled%22%3Afalse%2C%22theme_params%22%3A%5B%7B%22value%22%3A%5B%5D%2C%22design_system_name%22%3A%22FDS%22%7D%5D%2C%22bloks_version%22%3A%226dcff2f1522756669e85e348a541dcfcb9a4478ef7ce18b4132a7ebb177a99f1%22%7D%7D"

# Perbaiki string karena ada potongan 'params' di depan
pure_json_str = urllib.parse.unquote(encoded_vars.split("variables=")[-1])
if pure_json_str.startswith("params{"): pure_json_str = pure_json_str[6:]

try:
    data = json.loads(pure_json_str)
    print("KEYS LEVEL 1:", list(data.keys()))
    print("TYPES LEVEL 1:")
    for k, v in data.items():
        print(f"  {k}: {type(v).__name__}")
    
    print("\nCONTENT OF 'params':", list(data['params'].keys()))
    print("TYPE OF 'params['params']':", type(data['params']['params']).__name__)
    
    # BEDAH INNER PARAMS
    p2 = json.loads(data['params']['params'])
    print("\nKEYS LEVEL 2 (from middle_params):", list(p2.keys()))
    
    p3 = json.loads(p2['params'])
    print("\nKEYS LEVEL 3 (from inner_params):", list(p3.keys()))
    
except Exception as e:
    print(f"Error parsing dump: {e}")
    # Jika gagal, tampilkan string bersihnya
    print(f"Clean string: {pure_json_str[:100]}...")
