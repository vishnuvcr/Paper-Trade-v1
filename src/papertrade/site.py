from pathlib import Path
import html,json,shutil
from .ledger import read,open_positions
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'site'
CSS='body{margin:0;background:#07101c;color:#e8f0fb;font:14px system-ui}main{max-width:1400px;margin:auto;padding:24px}.nav a{display:inline-block;margin:4px;padding:7px 10px;border:1px solid #29405e;border-radius:12px;color:#7ee0c2;text-decoration:none}.grid{display:grid;grid-template-columns:repeat(4,1fr);gap:12px}.card{background:#0d1726;border:1px solid #263b55;border-radius:16px;padding:15px;margin:12px 0}.k{color:#96a9c2;text-transform:uppercase;font-size:11px}.v{font-size:28px;font-weight:800;margin-top:5px}.table{overflow:auto}table{width:100%;border-collapse:collapse}th,td{padding:8px;border-bottom:1px solid #20334a;text-align:left;white-space:nowrap}th{color:#9aadc4}.small{color:#9aadc4;font-size:12px;line-height:1.5}.ok{color:#7ee0c2}.bad{color:#ff8a8a}@media(max-width:800px){.grid{grid-template-columns:1fr 1fr}}'
def esc(x): return html.escape(str(x))
def money(x):
    try:return '₹'+format(float(x),',.2f')
    except:return '—'
def layout(title,body):
    return '<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(title)+'</title><style>'+CSS+'</style></head><body><main><div><b>BATMAN + NoDip · PAPER TRADE v1</b></div><div class="nav"><a href="index.html">Dashboard</a><a href="signals.html">Signals</a><a href="trades.html">Trades</a><a href="errors.html">Errors</a><a href="methodology.html">Method</a><a href="https://github.com/vishnuvcr/Paper-Trade-v1/actions">Run workflows</a></div>'+body+'<div class="small">Paper-only validation. No broker orders are submitted.</div></main></body></html>'
def latest_by_key(signals):
    out={}
    for s in signals: out[(s.get('strategy'),s.get('underlying'))]=s
    return out
