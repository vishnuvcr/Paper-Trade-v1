import argparse
from .mark import mark_all
from .runtime import master,mc_safe
from .run_nodip import run as nodip_run
from .nodip_exit import close_due
from .lock import check,capture

def main():
 p=argparse.ArgumentParser();p.add_argument('action',choices=['scan','mark']);p.add_argument('--strategy',choices=['ALL','NODIP','MC'],default='ALL');p.add_argument('--manual',action='store_true');a=p.parse_args()
 if not check(): raise SystemExit('prospective configuration fingerprint mismatch')
 if a.action=='mark': close_due(); mark_all(); return
 if a.strategy=='NODIP':out=[nodip_run(manual=a.manual)]
 elif a.strategy=='MC':out=[mc_safe(u,manual=a.manual) for u in ('NIFTY','SENSEX')]
 else:out=master(a.manual)
 if any(x.get('prospective_valid') and x.get('trade') for x in out): capture()

if __name__=='__main__':main()
