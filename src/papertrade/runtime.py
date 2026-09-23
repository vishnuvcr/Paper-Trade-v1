from datetime import date
import pandas as pd
from .calendar import nse_fo_holidays,d3_date,is_trading_day
from .ledger import append
from .run_nodip import run as nodip_run
from .scan import scan_mc

def mc_safe(underlying,now=None,manual=False):
 now=now or pd.Timestamp.now(tz='Asia/Kolkata')
 if not manual and not is_trading_day(now.date(),nse_fo_holidays(now.year)):
  r={'strategy':'MC-RQ6-v1','underlying':underlying,'observed_ist':now.isoformat(),'prospective_valid':False,'status':'NOT_TRADING_DAY','gate':False,'trade':False};append('signals',r);return r
 if not manual:
  from .market import option_chain
  from .common import nearest_expiry
  c,_=option_chain(underlying);e=nearest_expiry(c,now.date());h=nse_fo_holidays(e.year)
  if d3_date(e,h)!=now.date():
   r={'strategy':'MC-RQ6-v1','underlying':underlying,'expiry':str(e),'observed_ist':now.isoformat(),'prospective_valid':False,'status':'NOT_D3','gate':False,'trade':False};append('signals',r);return r
 return scan_mc(underlying,now=now,manual=manual)

def master(manual=False):
 now=pd.Timestamp.now(tz='Asia/Kolkata'); out=[nodip_run(now,manual)]
 for u in ('NIFTY','SENSEX'): out.append(mc_safe(u,now,manual))
 return out
