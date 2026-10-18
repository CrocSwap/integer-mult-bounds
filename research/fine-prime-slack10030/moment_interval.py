"""Directed integer moment intervals using Aaron Wang / PR1982, retained unchanged."""
import importlib.util,json
from pathlib import Path
from fractions import Fraction as Q
P=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('root1982',P/'reference1982/verify.py')
v=importlib.util.module_from_spec(s);s.loader.exec_module(v)
v.check_inputs_pin();v.check_log_identities()
src=v.load_inputs()['sources']['pr1928']
BITS=v.default_bits(int(src['grid_digits']))
def moment(x,profile,m,live):
    assert m==73 and profile=={int(k):int(n) for k,n in src['global_profile'].items()} and live==int(src['live'])
    logs=v.log_table(m,sorted(profile),BITS)
    lo=hi=0
    for rank,count in profile.items():
        elo,ehi=v.exp_interval(*v.scaled_product(x,logs[rank]),BITS)
        lo+=rank*count*elo;hi+=rank*count*ehi
    target=(m*live)<<BITS
    return Q(lo,target),Q(hi,target)
