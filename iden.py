import uuid
import json
import urllib.parse
import time
import random
import requests

class FacebookRSAEncrypter:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        }
    def generate_pwd_enc(self, password):
        timestamp = str(int(time.time()))
        return f"#PWD_ENC:0:{timestamp}:{password}"

class BloksIdentityEngine:
    def __init__(self):
        self.device_id = str(uuid.uuid4())
        self.family_device_id = str(uuid.uuid4())
        self.conn_uuid_client = str(uuid.uuid4()).replace('-', '')
        self.carriers = [
            ("Tsel-MelayaniSepenuhHati", "51010"),
            ("Indosat Ooredoo", "51001"),
            ("XL Axiata", "51011"),
            ("3", "51089"),
            ("Smartfren", "51009")     
        ]
        self.devices = [
            ("Samsung", "SM-S928B", "{density=3.5,width=1440,height=3120}"),
            ("Samsung", "SM-S918B", "{density=3.5,width=1440,height=3088}"),
            ("Samsung", "SM-S908B", "{density=3.5,width=1440,height=3088}"),
            ("Samsung", "SM-G998B", "{density=3.0,width=1440,height=3200}"),
            ("Samsung", "SM-S711B", "{density=3.0,width=1080,height=2340}"),
            ("Samsung", "SM-A546B", "{density=2.625,width=1080,height=2340}"),
            ("Samsung", "SM-A346B", "{density=2.625,width=1080,height=2340}"),
            ("Samsung", "SM-A736B", "{density=2.625,width=1080,height=2400}"),
            ("Samsung", "SM-A525F", "{density=2.625,width=1080,height=2400}"),
            ("Samsung", "SM-M546B", "{density=2.625,width=1080,height=2400}"),
            ("Samsung", "SM-A146B", "{density=2.0,width=1080,height=2408}"),
            ("Samsung", "SM-A057F", "{density=1.75,width=720,height=1600}"),
            ("Xiaomi", "Xiaomi 14 Ultra", "{density=3.5,width=1440,height=3200}"),
            ("Xiaomi", "Xiaomi 13 Pro", "{density=3.5,width=1440,height=3200}"),
            ("Xiaomi", "Xiaomi 12T Pro", "{density=3.0,width=1220,height=2712}"),
            ("Xiaomi", "Redmi Note 13 Pro+", "{density=3.0,width=1220,height=2712}"),
            ("Xiaomi", "Redmi Note 12 Pro", "{density=2.75,width=1080,height=2400}"),
            ("Xiaomi", "Redmi Note 11", "{density=2.75,width=1080,height=2400}"),
            ("Xiaomi", "Redmi Note 10 Pro", "{density=2.75,width=1080,height=2400}"),
            ("Xiaomi", "POCO F5 Pro", "{density=3.5,width=1440,height=3200}"),
            ("Xiaomi", "POCO X6 Pro", "{density=3.0,width=1220,height=2712}"),
            ("Xiaomi", "POCO M6 Pro", "{density=2.75,width=1080,height=2400}"),
            ("Xiaomi", "POCO X3 Pro", "{density=2.75,width=1080,height=2400}"),
            ("Xiaomi", "Redmi 13C", "{density=1.75,width=720,height=1600}"),
            ("Xiaomi", "Redmi 12", "{density=2.0,width=1080,height=2460}"),
            ("Xiaomi", "Redmi 10 2022", "{density=2.0,width=1080,height=2400}"),
            ("Oppo", "CPH2521", "{density=3.0,width=1240,height=2772}"),
            ("Oppo", "CPH2487", "{density=3.0,width=1080,height=2412}"),
            ("Oppo", "CPH2359", "{density=2.625,width=1080,height=2400}"),
            ("Oppo", "CPH2551", "{density=3.0,width=1080,height=2412}"),
            ("Oppo", "CPH2495", "{density=2.0,width=1080,height=2400}"),
            ("Oppo", "CPH2577", "{density=1.75,width=720,height=1612}"),
            ("Oppo", "CPH2477", "{density=1.75,width=720,height=1612}"),
            ("Oppo", "CPH2269", "{density=1.75,width=720,height=1600}"),
            ("vivo", "V2303", "{density=3.0,width=1260,height=2800}"),
            ("vivo", "V2250", "{density=3.0,width=1080,height=2400}"),
            ("vivo", "V2202", "{density=2.75,width=1080,height=2404}"),
            ("vivo", "V2247", "{density=2.0,width=1080,height=2388}"),
            ("vivo", "V2144", "{density=2.0,width=1080,height=2408}"),
            ("vivo", "V2027", "{density=1.75,width=720,height=1600}"),
            ("vivo", "V2310", "{density=2.75,width=1080,height=2400}"),
            ("Realme", "RMX3741", "{density=3.5,width=1240,height=2772}"),
            ("Realme", "RMX3363", "{density=3.0,width=1080,height=2400}"),
            ("Realme", "RMX3771", "{density=3.0,width=1080,height=2412}"),
            ("Realme", "RMX3612", "{density=2.75,width=1080,height=2400}"),
            ("Realme", "RMX3393", "{density=2.75,width=1080,height=2400}"),
            ("Realme", "RMX3760", "{density=2.0,width=1080,height=2400}"),
            ("Realme", "RMX3501", "{density=1.75,width=720,height=1600}"),
            ("Realme", "RMX3263", "{density=1.75,width=720,height=1600}"),
            ("Infinix", "Infinix X6711", "{density=3.0,width=1080,height=2400}"),
            ("Infinix", "Infinix X6833B", "{density=2.75,width=1080,height=2460}"),
            ("Infinix", "Infinix X6831", "{density=2.75,width=1080,height=2460}"),
            ("Infinix", "Infinix X676B", "{density=2.75,width=1080,height=2400}"),
            ("Infinix", "Infinix X665", "{density=1.75,width=720,height=1600}"),
            ("Infinix", "Infinix X6836", "{density=3.0,width=1080,height=2400}"),
            ("Samsung", "SM-S921B", "{density=3.0,width=1080,height=2340}"),
            ("Samsung", "SM-S926B", "{density=3.5,width=1440,height=3120}"),
            ("Samsung", "SM-A556B", "{density=2.625,width=1080,height=2340}"),
            ("Samsung", "SM-M346B", "{density=2.25,width=1080,height=2340}"),
            ("Xiaomi", "Xiaomi 14 Pro", "{density=3.5,width=1440,height=3200}"),
            ("Xiaomi", "Xiaomi 14", "{density=3.0,width=1200,height=2670}"),
            ("Xiaomi", "Redmi 14C", "{density=1.75,width=720,height=1640}"),
            ("Xiaomi", "Redmi Note 13", "{density=2.75,width=1080,height=2400}"),
            ("Oppo", "CPH2631", "{density=3.0,width=1264,height=2780}"),
            ("Oppo", "CPH2641", "{density=2.0,width=1080,height=2412}"),
            ("Oppo", "CPH2655", "{density=2.75,width=1080,height=2412}"),
            ("Oppo", "CPH2581", "{density=2.25,width=1080,height=2400}"),
            ("vivo", "V2318", "{density=3.0,width=1260,height=2800}"),
            ("vivo", "V2405", "{density=3.0,width=1260,height=2800}"),
            ("vivo", "V2320", "{density=2.25,width=1080,height=2388}"),
            ("Infinix", "Infinix X6851", "{density=2.75,width=1080,height=2460}"),
            ("Infinix", "Infinix X6852", "{density=2.75,width=1080,height=2436}"),
            ("Infinix", "Infinix X6855", "{density=2.75,width=1080,height=2436}"),
            ("Tecno", "KJ6", "{density=2.75,width=1080,height=2460}"),
            ("Tecno", "CL9", "{density=3.0,width=1264,height=2780}"),
            ("Tecno", "LI9", "{density=2.75,width=1080,height=2436}"),
            ("Tecno", "BG7n", "{density=1.5,width=720,height=1612}"),
            ("Google", "Pixel 9 Pro XL", "{density=3.5,width=1344,height=2992}"),
            ("Google", "Pixel 9 Pro", "{density=3.5,width=1280,height=2856}"),
            ("Google", "Pixel 9", "{density=3.0,width=1080,height=2424}"),
            ("Google", "Pixel 8 Pro", "{density=3.0,width=1344,height=2992}"),
            ("Google", "Pixel 8", "{density=3.0,width=1080,height=2400}"),
            ("Google", "Pixel 7 Pro", "{density=3.5,width=1440,height=3120}"),
            ("Google", "Pixel 7", "{density=3.0,width=1080,height=2400}"),
            ("Google", "Pixel 6 Pro", "{density=3.5,width=1440,height=3120}"),
            ("Google", "Pixel 6a", "{density=2.625,width=1080,height=2400}"),
        ]
        self.android_versions = ["10", "11", "12", "13", "14", "15"]
        self.connection_types = ["WIFI", "CELLULAR"]
        self.carrier_name, self.carrier_hni = random.choice(self.carriers)
        self.device_manufacturer, self.device_model, self.screen_metrics = random.choice(self.devices)
        self.android_version = random.choice(self.android_versions)
        self.connection_type = random.choice(self.connection_types)
        self.user_agent = f"[FBAN/PAAA;FBAV/544.0.0.28.108;FBDM/{self.screen_metrics};FBLC/id_ID;FBBV/902102429;FB_FW/2;FBSN/Android;FBDI/{self.family_device_id};FBCR/{self.carrier_name};FBMF/{self.device_manufacturer};FBBD/Android;FBDV/{self.device_model};FBSV/{self.android_version};FBCA/arm64-v8a:null;]"

    def get_headers(self):
        headers = {
            "x-fb-request-analytics-tags": '{"network_tags":{"product":"121876164619130","request_category":"graphql","purpose":"fetch","retry_attempt":"0"},"application_tags":"graphservice"}',
            "x-fb-connection-type": self.connection_type, 
            "app-scope-id-header": self.device_id,
            "x-zero-state": "unknown",
            "authorization": "OAuth 121876164619130|1ab2c5c902faedd339c14b2d58e929dc", 
            "x-fb-sim-hni": self.carrier_hni,
            "x-fb-net-hni": self.carrier_hni,
            "content-type": "application/x-www-form-urlencoded",
            "x-graphql-client-library": "graphservice",
            "x-graphql-request-purpose": "fetch",
            "x-tigon-is-retry": "False",
            "x-zero-f-device-id": self.family_device_id,
            "x-fb-friendly-name": "com.bloks.www.bloks.caa.login.async.send_login_request",
            "user-agent": self.user_agent,
            "x-fb-http-engine": "Tigon/Liger",
            "x-fb-client-ip": "True",
            "x-fb-server-cluster": "True",
            "x-fb-conn-uuid-client": self.conn_uuid_client
        }
        return headers

    def get_payload(self, encrypted_password, contact_point=""):
        server_params = {
            "device_id": self.device_id,
            "server_login_source": "login",
            "waterfall_id": str(uuid.uuid4()),
            "attestation_result": {"errorMessage": "KeyAttestationException: No key found!"},
            "machine_id": "",
            "from_native_screen": True,
            "credential_type": "password",
            "password": encrypted_password,
            "try_num": "1",
            "family_device_id": self.family_device_id,
            "event_flow": "login_manual",
            "event_step": "home_page",
            "is_from_logged_in_switcher": False,
            "contact_point": contact_point
        }
        inner_params = json.dumps({"server_params": server_params})
        middle_params = json.dumps({"params": inner_params})
        variables = {
            "params": {
                "params": middle_params,
                "bloks_versioning_id": "6dcff2f1522756669e85e348a541dcfcb9a4478ef7ce18b4132a7ebb177a99f1",
                "app_id": "com.bloks.www.bloks.caa.login.async.send_login_request"
            },
            "scale": "2",
            "nt_context": {
                "using_white_navbar": True,
                "styles_id": "56749ebea2452a6119a9d01ce0f1bd9e",
                "pixel_ratio": 2,
                "is_push_on": True,
                "debug_tooling_metadata_token": None,
                "is_flipper_enabled": False,
                "theme_params": [{"value": [], "design_system_name": "FDS"}],
                "bloks_version": "6dcff2f1522756669e85e348a541dcfcb9a4478ef7ce18b4132a7ebb177a99f1"
            }
        }
        body_data = {
            "method": "post",
            "fb_api_req_friendly_name": "com.bloks.www.bloks.caa.login.async.send_login_request",
            "fb_api_caller_class": "graphservice",
            "client_doc_id": "11994080422468892357865317994", 
            "fb_api_client_context": '{"is_background":false}',
            "variables": json.dumps(variables),
            "fb_api_analytics_tags": '["GraphServices"]',
            "client_trace_id": str(uuid.uuid4())
        }
        return urllib.parse.urlencode(body_data)
