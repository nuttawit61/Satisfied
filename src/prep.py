import pandas as pd, datetime as dt, json, re, sys
df=pd.read_excel(sys.argv[1])
c=list(df.columns)
def clean_dd(x, ts):
    d=None
    if isinstance(x,(dt.datetime,pd.Timestamp)):
        y=x.year
        if y>=2500: y-=543
        try: d=dt.date(y,x.month,x.day)
        except: d=None
    elif isinstance(x,str):
        m=re.match(r'(\d+)/(\d+)/0*(\d+)$',x.strip())
        if m:
            mo,da,yy=map(int,m.groups())
            if yy in (68,69,70): y=2500+yy-543
            elif yy in (25,26): y=2000+yy
            else: y=None
            if y:
                try: d=dt.date(y,mo,da)
                except: d=None
    tsd=ts.date()
    if d is None or d>tsd or (tsd-d).days>90: return tsd.isoformat(), 1
    return d.isoformat(), 0
def raw(x):
    if isinstance(x,(dt.datetime,pd.Timestamp)): return f"{x.day}/{x.month}/{x.year}"
    return '' if pd.isna(x) else str(x)
def s(x):
    if x is None or (isinstance(x,float) and pd.isna(x)): return ''
    return str(x).strip()
rows=[];fix=0
for _,r in df.iterrows():
    ts=pd.Timestamp(r[c[0]]).to_pydatetime()
    ddc,f=clean_dd(r[c[1]],ts); fix+=f
    sc=[int(r[c[i]]) for i in [6,7,9,10,12,13,14,16,17,18,20,21,22,23]]
    rows.append([ts.strftime('%Y-%m-%d %H:%M:%S'), raw(r[c[1]]), ddc, f,
        1 if r[c[2]]=='ยินยอม' else 0, s(r[c[3]]), s(r[c[4]]), s(r[c[5]]), sc,
        [s(r[c[i]]) for i in [8,11,15,19,26]], 1 if r[c[24]]=='กลับ' else 0, 1 if r[c[25]]=='แนะนำ' else 0])
print('fallback',fix, 'rows',len(rows), file=sys.stderr)
json.dump(rows,open('data.json','w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
