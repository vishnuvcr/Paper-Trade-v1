import pandas as pd
from .calendar import nse_fo_holidays,is_trading_day
from .ledger import append,now_utc
from .run_nodip import run as nodip_run
from .scan import scan_mc


def mc_safe(underlying,now=None,manual=False):
 now=now or pd.Timestamp.now(tz='Asia/Kolkata')
 if not manual and not is_trading_day(now.date(),nse_fo_holidays(now.year)):
  r={'strategy':'MC-RQ6-v1','underlying':underlying,'observed_ist':now.isoformat(),'prospective_valid':False,'status':'NOT_TRADING_DAY','gate':False,'trade':False};append('signals',r);return r
 try:
  return scan_mc(underlying,now=now,manual=manual)
 except Exception as e:
  # A provider outage must not abort the master run or contaminate the other strategy.
  r={'strategy':'MC-RQ6-v1','underlying':underlying,'observed_ist':now.isoformat(),'prospective_valid':False,'status':'DATA_UNAVAILABLE','gate':False,'trade':False,'error':type(e).__name__}
  append('errors',{'timestamp_utc':now_utc(),'strategy':'MC-RQ6-v1','underlying':underlying,'mode':'master','error':type(e).__name__,'message':str(e)})
  append('signals',r)
  return r


def master(manual=False):
 now=pd.Timestamp.now(tz='Asia/Kolkata');out=[]
 try:
  out.append(nodip_run(now,manual))
 except Exception as e:
  append('errors',{'timestamp_utc':now_utc(),'strategy':'NoDip','mode':'master','error':type(e).__name__,'message':str(e)})
  out.append({'strategy':'NoDip','underlying':'NIFTY','observed_ist':now.isoformat(),'prospective_valid':False,'status':'DATA_UNAVAILABLE','gate':False,'trade':False})
 for u in ('NIFTY','SENSEX'): out.append(mc_safe(u,now,manual))
 return out