def build():
    OUT.mkdir(parents=True,exist_ok=True); (OUT/'data').mkdir(exist_ok=True); (OUT/'style.css').write_text(CSS)
    sig=read('signals'); evt=read('events'); err=read('errors'); pos=open_positions()
    closes=[e for e in evt if e.get('event_type')=='CLOSE']; marks=[e for e in evt if e.get('event_type')=='MARK']
    real=sum(float(e.get('realized_net_pnl_rupees',0)) for e in closes); valid=[x for x in sig if x.get('prospective_valid')]; traded=[x for x in valid if x.get('trade')]
    latest=latest_by_key(sig); sensex=latest.get(('MC-RQ6-v1','SENSEX'),{}); nodip=latest.get(('NoDip','NIFTY'),{}); nifty=latest.get(('MC-RQ6-v1','NIFTY'),{})
    sensex_source=(sensex.get('provider') or {}).get('source','—'); sensex_status=sensex.get('status','—')
    cards=''.join(f'<div class="card"><div class="k">{k}</div><div class="v">{v}</div></div>' for k,v in [('Signals',len(sig)),('Prospective',len(valid)),('Paper trades',len(traded)),('Open positions',len(pos)),('Realised net',money(real)),('Marks',len(marks)),('Historical errors',len(err)),('SENSEX source',sensex_source)])
    rows=[]
    for s in reversed(sig[-200:]): rows.append('<tr>'+''.join('<td>'+esc(s.get(k,''))+'</td>' for k in ['observed_ist','strategy','underlying','expiry','status','gate','trade','cbr','mc_ev_points'])+'</tr>')
    dash='<h1>Prospective validation dashboard</h1><div class="small">Frozen strategies; descriptive prospective record only.</div><div class="grid">'+cards+'</div><div class="card"><h2>Current provider status</h2><div class="small"><b>SENSEX:</b> <span class="ok">'+esc(sensex_source)+'</span> · <b>latest status:</b> '+esc(sensex_status)+' · <b>observed:</b> '+esc(sensex.get('observed_ist','—'))+'</div><div class="small"><b>NIFTY MC:</b> '+esc((nifty.get('provider') or {}).get('source','—'))+' · <b>NoDip NIFTY:</b> '+esc((nodip.get('provider') or {}).get('source','—'))+'</div></div><div class="card"><h2>Latest signals</h2><div class="table"><table><thead><tr>'+''.join('<th>'+esc(x)+'</th>' for x in ['Time','Strategy','Underlying','Expiry','Status','Gate','Trade','CBR','MC-EV'])+'</tr></thead><tbody>'+''.join(rows)+'</tbody></table></div></div>'
    (OUT/'index.html').write_text(layout('Dashboard',dash))
    (OUT/'signals.html').write_text(layout('Signals','<h1>Signal ledger</h1><div class="card"><div class="table"><table><thead><tr>'+''.join('<th>'+esc(x)+'</th>' for x in ['Time','Strategy','Underlying','Expiry','Status','Gate','Trade','Prospective'])+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+esc(s.get(k,''))+'</td>' for k in ['observed_ist','strategy','underlying','expiry','status','gate','trade','prospective_valid'])+'</tr>' for s in reversed(sig))+'</tbody></table></div></div>'))
    (OUT/'trades.html').write_text(layout('Trades','<h1>Paper trade lifecycle</h1><div class="card"><div class="table"><table><thead><tr>'+''.join('<th>'+x+'</th>' for x in ['UTC','Event','ID','Strategy','Underlying','Expiry','Net P&L'])+'</tr></thead><tbody>'+''.join('<tr><td>'+esc(e.get('timestamp_utc'))+'</td><td>'+esc(e.get('event_type'))+'</td><td>'+esc(e.get('position_id'))+'</td><td>'+esc(e.get('strategy') or e.get('position',{}).get('strategy'))+'</td><td>'+esc(e.get('underlying') or e.get('position',{}).get('underlying'))+'</td><td>'+esc(e.get('expiry') or e.get('position',{}).get('expiry'))+'</td><td>'+money(e.get('realized_net_pnl_rupees'))+'</td></tr>' for e in reversed(evt))+'</tbody></table></div></div>'))
    error_rows=[]
    for e in reversed(err):
        latest_state=(latest.get((e.get('strategy'),e.get('underlying'))) or {}).get('status')
        resolved=latest_state not in ('DATA_UNAVAILABLE',None,'')
        state='<span class="ok">RESOLVED / HISTORICAL</span>' if resolved else '<span class="bad">CURRENT</span>'
        error_rows.append('<tr><td>'+esc(e.get('timestamp_utc'))+'</td><td>'+esc(e.get('strategy'))+'</td><td>'+esc(e.get('underlying'))+'</td><td>'+state+'</td><td>'+esc(e.get('error'))+'</td><td>'+esc(e.get('message'))+'</td></tr>')
    (OUT/'errors.html').write_text(layout('Errors','<h1>Error ledger</h1><div class="card"><div class="small"><b>Historical errors are retained for auditability.</b> A row below is marked current only when the latest signal for that strategy/underlying is still DATA_UNAVAILABLE.</div></div><div class="card"><div class="table"><table><thead><tr><th>UTC</th><th>Strategy</th><th>Underlying</th><th>State</th><th>Type</th><th>Message</th></tr></thead><tbody>'+''.join(error_rows)+'</tbody></table></div></div>'))
    method='<h1>Frozen method</h1><div class="card"><h2>NoDip — 3W far expiry</h2><div class="small">NIFTY, 09:35 IST. Near expiry is the nearest listed expiry. Far expiry is the first listed expiry on/after near expiry + 21 calendar days. Near CE/PE are ATM at near expiry; far CE/PE use immediately adjacent strikes at the selected far expiry. CBR=(Far-expiry CE/Near-expiry CE)/(Far-expiry PE/Near-expiry PE); trade only when CBR≤1.20. Exit on the previous trading session before near expiry. 2-point adverse slippage.</div></div><div class="card"><h2>NoDip — 1W far expiry</h2><div class="small">Same frozen rules, except far expiry is the first listed expiry on/after near expiry + 7 calendar days. This is a separate pre-specified validation arm; it does not alter the 3W control.</div></div><div class="card"><h2>MC-RQ6-v1</h2><div class="small">D3 09:30; 756 historical finite daily log returns; 5,000 IID paths; seed 756; 3-session horizon; P20/P35/P65/P80; BUY 1 P35 PE, SELL 2 P20 PE, BUY 1 P65 CE, SELL 2 C80; gross MC-EV&gt;0; expiry settlement; 2-point adverse slippage.</div></div><div class="card"><h2>Scientific controls</h2><div class="small">Point-in-time data only; source snapshots and hashes; configuration fingerprint lock; append-only ledgers; no synthetic live quotes; manual runs are diagnostic by design; no live broker orders.</div></div>'
    (OUT/'methodology.html').write_text(layout('Methodology',method))
    for n in ('signals','events','errors','runs'):
        p=ROOT/'data'/'ledger'/(n+'.jsonl')
        if p.exists(): shutil.copyfile(p,OUT/'data'/(n+'.jsonl'))
        else: (OUT/'data'/(n+'.jsonl')).write_text('')
    (OUT/'data'/'summary.json').write_text(json.dumps({'signals':len(sig),'prospective':len(valid),'trades':len(traded),'open_positions':len(pos),'realised_net':real,'historical_errors':len(err),'latest_sensex_provider':sensex_source,'latest_sensex_status':sensex_status},indent=2)+'\n')
if __name__=='__main__': build()
