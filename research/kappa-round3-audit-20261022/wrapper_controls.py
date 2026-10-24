"""In-memory adversarial controls against the actual round-three Lean wrapper.

No frozen proof input, receipt or source is edited. Temporary numerical
sources live only inside this audit directory. No Lean compilation is claimed.
Cao Yifan; substantial OpenAI Codex assistance; Apache-2.0.
"""
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import importlib.util,json,re,sys,tempfile,time
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
PACKAGE=ROOT/'research/kappa-round3-warp-lean-20261022'
OLD=ROOT/'research/kappa-lean-verification-20261022'
def load(p,n):
    sp=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(sp);sys.modules[n]=m;sp.loader.exec_module(m);return m
def digest(p):return sha256(p.read_bytes()).hexdigest()

def main():
    start=time.monotonic();R=load(PACKAGE/'replay.py','audit_actual_round3_wrapper');W=load(OLD/'verify_lean.py','audit_retained_support')
    need=lambda p,s: (_ for _ in ()).throw(ValueError(s)) if not p else None
    original=(OLD/'verify_lean.py').read_text(encoding='utf-8');left=original.index('def numerical_binding(');right=original.index('\ndef authenticate_inputs()',left)
    fragment=original[left:right].replace('302153, 100000000','302177, 100000000').replace('37769, 12500000','9443, 3125000')
    exec(compile(fragment,str(PACKAGE/'replay.py'),'exec'),W.__dict__);W.HERE=PACKAGE
    # Successful real wrapper binding before every negative case is required.
    baseline=R.bindings(W);controls=[];actual_read=R.read
    def test(name,fn):
        try:fn()
        except (ValueError,AssertionError) as e:controls.append({'name':name,'rejected':str(e)})
        else:raise ValueError('Corruption accepted: '+name)
    def receipt_case(name,filename,edit):
        target=R.SOURCE/filename
        def altered(p):
            value=actual_read(p)
            if p==target:value=deepcopy(value);edit(value)
            return value
        R.read=altered
        try:test(name,lambda:R.bindings(W))
        finally:R.read=actual_read
    receipt_case('stale_native_payload','NATIVE-VALIDATION.json',lambda x:x.__setitem__('actual_word_canonical_sha256','0'*64))
    receipt_case('stale_phase_payload','PHASE-VALIDATION.json.gz',lambda x:x.__setitem__('actual_word_canonical_sha256','0'*64))
    receipt_case('stale_native_verifier','NATIVE-VALIDATION.json',lambda x:x.__setitem__('verifier_sha256','0'*64))
    receipt_case('stale_phase_verifier','PHASE-VALIDATION.json.gz',lambda x:x.__setitem__('verifier_sha256','0'*64))
    receipt_case('stale_phase_source_manifest','PHASE-VALIDATION.json.gz',lambda x:x.__setitem__('source_manifest_sha256','0'*64))
    receipt_case('duplicate_helper_phase_coverage','PHASE-VALIDATION.json.gz',lambda x:x['changed_helper_boundaries'][0]['helpers'].append(x['changed_helper_boundaries'][0]['helpers'][0]))
    receipt_case('duplicate_warp_class_same_count','PHASE-VALIDATION.json.gz',lambda x:x['actual_warp_classes'].__setitem__(0,deepcopy(x['actual_warp_classes'][1])))
    receipt_case('duplicate_paid_pair_same_count','PHASE-VALIDATION.json.gz',lambda x:x['new_paid_pairs'].__setitem__(0,deepcopy(x['new_paid_pairs'][1])))
    receipt_case('wrong_helper_phase_input','PHASE-VALIDATION.json.gz',lambda x:x['changed_helper_boundaries'][0].__setitem__('input',1))
    receipt_case('wrong_native_paid_coefficient','NATIVE-VALIDATION.json',lambda x:x['paid'].__setitem__('1',x['paid']['1']+1))
    # Mutate just one literal Lean paid coefficient, leaving runtime and original
    # native/controller/JSON records intact. The actual parser must reject it.
    with tempfile.TemporaryDirectory(prefix='numeric-control-',dir=HERE) as directory:
        temp=Path(directory);(temp/'numerical_generate.py').write_bytes((PACKAGE/'numerical_generate.py').read_bytes())
        code=(PACKAGE/'NumericalMoments.lean').read_text(encoding='utf-8')
        pattern=r'(noncomputable def paidMoment\s*\(t : ℝ\) : ℝ :=\s*\n\s*)(\d+)(\s*\*)'
        altered,count=re.subn(pattern,lambda m:m[1]+str(int(m[2])+1)+m[3],code,count=1)
        need(count==1,'expected exact literal paid definition syntax')
        (temp/'NumericalMoments.lean').write_text(altered,encoding='utf-8',newline='\n')
        W.HERE=temp
        test('wrong_Lean_paid_coefficient',lambda:W.numerical_binding(actual_read(R.SOURCE/'ARITHMETIC.json'),actual_read(R.SOURCE/'NATIVE-VALIDATION.json')))
        W.HERE=PACKAGE
    need(R.bindings(W)==baseline,'positive baseline changed during controls')
    result={'status':'PASS_ROUND3_WRAPPER_ADVERSARIAL_CONTROLS','controls':controls,'positive_binding_before_and_after':True,'wrapper_sha256':digest(PACKAGE/'replay.py'),'retained_support_sha256':digest(OLD/'verify_lean.py'),'numerical_source_sha256':digest(PACKAGE/'NumericalMoments.lean'),'script_sha256':digest(Path(__file__)),'seconds':time.monotonic()-start,'scope':'Actual wrapper input-binding and numerical-literal parsers exercised in memory. No source/receipt mutation, no kernel replay, no new proof theorem.'}
    (HERE/'WRAPPER-CONTROLS.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
