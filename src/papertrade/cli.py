import argparse
from .scan import scan_all,scan_nodip,scan_mc
from .mark import mark_all

def main():
 p=argparse.ArgumentParser(); p.add_argument('action',choices=['scan','mark']); p.add_argument('--strategy',choices=['ALL','NODIP','MC'],default='ALL'); p.add_argument('--manual',action='store_true'); a=p.parse_args()
 if a.action=='mark':mark_all();return
 if a.strategy=='NODIP':scan_nodip(manual=a.manual)
 elif a.strategy=='MC':
  for u in ('NIFTY','SENSEX'):scan_mc(u,manual=a.manual)
 else:scan_all(manual=a.manual)

if __name__=='__main__':main()
