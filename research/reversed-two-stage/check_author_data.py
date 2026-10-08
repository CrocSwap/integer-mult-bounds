from fractions import Fraction as Q
from pathlib import Path
import hashlib,json,resource,time,sys
from independent_controls import corner_labels,expected_pivots,completion,check_cuts
resource.setrlimit(resource.RLIMIT_AS,(100*1024*1024,100*1024*1024))
resource.setrlimit(resource.RLIMIT_CPU,(110,110))
HERE=Path(__file__).resolve().parent
start=time.monotonic();h=int(sys.argv[1]) if len(sys.argv)>1 else 45;b=h+2;d=2*h+1
path=HERE/f'REVERSED_{h}_CERTIFICATE.json';raw=path.read_bytes();author=json.loads(raw)
rows,cols=corner_labels(h);expected=expected_pivots(h)
assert author['row_edges']==[list(e) for e in rows] and author['column_edges']==[list(e) for e in cols]
assert author['pivots']==expected
assert author['permutation_completions']==completion(h,rows,cols)
cuts=check_cuts(h,rows,cols,expected)
for own,supplied in zip(cuts,author['rank_cuts']):
    assert own['row']==supplied['row'] and own['pivot']==supplied['column']
    if 'selected' in own:
        assert own['selected']==supplied['selected']
        assert [own['left_rank'],own['right_rank']]==supplied['ranks']
        assert own['preceding_right_pivots']==supplied['prior']
    else:assert own['trivial_suffix_bound']==supplied['prior']
assert len(cuts)==len(author['rank_cuts'])==d
w=author['witness'];wa=[(i+1)**2 for i in range(h)];wb=[(i+1)**3 for i in range(b)]
assert w['xi_numerators']==wa and w['nu_numerators']==wb
assert w['xi_denominator']==sum(wa) and w['nu_denominator']==sum(wb)
xi=[Q(v,sum(wa)) for v in wa];nu=[Q(v,sum(wb)) for v in wb]
assert sum(xi)==sum(nu)==1
M=[[Q(int(r==c),xi[r])+Q(int(be==ga),nu[be])-1 for c,ga in cols] for r,be in rows]
values=[];remaining=set(range(d))
for i,q in enumerate(expected):
    assert max(j for j in remaining if M[i][j])==q
    pivot=M[i][q];values.append(str(pivot));remaining.remove(q)
    for k in range(i+1,d):
        if M[k][q]:
            multiple=M[k][q]/pivot
            for j in remaining:M[k][j]-=multiple*M[i][j]
            M[k][q]=Q(0)
assert values==w['pivot_values']
assert author['profile']==[1]*9+[h-2,h-6,h*h-2*h-2]
out={'author_certificate_sha256':hashlib.sha256(raw).hexdigest(),'all_pivots_match':d,'all_rank_cut_records_match':d,'all_permutation_completions_match':b,'normalized_rational_witness':True,'elapsed_seconds':time.monotonic()-start,'no_author_code_executed':True}
(HERE/('AUTHOR_DATA_REPRODUCTION.json' if h==45 else f'AUTHOR_{h}_DATA_REPRODUCTION.json')).write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
