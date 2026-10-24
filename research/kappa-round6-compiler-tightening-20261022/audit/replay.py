"""Independent read-only arithmetic audit; writes only audit/AUDIT.json.

No producer arithmetic/ledger/moment function is imported. Outer source
expressions are separately interpreted by a restricted exact AST evaluator.
Cao Yifan; substantial OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from fractions import Fraction as F
from functools import lru_cache
from hashlib import sha256
from pathlib import Path
import ast,gzip,importlib.util,json,sys,time
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;PACKAGE=HERE.parent;ROOT=PACKAGE.parents[1]


def digest(p):return sha256(Path(p).read_bytes()).hexdigest()
def read(p):return json.loads(Path(p).read_text(encoding='utf-8'))


def main():
    began=time.monotonic();a=read(PACKAGE/'ARITHMETIC.json');initial=digest(PACKAGE/'ARITHMETIC.json')
    assert a['status']=='PASS_CHANGED_PROFILE_ARITHMETIC_NATIVE_ADMISSION_SEPARATE'
    for p,v in a['source_sha256'].items():assert digest(ROOT/p)==v,p
    patch=read(PACKAGE/'ARITHMETIC-SOURCE-PATCH.json')
    assert digest(ROOT/patch['source'])==patch['source_sha256']
    source=(ROOT/patch['source']).read_text(encoding='utf-8')
    for old,new in patch['changes']:assert source.count(old)==1;source=source.replace(old,new)
    assert len(patch['changes'])==4 and source==(PACKAGE/'arithmetic.py').read_text(encoding='utf-8')
    assert digest(PACKAGE/'arithmetic.py')==patch['derived_sha256']
    nativefolder=ROOT/'research/kappa-round3-warp-20261022';native=read(nativefolder/'NATIVE-VALIDATION.json')
    assert digest(nativefolder/'NATIVE-VALIDATION.json')==a['native_receipt_sha256']
    blob=(nativefolder/'ACTUAL-WORD.json.gz').read_bytes();assert sha256(blob).hexdigest()=='7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05'
    assert sha256(gzip.decompress(blob)).hexdigest()==native['actual_word_canonical_sha256']
    word=json.loads(gzip.decompress(blob));c=word['canonical']
    helpers=Counter(len(c['frames'][c['final'][r]])-len(c['frames'][c['start'][r]]) for r in range(224,632))
    local=[]
    for direction,events in word['programs'].items():
        p=Counter(e[5] for e in events if e[0]=='climb')+Counter(e[4] for e in events if e[0]=='center')
        assert p==Counter({int(k):v for k,v in a['local_paid'].items()})
        assert p==Counter({int(k):v for k,v in native['native'][direction]['paid_profile'].items()});local.append(p)
    assert local[0]==local[1] and helpers==Counter({int(k):v for k,v in a['local_helpers'].items()})
    controller=read(ROOT/'research/joint-helper-lattice/CONTROLLER.json');T,P=Counter(),Counter();counts=Counter()
    for e in controller['physical_events']:
        counts[e[0]]+=1
        if e[0]=='LOCAL':T.update(helpers);P.update(local[0])
        elif e[0]=='QUERY_SHEAR':P[1]+=112
        elif e[0]=='IDLE':P[8*len(e[2])]+=224
    for term in controller['diagonal']:assert term[0] in [-1,1];T[1+8*sum(term[1:])]+=112
    assert counts['LOCAL']==18 and counts['QUERY_SHEAR']==15
    assert T==Counter({int(k):v for k,v in a['targets'].items()}) and P==Counter({int(k):v for k,v in a['paid'].items()})
    assert sum(T.values())==10928 and sum(P.values())==64404 and sum(r*n for r,n in T.items())-sum(r*n for r,n in P.items())==752
    engine=ROOT/'research/kappa-rebuild/transfer-audit/outer_transfer_audit.py'
    spec=importlib.util.spec_from_file_location('independent_intervals',engine);X=importlib.util.module_from_spec(spec);spec.loader.exec_module(X)
    @lru_cache(None)
    def logs(k):return X.log_integer(k)
    def exp_point(x):
        if x<0:
            l,u=exp_point(-x);return X.down(1/u),X.up(1/l)
        shifts=0
        while x>=F(1,10):x/=2;shifts+=1
        l,u=X.exp_small(x)
        for _ in range(shifts):l,u=X.down(l*l),X.up(u*u)
        return l,u
    def power(k,e):
        l,u=logs(k);l,u=(e*l,e*u) if e>=0 else (e*u,e*l)
        return exp_point(l)[0],exp_point(u)[1]
    def moment(profile,e):
        l=u=F(0)
        for k,n in profile.items():
            lo,hi=power(k,e);l+=n*lo;u+=n*hi
        return X.down(l),X.up(u)
    def mul(x,y):return X.down(x[0]*y[0]),X.up(x[1]*y[1])
    def div(x,y):assert y[0]>0;return X.down(x[0]/y[1]),X.up(x[1]/y[0])
    def enclosed(x,d):assert F(d['lower'])<=x[0]<=x[1]<=F(d['upper'])
    k,tested=F('.0030217758'),F('.00302177581');t=1-tested;gap=(tested-k)/7
    assert F(a['kappa'])==k and F(a['strictification']['tested'])==tested and gap==F(1,700000000000)
    target,paid=moment(T,t),moment(P,t);alpha=div(paid,target)
    gamma=div(moment(P,t+F(1,5)),mul(power(20,F(1,5)),target))
    delta=div((F(sum(T.values())*21),)*2,mul(power(20,tested),target))
    for name,value in [('alpha',alpha),('gamma',gamma),('delta',delta)]:enclosed(value,a['strictification'][name])
    reserve=F(1,10**11)
    assert alpha[0]>1-F(1,10**9)  # Old reserve cannot certify this tested saving.
    assert alpha[1]<1-reserve and gamma[1]<F(97,100) and delta[1]<F(97,100)
    assert F(97,100)**128<F(1,16)
    normalized=1/(1+1024*reserve)+F(4,2**32)
    assert normalized==F(a['strictification']['normalized_paid_upper'])<1
    rl,rh=map(F,a['raw_root_interval']);rlT,rlP=moment(T,1-rl),moment(P,1-rl);rhT,rhP=moment(T,1-rh),moment(P,1-rh)
    assert rlT[0]-rlP[1]>0 and rhT[1]-rhP[0]<0
    step,j=700000000000,55099;height=step*j
    assert height==a['compiler']['H']==38569300000000000 and j==a['compiler']['integer_test_exponent']
    assert height>8*1024 and (height+1)**1000<2**j
    assert F(63,64)**1000<t/F(6097250)
    assert 1024*tested<F(25,8) and 145<2**8 and 2*145**3==6097250<2**1000
    assert 2*(20**1024)**64<=(145**1024)**63 and 20**64<21**63
    p=power(145,-1024*tested);eta=X.down(t*p[0]),X.up(t*p[1]);enclosed(eta,a['compiler']['eta'])
    scalar=max(x['real_scalar_allowance'] for x in native['native'].values());routes=(sum(local[0].values())+2*408+688)*1000
    raw_scalar=18*10**7+15*1792+32*112*(len(controller['physical_events'])+sum(len(controller['boundaries'][q+'_program']) for q in ['left','right']))
    assert scalar==158168 and routes==4802000 and raw_scalar==181098496
    assert scalar+routes<10**7 and raw_scalar<10**9
    # Independently interpret exact source formulas, without calling ledger().
    outerpath=ROOT/'research/pr4359-p7-padding/dependencies/compiler-refill/endpoint.py'
    module=ast.parse(outerpath.read_text(encoding='utf-8'))
    function=next(n for n in module.body if isinstance(n,ast.FunctionDef) and n.name=='ledger')
    tables={n.targets[0].id:n.value for n in function.body if isinstance(n,ast.Assign) and isinstance(n.targets[0],ast.Name) and isinstance(n.value,ast.Dict)}
    def ledger(p):
        b,a,q,ep,be,r,st,la=[p[x] for x in ['b','a','q','epsilon','beta','r0','stop','layout']]
        si,ta=1-b,1-a;inte=ta+(1-st)*max(si-ta,F(0));leaf=si+st*(1-si);lm=1-(q+a)/2;cap=F(3,32);xi=ep*(1+q)-cap+la;key=be+1-ep
        env=dict(p=p,kappa=p['kappa'],b=b,a=a,q=q,epsilon=ep,beta=be,r0=r,stop=st,layout=la,sigma=si,tau=ta,internal=inte,leaf=leaf,lam=lm,c=cap,xi=xi,key=key,OLD_BASELINE=F('.001730970419199163702738'))
        def ev(n):
            if isinstance(n,ast.Constant):return n.value
            if isinstance(n,ast.Name):return env[n.id]
            if isinstance(n,ast.UnaryOp) and isinstance(n.op,ast.USub):return -ev(n.operand)
            if isinstance(n,ast.Subscript):return ev(n.value)[ev(n.slice)]
            if isinstance(n,ast.Call):assert isinstance(n.func,ast.Name) and n.func.id=='Q';return F(*[ev(x) for x in n.args])
            if isinstance(n,ast.Dict):return {ev(x):ev(y) for x,y in zip(n.keys,n.values)}
            if isinstance(n,ast.BinOp):
                l,r=ev(n.left),ev(n.right)
                if isinstance(n.op,ast.Add):return l+r
                if isinstance(n.op,ast.Sub):return l-r
                if isinstance(n.op,ast.Mult):return l*r
                if isinstance(n.op,ast.Div):return F(l)/r
                if isinstance(n.op,ast.Pow):return l**r
            raise ValueError(ast.dump(n))
        margins=ev(tables['margins']);env['margins']=margins;checks=ev(tables['checks'])
        checks.update({name+'_above_kappa':v-p['kappa'] for name,v in margins.items()})
        functional=ev(tables['functional']);functional['actual_new_BIT_stock_sublinear']=be*(1-F(4,1000))
        return dict(parameters=dict(p,cap_xi=xi,lambda_=lm,lambda_prime=1-q),margins=margins,strict_checks=checks,functional_checks=functional)
    params=dict(kappa=k,tested_saving=tested,complex_uniform_saving=k+6*gap,b=k+5*gap,a=k+4*gap,q=k+3*gap,bit_saving=F(17,5000),epsilon=1-gap,beta=1-3*gap,r0=gap/10,stop=gap,layout=gap,d=gap)
    own=ledger(params)
    for group,rows in own.items():assert rows=={key:F(value) for key,value in a['outer'][group].items()},group
    assert len(own['strict_checks'])==54 and len(own['functional_checks'])==4 and len(own['margins'])==9
    assert all(v>0 for group in ['strict_checks','functional_checks'] for v in own[group].values())
    assert all(0<own['functional_checks'][key]<1 for key in ['new_BIT_row_stock_sublinear_in_active_group','actual_new_BIT_stock_sublinear'])
    controls={}
    for name,change in [('old_BIT',{'bit_saving':F('.0027')}),('closed_uniform',{'complex_uniform_saving':params['b']}),('unfunded_endpoint',{'kappa':tested}),('closed_epsilon',{'epsilon':F(1)})]:
        bad=ledger(dict(params,**change));failed=[key for key,value in bad['strict_checks'].items() if value<=0]
        assert failed and set(failed)==set(a['negative_controls'][name]);controls[name]=failed
    bit=a['ordinary_BIT'];atom=F(bit['atom']);ordinary=(1-atom)*F(bit['after_cover'])+atom*F('.0000384599')
    assert atom==F(1,250) and ordinary==F(bit['ordinary_saving']) and atom>ordinary>F(bit['admitted'])>tested and atom<1-ordinary
    assert 2**26>256/(F(bit['before_cover'])-F(bit['after_cover']))
    num=read(PACKAGE/'numerical_generate-output.json')
    assert F(num['target_lower'])<=target[0] and paid[1]<=F(num['paid_upper'])
    assert F(num['margin_lower'])==F(num['target_lower'])-F(num['paid_upper'])>0
    contraction_witness_slack=(1-reserve)*F(num['target_lower'])-F(num['paid_upper']);assert contraction_witness_slack>0
    transcription=read(PACKAGE/'ARITHMETIC-TRANSCRIPTION.json')
    assert transcription['receipt_sha256']==initial and transcription['source_sha256']==digest(outerpath) and transcription['lean_sha256']==digest(PACKAGE/'TightenedArithmetic.lean')
    proof=read(PACKAGE/'PROOF-SOURCES.json')
    for name,value in proof['prepared_sha256'].items():assert digest(PACKAGE/name)==value
    assert digest(PACKAGE/'ARITHMETIC.json')==initial
    # Authenticate the parent's fresh four-module replay and explicit native reuse.
    lean=read(PACKAGE/'LEAN-VERIFICATION.json')
    assert lean['status']=='PASS_TIGHTENED_SCOPED_LEAN_CERTIFICATES' and lean['fresh_axiom_reports']==31 and len(lean['modules'])==4
    assert lean['arithmetic_sha256']==initial and lean['script_sha256']==digest(PACKAGE/'verify_lean.py')
    for name,value in lean['input_sha256'].items():assert digest(ROOT/name)==value
    for name,value in lean['local_source_sha256'].items():assert digest(PACKAGE/name)==value
    runtime=ROOT/'research/kappa-lean-verification-20261022'
    auditor_path=runtime/'verify_lean.py';assert digest(auditor_path)=='6c953b31c385179f852eb4b56246e62a4084cb8906843f15fbf2724508539895'
    spec=importlib.util.spec_from_file_location('proof_log_auditor',auditor_path);auditor=importlib.util.module_from_spec(spec);spec.loader.exec_module(auditor)
    nativeproof=ROOT/'research/kappa-round3-warp-lean-20261022';old=read(nativeproof/'LEAN-VERIFICATION.json')
    assert digest(nativeproof/'LEAN-VERIFICATION.json')==lean['native_reuse_receipt_sha256'] and old['runtime']==lean['runtime']
    assert digest(runtime/'.toolchain/lean-4.21.0-windows/bin/lean.exe')==lean['runtime']['lean_executable_sha256']
    def check_module(base,row):
        name=row['module']
        for suffix,field in [('.lean','source_sha256'),('.log','log_sha256'),('.olean','olean_sha256')]:assert digest(base/(name+suffix))==row[field],name+suffix
        assert auditor.parse_axioms(base/(name+'.log'),auditor.audit_source(base/(name+'.lean')))==row['axioms']
    for row in lean['modules']:
        check_module(PACKAGE,row);assert row['exit_code']==0 and row['argv']==['lean','-s','262144','-o',row['module']+'.olean',row['module']+'.lean']
    oldrows={x['module']:x for x in old['modules']}
    assert len(lean['native_reuse_modules'])==31
    for row in lean['native_reuse_modules']:
        check_module(nativeproof,row);prior=oldrows[row['module']]
        assert prior['exit_code']==0
        for field in ['source_sha256','log_sha256','olean_sha256','axioms']:assert row[field]==prior[field]
        for name,value in prior['dependency_olean_sha256'].items():assert value==oldrows[name]['olean_sha256']==digest(nativeproof/(name+'.olean'))
    proof_evidence=dict(lean_receipt_sha256=digest(PACKAGE/'LEAN-VERIFICATION.json'),verification_script_sha256=digest(PACKAGE/'verify_lean.py'),
                        fresh_modules=4,fresh_axiom_reports=31,reused_native_modules=31,reused_native_axiom_reports=sum(len(x['axioms']) for x in lean['native_reuse_modules']),
                        native_reuse_receipt_sha256=lean['native_reuse_receipt_sha256'],source_log_object_hashes_checked=True,allowed_axioms=lean['allowed_axioms'],
                        auditor_recompiled_modules=False,new_compile_stack_kilobytes=262144)
    report=dict(status='PASS_INDEPENDENT_COMPLETE_INVOICE_COMPILER_AND_58_OUTER_FORMULAS',replay_sha256=digest(__file__),
        arithmetic_sha256=initial,arithmetic_source_sha256=digest(PACKAGE/'arithmetic.py'),source_patch_exact_four_changes=True,
        native_word_sha256=digest(nativefolder/'ACTUAL-WORD.json.gz'),native_receipt_sha256=digest(nativefolder/'NATIVE-VALIDATION.json'),controller_sha256=digest(ROOT/'research/joint-helper-lattice/CONTROLLER.json'),independent_interval_engine_sha256=digest(engine),outer_formula_source_sha256=digest(outerpath),
        claimed_kappa=str(k),tested_saving=str(tested),gain_over_PR4610=str(k-F('.00302176')),productive_fields=sum(T.values()),paid_calls=sum(P.values()),rank_mass_surplus=752,
        independent_intervals={name:[str(q) for q in value] for name,value in [('alpha',alpha),('gamma',gamma),('delta',delta),('eta',eta),('target',target),('paid',paid)]},
        reserve=str(reserve),old_contraction_reserve_rejected=True,normalized_paid_upper=str(normalized),normalized_completion_slack=str(1-normalized),kernel_witness_contraction_slack=str(contraction_witness_slack),
        compiler=dict(product_power=1024,H=height,N='2^'+str(height),gap=str(gap),step=step,integer_test_exponent=j,logarithm_power=1000,integer_predicate=True,eta_capacity=True,initial_range=True,shifted_exit_capacity=True,threshold_minimality_claimed=False),
        nonrecursive=dict(local_scalar=scalar,local_routes=routes,raw_scalar_upper=raw_scalar),strict_outer_formulas=54,functional_outer_formulas=4,outer_margin_formulas=9,
        outer_minimum_strict_slack=str(min(own['strict_checks'].values())),negative_controls=controls,finite_native_admission_reused=True,new_native_profile=False,new_raw_root=False,
        root_bracket_endpoint_signs_checked=True,fresh_Lean_recompile_by_auditor=False,lean_evidence=proof_evidence,package_script_sha256={name:digest(PACKAGE/name) for name in ['arithmetic.py','prepare.py','numerical_generate.py','generate_arithmetic.py','verify_lean.py']},stock_exponents_below_one=True,proof_source_sha256=proof['prepared_sha256'],seconds=time.monotonic()-began,
        scope='Independent arithmetic, boundary inventory and compiler sufficient-predicate audit. No root search or minimal threshold claim. No new native profile, native theorem, unconditional multiplication theorem or relaxed external hypothesis. Root fresh Lean replay is separate.')
    (HERE/'AUDIT.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({key:report[key] for key in ['status','claimed_kappa','gain_over_PR4610','normalized_completion_slack','kernel_witness_contraction_slack','strict_outer_formulas','functional_outer_formulas','seconds']},sort_keys=True))


if __name__=='__main__':main()
