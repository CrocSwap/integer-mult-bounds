"""Replay the source census, directed witnesses, and positive Farkas proofs."""
from collections import Counter
from fractions import Fraction as Q
from hashlib import sha1, sha256
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from directed import UNIT
from model import (P, addmul, all_cuts, continuous_dual, dual_record, flow_record,
                   fractional_witness, hist_digest, integer_dual, margin,
                   qstr, ratio_witness, scales, split_paid, witness_flow)
from series_control import check as independent_series_check

HEAD='75f7e1c44f48c43983016bcf8878c4d9e5e87c62'
EXPECTED_HIST='49f22c0d2d235138173b599004d49b6593244cca8aa5e3a6e6999444308f9cba'
INT_LO=Q('0.003898466610885757242')
INT_HI=Q('0.003898466610885757243')
RELAX_LO=Q('0.003898466621505769638')
RELAX_HI=Q('0.003898466621505769639')
TRIAL=Q(17145637307,2**42)
SOURCE=HERE/'source'
SOURCE_RECEIPT_SHA='6ed3459e228af5b93a766ab82033513ecd6e662498d9749cab810fa48b20d58f'


def public_files():
    """Check the exact allowlist; its own digest is supplied with the archive."""
    manifest=json.loads((HERE/'PUBLIC-FILES.json').read_text())
    assert manifest['algorithm']=='sha256'
    listed=manifest['files']
    actual={str(p.relative_to(HERE)) for p in HERE.rglob('*') if p.is_file()}
    assert actual==set(listed)|{'PUBLIC-FILES.json'}
    for name,digest in listed.items():
        relative=Path(name)
        assert not relative.is_absolute() and '..' not in relative.parts
        path=HERE/name
        assert path.is_file() and not path.is_symlink()
        assert sha256(path.read_bytes()).hexdigest()==digest,name


def validate_hist(t0,p0,expected):
    assert t0==expected[0] and p0==expected[1]
    assert sum(t0.values())==52608 and sum(p0.values())==281568 and p0[1]==P
    assert hist_digest(t0,p0)==EXPECTED_HIST


def census_from_stage():
    receipt_bytes=(SOURCE/'SOURCE-RECEIPT.json').read_bytes()
    assert sha256(receipt_bytes).hexdigest()==SOURCE_RECEIPT_SHA
    receipt=json.loads(receipt_bytes)
    assert receipt['repository']=='CrocSwap/integer-mult-bounds'
    assert receipt['pull_request']==8072 and receipt['head']==HEAD
    upstream=SOURCE/'upstream'
    for path,entry in receipt['head_files'].items():
        if entry.get('included') is False:continue
        name=Path(path).name
        data=(upstream/name).read_bytes()
        assert sha256(data).hexdigest()==entry['sha256'],name
        assert sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==entry['git_blob'],name
    original=json.loads((upstream/'PEER-SOURCE.json').read_text())
    archive=receipt['head_files']['research/p104-weighted-capped-allocation-490950/peer8057.tar.gz']
    assert original['head']==receipt['peer_head'] and original['archive_sha256']==archive['sha256']
    snapshot=receipt['curated_source_files']
    assert {str(p.relative_to(SOURCE)) for p in (SOURCE/'canonical').rglob('*') if p.is_file()}==set(snapshot)
    for name,digest in snapshot.items():
        assert sha256((SOURCE/name).read_bytes()).hexdigest()==digest,name
    record=json.loads((HERE/'census.json').read_text())
    expected=(Counter({Q(k):v for k,v in record['targets_type0'].items()}),
              Counter({Q(k):v for k,v in record['paid_unsplit_type0'].items()}))
    expected_targets,expected_paid=scales(*expected)
    assert expected_targets[1]==Counter({Q(k):v for k,v in record['targets_type1'].items()})
    assert expected_paid[1]==Counter({Q(k):v for k,v in record['paid_unsplit_type1'].items()})
    canonical=SOURCE/'canonical'
    sys.path.insert(0,str(canonical))
    from strong_complex import load_changed, word
    raw=word(*load_changed(canonical/'inputs'))
    t0=Counter(Q(port.rank) for port in raw.targets)
    p0=Counter(Q(port.rank) for port in raw.paid)
    validate_hist(t0,p0,expected)
    return t0,p0,expected


def lower_record(t0,p0,c,x,n0,n1,margins):
    flows,capacity=witness_flow(t0,p0,c,x,n0,n1)
    return {'rate':qstr(c),'weight_0':'1','weight_1':qstr(x),
            'split_0':qstr(n0),'split_1':qstr(n1),
            'all_cut_margins':[[str(cut),qstr(v/UNIT)] for cut,v in margins],
            'greedy_directed_flow':flow_record(flows),
            'unused_directed_capacity':[[str(k),qstr(v/UNIT)] for k,v in sorted(capacity.items()) if v]}


