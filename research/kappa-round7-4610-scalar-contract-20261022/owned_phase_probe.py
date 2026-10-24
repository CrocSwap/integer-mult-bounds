"""Exact phase-system test with only owned source contacts unfrozen.

This is a changed owned-center interface candidate gate, not native admission.
The credited PR4665 graph/equation implementation is imported byte-for-byte;
one AST-local boundary predicate is changed and the graph is compared exactly.
"""
from pathlib import Path
from hashlib import sha256
from collections import Counter
import ast,gzip,importlib.util,json,sys,time
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]

def digest(p):return sha256(Path(p).read_bytes()).hexdigest()
def load():
    path=HERE/'sources/PR4665-verify.py'
    spec=importlib.util.spec_from_file_location('phase_rigidity_source',path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m

def relaxed_graph(M,payload):
    source=(HERE/'sources/PR4665-verify.py').read_text(encoding='utf-8')
    tree=ast.parse(source);graph=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='graph')
    changed=0
    for node in ast.walk(graph):
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='new' and len(node.args)==2:
            arg=node.args[1]
            if isinstance(arg,ast.Call) and isinstance(arg.func,ast.Name) and arg.func.id=='any':
                node.args[1]=ast.Constant(False);changed+=1
    assert changed==1
    env=dict(vars(M));exec(compile(ast.fix_missing_locations(ast.Module(body=[graph],type_ignores=[])),str(HERE/'sources/PR4665-verify.py'),'exec'),env)
    original=M.graph(payload);relaxed=env['graph'](payload)
    assert original[0:2]==relaxed[0:2] and original[3:]==relaxed[3:]
    assert relaxed[2]<=original[2]
    return original,relaxed

def main():
    began=time.monotonic();pins=json.loads((HERE/'SOURCES.json').read_text(encoding='utf-8'))
    for row in pins['sources']:
        path=ROOT/row['path'] if row['name']=='native-word' else HERE/'sources'/row['name']
        assert digest(path)==row['sha256'],row['name']
    raw=(ROOT/'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz').read_bytes()
    assert sha256(gzip.decompress(raw)).hexdigest()=='cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd'
    payload=json.loads(gzip.decompress(raw));M=load();original,relaxed=relaxed_graph(M,payload)
    frames,nodes,fixed,edges,helpers=relaxed
    freed=sorted(original[2]-fixed)
    forms=M.Forms(frames,nodes,fixed);eq=M.Equalities(forms.count);counts=Counter()
    for kind,a,b,old,image in edges:
        for i,x in enumerate(old):
            for j in range(i,len(old)):
                row=sorted(set(forms.at(a,x,old[j]))^set(forms.at(b,image[i],image[j])))
                if row:counts[kind]+=1;eq.equation(row)
    eq.finish()
    active=Counter(eq.root(i) for i in range(1,forms.count+1));active.pop(0,None)
    incident={n for edge in edges for n in edge[1:3]}
    free_nodes=[]
    for n,f in enumerate(nodes):
        if n<2 or n in fixed:continue
        d=len(frames[f]);coords=range(forms.offsets[n],forms.offsets[n]+d*(d+1)//2)
        if any(eq.root(i)!=0 for i in coords):
            assert n in freed and n not in incident
            free_nodes.append(n)
    queries=[]
    for r,a,b,basis in helpers:
        for i,x in enumerate(basis):
            for j in range(i,len(basis)):
                row=eq.simplify(sorted(set(forms.at(a,x,basis[j]))^set(forms.at(b,x,basis[j]))))
                if row:queries.append(dict(role=r,basis_pair=[i,j],remaining=row))
    report=dict(status='EXACT_RELAXED_OWNED_PHASE_LINEAR_GATE',script_sha256=digest(__file__),
        sources_sha256=digest(HERE/'SOURCES.json'),native_word_sha256=sha256(raw).hexdigest(),
        canonical_payload_sha256=sha256(gzip.decompress(raw)).hexdigest(),
        original_frozen_nodes=len(original[2]),relaxed_frozen_nodes=len(fixed),
        freed_contacts=[dict(node=n,frame=nodes[n],dimension=len(frames[nodes[n]])) for n in freed],
        form_coordinates=forms.count,equations=dict(counts),remaining_equations=len(eq.pending),
        nonzero_equality_classes=len(active),nonzero_coordinates=sum(active.values()),
        free_forms_only_at_isolated_clear_nodes=free_nodes,
        useful_helper_queries=queries,seconds=time.monotonic()-began,
        scope='Only owned-contact zero-form boundary predicate relaxed; subspaces, scalar order, shared G maps, paid-rank constraints, main/adapter endpoints and helper identity remain unchanged. Unresolved rows are not a feasibility certificate. No native/phase lowering, helper supplier, controller or kappa claim.')
    (HERE/'OWNED-PHASE-GATE.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:report[k] for k in ['status','form_coordinates','remaining_equations','nonzero_equality_classes','nonzero_coordinates','seconds']}))
    print('useful_helper_queries',len(queries),'freed_contacts',len(freed))

if __name__=='__main__':main()
