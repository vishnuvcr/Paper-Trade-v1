from datetime import date
import numpy as np,pandas as pd
from src.papertrade.common import normalize_chain,entry_price,LegQuote
from src.papertrade.mc import simulate_terminal_paths,quantile_targets,choose_unique_strikes
from src.papertrade.strategies import nodip_signal

def chain():
 rows=[]
 for k in [19800,19900,20000,20100,20200]:
  for typ,base in [('CE',100+(k-20000)*.02),('PE',100-(k-20000)*.02)]:
   rows.append({'expiry':'2026-09-29','strike':k,'option_type':typ,'ltp':max(20,base),'bid':max(18,base-1),'ask':base+1})
 return normalize_chain(rows)

def test_mc_deterministic():
 r=np.tile(np.array([.01,-.005,.002]),300)
 a=simulate_terminal_paths(100,r,3,5000,756); b=simulate_terminal_paths(100,r,3,5000,756)
 assert np.array_equal(a,b)
 assert a.shape==(5000,)

def test_unique_quantile_mapping():
 x=chain(); t={'P20_PE':19920,'P35_PE':19950,'P65_CE':20060,'P80_CE':20110}; s=choose_unique_strikes(x,t)
 assert len(set(s.values()))==4

def test_nodip_gate_changes_with_ratio():
 x=chain(); a=nodip_signal(x,20000,pd.Timestamp('2026-09-29'))
 assert a['strikes']['NEAR_CE']==20000 and a['strikes']['NEAR_PE']==20000
 assert 4 in [len(a['prices']),len(a['strikes'])]
 assert a['cbr']>0

def test_entry_price_respects_slippage():
 assert entry_price(LegQuote(99,101,100),1,2)[0]==103
 assert entry_price(LegQuote(99,101,100),-1,2)[0]==97
