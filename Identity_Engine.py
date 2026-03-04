import uuid
import hashlib
import random
import time
import json
import base64
import urllib.request
import os
import re

class IdentityEngine:
    """
    Facebook Identity Emulation Engine
    Generates consistent device signatures, integrity tokens (ZCA/Attestation),
    and User-Agents to mimic a real Android device.
    Supports identity ROTATION for anti-rate-limit.
    """

    DEVICE_POOL = [
        ("Xiaomi", "M2010J19CG", "10"),
        ("Xiaomi", "22071219CG", "13"),
        ("Samsung", "SM-A115F", "11"),
        ("Samsung", "SM-G975F", "12"),
        ("Samsung", "SM-A536B", "13"),
        ("Oppo", "CPH2481", "12"),
        ("Oppo", "CPH2239", "11"),
        ("Vivo", "V2027", "11"),
        ("Vivo", "V2111", "12"),
        ("Realme", "RMX3765", "13"),
        ("Realme", "RMX3085", "11"),
        ("Infinix", "X6816", "12"),
        ("Infinix", "X682B", "11"),
        ("Tecno", "KI7", "12"),
        ("Poco", "M2012K11AG", "11"),
    ]

    # Fallback values yang SUDAH TERBUKTI BEKERJA (dari capture sebelumnya)
    STATIC_FALLBACK = {
        "device_id": "e846ebd1-b504-4c93-9e82-813415056b0d",
        "family_device_id": "11ce8f7e-a894-4264-89e6-6b9b5c183622",
        "machine_id": "qwubafkTUHIUwScSQ6EzN9LH",
        "usdid": "fd407b7d-d14d-43f8-807f-c1d8499bb362.1772456236.MEYCIQCOYU75UMSUH1ebP1O06WL5TalFajHjfNHzcUvzFPkTWAIhAOgDi7z_G3fwxvy6_TCf4Zx6cfueXvrGBYxHAPMg2Al-",
        "attestation": {"keyHash":"c180b16c3b682ba6a360a764896ce14a30376ab31b02c3be8ef847f3b78add8a","data":"eyJjaGFsbGVuZ2Vfbm9uY2UiOiJXU0NJTmFYUHpibmZ0SkNkcEJTcUQxL1ljNnFTdThHd1lzQ3ZtRkdLbDFRPSIsInVzZXJuYW1lIjoic2FwdXRyYXg0MEBnbWFpbC5jb20ifQ==","signature":"MEUCIBPT7XdIxWtavwhOtQ8KfMD7rmbo85UdtBuym/XgRqxFAiEAxbQX8c9IRpIdHQIKDDsj8Qf0YQVT1zHRqzz7Q1txUfY="},
        "user_agent": "[FBAN/FB4A;FBAV/548.1.0.51.64;FBBV/882676621;FBDM/{density=2.0,width=720,height=1184};FBLC/id_ID;FBRV/894237573;FBCR/Tsel-MelayaniSepenuhHati;FBMF/unknown;FBBD/Android;FBPN/com.facebook.katana;FBDV/Phh-Treble vanilla;FBSV/10;FBOP/1;FBCA/arm64-v8a:;]",
        "zca": "empty_token",
    }

    def __init__(self, master_identity_path="identity.json"):
        self.master_identity = self._load_master_identity(master_identity_path)
        self.rotation_count = 0
        self._session = {}
        self._base_identity = None  # Identitas perangkat tetap
        self._init_base_identity()
        self.rotate()  # Generate initial session

    def _load_master_identity(self, path):
        try:
            with open(path, "r") as f:
                data = json.load(f)
            # Validasi: minimal harus ada device_id
            if data.get("device_id"):
                print(f"[*] Identity Engine: Memuat identitas ASLI dari {path}")
                return data
            return None
        except:
            return None

    def _init_base_identity(self):
        """
        Inisialisasi identitas DASAR perangkat (tidak berubah saat rotasi).
        Prioritas: identity.json > static fallback
        """
        if self.master_identity:
            # Pakai data asli dari Frida capture
            device_id = self.master_identity.get("device_id") or self.STATIC_FALLBACK["device_id"]
            self._base_identity = {
                "device_id": device_id,
                "family_device_id": self.master_identity.get("family_device_id") or self.STATIC_FALLBACK["family_device_id"],
                "android_id": hashlib.md5(device_id.encode()).hexdigest()[:16],
                "machine_id": self.master_identity.get("machine_id") or self.STATIC_FALLBACK["machine_id"],
                "usdid": self.master_identity.get("usdid") or self.STATIC_FALLBACK["usdid"],
                "user_agent": self.master_identity.get("user_agent") or self.STATIC_FALLBACK["user_agent"],
                "zca": self.master_identity.get("zca") or self.STATIC_FALLBACK["zca"],
                "attestation": self.master_identity.get("attestation") or self.STATIC_FALLBACK["attestation"],
                "source": "capture"
            }
        else:
            # Pakai static fallback yang sudah terbukti bekerja
            device_id = self.STATIC_FALLBACK["device_id"]
            self._base_identity = {
                "device_id": device_id,
                "family_device_id": self.STATIC_FALLBACK["family_device_id"],
                "android_id": hashlib.md5(device_id.encode()).hexdigest()[:16],
                "machine_id": self.STATIC_FALLBACK["machine_id"],
                "usdid": self.STATIC_FALLBACK["usdid"],
                "user_agent": self.STATIC_FALLBACK["user_agent"],
                "zca": self.STATIC_FALLBACK["zca"],
                "attestation": self.STATIC_FALLBACK["attestation"],
                "source": "fallback"
            }
            print(f"[*] Identity Engine: Menggunakan identitas FALLBACK (sudah terbukti)")
        
        self.blueprint = self._create_blueprint()

    def rotate(self):
        """
        SOFT ROTATE: Identitas perangkat TETAP SAMA (agar lolos integrity check),
        tapi metadata sesi di-rotasi agar terlihat seperti sesi baru.
        """
        self.rotation_count += 1
        timestamp = int(time.time())
        
        # Gabungkan: identitas perangkat tetap + metadata sesi baru
        self._session = {
            **self._base_identity,
            "timestamp": timestamp,
            "waterfall_id": str(uuid.uuid4()),
            "pigeon_session_id": f"UFS-{str(uuid.uuid4())}-{random.randint(0,3)}",
            "conn_uuid": hashlib.md5(str(uuid.uuid4()).encode()).hexdigest(),
            "connection_type": random.choice(["WIFI", "MOBILE(LTE)", "MOBILE(5G)"]),
        }
        return self._session

    def rotate_full(self):
        """
        FULL ROTATE: Generate identitas perangkat BARU sepenuhnya.
        Gunakan ini hanya jika perlu bypass fingerprinting total.
        PERINGATAN: Identitas palsu mungkin kena e53!
        """
        self.rotation_count += 1
        self.blueprint = self._create_blueprint_random()
        
        device_id = str(uuid.uuid4())
        family_device_id = str(uuid.uuid4())
        android_id = hashlib.md5(device_id.encode()).hexdigest()[:16]
        timestamp = int(time.time())
        
        device_part = hashlib.md5(device_id.encode()).hexdigest()[:16]
        prefix = random.choice(["aWy","YXN","k3W","bGx","c2Q","dHk"])
        suffix = random.choice(["AeH","BfI","CgJ","DhK","EiL","FjM"])
        chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
        mid_part = ""
        for i in range(0, 16, 2):
            hex_val = int(device_part[i:i+2], 16)
            mid_part += chars[hex_val % len(chars)]
        machine_id = f"{prefix}{mid_part}{suffix}"[:22]
        usdid = f"{str(uuid.uuid4())}.{timestamp}.{machine_id[:20]}"
        
        self._session = {
            "device_id": device_id,
            "family_device_id": family_device_id,
            "android_id": android_id,
            "machine_id": machine_id,
            "usdid": usdid,
            "timestamp": timestamp,
            "user_agent": self.generate_user_agent(),
            "zca": self._generate_zca_fresh(android_id, timestamp),
            "attestation": self._generate_attestation_fresh(device_id),
            "waterfall_id": str(uuid.uuid4()),
            "pigeon_session_id": f"UFS-{str(uuid.uuid4())}-{random.randint(0,3)}",
            "conn_uuid": hashlib.md5(str(uuid.uuid4()).encode()).hexdigest(),
            "connection_type": random.choice(["WIFI", "MOBILE(LTE)", "MOBILE(5G)"]),
            "source": "generated"
        }
        return self._session

    def _create_blueprint(self):
        """Creates blueprint from base identity's user agent."""
        ua = self._base_identity.get("user_agent", "") if self._base_identity else ""
        if ua:
            mf = re.search(r'FBMF/([^;]+)', ua)
            dv = re.search(r'FBDV/([^;]+)', ua)
            sv = re.search(r'FBSV/([^;]+)', ua)
            if mf or dv:
                return {
                    "manufacturer": mf.group(1) if mf else "unknown",
                    "brand": mf.group(1) if mf else "Android",
                    "model": dv.group(1) if dv else "Phh-Treble vanilla",
                    "os_version": sv.group(1) if sv else "10",
                    "is_real": True
                }
        # Fallback
        return {"manufacturer": "unknown", "brand": "Android", "model": "Phh-Treble vanilla", "os_version": "10", "is_real": True}

    def _create_blueprint_random(self):
        """Creates a random blueprint from device pool (for rotate_full)."""
        mf, dv, sv = random.choice(self.DEVICE_POOL)
        return {"manufacturer": mf, "brand": mf, "model": dv, "os_version": sv, "is_real": False}

    def generate_user_agent(self):
        """Generates FB4A User Agent matching the blueprint."""
        fbav = f"{random.randint(400, 550)}.0.0.{random.randint(30, 50)}.{random.randint(50, 120)}"
        fbbv = random.randint(100000000, 999999999)
        fbrv = random.randint(100000000, 999999999)
        density = random.choice([2.0, 3.0])
        res = random.choice([(720, 1280), (1080, 1920)])
        
        ua = (f"FBAN/FB4A;FBAV/{fbav};FBBV/{fbbv};"
              f"FBDM/{{density={density},width={res[0]},height={res[1]}}};"
              f"FBLC/id_ID;FBRV/{fbrv};FBCR/Tsel;FBMF/{self.blueprint['manufacturer']};"
              f"FBBD/{self.blueprint['brand']};FBPN/com.facebook.katana;"
              f"FBDV/{self.blueprint['model']};FBSV/{self.blueprint['os_version']};"
              f"FBOP/1;FBCA/arm64-v8a:;")
        return ua

    def get_session(self):
        """Returns current session identity dict."""
        return self._session

    # === Convenience getters (backward compatible) ===
    def get_device_id(self):      return self._session["device_id"]
    def get_family_device_id(self): return self._session["family_device_id"]
    def get_machine_id(self, device_id=None): return self._session["machine_id"]
    def get_usdid(self):          return self._session["usdid"]
    def generate_zca(self, android_id=None): return self._session["zca"]
    def get_attestation(self, device_id=None): return self._session["attestation"]

    def get_integrity_headers(self):
        """
        Returns headers for Facebook GraphQL Native login.
        Disesuaikan dari logika dez_dec untuk FB environment.
        """
        s = self._session
        return {
            'x-meta-zca': s["zca"],
            'x-meta-usdid': s["usdid"],
            'x-fb-integrity-machine-id': s["machine_id"],
            'x-fb-connection-type': s.get("connection_type", "WIFI"),
            'x-fb-conn-uuid-client': s["conn_uuid"],
            'app-scope-id-header': s["device_id"],
        }

    def get_graphql_variables(self, username, password):
        """
        Returns dictionary of variables for Facebook login GraphQL.
        Logika nesting 'client_input_params' dari dez_dec diadaptasi ke FB.
        """
        s = self._session
        ts = int(time.time())
        return {
            "client_input_params": {
                "password": f"#PWD_FACEBOOK:0:{ts}:{password}",
                "contact_point": username,
                "device_id": s["device_id"],
                "family_device_id": s["family_device_id"],
                "machine_id": s["machine_id"],
                "event_flow": "login_manual",
                "try_num": 1,
            },
            "server_params": {
                "waterfall_id": s["waterfall_id"],
                "login_source": "login",
                "device_id": s["device_id"],
            }
        }

    # === Internal generators (untuk rotate_full) ===
    def _generate_zca_fresh(self, android_id, timestamp_s):
        ts_ms = timestamp_s * 1000
        data_to_sign = {"time": ts_ms, "hash": hashlib.md5(f"{android_id}{ts_ms}".encode()).hexdigest()[:20]}
        signed_data = base64.urlsafe_b64encode(json.dumps({
            "signature": hashlib.sha256(f"{data_to_sign}{random.randint(0,9999)}".encode()).hexdigest(),
            "timestamp": ts_ms
        }).encode()).decode()
        last_key_ms = ts_ms - random.randint(1000, 86400000)
        aka_data = {
            "dataToSign": json.dumps(data_to_sign),
            "signedData": signed_data,
            "keyHash": hashlib.sha256(f"{android_id}{last_key_ms}".encode()).hexdigest(),
            "lastUploadedKeyTimeMs": last_key_ms
        }
        bat_status = random.choice(["Charging", "Discharging", "Full", "NotCharging"])
        zca_payload = {
            "android": {
                "aka": aka_data,
                "gpia": {"token": ""},
                "payload": {"plugins": {
                    "bat": {"sta": bat_status, "lvl": random.randint(15, 100)},
                    "sct": {},
                    "adb": {"usb": 0, "adb": 0, "usb_adb": 0}
                }}
            }
        }
        return base64.urlsafe_b64encode(json.dumps(zca_payload).encode()).decode()

    def _generate_attestation_fresh(self, device_id):
        challenge = base64.urlsafe_b64encode(os.urandom(24)).decode().replace('=', '')
        header = '{"alg":"ES256","typ":"JWT"}'
        payload = f'{{"nonce":"{challenge}","ts":{int(time.time())},"did":"{device_id}"}}'
        enc_h = base64.urlsafe_b64encode(header.encode()).decode().replace('=', '')
        enc_p = base64.urlsafe_b64encode(payload.encode()).decode().replace('=', '')
        sig = hashlib.sha256(f"{enc_h}.{enc_p}{random.randint(1000,9999)}".encode()).hexdigest()
        signed_nonce = f"{enc_h}.{enc_p}.{sig[:86]}"
        key_hash = hashlib.sha256(f"{device_id}{int(time.time()/3600)}".encode()).hexdigest()

        return {
            "attestation": [{
                "version": random.choice([2, 3]),
                "type": random.choice(["keystore", "safetynet", "playintegrity"]),
                "errors": random.choice([[0], [0], [0], [1]]),
                "challenge_nonce": challenge,
                "signed_nonce": signed_nonce,
                "key_hash": key_hash
            }]
        }

if __name__ == "__main__":
    engine = IdentityEngine()
    
    print("=== DEMO ROTASI IDENTITAS ===\n")
    for i in range(3):
        session = engine.get_session()
        print(f"--- Sesi #{i+1} (Rotasi #{engine.rotation_count}) ---")
        print(f"  Source : {session.get('source', 'unknown')}")
        print(f"  Device : {session['device_id'][:20]}...")
        print(f"  Machine: {session['machine_id']}")
        print(f"  WF ID  : {session['waterfall_id'][:12]}... (berubah tiap rotasi)")
        print(f"  Conn   : {session['connection_type']}")
        print()
        engine.rotate()  # Soft rotate - device tetap, sesi baru
