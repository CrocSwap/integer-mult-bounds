"""e264 exact-source financial and first-external-location refit; no payload materialization."""
from collections import Counter
from decimal import Decimal,localcontext
from fractions import Fraction as Q
from pathlib import Path
import hashlib,json,sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(Path(sys.argv[1]).resolve()))
from upstream import install
install()
from installations import DYADIC_ENDPOINT as LAST_GRID,BINARY_C,GAUSSIAN_C,PROFILES
from check_complete import profile_row,tariff,first_external_swap
from independent_binary_price import raw_moments
from strong_binary import graph,caller
from unpowered_price import ranks
from outer_budget import qualify
from outer_clock import financial_checks
from ordinary_clock import first_stage_bound,polynomial_to_fibre_bound

def dec(x):
    with localcontext() as c:
        c.prec=48
        return str(Decimal(x.numerator)/Decimal(x.denominator))
def hashint(x):
    return hashlib.sha256(x.to_bytes(max(1,(x.bit_length()+7)//8),'big')).hexdigest()

profile=LAST_GRID
assert profile.kappa<BINARY_C<profile.kappa+Q(1,10**18)
assert BINARY_C==Q(287039844436133239,2**66)
row=profile_row(profile)
signed=row['signed_gate']
assert signed['strict']==54 and signed['functional']==4
positive=GAUSSIAN_C-Q(39,256*profile.complex_log)
assert positive>profile.ordinary>profile.kappa+Q(4,profile.positive_stop_denominator)
for args in ((profile.kappa,Q(0),profile.ordinary,positive),
             (profile.kappa,Q(1,10**17),profile.ordinary,positive),
             (profile.kappa,Q(1,10**21),profile.kappa+Q(4,10**21),positive),
             (profile.kappa,Q(1,10**21),profile.ordinary,profile.ordinary)):
    try:qualify(*args)
    except ArithmeticError:pass
    else:raise AssertionError('unfunded border accepted')
cuts=row['binary_cuts']
assert max(cuts).bit_length()<=65 and row['public_exponent_A'].bit_length()<=65
first=first_stage_bound(profile.eta);later=polynomial_to_fibre_bound()
assert first+80*profile.rank_logs[0]<1024*profile.rank_logs[0]
assert all(later+80*h<1024*h for h in profile.rank_logs[1:])
g=Q(1,profile.positive_stop_denominator)
stop_factor_log=((17*profile.positive_stop_denominator)**16-1).bit_length()
assert stop_factor_log==1182 and 400+stop_factor_log+9+2<1600
financial=financial_checks()
binary_census=raw_moments(graph(),caller())
binary=tariff(BINARY_C,binary_census,134)
positive_census=ranks()
numeric=tariff(GAUSSIAN_C,positive_census,1224)
assert (binary['cells'],numeric['cells'])==(24,54)
assert PROFILES['dyadic-endpoint'] is profile
placement=first_external_swap(positive_census)
first36000=placement['placements']['36000']
assert first36000['first_tickets'][0]==0 and first36000['first_tickets'][1]>1
period=first36000['period'];tickets=first36000['first_tickets']
actual_first={'period_bit_length':period.bit_length(),'period_sha256':hashint(period),
              'ticket_bit_lengths':[x.bit_length() for x in tickets],
              'ticket_sha256':[hashint(x) for x in tickets],
              'root_tag':placement['root_tag'],'per_target_probability':placement['per_target_probability'],
              'actual_position_probe':'first swap (1,ticket[1],1) was issued by ComplexRaw.align'}
previous=Q(0);stages=[]
for i,(h,r) in enumerate(zip(profile.rank_logs,row['stage_rates'],strict=True)):
    rate=Q(r);limit=min(profile.eta,(249*(BINARY_C-Q(11,8*h))+previous)/250)
    assert previous<rate<limit
    stages.append({'height':h,'rate':r,'margin':str(limit-rate),'margin_decimal':dec(limit-rate)})
    previous=rate
out={'scope':'finite financial and first-placement refit of pinned e264 source with a changed binary trial; physical production and full independent proof remain unexecuted',
     'pinned_head':'e26425171238e142cc9ffb510fd953f344bd41c7',
     'profile':{'ranks':list(profile.rank_logs),'numerical_H':profile.complex_log,
                'kappa':str(profile.kappa),'kappa_decimal':dec(profile.kappa),
                'gap':str(g),'binary_c':str(BINARY_C),'binary_c_decimal':dec(BINARY_C),
                'positive_c':str(GAUSSIAN_C),'positive_cap':str(positive),
                'positive_cap_decimal':dec(positive),'positive_margin_decimal':dec(positive-profile.ordinary)},
     'old_source_resolution_checked_separately':True,'source_binary_tariff':binary,
     'source_numerical_tariff':numeric,'stages':stages,'signed':signed,'receipt':row,
     'first_stage_bound':first,'later_stage_bound':later,'outer_stop_log2_ceiling':stop_factor_log,
     'outer_full_cofinal_constant_log2_le':400+stop_factor_log+9,
     'outer_original_financial_checks':financial,'first_positive_external':actual_first,
     'controls':'reject g=0, g=10^-17, ordinary equality and positive equality'}
Path(sys.argv[2]).write_text(json.dumps(out,indent=2)+'\n')
print('PASS_E264_LAST_GRID_FINANCIAL_AND_FIRST_EXTERNAL')
print('kappa',dec(profile.kappa),'final_margin',stages[-1]['margin_decimal'],
      'positive_margin',dec(positive-profile.ordinary))
print('source tariff cells',binary['cells'],numeric['cells'],'A',row['public_exponent_A'],
      'first_external',actual_first,'log2C',row['log2_C_le'])
