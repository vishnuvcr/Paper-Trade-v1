from datetime import date
from pathlib import Path
import json
import requests
ROOT=Path(__file__).resolve().parents[2]
CACHE=ROOT/'data'/'cache'/'calendars'

def nse_fo_holidays(year=2026):
 p=CACHE/f'NSE_FO_{year}.json'
 if p.exists():
  try:return {date.fromisoformat(x) for x in json.loads(p.read_text())}
  except Exception:pass
 try:
  u='https://www.nseindia.com/api/holiday-master?type=trading'
  h={'User-Agent':'Mozilla/5.0','Accept':'application/json','Referer':'https://www.nseindia.com/'}
  j=requests.get(u,headers=h,timeout=20).json()
  rows=j.get('FO',[]) or j.get('trading',[])
  xs=[]
  for r in rows:
   s=r.get('tradingDate') or r.get('date')
   if s and str(s).endswith(str(year)): xs.append(date.fromisoformat(str(s)[:10]))
  if xs:
   CACHE.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(sorted(str(x) for x in xs),indent=2)+'\n'); return set(xs)
 except Exception:pass
 return set()

def is_trading_day(d,holidays): return d.weekday()<5 and d not in holidays

def d3_date(expiry,holidays):
 xs=[]; cur=expiry
 while len(xs)<3:
  cur=cur.fromordinal(cur.toordinal()-1)
  if is_trading_day(cur,holidays): xs.append(cur)
 return list(reversed(xs))[0]
