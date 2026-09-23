from datetime import time,timedelta
import pandas as pd
from .ledger import open_positions,append,now_utc
from .market import option_chain
from .common import best_quote,mark_price
from .costs import entry_cost
from .calendar import nse_fo_holidays

def _previous_session(expiry,holidays):
    d=expiry-timedelta(days=1)
    while d.weekday()>=5 or d in holidays:
        d-=timedelta(days=1)
    return d

def close_due():
    now=pd.Timestamp.now(tz="Asia/Kolkata")
    holidays=nse_fo_holidays(now.year)

    for pid,pos in open_positions().items():
        if not str(pos.get("strategy","")).startswith("NODIP_"):
            continue

        near_expiry=pd.Timestamp(pos["near_expiry"]).date()
        exit_day=_previous_session(near_expiry,holidays)

        if now.date()!=exit_day or now.time()<time(15,20):
            continue

        try:
            chain,_=option_chain("NIFTY")
            gross_points=0.0
            px={}

            for label,q in pos["quantities"].items():
                side="PE" if label.endswith("PE") else "CE"
                leg_expiry=pd.Timestamp(pos["leg_expiries"][label])
                leg_chain=chain[chain.expiry==leg_expiry]
                p,_=mark_price(best_quote(leg_chain,side,pos["strikes"][label]),q)
                px[label]=p
                gross_points += q*(p-pos["entry_prices"][label])

            gross=gross_points*pos["lot_size"]
            exit_cost=entry_cost(
                "NIFTY",
                px,
                {k:-v for k,v in pos["quantities"].items()},
                pos["lot_size"],
                now.date()
            )
            net=gross-float(pos["entry_costs"]["total"])-exit_cost["total"]

            append("events",{
                "event_type":"CLOSE",
                "timestamp_utc":now_utc(),
                "position_id":pid,
                "strategy":pos["strategy"],
                "strategy_label":pos.get("strategy_label"),
                "underlying":"NIFTY",
                "near_expiry":pos["near_expiry"],
                "far_expiry":pos["far_expiry"],
                "reason":"previous_session_before_near_expiry",
                "gross_realized_pnl_rupees":gross,
                "entry_cost_rupees":pos["entry_costs"]["total"],
                "exit_cost_rupees":exit_cost["total"],
                "realized_net_pnl_rupees":net,
                "exit_prices":px,
                "closed_observed_ist":now.isoformat()
            })
        except Exception as e:
            append("errors",{
                "timestamp_utc":now_utc(),
                "mode":"nodip_exit",
                "strategy":pos.get("strategy"),
                "position_id":pid,
                "error":type(e).__name__,
                "message":str(e)
            })
