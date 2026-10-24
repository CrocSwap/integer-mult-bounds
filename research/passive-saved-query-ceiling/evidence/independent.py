"""Independent fixed passive-cut dependency/grade audit; no family search.

Uses our own D-left interpreter, no author interpreter or span routine.
The only reused scientific implementation is pinned Clifford composition.
Apache-2.0; substantial OpenAI Codex assistance.
"""
from pathlib import Path
from fractions import Fraction
from collections import Counter
from hashlib import sha256
import gzip,json,sys,types

HERE=Path(__file__).resolve().parent
def need(x,m):
    if not x:raise ValueError(m)
ae={'__name__':'independent_saved_algebra','__file__':str(HERE/'algebra.py')}
exec(compile((HERE/'algebra.py').read_bytes(),str(HERE/'algebra.py'),'exec'),ae)
a=types.SimpleNamespace(**ae)

def observations():
    # Original bank0 coefficient only, before the scalar right boundary.
    # The right boundary a=a'-h', k=b'+k' leaves its coefficient [I,0,0,0].
    rows=[a.one,{},{},{}];obs=[];cuts=[]
    def plus(i,j,z):rows[i]=a.add(rows[i],a.mul(z,rows[j]))
    def left(i,z):rows[i]=a.mul(z,rows[i])
    def snap(label):
        cuts.append(label)
        obs.extend((label+':'+str(i),x.copy())for i,x in enumerate(rows))
    def thin(pair,before,after,label):
        query=a.mul(before,rows[2*pair]);obs.append((label,query))
        rows[2*pair+1]=a.add(rows[2*pair+1],a.mul(after,query))
    def thick(pair,C,D):
        plus(2*pair,2*pair+1,a.neg(a.mul(a.q,C)))
        left(2*pair,D);left(2*pair+1,D)
    def bridge(i,j,sign):
        plus(2*i,2*j,a.one if sign==1 else a.neg(a.one))
        plus(2*j+1,2*i+1,a.neg(a.one)if sign==1 else a.one)
    snap('cut0_after_right_boundary')
    thin(0,a.qi,a.c,'paid_response0_Qinv_x');snap('cut1_after_thin0')
    thick(0,a.c,a.d);snap('cut2_after_FULL1')
    left(2,a.d);left(3,a.d);snap('cut3_after_IDLE')
    bridge(0,1,1)
    thin(0,a.mul(a.qi,a.c),a.one,'paid_response2_Qinv_C1_x')
    snap('cut4_after_bridge_plus_and_thin2')
    bridge(0,1,-1);snap('cut5_after_bridge_minus')
    thick(1,a.e,a.f);snap('cut6_after_FULL3')
    thin(1,a.mul(a.qi,a.e),a.one,'paid_response4_Qinv_C3_x');snap('cut7_after_thin4')
    bridge(1,0,1)
    for i in (0,1):rows[2*i],rows[2*i+1]=rows[2*i+1],a.neg(rows[2*i])
    plus(0,2,a.one);plus(3,1,a.neg(a.one))
    snap('cut8_after_final_standard_boundary')
    return obs,cuts

def author_poly(records):
    # Data conversion only: author normal form has D powers on the RIGHT.
    # Convert each supplied monomial to our independently reduced D-left form.
    out={}
    for r in records:
        p=a.one
        for x in r['word']:p=a.mul(p,{1:a.q,-1:a.qi,2:a.c,3:a.e}[x])
        powers=r['fresh_powers']
        need(all(n>=0 for n in powers),'Source trace fresh powers nonnegative')
        for D,n in zip((a.d,a.f),powers):
            for _ in range(n):p=a.mul(p,D)
        p={key:Fraction(r['coefficient'])*v for key,v in p.items()}
        out=a.add(out,p)
    return out

def rank(rows):
    piv={}
    for x in rows:
        while x:
            k=x.bit_length()-1
            if k in piv:x^=piv[k]
            else:piv[k]=x;break
    return len(piv)

