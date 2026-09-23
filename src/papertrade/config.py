from pathlib import Path
import hashlib,yaml
ROOT=Path(__file__).resolve().parents[2]
def load(name): return yaml.safe_load((ROOT/'config'/name).read_text())
def fingerprint():
 raw=(ROOT/'config'/'strategies.yml').read_bytes()+(ROOT/'config'/'costs.yml').read_bytes(); return hashlib.sha256(raw).hexdigest()
CFG=load('strategies.yml'); COSTS=load('costs.yml')
