from datetime import time,date,timedelta
import pandas as pd
from .market import option_chain,daily_close
from .common import entry_price,best_quote,stable_id
from .mc import parity_spot
from .strategies import nodip_signal,NODIP_LEGS,NODIP_VARIANTS,select_nodip_expiries
from .ledger import append,open_positions,now_utc
from .calendar import nse_fo_holidays,is_trading_day
from .costs import entry_cost
from .config import fingerprint

def _lot(): return 65

def _variant_label(variant):
    return "NoDip — 3W far expiry" if variant=="NODIP_3W" else "NoDip — 1W far expiry"

def _already(variant,near_expiry,far_expiry):
    return any(
        p.get("strategy")==variant
        and p.get("near_expiry")==str(near_expiry)
        and p.get("far_expiry")==str(far_expiry)
        for p in open_positions().values()
    )

def run_variant(variant="NODIP_3W",now=None,manual=False):
    if variant not in NODIP_VARIANTS:
        raise ValueError(f"unknown NoDip variant: {variant}")

    now=now or pd.Timestamp.now(tz="Asia/Kolkata")
    holidays=nse_fo_holidays(now.year)
    base={
        "strategy":variant,
        "strategy_label":_variant_label(variant),
        "underlying":"NIFTY",
        "observed_ist":now.isoformat(),
        "prospective_valid":False
    }

    if not is_trading_day(now.date(),holidays):
        base.update(status="NOT_TRADING_DAY",gate=False,trade=False)
        append("signals",base)
        return base

    # Scheduled prospective observation is exactly 09:35 IST.
    # A delayed GitHub Actions run is recorded as TIMING_INVALID rather than
    # silently converting a later observation into the frozen signal timestamp.
    if manual or not (time(9,35)<=now.time()<time(9,36)):
        base.update(status="DIAGNOSTIC" if manual else "TIMING_INVALID",gate=False,trade=False)
        append("signals",base)
        return base

    try:
        chain,meta=option_chain("NIFTY")
        near_expiry,far_expiry=select_nodip_expiries(chain,now.date(),NODIP_VARIANTS[variant])
        near=chain[chain.expiry==pd.Timestamp(near_expiry)]
        prev_close=daily_close("^NSEI")
        prev=float(prev_close[prev_close.index<pd.Timestamp(now.date())].iloc[-1])
        spot,spot_src=parity_spot(near,prev)

        s=nodip_signal(chain,spot,pd.Timestamp(near_expiry),pd.Timestamp(far_expiry),variant)
        sid=stable_id({
            "strategy":variant,
            "near_expiry":str(near_expiry),
            "far_expiry":str(far_expiry),
            "date":str(now.date())
        })

        base.update(s)
        base.update({
            "signal_id":sid,
            "provider":meta,
            "spot":spot,
            "spot_source":spot_src,
            "prospective_valid":True,
            "trade":False
        })

        already=_already(variant,near_expiry,far_expiry)
        if s["gate"] and not already:
            try:
                qty={x[0]:x[2] for x in NODIP_LEGS}
                prices={};sources={}
                for lab,side,q in NODIP_LEGS:
                    expiry_date=pd.Timestamp(s["leg_expiries"][lab])
                    expiry_slice=chain[chain.expiry==expiry_date]
                    prices[lab],sources[lab]=entry_price(
                        best_quote(expiry_slice,side,s["strikes"][lab]),q,2.0
                    )

                costs=entry_cost("NIFTY",prices,qty,_lot(),now.date())
                pid=stable_id({"signal_id":sid,"prices":prices})

                pos={
                    "position_id":pid,
                    "signal_id":sid,
                    "strategy":variant,
                    "strategy_label":_variant_label(variant),
                    "underlying":"NIFTY",
                    "near_expiry":str(near_expiry),
                    "far_expiry":str(far_expiry),
                    "expiry":str(near_expiry),
                    "lot_size":_lot(),
                    "strikes":s["strikes"],
                    "leg_expiries":s["leg_expiries"],
                    "entry_prices":prices,
                    "entry_sources":sources,
                    "quantities":qty,
                    "entry_costs":costs,
                    "config_fingerprint":fingerprint(),
                    "paper_only":True,
                    "opened_at_utc":now_utc()
                }
                append("events",{
                    "event_type":"OPEN",
                    "timestamp_utc":now_utc(),
                    "position_id":pid,
                    "position":pos
                })
                base.update(trade=True,status="PAPER_OPEN",position_id=pid)
            except Exception as e:
                append("errors",{
                    "timestamp_utc":now_utc(),
                    "strategy":variant,
                    "mode":"entry",
                    "error":type(e).__name__,
                    "message":str(e)
                })
                base.update(trade=False,status="ENTRY_UNAVAILABLE")
        else:
            base["status"]="GATE_PASS" if s["gate"] else "GATE_FAIL"

        append("signals",base)
        return base

    except Exception as e:
        append("errors",{
            "timestamp_utc":now_utc(),
            "strategy":variant,
            "mode":"scheduled_signal",
            "error":type(e).__name__,
            "message":str(e)
        })
        base.update(status="DATA_UNAVAILABLE",gate=False,trade=False,error=type(e).__name__)
        append("signals",base)
        return base

def run(now=None,manual=False):
    return run_variant("NODIP_3W",now,manual)

def run_all_variants(now=None,manual=False):
    return [
        run_variant("NODIP_3W",now,manual),
        run_variant("NODIP_1W",now,manual)
    ]
