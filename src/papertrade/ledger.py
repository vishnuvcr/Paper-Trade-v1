from pathlib import Path
import json
from datetime import datetime
ROOT=Path(__file__).resolve().parents[2]; DATA=ROOT/'data'/'ledger'
for n in ('runs','signals','events','errors'): (DATA/(n+'.jsonl')).parent.mkdir(parents=True,exist_ok=True)

def append(name,obj):
 p=DATA/(name+'.jsonl'); with open(p,'a',encoding='utf-8') as f:f.write(json.dumps(obj,default=str,sort_keys=True)+'\n')

def read(name):
 p=DATA/(name+'.jsonl')
 if not p.exists(): return []
 out=[]
 for line in p.read_text().splitlines():
  try: out.append(json.loads(line))
  except Exception: pass
 return out

def now_utc(): return datetime.utcnow().isoformat(timespec='seconds')+'Z'

def open_positions():
 pos={}
 for e in read('events'):
  pid=e.get('position_id')
  if not pid: continue
  if e.get('event_type')=='OPEN': pos[pid]=e.get('position',{})
  if e.get('event_type')=='CLOSE': pos.pop(pid,None)
  if e.get('event_type')=='MARK' and pid in pos: pos[pid]['last_mark']=e
 return pos
