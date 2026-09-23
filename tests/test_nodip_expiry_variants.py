import pandas as pd
from src.papertrade.common import normalize_chain
from src.papertrade.strategies import select_nodip_expiries,nodip_signal

def make_chain():
    expiries=["2026-09-24","2026-10-01","2026-10-08","2026-10-15","2026-10-22"]
    rows=[]
    for i,e in enumerate(expiries):
        for k in [19800,19900,20000,20100,20200]:
            rows.append({"expiry":e,"strike":k,"option_type":"CE","ltp":100+i+k/100000,"bid":99+i+k/100000,"ask":101+i+k/100000})
            rows.append({"expiry":e,"strike":k,"option_type":"PE","ltp":100-i+k/100000,"bid":99-i+k/100000,"ask":101-i+k/100000})
    return normalize_chain(rows)

def test_far_expiry_selection():
    x=make_chain()
    near,far1=select_nodip_expiries(x, pd.Timestamp("2026-09-23").date(), 1)
    near2,far3=select_nodip_expiries(x, pd.Timestamp("2026-09-23").date(), 3)
    assert near==near2
    assert near==pd.Timestamp("2026-09-24").date()
    assert far1==pd.Timestamp("2026-10-01").date()
    assert far3==pd.Timestamp("2026-10-15").date()

def test_nodip_signal_uses_different_far_expiry():
    x=make_chain()
    near,far1=select_nodip_expiries(x,pd.Timestamp("2026-09-23").date(),1)
    _,far3=select_nodip_expiries(x,pd.Timestamp("2026-09-23").date(),3)
    s1=nodip_signal(x,20000,pd.Timestamp(near),pd.Timestamp(far1),"NODIP_1W")
    s3=nodip_signal(x,20000,pd.Timestamp(near),pd.Timestamp(far3),"NODIP_3W")
    assert s1["far_expiry"].startswith("2026-10-01")
    assert s3["far_expiry"].startswith("2026-10-15")
    assert s1["leg_expiries"]["NEAR_CE"].startswith("2026-09-24")
    assert s1["leg_expiries"]["FAR_CE"].startswith("2026-10-01")
    assert s3["leg_expiries"]["FAR_CE"].startswith("2026-10-15")
