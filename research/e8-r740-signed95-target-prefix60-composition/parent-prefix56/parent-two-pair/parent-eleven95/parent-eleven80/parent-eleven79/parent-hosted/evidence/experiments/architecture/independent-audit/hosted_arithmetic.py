"""Independent moment endpoint, finite invoice and closed bootstrap audit."""
from pathlib import Path
from fractions import Fraction as Q
import json,hashlib,struct,importlib.util,math
ROOT=Path(__file__).resolve().parents[3];OUT=Path(__file__).resolve().parent;P=ROOT/'experiments/stage-search/pr441-signed75-hosting'
rd=lambda p:json.loads(Path(p).read_text());sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
ENGINE=ROOT/'experiments/bit-search/pr433/source/research/split-centres-global/vendor/engines/base_two_moment.py'
spec=importlib.util.spec_from_file_location('second',ENGINE);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def main():
    r=rd(P/'REFINED-ASSEMBLY.json');bg=rd(P/'hosted/GLOBAL.json');geo=rd(P/'hosted/GEOMETRY.json');cx=rd(P/'complex-hosted/HOSTED.json');sig=rd(P/'signed/RESULT.json');bc=rd(P/'signed/GLOBAL-BOUND.json');cf=rd(P/'complex-hosted/FINITE-INVOICE.json')
    closure=0
    for key,digest in r['input_sha256'].items():
        path=Path(key);path=path if path.is_absolute() else P/path
        assert sha(path)==digest;closure+=1
    for key,digest in bc['source_inputs'].items():assert sha(key)==digest;closure+=1
    moments=[]
    for label,H,mm,W,rate in [('bit',bg['profile'],64,bg['live'],Q(r['bit_c'])),('complex',cx['global_profile'],73,cx['live'],Q(r['complex_b']))]:
        entries=[(int(k),v) for k,v in H.items()];E=sum(H.values());checks=[]
        for z in [rate,rate+Q(1,10**24)]:
            lo,hi=m.moment(mm,W,entries,z);bl,bh=m.moment(mm,W,[(1,32*mm*mm*E)],z)
            checks.append((lo+bl/10**16,hi+bh/10**16))
        assert checks[0][1]<1<checks[1][0]
        moments.append(dict(supplier=label,rate=str(rate),lower_upper_residual=str(checks[0][1]-1),next_lower_residual=str(checks[1][0]-1)))
    raw=list(struct.iter_unpack('<6i',(P/'signed/records/249-records.bin').read_bytes()));signed=list(struct.iter_unpack('<6i',(P/'signed/signed-records.bin').read_bytes()))
    rawunit=sum(abs(z[3]) for z in raw if z[0]==1);signedunit=sum(abs(z[3]) for z in signed if z[0]==1)
    assert rawunit==15314 and signedunit-rawunit==1274
    prefix=804**5*26806**4*2**18;E=sum(bg['profile'].values());J=8*64*9*980+8*960*64+2*(bg['bank_assignments']+bg['hosted_residuals'])+2*bg['copy_erase_episodes']
    selectors=2*9*64*((bg['live']-1)+740*64*(geo['max_route_factors']+63+64))
    unit=576*signedunit+bg['bridge_additions']
    coef=unit+J*(16*4097**2+bg['physical'])+E*(8*4096+8+128*128**3)+16*64**3+bg['copy_erase_episodes']+selectors+prefix+1
    two=(coef+1)**2*(E+1)**2
    assert coef==int(bc['finite']['signed_coefficient'])==int(r['finite']['bit_coefficient'])
    assert two==int(r['finite']['bit_composed_coefficient']) and prefix==int(r['finite']['prefix'])
    assert prefix<2**128 and coef<2**128 and two<2**512
    assert cf['charged_pervertex']==cf['retained_parent_pervertex']+2*8*9*560*73*2
    assert cf['extra_selector_calls']==2*8*9*560*73*2
    assert cf['row_coefficient']==15737<20161 and bc['finite']['row_coefficient']==18611<20161
    s=Q(r['selected_saving']);b=Q(r['complex_b']);c=Q(r['bit_c']);eta=Q(r['eta']);beta=Q(r['beta'])
    assert s<c and s<(1-beta)*b
    base=Q(384599,10**10);chain=[s+(base-s)*s**i for i in range(9)]
    assert chain==list(map(Q,r['bootstrap_chain']))
    for i,row in enumerate(r['finite_cutoffs'],1):
        old,new=chain[i-1:i+1];gaps=[s-new,1-new-s,1-new-s*(1-old),1-s];gap=min(gaps)
        assert gap==Q(row['minimum_gap']) and gap>0 and old<new<s
        cut=row['cutoff_log2'];assert cut*gap**2>=36 and cut*gap>=2*(4+(two-1).bit_length())
    q=chain[-1]*(1-2*eta);eps=(1-eta)/(1+q);minimum=eps*q;k=Q(r['kappa']);grid=Q(1,10**27)
    assert k<minimum<=k+grid and k==Q(1226436893071357254689269,10**27)
    assert all(Q(x)>0 for x in r['assembly']['strict_constraints'].values()) and len(r['assembly']['strict_constraints'])==47
    assert Q(r['assembly']['minimum_margin'])==minimum
    assert max(r['outer_cutoffs']['components'].values())==r['outer_cutoffs']['common']==14*10**30
    out=dict(status='PASS_INDEPENDENT_HOSTED_BOTH_MOMENTS_FINITE_INVOICE_CLOSED_BOOTSTRAP_AND_SOURCE_CLOSURE',
        receipt_sha256=sha(P/'REFINED-ASSEMBLY.json'),closed_source_checks=closure,moment_sign_checks=moments,kappa=str(k),
        prefix_bits=prefix.bit_length(),coefficient_bits=coef.bit_length(),composed_bits=two.bit_length(),extra_signed_units=576*1274,
        exact_closed_bootstrap=True,eight_finite_gap_checks=True,strict47_positive=True,complex_route_increment=cf['extra_selector_calls'],
        scope='Independent exact arithmetic/source closure plus separately admitted full geometry/payment. Prefix uses signed local source-bound majorants; all-size compiler/chart/common-prime/precision/tape/recovery/analytic and C_full remain conditional.')
    (OUT/'HOSTED-ARITHMETIC.json').write_text(json.dumps(out,indent=2)+'\n');print(out['status']);print(k)
if __name__=='__main__':main()
