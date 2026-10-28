"""สร้าง index.html ใหม่จากไฟล์ Excel (ข้อมูลถูกเข้ารหัสด้วยรหัสผ่าน)
ใช้งาน:  pip install pandas openpyxl cryptography
         python src/build.py "data/ไฟล์.xlsx" --password รหัสผ่าน
         (ถ้าไม่ใส่ --password จะถามรหัสผ่านตอนรัน)
"""
import sys, os, json, base64, getpass, argparse, subprocess, pathlib, urllib.request
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

ITER = 310_000
root = pathlib.Path(__file__).resolve().parent.parent
ap = argparse.ArgumentParser()
ap.add_argument('xlsx', nargs='?')
ap.add_argument('--password')
ap.add_argument('--out', default=str(root / 'index.html'))
a = ap.parse_args()
xlsx = a.xlsx or str(next((root / 'data').glob('*.xlsx')))
pw = a.password or os.environ.get('DASHBOARD_PASSWORD') or getpass.getpass('รหัสผ่าน: ')

subprocess.run([sys.executable, str(root / 'src' / 'prep.py'), xlsx], check=True, cwd=root / 'src')
data_path = root / 'src' / 'data.json'
plain = data_path.read_bytes(); data_path.unlink()

salt, iv = os.urandom(16), os.urandom(12)
key = PBKDF2HMAC(algorithm=hashes.SHA256(), length=32, salt=salt, iterations=ITER).derive(pw.encode('utf-8'))
ct = AESGCM(key).encrypt(iv, plain, None)
b = lambda x: base64.b64encode(x).decode()
enc = json.dumps({'s': b(salt), 'i': b(iv), 'c': b(ct), 'n': ITER})

lib = root / 'src' / 'xlsx.full.min.js'
if not lib.exists():
    urllib.request.urlretrieve('https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js', lib)
t = (root / 'src' / 'template.html').read_text(encoding='utf-8')
x = lib.read_text(encoding='utf-8').replace('</script', '<\\/script')
uri = lambda f: 'data:image/png;base64,' + b((root / 'src' / 'assets' / f).read_bytes())
t = t.replace('{{LOGO}}', uri('logo-white.png')).replace('{{SEAL}}', uri('seal.png')).replace('{{FAVICON}}', uri('favicon.png'))
pathlib.Path(a.out).write_text(t.replace('/*__XLSX__*/', x, 1).replace('/*__ENC__*/', enc, 1), encoding='utf-8')
print('สร้าง', a.out, 'แล้ว (ข้อมูลเข้ารหัส AES-256-GCM)')
