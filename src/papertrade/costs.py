from datetime import date
from pathlib import Path
import os,yaml
ROOT=Path(__file__).resolve().parents[2]
CFG=yaml.safe_load((ROOT/'config'/'costs.yml').read_text())

def brokerage_per_order(): return float(os.getenv('PAYTM_MONEY_BROKERAGE_PER_ORDER',CFG['brokerage']['rupees_per_unique_executed_order']))

def stt_sale_rate(d): return 0.0015 if d>=date(2026,4,1) else 0.0010

def stt_exercise_rate(d): return 0.0015 if d>=date(2026,4,1) else 0.00125

def entry_cost(underlying,prices,qty,lot,d):
 turn=sum(abs(q)*abs(prices[k])*lot for k,q in qty.items()); buy=sum(max(q,0)*abs(prices[k])*lot for k,q in qty.items()); sell=sum(abs(q)*abs(prices[k])*lot for k,q in qty.items() if q<0)
 brok=4*brokerage_per_order(); venue=CFG['venue']['exchange_transaction_rupees_per_crore'][underlying]/1e7*turn; sebi=CFG['venue']['sebi_rate_on_turnover']*turn; stamp=CFG['venue']['stamp_duty_on_buy_turnover']*buy; gst=CFG['venue']['gst_rate']*(brok+venue+sebi); stt=stt_sale_rate(d)*sell
 return {'brokerage':brok,'exchange_transaction':venue,'sebi':sebi,'stamp_duty':stamp,'gst':gst,'stt_entry':stt,'total':brok+venue+sebi+stamp+gst+stt}

def expiry_cost(d,settlement,strikes,qty,lot):
 total=0.0; rate=stt_exercise_rate(d)
 for k,q in qty.items():
  if q<=0: continue
  strike=strikes[k]; intrinsic=max(strike-settlement,0) if k.endswith('_PE') else max(settlement-strike,0); total+=rate*intrinsic*abs(q)*lot
 return total
