"""Exact coarse moment and unchanged physical-ledger binding.

The 24-term logarithm and exponential enclosure follow icekylinx's
Apache-2.0 partial_swap_network.py, retained PR110 lineage. This local
adaptation was prepared with OpenAI Codex assistance.
"""
from pathlib import Path
from fractions import Fraction as Q
from hashlib import sha256
import json, gzip

D=Path(__file__).resolve().parent
P=D/'inputs/research'

def log_upper(value):
    value=Q(value);assert value>=1
    power=0
    while value>2:value/=2;power+=1
    def series(x):
        z=(x-1)/(x+1)
        return 2*sum((z**(2*j+1)/(2*j+1)for j in range(24)),Q(0))+2*z**49/(49*(1-z*z))
    scaled=(power*series(Q(2))+series(value))*10**12
    return Q(-(-scaled.numerator//scaled.denominator),10**12)

def moment(m,W,rows,saving):
    upper=Q(0);logs={}
    for t,count in sorted(rows.items()):
        assert 0<t<m and count>=0
        ell=log_upper(Q(m,t));u=saving*ell;assert 0<=u<1
        bound=1+u+u*u/(2*(1-u/3))
        upper+=Q(count*t,W*m)*bound;logs[str(t)]=str(ell)
    return dict(saving=str(saving),exponent=str(1-saving),moment_upper=str(upper),
                strict_gap=str(1-upper),logarithm_upper_bounds=logs,
                child_width_multiplicities=sorted(rows.items()),
                enclosure='1+u+u^2/(2(1-u/3))')

def main():
    profile=json.loads((D/'profile161.json').read_text())
    rows={int(t):n for t,n in profile['child_multiplicities'].items()}
    assert sum(t*n for t,n in rows.items())==profile['total_rank']
    assert profile['W']*profile['m']-profile['total_rank']==profile['deficit']
    saving=Q(129310447,10**12)
    certificate=moment(profile['m'],profile['W'],rows,saving)
    assert Q(certificate['moment_upper'])<1
    next_certificate=moment(profile['m'],profile['W'],rows,saving+Q(1,10**12))
    assert Q(next_certificate['moment_upper'])>=1
    m,r=profile['m'],profile['maxchild'];d=1
    while 2*r**d>m**d:d+=1
    assert d==33 and 2*r**(d-1)>m**(d-1)
    fresh=D/'literal-replay';frozen=P/'round8-network-minimal-v-ledger'
    event_hashes=[sha256(gzip.decompress((root/'forward-events.i32.gz').read_bytes())).hexdigest()for root in(fresh,frozen)]
    assert event_hashes[0]==event_hashes[1]
    fresh_result=json.loads((fresh/'result.json').read_text());frozen_result=json.loads((frozen/'result.json').read_text())
    keys=('candidate_sha256','h','roles','formal_basis','events','rank_histograms','histogram','recursive_rank','complete_forward_F2','complete_reflected_F2','actual_source_V_order_checked','reflected_frame_continuity','all_scalar_gates_equal_frame_keys')
    for key in keys:assert fresh_result[key]==frozen_result[key],key
    assert fresh_result['candidate_sha256']==profile['minimal_v_word_sha256']=='298c11fb29ab0afdf8d762c64a9b99d19a1e58465f3a0cbc9d2a59367c438fb7'
    out=dict(certified_bit_saving=str(saving),halving_degree=d,
             next_1e12_grid_enclosure_rejected=True,
             next_grid_note='The inherited upper enclosure fails at the next grid point; this does not prove noncontraction of the exact characteristic moment.',
             moment=certificate,fresh_literal_replay_matches_frozen_events=True,
             decompressed_event_sha256=event_hashes[0],
             frozen_metadata_fields_checked=list(keys),candidate_sha256=fresh_result['candidate_sha256'],
             groups_sha256=sha256((D/'groups161.json').read_bytes()).hexdigest(),
             scope='Exact coarse bit moment only; not a final multiplication exponent or ordinary stopped-wrapper certificate.')
    (D/'certificate.json').write_text(json.dumps(out,indent=2)+'\n')
    print('PASS coarse bit moment',saving,'halving degree',d,flush=True)

if __name__=='__main__':main()