def verify_controls(t0,p0,expected,x,duals):
    # The installed baseline is a strict positive transport control.
    targets,_=scales(t0,p0); paid=split_paid(p0,1008,0); ratio=Q(451,5)
    baseline=[]
    for cut in all_cuts(paid):
        baseline.append(margin(targets[0],paid[0],cut,TRIAL,True)+ratio*margin(targets[1],paid[1],cut,TRIAL,True))
    assert min(baseline)>0
    # Neighbouring whole counts fail at the certified lower witness ratio.
    for n0,cut in ((1005,Q(1)),(1007,None)):
        wrong=split_paid(p0,n0,0)
        upper=margin(targets[0],wrong[0],cut,INT_LO,False)+x*margin(targets[1],wrong[1],cut,INT_LO,False)
        assert upper<0,(n0,cut)
    # Mutated dual multipliers must fail exact cancellation.
    for rows,weights,_ in duals:
        changed=weights.copy();changed[1]+=1
        assert any(addmul(rows,changed)[1:])
    # Reject altered source census and impossible loan count.
    damaged=Counter(t0);damaged[1]+=1
    try:validate_hist(damaged,p0,expected)
    except AssertionError:pass
    else:raise AssertionError('damaged source census accepted')
    try:split_paid(p0,P+1,0)
    except ValueError:pass
    else:raise AssertionError('out-of-stock split count accepted')
    assert not (4*Q(2)>=5*Q(2))  # forbidden r=2 -> k=2 transfer
    independent_series_check(INT_HI)
    independent_series_check(RELAX_HI)
    independent_series_check(Q('0.0039'))
    return {'source_installed_trial':qstr(TRIAL),
            'baseline_minimum_cut_margin':qstr(min(baseline)/UNIT),
            'neighbor_counts_fail':[1005,1007],
            'mutated_duals_rejected':len(duals),
            'altered_source_rejected':True,'excess_split_rejected':True,
            'forbidden_transfer_rejected':True,'independent_power_enclosures_checked':True}


def run(emit):
    assert __debug__,'Do not run with optimizations that disable assertions.'
    if not emit:public_files()
    t0,p0,expected=census_from_stage()
    x,margins,_=ratio_witness(t0,p0,INT_LO,1006,0)
    rx,rn,rmargins,_=fractional_witness(t0,p0,RELAX_LO)
    integer_lower=lower_record(t0,p0,INT_LO,x,1006,0,margins)
    relaxed_lower=lower_record(t0,p0,RELAX_LO,rx,rn,0,rmargins)
    d0=integer_dual(t0,p0,INT_HI,'at-most-1005')
    d1=integer_dual(t0,p0,INT_HI,'at-least-1006')
    d2=continuous_dual(t0,p0,RELAX_HI)
    controls=verify_controls(t0,p0,expected,x,[d0,d1,d2])
    general_rate=Q('0.0039')
    base_upper=Q(margin(t0,p0,None,general_rate,False),UNIT)
    assert 0 < 1-general_rate < 1 and base_upper < Q('-1.53934254762')
    certificate={
       'source_head':HEAD,'source_histogram_sha256':EXPECTED_HIST,
       'exponent_power_grid_bits':{'exponent':128,'values':224},
       'integer_lower':integer_lower,
       'integer_upper_rate':qstr(INT_HI),
       'integer_upper_at_most_1005':dual_record(*d0),
       'integer_upper_at_least_1006':dual_record(*d1),
       'relaxed_lower':relaxed_lower,
       'relaxed_upper_rate':qstr(RELAX_HI),
       'relaxed_upper':dual_record(*d2),
       'arbitrary_scale_subdivision_corollary':{
           'rate':qstr(general_rate),
           'base_unsplit_directed_upper':qstr(base_upper),
           'strict_decimal_upper':'-1.53934254762',
           'scope':'finite positive scale mixtures and finite positive rank-preserving paid subdivisions, fixed targets; compatibility relaxed'},
       'controls':controls,
    }
    out=HERE/'CERTIFICATE.json'
    if emit:out.write_text(json.dumps(certificate,indent=2)+'\n')
    else:assert json.loads(out.read_text())==certificate,'The replayed certificate differs'
    print('PASS_PINNED_CURATED_SOURCE_AND_CANONICAL_WORD')
    print('PASS_INTEGER_LOWER_FLOW_5R_LE_4K')
    print('PASS_INTEGER_UPPER_TWO_POSITIVE_FARKAS_COMBINATIONS')
    print('PASS_FRACTIONAL_LOWER_FLOW_AND_UPPER_POSITIVE_FARKAS')
    print('PASS_ARBITRARY_SCALE_PAID_SUBDIVISION_TOTAL_OBSTRUCTION_0039')
    print('PASS_BASELINE_AND_NEGATIVE_CONTROLS_AND_INDEPENDENT_ENCLOSURES')
    print('integer',str(INT_LO),'< threshold <',str(INT_HI))
    print('fractional',str(RELAX_LO),'< threshold <',str(RELAX_HI))
    print('scope: aggregate raw price/stock transport only; no signed-multiplier or kappa admission')

if __name__=='__main__':
    if len(sys.argv)>2 or (len(sys.argv)==2 and sys.argv[1]!='--emit'):
        raise SystemExit('usage: verify.py [--emit]')
    run('--emit' in sys.argv)
