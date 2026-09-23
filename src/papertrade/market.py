from __future__ import annotations
import asyncio,json,hashlib
from datetime import datetime,timedelta,date
from pathlib import Path
import pandas as pd, requests
from .common import normalize_chain

ROOT=Path(__file__).resolve().parents[2]
SNAP=ROOT/'data'/'snapshots'
CACHE=ROOT/'data'/'cache'/'daily'

BSE_BASE='https://api.bseindia.com/BseIndiaAPI/api'
BSE_HEADERS={
    'Accept':'application/json, text/plain, */*',
    'Accept-Language':'en-US,en;q=0.9',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Referer':'https://www.bseindia.com/markets/Derivatives/DeriReports/DeriOptionchain.html',
    'Origin':'https://www.bseindia.com',
    'sec-fetch-site':'same-site',
    'sec-fetch-mode':'cors',
}
BSE_SENSEX_SCRIP='1'
BSE_PRODUCT_TYPE='IO'

def _save(obj,prefix):
    SNAP.mkdir(parents=True,exist_ok=True)
    ts=datetime.utcnow().strftime('%Y%m%dT%H%M%SZ')
    raw=json.dumps(obj,default=str,sort_keys=True,separators=(',',':'))
    h=hashlib.sha256(raw.encode()).hexdigest()
    p=SNAP/f'{prefix}_{ts}_{h[:10]}.json'
    p.write_text(raw+'\n')
    return str(p),h

def _nse_direct():
    s=requests.Session()
    h={'User-Agent':'Mozilla/5.0','Accept':'application/json,text/plain,*/*','Referer':'https://www.nseindia.com/option-chain'}
    s.get('https://www.nseindia.com/option-chain',headers=h,timeout=15)
    j=s.get('https://www.nseindia.com/api/option-chain-v3',params={'type':'indices','symbol':'NIFTY'},headers=h,timeout=20).json()
    rows=[]
    for z in (j.get('records',{}).get('data',[]) or j.get('data',[])):
        e=z.get('expiryDate') or z.get('expiry'); k=z.get('strikePrice') or z.get('strike')
        for side,key in [('CE','CE'),('PE','PE')]:
            q=z.get(key) or z.get(side) or {}
            if k is not None and q:
                rows.append({'expiry':e,'strike':k,'option_type':side,'ltp':q.get('lastPrice') or q.get('ltp'),'bid':q.get('bidprice') or q.get('bid'),'ask':q.get('askPrice') or q.get('ask'),'volume':q.get('totalTradedVolume'),'open_interest':q.get('openInterest')})
    if not rows: raise RuntimeError('NSE direct option chain empty')
    return normalize_chain(rows),{'source':'NSE_DIRECT_OPTION_CHAIN_V3','official':True}

async def _india(exchange,symbol):
    from indiaopt import NSEClient,BSEClient
    C=NSEClient if exchange=='NSE' else BSEClient
    async with C() as c:
        return await c.fetch_option_chain(symbol,is_index=True)

def _india_rows(res):
    data=getattr(res,'data',None) or (res.get('data') if isinstance(res,dict) else None) or []
    rows=[]; expiry=getattr(res,'expiry',None) if not isinstance(res,dict) else res.get('expiry')
    for r in data:
        def g(k): return r.get(k) if isinstance(r,dict) else getattr(r,k,None)
        k=g('strike') or g('strike_price')
        for side,lt,bid,ask in [('CE','call_ltp','call_bid','call_ask'),('PE','put_ltp','put_bid','put_ask')]:
            p=g(lt)
            if k is not None and p is not None:
                rows.append({'expiry':g('expiry') or expiry,'strike':k,'option_type':side,'ltp':p,'bid':g(bid),'ask':g(ask),'volume':g('volume'),'open_interest':g('oi') or g('open_interest')})
    if not rows: raise RuntimeError('indiaopt returned no option rows')
    return normalize_chain(rows)

def _num(v):
    try:
        if v is None: return 0.0
        return float(str(v).replace(',','').strip() or 0)
    except Exception:
        return 0.0

def _expiry_to_bse(value):
    if not value: return None
    raw=str(value).strip().replace('/','-')
    for fmt in ('%d-%m-%Y','%Y-%m-%d','%d-%b-%Y','%d %b %Y','%d-%B-%Y','%d %B %Y'):
        try:
            return datetime.strptime(raw,fmt).date().strftime('%d %b %Y')
        except ValueError:
            pass
    return None

