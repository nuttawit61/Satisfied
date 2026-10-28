"""สร้าง index.html ใหม่จากไฟล์ Excel
ใช้งาน:  pip install pandas openpyxl
         python src/build.py "data/แบบประเมินความพึงพอใจ_ผู้บริจาคเลือด_2569.xlsx"
"""
import sys, subprocess, pathlib, urllib.request
root = pathlib.Path(__file__).resolve().parent.parent
xlsx = sys.argv[1] if len(sys.argv) > 1 else str(next((root / 'data').glob('*.xlsx')))
subprocess.run([sys.executable, str(root / 'src' / 'prep.py'), xlsx], check=True, cwd=root / 'src')
lib = root / 'src' / 'xlsx.full.min.js'
if not lib.exists():
    urllib.request.urlretrieve('https://cdn.jsdelivr.net/npm/xlsx@0.18.5/dist/xlsx.full.min.js', lib)
t = (root / 'src' / 'template.html').read_text(encoding='utf-8')
x = lib.read_text(encoding='utf-8').replace('</script', '<\\/script')
d = (root / 'src' / 'data.json').read_text(encoding='utf-8').replace('</', '<\\/')
(root / 'index.html').write_text(t.replace('/*__XLSX__*/', x, 1).replace('/*__DATA__*/', d, 1), encoding='utf-8')
(root / 'src' / 'data.json').unlink()
print('สร้าง index.html แล้ว')
