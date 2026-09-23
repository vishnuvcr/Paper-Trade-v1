from datetime import datetime,time,date,timedelta
import pandas as pd
from .ledger import append,open_positions,now_utc
from .market import option_chain,daily_close
from .common import best_quote,mark_price,stable_id
from .costs import expiry_cost
IST='Asia/Kolkata'

def _expiry_close_time(u): return time(15,35) if u=='SENSEX' else time(15,35)

def _mark_one(pid,pos,now):
 chain,meta=option_chain(pos['underlying']); e=date.fromisoformat(pos['expiry']); x=chain[chain.expiry==pd.Timestamp(e)]
 if x.empty:raise ValueError('open expiry missing from current chain')
 points=0.0; marks={}
 for label,q in pos['quantities'].items():
  side='PE' if label.endswith('PE') else 'CE'; k=pos['strikes'][label]; px,src=mark_price(best_quote(x,side,k),q); points+=q*(px-pos['entry_prices'][label]);marks[label]={'price':px,'source':src}
 gross=points*pos['lot_size']; net=gross-float(pos['entry_costs']['total'])
 append('events',{'event_type':'MARK','timestamp_utc':now_utc(),'position_id':pid,'strategy':pos['strategy'],'underlying':pos['underlying'],'expiry':pos['expiry'],'gross_mtm_rupees':gross,'net_est_mtm_rupees':net,'marks':marks,'provider':meta,'observed_ist':now.isoformat()})

def _close_one(pid,pos,now,reason='expiry_settlement'):
 e=date.fromisoformat(pos['expiry']); daily=daily_close('^NSEI' if pos['underlying']=='NIFTY' else '^BSESN'); rows=daily[daily.index<=pd.Timestamp(e)]
 if rows.empty:raise ValueError('settlement close unavailable')
 settlement=float(rows.iloc[-1]); pnl=0.0
 for label,q in pos['quantities'].items():
  k=pos['strikes'][label]; intrinsic=max(k-settlement,0) if label.endswith('PE') else max(settlement-k,0); pnl+=q*(intrinsic-pos['entry_prices'][label])
 gross=pnl*pos['lot_size']; stt=expiry_cost(e,settlement,pos['strikes'],pos['quantities'],pos['lot_size']); net=gross-float(pos['entry_costs']['total'])-stt
 append('events',{'event_type':'CLOSE','timestamp_utc':now_utc(),'position_id':pid,'strategy':pos['strategy'],'underlying':pos['underlying'],'expiry':pos['expiry'],'reason':reason,'settlement':settlement,'gross_realized_pnl_rupees':gross,'entry_cost_rupees':pos['entry_costs']['total'],'expiry_stt_rupees':stt,'realized_net_pnl_rupees':net,'closed_observed_ist':now.isoformat()})

def mark_all():
 now=pd.Timestamp.now(tz=IST); rid=stable_id({'mode':'mark','ts':now.isoformat()});append('runs',{'run_id':rid,'mode':'mark','timestamp_utc':now_utc()})
 for pid,pos in open_positions().items():
  try:
   e=date.fromisoformat(pos['expiry']);
   if now.date()>e or (now.date()==e and now.time()>=_expiry_close_time(pos['underlying'])): _close_one(pid,pos,now)
   else:_mark_one(pid,pos,now)
  except Exception as ex:append('errors',{'timestamp_utc':now_utc(),'mode':'mark','position_id':pid,'error':type(ex).__name__,'message':str(ex)})
