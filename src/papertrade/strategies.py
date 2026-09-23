from .mc import LEGS as MC_LEGS,quantile_targets,choose_unique_strikes,portfolio_mc_ev
from .common import best_quote

NODIP_LEGS=(("NEAR_PE","PE",1),("NEAR_CE","CE",-1),("FAR_CE","CE",1),("FAR_PE","PE",-1))

def nodip_signal(chain,spot,expiry):
 x=chain[chain.expiry==expiry]
 strikes=sorted({float(k) for k in x.strike.dropna()}); atm=min(strikes,key=lambda k:(abs(k-spot),k))
 ces=sorted(k for k in strikes if not x[(x.option_type=='CE')&(x.strike==k)].empty); pes=sorted(k for k in strikes if not x[(x.option_type=='PE')&(x.strike==k)].empty)
 far_ce=next((k for k in ces if k>atm),None); far_pe=next((k for k in reversed(pes) if k<atm),None)
 if far_ce is None or far_pe is None: raise ValueError('missing adjacent far strikes')
 labels={'NEAR_CE':atm,'NEAR_PE':atm,'FAR_CE':far_ce,'FAR_PE':far_pe}; px={}
 for lab in labels:
  side='CE' if lab.endswith('CE') else 'PE'; q=best_quote(x,side,labels[lab]); px[lab]=q.ltp
 if any(v is None or v<=0 for v in px.values()): raise ValueError('four positive LTPs required')
 cbr=(px['FAR_CE']/px['NEAR_CE'])/(px['FAR_PE']/px['NEAR_PE'])
 return {'strategy':'NoDip','underlying':'NIFTY','expiry':str(expiry),'atm':atm,'strikes':labels,'prices':px,'cbr':float(cbr),'gate':bool(cbr<=1.20),'legs':NODIP_LEGS}

def mc_signal(chain,s0,returns):
 terminals=__import__('papertrade.mc',fromlist=['simulate_terminal_paths']).simulate_terminal_paths(s0,returns)
 targets=quantile_targets(terminals); strikes=choose_unique_strikes(chain,targets); ev=portfolio_mc_ev(terminals,strikes,chain)
 return {'targets':targets,'strikes':strikes,'mc_ev_points':float(ev),'gate':bool(ev>0),'legs':MC_LEGS,'terminal_mean':float(terminals.mean())}

def entry_prices(chain,legs,strikes,slippage=2.0):
 out={}; sources={}
 from .common import entry_price
 for label,side,qty,*_ in legs:
  q=best_quote(chain,side,strikes[label]); out[label],sources[label]=entry_price(q,qty,slippage)
 return out,sources
