from __future__ import annotations
import asyncio,json,hashlib
from datetime import datetime,timedelta
from pathlib import Path
import pandas as pd, requests
from .common import normalize_chain
ROOT=Path(__file__).resolve().parents[2]; SNAP=ROOT/'data'/'snapshots'; CACHE=ROOT/'data'/'cache'/'daily'

def _save(obj,prefix):
 SNAP.mkdir(parents=True,exist_ok=True); ts=datetime.utcnow().strftime('%Y%m%dT%H%M%SZ'); raw=json.dumps(obj,default=str,sort_keys=True,separators=(',',':')); h=hashlib.sha256(raw.encode()).hexdigest(); p=SNAP/f'{prefix}_{ts}_{h[:10]}.json'; p.write_text(raw+'\n'); return str(p),h

def _nse_direct():
 s=requests.Session(); h={'User-Agent':'Mozilla/5.0','Accept':'application/json,text/plain,*/*','Referer':'https://www.nseindia.com/option-chain'}; s.get('https://www.nseindia.com/option-chain',headers=h,timeout=15)
 j=s.get('https://www.nseindia.com/api/option-chain-v3',params={'type':'indices','symbol':'NIFTY'},headers=h,timeout=20).json()
 rows=[]
 for z in (j.get('records',{}).get('data',[]) or j.get('data',[])):
  e=z.get('expiryDate') or z.get('expiry'); k=z.get('strikePrice') or z.get('strike')
  for side,key in [('CE','CE'),('PE','PE')]:
   q=z.get(key) or z.get(side) or {}
   if k is not None and q: rows.append({'expiry':e,'strike':k,'option_type':side,'ltp':q.get('lastPrice') or q.get('ltp'),'bid':q.get('bidprice') or q.get('bid'),'ask':q.get('askPrice') or q.get('ask'),'volume':q.get('totalTradedVolume'),'open_interest':q.get('openInterest')})
 if not rows: raise RuntimeError('NSE direct option chain empty')
 return normalize_chain(rows),{'source':'NSE_DIRECT_OPTION_CHAIN_V3','official':True}

async def _india(exchange,symbol):
 from indiaopt import NSEClient,BSEClient
 C=NSEClient if exchange=='NSE' else BSEClient
 async with C() as c: return await c.fetch_option_chain(symbol,is_index=True)

def _india_rows(res):
 data=getattr(res,'data',None) or (res.get('data') if isinstance(res,dict) else None) or []
 rows=[]; expiry=getattr(res,'expiry',None) if not isinstance(res,dict) else res.get('expiry')
 for r in data:
  def g(k): return r.get(k) if isinstance(r,dict) else getattr(r,k,None)
  k=g('strike') or g('strike_price')
  for side,lt,bid,ask in [('CE','call_ltp','call_bid','call_ask'),('PE','put_ltp','put_bid','put_ask')]:
   p=g(lt)
   if k is not None and p is not None: rows.append({'expiry':g('expiry') or expiry,'strike':k,'option_type':side,'ltp':p,'bid':g(bid),'ask':g(ask),'volume':g('volume'),'open_interest':g('oi') or g('open_interest')})
 if not rows: raise RuntimeError('indiaopt returned no option rows')
 return normalize_chain(rows)

def option_chain(underlying):
 if underlying=='NIFTY':
  try:
   res=asyncio.run(_india('NSE','NIFTY')); x=_india_rows(res); meta={'source':'INDIAOPT_NSE','official':False}
  except Exception as e:
   x,meta=_nse_direct(); meta['indiaopt_error']=type(e).__name__+': '+str(e)
 elif underlying=='SENSEX':
  try:
   res=asyncio.run(_india('BSE','999920')); x=_india_rows(res); meta={'source':'INDIAOPT_BSE_999920','official':False}
  except Exception as e: raise RuntimeError('SENSEX provider unavailable: '+str(e))
 else: raise ValueError(underlying)
 path,h=_save({'provider':meta,'rows':x.to_dict('records')},underlying.lower()+'_chain'); meta.update({'snapshot_path':path,'snapshot_sha256':h}); return x,meta

def daily_close(ticker,years=6):
 CACHE.mkdir(parents=True,exist_ok=True); safe=ticker.replace('^',''); p=CACHE/(safe+'.csv')
 old=None
 if p.exists():
  try:
   d=pd.read_csv(p); old=pd.Series(pd.to_numeric(d.close),index=pd.to_datetime(d.date)).sort_index()
  except Exception: old=None
 now=pd.Timestamp.now(tz='Asia/Kolkata').tz_localize(None).normalize()
 if old is not None and len(old)>800 and old.index.max()>=now-pd.Timedelta(days=2): return old
 end=int(datetime.utcnow().timestamp()); start=int((datetime.utcnow()-timedelta(days=365*years)).timestamp()); u=f'https://query1.finance.yahoo.com/v8/finance/chart/{ticker}'
 j=requests.get(u,params={'period1':start,'period2':end,'interval':'1d','events':'history'},timeout=20).json()['chart']['result'][0]
 idx=pd.to_datetime(j['timestamp'],unit='s',utc=True).tz_convert('Asia/Kolkata').tz_localize(None).normalize(); s=pd.Series(j['indicators']['quote'][0]['close'],index=idx,name='close').dropna(); s=s[~s.index.duplicated()].sort_index(); s.to_csv(p,header=['close'],index_label='date'); return s
