import json
from pathlib import Path
from .config import fingerprint
ROOT=Path(__file__).resolve().parents[2]; P=ROOT/'data'/'state'/'prospective_lock.json'

def check():
 if not P.exists():return True
 x=json.loads(P.read_text()); return x.get('config_fingerprint')==fingerprint()

def capture():
 P.parent.mkdir(parents=True,exist_ok=True);P.write_text(json.dumps({'config_fingerprint':fingerprint()},indent=2)+'\n')