def main():
    pins=json.loads((HERE/'SOURCES.json').read_text())['sources']
    for r in pins:need(sha256((HERE/'inputs'/r['path'].split('/')[-1]).read_bytes()).hexdigest()==r['sha256'],'Source bytes '+r['path'])
    f=HERE/'frozen'/'pr4948-saved-query-macro-gate'
    frozen=json.loads((HERE/'FROZEN-HASHES.json').read_text())
    for n,h in frozen['science'].items():need(sha256((f/n).read_bytes()).hexdigest()==h,'Author frozen science '+n)
    for n,h in json.loads((HERE/'ADDENDUM-HASH.json').read_text()).items():
        need(sha256((f/n).read_bytes()).hexdigest()==h,'Written scope clarification '+n)
    need(sha256((f/'FILES.json').read_bytes()).hexdigest()==frozen['author_manifest_sha256'],'Author manifest')
    need(sha256((f.parent/'pr4948-mixed-thin-gate'/'check.py').read_bytes()).hexdigest()==frozen['mixed_check_sha256'],'Mixed dependency')
    receipt=json.loads((f/'GRADE-GATE.json').read_text())
    for stem,want in [('bank_span','BANK-SPAN.json'),('grade_gate','GRADE-GATE.json')]:
        for mode in ('normal','optimized'):
            need(json.loads((HERE/(stem+'-'+mode+'.json')).read_text())==json.loads((f/want).read_text()),'Author read-only replay '+stem+' '+mode)
    obs,cuts=observations()
    need(len(obs)==39 and len(cuts)==9 and cuts==receipt['declared_cuts'],'Exact nine cuts and three paid responses')
    expected=[('I',a.one),('Qinv',a.qi),('C1_Qinv',a.mul(a.c,a.qi)),('Qinv_C1_D1',a.mul(a.qi,a.c,a.d))]
    trace=[];counts=Counter()
    for (label,p),record in zip(obs,receipt['original_input0_dependency_trace'],strict=True):
        need(label==record['observation'] and p==author_poly(record['original_input0_terms']),'Independent original-input0 trace '+label)
        if not p:kind='zero'
        else:
            found=[name+(''if p==word else '_negative') for name,word in expected if p==word or p==a.neg(word)]
            need(len(found)==1,'Only four advertised source path families')
            kind=found[0]
        counts[kind]+=1;trace.append({'observation':label,'input0_path':kind})
    need(counts==Counter({'zero':27,'I':2,'C1_Qinv':1,'Qinv':1,'Qinv_C1_D1':7,'Qinv_C1_D1_negative':1}),'Exact dependency census')
    need(all(b==0 for _,p in obs for (D,w)in p for b in D[1:]),'No D3 original-input0 path')
    # Explicit cancellation checkpoints: no source0 X after FULL1; no
    # source0 pair1 Y after bridge-minus, before FULL3 acts there.
    lookup=dict(obs)
    need(not lookup['cut2_after_FULL1:0'],'FULL1 original X cancellation')
    need(not lookup['cut5_after_bridge_minus:3'],'Pair1 Y canceled before FULL3')
    need(not lookup['paid_response2_Qinv_C1_x'] and not lookup['paid_response4_Qinv_C3_x'],'No late paid-response observation of original input0')

    ce=types.ModuleType('independent_saved_ce');sys.modules[ce.__name__]=ce
    ce.__file__=str(HERE/'inputs/clifford_exact.py')
    exec(compile((HERE/'inputs/clifford_exact.py').read_bytes(),ce.__file__,'exec'),ce.__dict__)
    normal=json.loads((HERE/'inputs/NORMALIZERS.json').read_text())
    def monomial(circ):
        op=ce.ident(9)
        for t in circ:
            if t[0]=='P':step=ce.perm(9,t[1])
            elif t[0]=='D':step=ce.diag(9,t[1],t[2])
            elif t[0]=='X':step=ce.xgate(9,t[1])
            elif t[0]=='phase':step=ce.Op(9,ce.identity(9),[('phase',t[1])])
            else:raise ValueError('Actual K must be monomial')
            op=op.then(step)
        return op
    Ks=[monomial(r['K_word'])for r in normal['ports']]
    inverses=[K.adjoint()for K in Ks]
    def grade(op):return rank([x for x,z,p in op.tab[9:]])
    need(len(Ks)==112 and all(grade(K)==0 for K in Ks),'112 actual monomial source K words')
    matrix=json.loads(gzip.decompress((HERE/'inputs/INVOLUTIVE-WORD.json.gz').read_bytes()))['F']
    Ft=[[Fraction(matrix[j][i])for j in range(112)]for i in range(112)]
    selected=[j for j in range(112)if Ft[j][j]];other=[j for j in range(112)if not Ft[j][j]]
    need(selected==[0,7,20,23,86,93,108,111]and len(other)==104,'Actual selected/zero-diagonal source columns')
    need(all(Ft[j][j]==12 for j in selected),'Actual nonzero diagonal value')
    need(other==receipt['actual_source_zero_diagonal_ports'],'Author original source-column census')
    D=ce.fourier(9,range(1,9));Qi=ce.cgate(9,1).adjoint()
    words=[];hist=Counter();per_source=[]
    for j in other:
        support=[]
        for i in range(112):
            if not Ft[i][j]:continue
            # Literal matrix order Qi Ki^-1 Kj D, chronology opposite.
            word=D.then(Ks[j]).then(inverses[i]).then(Qi)
            g=grade(word);need(g==7,'Literal unselected pair grade7')
            support.append(i);hist[g]+=1
            words.append({'destination_port':i,'source_port':j,'coefficient':str(Ft[i][j]),'grade':g})
        need(len(support)==52,'Actual support52 for every zero-diagonal source')
        per_source.append({'source_port':j,'support':support,'grades':{'7':52}})
    need(hist==Counter({7:5408}),'Independent complete grade census')
    need(words==receipt['all_supported_words']and per_source==receipt['per_source'],'All5408 exact pair records and 104 supports')
    target_grade=grade(Qi.then(D));need(target_grade==9 and grade(Qi)==1 and grade(ce.ident(9))==0,'Target and earlier grades')
    for j in selected:
        need(grade(D.then(Ks[j]).then(inverses[j]).then(Qi))==9,'Selected diagonal positive control')
    need(grade(D.then(Qi))==9,'Uncoded identity positive control')
    # A falsely homogenized off-diagonal pair would expose grade9, showing
    # that grade7 is tied to the actual distinct native port frames.
    need(grade(D.then(ce.ident(9)).then(Qi))!=7,'False frame-homogenization control')
    out={'status':'PASS_INDEPENDENT_FIXED_PASSIVE_CUT_GATE','source_head':'86e474038e05f99a76d41f71d81946ad2327e4a4',
         'dependency_interpreter':'Own D-left semidirect normal form; no producer Algebra/span code',
         'nine_cuts':cuts,'observed_bank_fields':39,'original_input0_trace':trace,
         'dependency_path_counts':dict(counts),'D3_dependency':False,
         'post_FULL_unselected_grade_census':dict(hist),'zero_diagonal_original_inputs':104,
         'every_zero_diagonal_column_support':52,'earlier_grades':[0,1],'target_grade':target_grade,
         'all5408_exact_records_equal':True,
         'allwidth_scope':'Uniform finite projective Clifford alphabet at fixed ambient17; projective tensor Gram separation excludes reconstruction for all sufficiently large f, not necessarily every finite f',
         'phase_qualification':'Actual pure-word grades are phase-invariant; finite scalar phases^f are absorbed into external owner coefficients. No new native phase campaign or physical prefix replay.',
         'passive_only':True,'physical_emission':False,'new_kappa':None,
         'ownership':{'original_main_fields':448,'independent_native_helpers':816,'all_snapshot_fields':4368,'snapshot_reward':0,'all_owned_resets_granted_free_for_negative':True,'particular_erase_implementation_needed_for_negative':False},
         'exclusions':['Active injection into future paid gates','Other thin placements or cuts','Native internal prefix observations','New Gaussian calls','Arbitrary f-specific noncolumnwise monomial controllers','Changed targets or complete caller/compiler admission']}
    print(json.dumps(out,indent=2,sort_keys=True))
    if '--emit'in sys.argv:(HERE/'INDEPENDENT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')

if __name__=='__main__':main()
