from datetime import time
import pandas as pd
from .ledger import open_positions,append,now_utc
from .market import option_chain
from .common import best_quote,mark_price
from .costs import entry_cost
from .calendar import nse_fo_holidays,d3_date,is_trading_day

def close_due():
 now=pd.Timestamp.now(tz='Asia/Kolkata'); holidays=nse_fo_holidays(now.year)
 for pid,pos in open_positions().items():
  if pos.get('strategy')!='NoDip': continue
  e=pd.Timestamp(pos['expiry']).date(); exit_day=d3_date(e,holidays)
  if now.date()!=exit_day or now.time()<time(15,20): continue
  try:
   chain,_=option_chain('NIFTY');x=chain[chain.expiry==pd.Timestamp(e)];points=0;pxs={}
   for label,q in pos['quantities'].items():
    side='PE' if label.endswith('PE') else 'CE';px,_s=mark_price(best_quote(x,side,pos['strikes'][label]),q);pxs[label]=px;points+=q*(px-pos['entry_prices'][label])
   gross=points*pos['lot_size']; exit_cost=entry_cost('NIFTY',pxs,{k:-v for k,v in pos['quantities'].items()},pos['lot_size'],now.date());net=gross-float(pos['entry_costs']['total'])-exit_cost['total']
   append('events',{'event_type':'CLOSE','timestamp_utc':now_utc(),'position_id':pid,'strategy':'NoDip','underlying':'NIFTY','expiry':pos['expiry'],'reason':'near_expiry','gross_realized_pnl_rupees':gross,'entry_cost_rupees':pos['entry_costs']['total'],'exit_cost_rupees':exit_cost['total'],'realized_net_pnl_rupees':net,'exit_prices':pxs,'observed_ist':now.isoformat()})
  except Exception as e:append('errors',{'timestamp_utc':now_utc(),'mode':'nodip_exit','position_id':pid,'error':type(e).__name__,'message':str(e)})
