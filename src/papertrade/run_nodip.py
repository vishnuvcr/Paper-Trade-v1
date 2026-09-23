from datetime import time,date
import pandas as pd
from .market import option_chain,daily_close
from .common import nearest_expiry,entry_price,best_quote,stable_id
from .mc import parity_spot
from .strategies import nodip_signal,NODIP_LEGS
from .ledger import append,open_positions,now_utc
from .calendar import nse_fo_holidays,is_trading_day
from .costs import entry_cost

def _lot(): return 65

def run(now=None,manual=False):
    now=now or pd.Timestamp.now(tz='Asia/Kolkata')
    holidays=nse_fo_holidays(now.year)
    base={'strategy':'NoDip','underlying':'NIFTY','observed_ist':now.isoformat(),'prospective_valid':False}

    if not is_trading_day(now.date(),holidays):
        base.update(status='NOT_TRADING_DAY',gate=False,trade=False)
        append('signals',base)
        return base

    # Frozen signal time. We deliberately do not "catch up" with a late quote,
    # because that would change the prospective strategy definition.
    if manual or now.time()!=time(9,35):
        status='DIAGNOSTIC' if manual else 'TIMING_INVALID'
        base.update(status=status,gate=False,trade=False)
        append('signals',base)
        return base

    try:
        chain,meta=option_chain('NIFTY')
        expiry=nearest_expiry(chain,now.date())
        if expiry<=now.date():
            base.update(expiry=str(expiry),status='NO_EXPIRY_HEADROOM',gate=False,trade=False)
            append('signals',base)
            return base

        x=chain[chain.expiry==pd.Timestamp(expiry)]
        daily=daily_close('^NSEI')
        prev=float(daily[daily.index<pd.Timestamp(now.date())].iloc[-1])
        spot,spot_src=parity_spot(x,prev)
        s=nodip_signal(x,spot,pd.Timestamp(expiry))
        sid=stable_id({'strategy':'NoDip','expiry':str(expiry),'date':str(now.date())})
        base.update(s)
        base.update({'signal_id':sid,'provider':meta,'spot':spot,'spot_source':spot_src,
                     'prospective_valid':True,'trade':False})

        already=any(p.get('strategy')=='NoDip' and p.get('expiry')==str(expiry)
                    for p in open_positions().values())
        if s['gate'] and not already:
            try:
                qty={x[0]:x[2] for x in NODIP_LEGS}
                prices={}; srcs={}
                for lab,side,q in NODIP_LEGS:
                    prices[lab],srcs[lab]=entry_price(
                        best_quote(x,side,s['strikes'][lab]),q,2.0)
                costs=entry_cost('NIFTY',prices,qty,_lot(),now.date())
                pid=stable_id({'signal_id':sid,'prices':prices})
                pos={'position_id':pid,'signal_id':sid,'strategy':'NoDip',
                     'underlying':'NIFTY','expiry':str(expiry),'opened_at_utc':now_utc(),
                     'lot_size':_lot(),'strikes':s['strikes'],'entry_prices':prices,
                     'entry_sources':srcs,'quantities':qty,'entry_costs':costs,
                     'config_fingerprint':__import__('src.papertrade.config',fromlist=['fingerprint']).fingerprint(),
                     'paper_only':True}
                append('events',{'event_type':'OPEN','timestamp_utc':now_utc(),
                                 'position_id':pid,'position':pos})
                base.update(trade=True,status='PAPER_OPEN',position_id=pid)
            except Exception as e:
                append('errors',{'timestamp_utc':now_utc(),'strategy':'NoDip',
                                 'error':type(e).__name__,'message':str(e)})
                base.update(trade=False,status='ENTRY_UNAVAILABLE')
        else:
            base['status']='GATE_PASS' if s['gate'] else 'GATE_FAIL'
        append('signals',base)
        return base

    except Exception as e:
        append('errors',{'timestamp_utc':now_utc(),'strategy':'NoDip',
                         'mode':'scheduled_signal','error':type(e).__name__,'message':str(e)})
        base.update(status='DATA_UNAVAILABLE',gate=False,trade=False,
                    error=type(e).__name__)
        append('signals',base)
        return base
