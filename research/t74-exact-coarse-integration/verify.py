"""Verify the exact caller derivation; optionally compare actual full replay receipts."""
from pathlib import Path
import argparse,json,hashlib,ast,subprocess,sys
from collections import Counter
import build
if not __debug__:raise RuntimeError('Assertions must be enabled')
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
def rd(p):return json.loads(p.read_text())
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def check():
    pin=build.pins();source=(P/'reference/assemble.py').read_bytes();helper=(ROOT/pin['helper_source']).read_bytes()
    assert digest(P/'reference/PARENT-MANIFEST.json')==pin['parent_manifest_sha256']
    parent_manifest=rd(P/'reference/PARENT-MANIFEST.json');assert parent_manifest['code/assemble.py']==pin['caller_sha256']
    changed=build.caller(source,helper)
    assert changed.count(build.NEW)==1 and build.OLD not in changed
    negative=0
    for a,b in ((source+b'\n',helper),(source,helper+b'\n'),(source.replace(build.OLD,b'assert True'),helper)):
        try:build.caller(a,b)
        except AssertionError:negative+=1
        else:raise AssertionError('Invalid derivation input accepted')
    cp=subprocess.run([sys.executable,'-O','-B',str(P/'build.py'),'--help'],capture_output=True,text=True)
    assert cp.returncode!=0 and 'Assertions must be enabled' in cp.stderr
    return {'status':'PASS_EXACT_CALLER_DERIVATION_ONLY','parent_head':pin['parent_head'],'parent_manifest_sha256':pin['parent_manifest_sha256'],'original_caller_sha256':pin['caller_sha256'],'derived_caller_sha256':hashlib.sha256(changed).hexdigest(),'adapter_sha256':pin['helper_sha256'],'preserved_original_assertions':sum(isinstance(n,ast.Assert) for n in ast.walk(ast.parse(source.decode()))),'rejection_controls':negative+1,'scope':'Source-level integration only until actual complete derived replay and baseline comparison are supplied. Frozen parent and engine unchanged; no new kappa.'}

def full(result,baseline,derived):
    old=rd(baseline/'RESULT.json');new=rd(derived/'RESULT.json')
    assert old['status']==new['status']=='PASS_T74_EXACT_FILL_COMPLETE_FINITE_ADMISSION'
    assert old['kappa']==new['kappa'] and old['kappa_decimal']==new['kappa_decimal']
    assert old['controls']==new['controls']
    assert all(x['exit_code']==0 for x in old['stages']+new['stages'])
    # Compare every assembly field. No broad normalization or dropped proof keys.
    a=rd(baseline/'strict/ASSEMBLY.json');b=rd(derived/'strict/ASSEMBLY.json')
    assert a==b,'Complete assembly differs: '+str([k for k in a.keys()|b.keys() if a.get(k)!=b.get(k)])
    assert len(b['outer'])==len(b['conservative_outer'])==47
    for name in ('ADMISSION-CONTROLS.json','BIT-CONTROLS.json'):
        left=rd(baseline/'strict'/name);right=rd(derived/'strict'/name)
        assert left['assembler_sha256']==result['original_caller_sha256']
        assert right['assembler_sha256']==result['derived_caller_sha256']
        assert {k:v for k,v in left.items() if k!='assembler_sha256'}=={k:v for k,v in right.items() if k!='assembler_sha256'},name
    left=rd(baseline/'strict/INDEPENDENT.json');right=rd(derived/'strict/INDEPENDENT.json')
    assert {k:v for k,v in left.items() if k!='input_sha256'}=={k:v for k,v in right.items() if k!='input_sha256'}
    # Input locations differ in fresh work directories/native reuse. Keep and
    # validate every digest; compare the complete (basename,digest) inventory.
    inventories=[]
    for receipt in (left,right):
        inventory=Counter()
        for name,h in receipt['input_sha256'].items():
            path=Path(name)
            parts=name.split('/')
            if sys.platform=='win32' and len(parts)>3 and parts[:2]==['','mnt']:
                assert len(parts[2])==1
                path=Path(parts[2].upper()+':/').joinpath(*parts[3:])
            assert path.is_file() and digest(path)==h,'Independent input bytes differ'
            inventory[path.name,h]+=1
        inventories.append(inventory)
    assert inventories[0]==inventories[1] and sum(inventories[0].values())==6
    result['independent_input_digest_inventory_identical']=True
    result['source_hash_transition_checked']=True
    assert rd(baseline/'GEOMETRY-CONTROLS.json')==rd(derived/'GEOMETRY-CONTROLS.json')
    result['status']='PASS_FULL_T74_EXACT_ARITHMETIC_INTEGRATION'
    result['all_assembly_fields_identical']=True
    result['assembly_byte_identical']=(baseline/'strict/ASSEMBLY.json').read_bytes()==(derived/'strict/ASSEMBLY.json').read_bytes()
    assert result['assembly_byte_identical']
    result['controls']=new['controls']
    result['proof_receipt_sha256']={side:{name:digest(path/name) for name in ('RESULT.json','strict/ASSEMBLY.json','GEOMETRY-CONTROLS.json')} for side,path in [('baseline',baseline),('derived',derived)]}
    result['scope']='Actual complete derived T74 admission passes; every assembly field equals the previously executed original. Source-bound native reuse; no new kappa, theorem or default frozen-parent edit.'
    return result

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--baseline',type=Path);ap.add_argument('--derived',type=Path);ap.add_argument('--out',type=Path);a=ap.parse_args()
    result=check()
    if a.baseline or a.derived:
        assert a.baseline and a.derived
        result=full(result,a.baseline,a.derived)
    if a.out:a.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(result['status'])
