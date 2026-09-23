import numpy as np

LEGS=(("P35_PE","PE",1,.35),("P20_PE","PE",-2,.20),("P65_CE","CE",1,.65),("P80_CE","CE",-2,.80))

def historical_log_returns(close,signal_date,window=756):
 x=close.copy(); x.index=np.array(x.index,dtype='datetime64[ns]'); x=x[x.index<np.datetime64(signal_date.date())].sort_index()
 r=np.log(x.astype(float)).diff().dropna().to_numpy(); r=r[np.isfinite(r)]
 if len(r)<window: raise ValueError(f'need {window} returns; got {len(r)}')
 return r[-window:]

def simulate_terminal_paths(s0,returns,horizon=3,paths=5000,seed=756):
 r=np.asarray(returns,float); r=r[np.isfinite(r)]
 if s0<=0 or len(r)<756: raise ValueError('invalid MC input')
 g=np.random.default_rng(seed); idx=g.integers(0,756,size=(paths,horizon)); return s0*np.exp(r[idx].sum(1))

def quantile_targets(t):
 return {'P20_PE':float(np.quantile(t,.2)),'P35_PE':float(np.quantile(t,.35)),'P65_CE':float(np.quantile(t,.65)),'P80_CE':float(np.quantile(t,.8))}

def choose_unique_strikes(chain,targets):
 out={}; used=set()
 for label in ('P20_PE','P35_PE','P65_CE','P80_CE'):
  side='PE' if label.endswith('PE') else 'CE'; ks=sorted({float(k) for k in chain.loc[chain.option_type==side,'strike'].dropna()})
  for k in sorted(ks,key=lambda z:(abs(z-targets[label]),z)):
   if k not in used: out[label]=k; used.add(k); break
  if label not in out: raise ValueError('cannot map strike')
 return out

def parity_spot(chain,previous_close):
 ce=chain.loc[chain.option_type=='CE',['strike','ltp']].rename(columns={'ltp':'ce'}); pe=chain.loc[chain.option_type=='PE',['strike','ltp']].rename(columns={'ltp':'pe'}); m=ce.merge(pe,on='strike')
 m=m[(m.strike-previous_close).abs()<=.02*previous_close]
 if m.empty:return float(previous_close),'previous_close_fallback'
 z=m.strike+m.ce-m.pe; z=z[(z>0)&np.isfinite(z)]
 return (float(z.median()),'put_call_parity_snapshot') if len(z) else (float(previous_close),'previous_close_fallback')

def portfolio_mc_ev(terminals,strikes,chain):
 p=np.zeros_like(terminals,float); entry=0.0
 for label,side,qty,_ in LEGS:
  k=strikes[label]; p+=qty*(np.maximum(k-terminals,0) if side=='PE' else np.maximum(terminals-k,0)); q=chain.loc[(chain.option_type==side)&(chain.strike==k),'ltp']
  if q.empty: raise ValueError('missing gate quote')
  entry+=qty*float(q.iloc[-1])
 return float(p.mean()-entry)
