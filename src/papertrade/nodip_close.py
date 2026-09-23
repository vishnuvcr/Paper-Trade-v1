from datetime import time,timedelta
import pandas as pd
from .ledger import open_positions,append,now_utc
from .market import option_chain
from .common import best_quote,mark_price
from .costs import entry_cost
from .calendar import nse_fo_holidays

def close_due():
 now=pd.Timestamp.now(tz='Asia/Kolkata'); h=nse_fo_holidays(now.year)
 for pid,pos in open_positions().items():
  if pos.get('strategy')!='NoDip': continue
  e=pd.Timestamp(pos['expiry']).date(); d=e-timedelta(days=1)
  while d.weekday()>=5 or d in h: d-=timedelta(days=1)
  if now.date()!=d or now.time()<time(15,20): continue
  try:
   c,_=option_chain('NIFTY'); x=c[c.expiry==pd.Timestamp(e)]; gross=0.0; px={}
   for lab,q in pos['quantities'].items():
    side='PE' if lab.endswith('PE') else 'CE'; p,_=mark_price(best_quote(x,side,pos['strikes'][lab]),q); px[lab]=p; gross+=q*(p-pos['entry_prices'][lab])
   gross*=pos['lot_size']; ec=entry_cost('NIFTY',px,{k:-v for k,v in pos['quantities'].items()},pos['lot_size'],now.date())
   append('events',{'event_type':'CLOSE','timestamp_utc':now_utc(),'position_id':pid,'strategy':'NoDip','underlying':'NIFTY','expiry':pos['expiry'],'reason':'near_expiry','gross_realized_pnl_rupees':gross,'entry_cost_rupees':pos['entry_costs']['total'],'exit_cost_rupees':ec['total'],'realized_net_pnl_rupees':gross-pos['entry_costs']['total']-ec['total'],'exit_prices':px})
  except Exception as e: append('errors',{'timestamp_utc':now_utc(),'mode':'nodip_exit','position_id':pid,'error':type(e).__name__,'message':str(e)})
