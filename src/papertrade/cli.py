import argparse
from .mark import mark_all
from .runtime import master,mc_safe
from .run_nodip import run_variant,run_all_variants
from .nodip_close import close_due
from .lock import check,capture

def main():
    p=argparse.ArgumentParser()
    p.add_argument("action",choices=["scan","mark"])
    p.add_argument("--strategy",choices=["ALL","NODIP","NODIP_3W","NODIP_1W","MC"],default="ALL")
    p.add_argument("--manual",action="store_true")
    a=p.parse_args()

    if not check():
        raise SystemExit("prospective configuration fingerprint mismatch")

    if a.action=="mark":
        close_due()
        mark_all()
        return

    if a.strategy=="NODIP_3W":
        out=[run_variant("NODIP_3W",manual=a.manual)]
    elif a.strategy=="NODIP_1W":
        out=[run_variant("NODIP_1W",manual=a.manual)]
    elif a.strategy=="NODIP":
        out=run_all_variants(manual=a.manual)
    elif a.strategy=="MC":
        out=[mc_safe(u,manual=a.manual) for u in ("NIFTY","SENSEX")]
    else:
        out=master(a.manual)
        # ALL includes both NoDip variants via the master runtime below.

    if any(x.get("prospective_valid") and x.get("trade") for x in out):
        capture()

if __name__=="__main__":
    main()