def _fetch_bse_direct():
    s=requests.Session()
    s.headers.update(BSE_HEADERS)
    exp_url=f'{BSE_BASE}/ddlExpiry_IV/w'
    resp=s.get(exp_url,params={'ProductType':BSE_PRODUCT_TYPE,'scrip_cd':BSE_SENSEX_SCRIP},timeout=20)
    resp.raise_for_status()
    payload=resp.json()
    table1=payload.get('Table1') if isinstance(payload,dict) else None
    expiries=[str(r.get('ExpiryDate','')).strip() for r in (table1 or []) if r.get('ExpiryDate')]
    normalized=[_expiry_to_bse(x) or x for x in expiries]
    today=date.today()
    parsed=[]
    for x in normalized:
        try:
            d=datetime.strptime(x,'%d %b %Y').date()
            if d>=today: parsed.append((d,x))
        except ValueError:
            continue
    if not parsed:
        raise RuntimeError('BSE expiry API returned no parseable future SENSEX expiries')
    parsed.sort(key=lambda z:z[0])
    expiry_bse=parsed[0][1]

    data_url=f'{BSE_BASE}/DerivOptionChain_IV/w'
    dresp=s.get(data_url,params={'Expiry':expiry_bse,'scrip_cd':BSE_SENSEX_SCRIP,'strprice':'0'},timeout=20)
    dresp.raise_for_status()
    data=dresp.json()
    rows=[]
    spot=0.0
    table=data.get('Table') if isinstance(data,dict) else None
    if not isinstance(table,list): table=[]
    for row in table:
        k=_num(row.get('Strike_Price1') or row.get('Strike_Price'))
        if k<=0: continue
        ce={
            'openInterest':_num(row.get('C_Open_Interest')),
            'changeinOpenInterest':_num(row.get('C_Absolute_Change_OI')),
            'totalTradedVolume':_num(row.get('C_Vol_Traded')),
            'impliedVolatility':_num(row.get('C_IV')),
            'lastPrice':_num(row.get('C_Last_Trd_Price')),
            'bidprice':_num(row.get('C_BidPrice')),
            'askPrice':_num(row.get('C_OfferPrice')),
        }
        pe={
            'openInterest':_num(row.get('Open_Interest')),
            'changeinOpenInterest':_num(row.get('Absolute_Change_OI')),
            'totalTradedVolume':_num(row.get('Vol_Traded')),
            'impliedVolatility':_num(row.get('IV')),
            'lastPrice':_num(row.get('Last_Trd_Price')),
            'bidprice':_num(row.get('BidPrice')),
            'askPrice':_num(row.get('OfferPrice')),
        }
        rows.extend([
            {'expiry':normalized[0] if normalized else expiry_bse,'strike':k,'option_type':'CE','ltp':ce['lastPrice'],'bid':ce['bidprice'],'ask':ce['askPrice'],'volume':ce['totalTradedVolume'],'open_interest':ce['openInterest']},
            {'expiry':normalized[0] if normalized else expiry_bse,'strike':k,'option_type':'PE','ltp':pe['lastPrice'],'bid':pe['bidprice'],'ask':pe['askPrice'],'volume':pe['totalTradedVolume'],'open_interest':pe['openInterest']},
        ])
        if not spot: spot=_num(row.get('UlaValue'))
    if not rows:
        raise RuntimeError('BSE official option-chain API returned no valid strikes')
    x=normalize_chain(rows)
    x.attrs['spot']=spot
    return x,{'source':'BSE_OFFICIAL_DERIVOPTIONCHAIN_IV','official':True,'scrip_cd':BSE_SENSEX_SCRIP,'expiry':expiry_bse}

def option_chain(underlying):
    if underlying=='NIFTY':
        try:
            res=asyncio.run(_india('NSE','NIFTY'))
            x=_india_rows(res)
            meta={'source':'INDIAOPT_NSE','official':False}
        except Exception as e:
            x,meta=_nse_direct()
            meta['indiaopt_error']=type(e).__name__+': '+str(e)
    elif underlying=='SENSEX':
        direct_error=None
        try:
            x,meta=_fetch_bse_direct()
        except Exception as e:
            direct_error=type(e).__name__+': '+str(e)
            try:
                res=asyncio.run(_india('BSE','999920'))
                x=_india_rows(res)
                meta={'source':'INDIAOPT_BSE_FALLBACK','official':False,'direct_bse_error':direct_error}
            except Exception as e2:
                raise RuntimeError(f'SENSEX providers unavailable. BSE official error={direct_error}; indiaopt fallback error={type(e2).__name__}: {e2}')
    else:
        raise ValueError(underlying)
    path,h=_save({'provider':meta,'rows':x.to_dict('records')},underlying.lower()+'_chain')
    meta.update({'snapshot_path':path,'snapshot_sha256':h})
    return x,meta

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
    idx=pd.to_datetime(j['timestamp'],unit='s',utc=True).tz_convert('Asia/Kolkata').tz_localize(None).normalize()
    s=pd.Series(j['indicators']['quote'][0]['close'],index=idx,name='close').dropna()
    s=s[~s.index.duplicated()].sort_index(); s.to_csv(p,header=['close'],index_label='date'); return s
