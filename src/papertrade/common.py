import hashlib,json
from dataclasses import dataclass
import pandas as pd

@dataclass(frozen=True)
class LegQuote:
 bid: float|None
 ask: float|None
 ltp: float|None

def normalize_chain(rows):
 x=pd.DataFrame(rows)
 if x.empty: raise ValueError('empty option chain')
 aliases={'strikePrice':'strike','lastPrice':'ltp','optionType':'option_type','expiryDate':'expiry','bidPrice':'bid','offerPrice':'ask'}
 for s,d in aliases.items():
  if s in x and d not in x:x[d]=x[s]
 if not {'strike','option_type','ltp'}.issubset(x.columns): raise ValueError('chain schema incomplete')
 for c in ('strike','ltp','bid','ask','volume','open_interest'):
  if c in x:x[c]=pd.to_numeric(x[c],errors='coerce')
 x['option_type']=x['option_type'].astype(str).str.upper().replace({'CALL':'CE','PUT':'PE'})
 if 'expiry' in x:x['expiry']=pd.to_datetime(x['expiry'],errors='coerce').dt.normalize()
 return x

def nearest_expiry(chain,today):
 xs=sorted({d.date() for d in pd.to_datetime(chain['expiry'],errors='coerce').dropna() if d.date()>=today})
 if not xs:raise ValueError('no future expiry')
 return xs[0]

def best_quote(chain,side,strike):
 x=chain.loc[(chain.option_type==side)&(chain.strike==float(strike))]
 if x.empty:raise ValueError('missing quote')
 r=x.iloc[-1]
 return LegQuote(None if pd.isna(r.get('bid')) else float(r.bid),None if pd.isna(r.get('ask')) else float(r.ask),None if pd.isna(r.get('ltp')) else float(r.ltp))

def entry_price(q,qty,slippage=2.0):
 if qty>0 and q.ask and q.ask>0:return q.ask+slippage,'ask_plus_slippage'
 if qty<0 and q.bid and q.bid>0 and q.bid-slippage>0:return q.bid-slippage,'bid_minus_slippage'
 if q.ltp and q.ltp>0 and (q.ltp+slippage if qty>0 else q.ltp-slippage)>0:return (q.ltp+slippage if qty>0 else q.ltp-slippage),'ltp_slippage'
 raise ValueError('no executable price')

def mark_price(q,qty):
 if qty>0 and q.bid and q.bid>0:return q.bid,'bid'
 if qty<0 and q.ask and q.ask>0:return q.ask,'ask'
 if q.ltp and q.ltp>0:return q.ltp,'ltp_fallback'
 raise ValueError('no mark price')

def stable_id(payload):
 return hashlib.sha256(json.dumps(payload,sort_keys=True,default=str,separators=(',',':')).encode()).hexdigest()[:20]
