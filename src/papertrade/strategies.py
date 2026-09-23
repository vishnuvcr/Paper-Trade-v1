from datetime import date,timedelta
import pandas as pd
from .mc import LEGS as MC_LEGS,quantile_targets,choose_unique_strikes,portfolio_mc_ev
from .common import best_quote

NODIP_LEGS=(("NEAR_PE","PE",1),("NEAR_CE","CE",-1),("FAR_CE","CE",1),("FAR_PE","PE",-1))
NODIP_VARIANTS={"NODIP_3W":3,"NODIP_1W":1}

def select_nodip_expiries(chain,today,far_weeks):
    if "expiry" not in chain.columns:
        raise ValueError("option chain has no expiry")
    xs=sorted({d.date() for d in pd.to_datetime(chain["expiry"],errors="coerce").dropna() if d.date()>=today})
    if not xs:
        raise ValueError("no listed NIFTY expiry")
    near=xs[0]
    target=near+timedelta(days=7*far_weeks)
    far=next((d for d in xs if d>=target),None)
    if far is None:
        raise ValueError(f"no far expiry available for {far_weeks}-week variant")
    if far==near:
        raise ValueError("far expiry must differ from near expiry")
    return near,far

def nodip_signal(chain,spot,near_expiry,far_expiry=None,variant="NODIP_3W"):
    # Backward-compatible unit-test/control signature: when no far expiry is supplied,
    # use the same expiry for both legs. Production runners always provide a selected far expiry.
    near=chain[chain.expiry==pd.Timestamp(near_expiry)]
    far=chain[chain.expiry==pd.Timestamp(far_expiry)]
    if near.empty or far.empty:
        raise ValueError("near/far expiry slice is empty")

    near_strikes=sorted({float(k) for k in near.strike.dropna()})
    if not near_strikes:
        raise ValueError("no near strikes")
    atm=min(near_strikes,key=lambda k:(abs(k-spot),k))

    near_ce=atm
    near_pe=atm

    far_ce_strikes=sorted(k for k in far.strike.dropna().unique()
                          if not far[(far.option_type=="CE")&(far.strike==k)].empty)
    far_pe_strikes=sorted(k for k in far.strike.dropna().unique()
                          if not far[(far.option_type=="PE")&(far.strike==k)].empty)
    far_ce=next((float(k) for k in far_ce_strikes if float(k)>atm),None)
    far_pe=next((float(k) for k in reversed(far_pe_strikes) if float(k)<atm),None)
    if far_ce is None or far_pe is None:
        raise ValueError("missing adjacent far-expiry strikes")

    labels={"NEAR_CE":near_ce,"NEAR_PE":near_pe,"FAR_CE":far_ce,"FAR_PE":far_pe}
    expiries={"NEAR_CE":str(near_expiry),"NEAR_PE":str(near_expiry),
              "FAR_CE":str(far_expiry),"FAR_PE":str(far_expiry)}

    px={}
    for lab in labels:
        side="CE" if lab.endswith("CE") else "PE"
        expiry_slice=near if lab.startswith("NEAR") else far
        q=best_quote(expiry_slice,side,labels[lab])
        px[lab]=q.ltp

    if any(v is None or v<=0 for v in px.values()):
        raise ValueError("four positive LTPs required")

    cbr=(px["FAR_CE"]/px["NEAR_CE"])/(px["FAR_PE"]/px["NEAR_PE"])
    return {
        "strategy":variant,
        "underlying":"NIFTY",
        "near_expiry":str(near_expiry),
        "far_expiry":str(far_expiry),
        "atm":atm,
        "strikes":labels,
        "leg_expiries":expiries,
        "prices":px,
        "cbr":float(cbr),
        "gate":bool(cbr<=1.20),
        "legs":NODIP_LEGS,
        "far_expiry_weeks":NODIP_VARIANTS[variant]
    }

def mc_signal(chain,s0,returns):
    terminals=__import__("papertrade.mc",fromlist=["simulate_terminal_paths"]).simulate_terminal_paths(s0,returns)
    targets=quantile_targets(terminals); strikes=choose_unique_strikes(chain,targets); ev=portfolio_mc_ev(terminals,strikes,chain)
    return {"targets":targets,"strikes":strikes,"mc_ev_points":float(ev),"gate":bool(ev>0),"legs":MC_LEGS,"terminal_mean":float(terminals.mean())}

def entry_prices(chain,legs,strikes,slippage=2.0):
    out={}; sources={}
    from .common import entry_price
    for label,side,q,*_ in legs:
        qte=best_quote(chain,side,strikes[label]); out[label],sources[label]=entry_price(qte,q,slippage)
    return out,sources
