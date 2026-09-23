from datetime import date
import pandas as pd
from src.papertrade.calendar import d3_date
from src.papertrade.strategies import nodip_signal
from src.papertrade.common import normalize_chain

def test_d3_calendar_counting():
 h={date(2026,9,14)}
 assert d3_date(date(2026,9,17),h)==date(2026,9,14)

def test_nodip_threshold_rule():
 rows=[]
 for k,ce,pe in [(19900,120,80),(20000,100,100),(20100,90,110)]:
  rows += [{'expiry':'2026-09-29','strike':k,'option_type':'CE','ltp':ce,'bid':ce-1,'ask':ce+1},{'expiry':'2026-09-29','strike':k,'option_type':'PE','ltp':pe,'bid':pe-1,'ask':pe+1}]
 x=normalize_chain(rows); s=nodip_signal(x,20000,pd.Timestamp('2026-09-29'))
 assert s['cbr']>0
 assert s['gate'] == (s['cbr']<=1.20)
