from collections import Counter
from fractions import Fraction as Q
from hashlib import sha256
import importlib.util,json,sys
from pathlib import Path


def main(p):
    assert sha256(p.read_bytes()).hexdigest()=='ca650d573f605bf51a8806a772903b6775cd036dfbfe7f043eccd3e51bc9977b';s=importlib.util.spec_from_file_location('p104_verified_reference',p);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);t,old=m.load_inputs();k=m.K;c=Q(70084296829703,2**54);ans={}
    for name,legs in [('4+4',(4,4))]:
        first=None;previous=None
        for n in range(37):
            paid=old.copy()
            for r in legs:paid[r]-=n
            paid[8]+=n;assert min(paid.values())>=0 and sum(paid.values())==104904-n and sum(r*v for r,v in paid.items())==285600
            raw=m.raw_difference(t,paid,k);pow=m.powered_surplus(t,paid,c,268,m.Z,m.W,m.WEIGHT,15)
            if raw[0]>0 and pow[0]>Q(2,1<<50):first=(n,m.enclosing_text(*raw),m.enclosing_text(*pow));break
            previous=(n,m.enclosing_text(*raw),m.enclosing_text(*pow))
        assert first is not None
        ans[name]={'uphill_local_saving_at_trial':m.enclosing_text(*m.raw_difference(Counter(legs),{8:1},k)),'downhill_change':0,'last_failure':previous,'first_raw_and_powered_price_success':first}
    return ans

if __name__=='__main__':print(json.dumps(main(Path(sys.argv[1])/'price_audit.py'),sort_keys=True,indent=2))
