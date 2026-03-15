import base64
import time
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto.Hash import SHA256

def encrypt_password(password, key_id, public_key_str):
    """
    Simulasi pembuatan format #PWD_ENC Facebook
    Note: Facebook aslinya menggunakan AES-GCM + RSA, 
    tapi versi RSA-only ini sering digunakan untuk testing.
    """
    try:
        # Bersihkan public key string
        public_key_str = public_key_str.replace("-----BEGIN PUBLIC KEY-----", "").replace("-----END PUBLIC KEY-----", "").replace("\n", "").strip()
        public_key_der = base64.b64decode(public_key_str)
        key = RSA.importKey(public_key_der)
        cipher = PKCS1_v1_5.new(key)
        
        timestamp = int(time.time())
        # Format dasar: #PWD_ENC:VERSION:TIMESTAMP:ENCRYPTED_PASSWORD
        encrypted_pw = base64.b64encode(cipher.encrypt(password.encode())).decode()
        
        return f"#PWD_ENC:3:{timestamp}:{encrypted_pw}".replace(":3:", f":{key_id}:")
    except Exception as e:
        return f"Error: {str(e)}"

# --- DATA DARI FRIDA ---
RSA_KEY = "MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAyD5wxR1BYF2nGjpRTUwm lx136/i9bLoi4g62R6HiYVG+jcgAoyFV0xcfYwgUudIox47saHCfHhxV0kTuO/K/ tYvW1Rl4ZBerGLuJQnHrkvUymL41BUeH50Eq4wLscJXB8emN45gT6J9YYfzaECT7 8Th7lFJ2FlsbRU4Q8yYu+OPXRlqaTLs4cXbUayiH67t7yJG0Bu5D4DL5dl72pIIC BhyrXXG3douOSzsFQ98m4WpktTXh+nMfGIrQp7QI8lfkWaPz9pt8+6r4wJI74Ul7 /xKTGAjqBDOG17GDw4saq4z0FVIQgpj2b/WnyedtGbzNLIGPO2l89QoTvwQvCkpd 7wIDAQAB"
KEY_ID = "1"
PASSWORD = "password_target"


print(encrypt_password(PASSWORD, KEY_ID, RSA_KEY))
