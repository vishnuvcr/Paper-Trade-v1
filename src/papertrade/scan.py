from datetime import datetime,date,time
import pandas as pd
from .config import CFG,fingerprint
from .market import option_chain,daily_close
from .common import nearest_expiry,entry_price,best_quote,stable_id
from .mc import historical_log_returns,simulate_terminal_paths,parity_spot,quantile_targets,choose_unique_strikes,portfolio_mc_ev,LEGS as MC_LEGS
from .strategies import nodip_signal,NODIP_LEGS
from .ledger import append,now_utc,open_positions
from .calendar import nse_fo_holidays,d3_date
from .costs import entry_cost
IST='Asia/Kolkata'

def _eligible_time(strategy,now):
 if strategy=='NoDip': return time(9,25)<=now.time()<=time(9,45)
 return time(9,25)<=now.time()<=time(9,40)

def _lot(u,d): return 65 if u=='NIFTY' and d>=date(2026,1,6) else 20 if u=='SENSEX' else 0

def _open(strategy,u,expiry,strikes,legs,chain,ts,extra):
 qty={x[0]:x[2] for x in legs}; prices={}; sources={}
 for label,side,q,*_ in legs:
  p,s=entry_price(best_quote(chain,side,strikes[label]),q,2.0); prices[label]=p; sources[label]=s
 lot=_lot(u,expiry)
 if not lot: raise ValueError('lot size unavailable')
 costs=entry_cost(u,prices,qty,lot,expiry if False else ts.date())
 sig=extra['signal_id']; pid=stable_id({'signal_id':sig,'prices':prices})
 position={'position_id':pid,'signal_id':sig,'strategy':strategy,'underlying':u,'expiry':str(expiry),'opened_at_utc':now_utc(),'lot_size':lot,'strikes':strikes,'entry_prices':prices,'entry_sources':sources,'quantities':qty,'entry_costs':costs,'config_fingerprint':fingerprint(),'paper_only':True}
 append('events',{'event_type':'OPEN','timestamp_utc':now_utc(),'position_id':pid,'position':position}); return position

def _already(strategy,u,expiry): return any(p.get('strategy')==strategy and p.get('underlying')==u and p.get('expiry')==str(expiry) for p in open_positions().values())

def scan_nodip(now=None,manual=False):
 now=now or pd.Timestamp.now(tz=IST); u='NIFTY'; chain,meta=option_chain(u); expiry=nearest_expiry(chain,now.date()); x=chain[chain.expiry==pd.Timestamp(expiry)]
 spot=float(x.attrs.get('spot',0) or x.strike.median())
 if 'last' in x.attrs: spot=float(x.attrs['last'])
 sig=stable_id({'strategy':'NoDip','underlying':u,'expiry':str(expiry),'date':str(now.date())}); base={'signal_id':sig,'strategy':'NoDip','underlying':u,'expiry':str(expiry),'observed_ist':now.isoformat(),'prospective_valid':bool(_eligible_time('NoDip',now) and not manual),'provider':meta}
 if manual or not _eligible_time('NoDip',now): append('signals',{**base,'status':'DIAGNOSTIC' if manual else 'TIMING_INVALID','gate':False,'trade':False}); return base
 s=nodip_signal(x,spot,pd.Timestamp(expiry)); base.update(s)
 base['prospective_valid']=True;base['gate']=s['gate'];base['status']='GATE_PASS' if s['gate'] else 'GATE_FAIL';base['trade']=False
 if s['gate'] and not _already('NoDip',u,expiry):
  try:
   p=_open('NoDip',u,expiry,s['strikes'],NODIP_LEGS,x,now,base); base.update({'trade':True,'position_id':p['position_id'],'status':'PAPER_OPEN'})
  except Exception as e: append('errors',{'timestamp_utc':now_utc(),'strategy':'NoDip','error':type(e).__name__,'message':str(e)});base['status']='ENTRY_UNAVAILABLE'
 append('signals',base);return base

def scan_mc(underlying,now=None,manual=False):
 now=now or pd.Timestamp.now(tz=IST); chain,meta=option_chain(underlying); expiry=nearest_expiry(chain,now.date()); holidays=nse_fo_holidays(expiry.year) if underlying=='NIFTY' else set()
 due=(d3_date(expiry,holidays)==now.date()) and _eligible_time('MC',now) if underlying=='NIFTY' else _eligible_time('MC',now)
 sig=stable_id({'strategy':'MC-RQ6-v1','underlying':underlying,'expiry':str(expiry),'date':str(now.date())}); base={'signal_id':sig,'strategy':'MC-RQ6-v1','underlying':underlying,'expiry':str(expiry),'observed_ist':now.isoformat(),'provider':meta,'prospective_valid':bool(due and not manual)}
 if manual or not due: append('signals',{**base,'status':'DIAGNOSTIC' if manual else 'NOT_D3','gate':False,'trade':False});return base
 ticker='^NSEI' if underlying=='NIFTY' else '^BSESN'; daily=daily_close(ticker); previous=float(daily[daily.index<pd.Timestamp(now.date())].iloc[-1]); x=chain[chain.expiry==pd.Timestamp(expiry)]; s0,src=parity_spot(x,previous); r=historical_log_returns(daily,pd.Timestamp(now.date()),756); terms=simulate_terminal_paths(s0,r); targets=quantile_targets(terms); strikes=choose_unique_strikes(x,targets); ev=portfolio_mc_ev(terms,strikes,x); base.update({'s0':s0,'s0_source':src,'targets':targets,'strikes':strikes,'mc_ev_points':ev,'gate':bool(ev>0),'trade':False,'status':'GATE_PASS' if ev>0 else 'GATE_FAIL'})
 if ev>0 and not _already('MC-RQ6-v1',underlying,expiry):
  try:
   p=_open('MC-RQ6-v1',underlying,expiry,strikes,MC_LEGS,x,now,base);base.update({'trade':True,'status':'PAPER_OPEN','position_id':p['position_id']})
  except Exception as e:append('errors',{'timestamp_utc':now_utc(),'strategy':'MC-RQ6-v1','underlying':underlying,'error':type(e).__name__,'message':str(e)});base['status']='ENTRY_UNAVAILABLE'
 append('signals',base);return base

def scan_all(manual=False):
 now=pd.Timestamp.now(tz=IST); rid=stable_id({'mode':'scan_all','ts':now.isoformat(),'manual':manual}); append('runs',{'run_id':rid,'mode':'scan_all','timestamp_utc':now_utc(),'config_fingerprint':fingerprint(),'manual':manual})
 out=[]
 try: out.append(scan_nodip(now,manual))
 except Exception as e:append('errors',{'timestamp_utc':now_utc(),'strategy':'NoDip','error':type(e).__name__,'message':str(e)})
 for u in ('NIFTY','SENSEX'):
  try:out.append(scan_mc(u,now,manual))
  except Exception as e:append('errors',{'timestamp_utc':now_utc(),'strategy':'MC-RQ6-v1','underlying':u,'error':type(e).__name__,'message':str(e)})
 return out
