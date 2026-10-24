"""Actual-contact unrestricted symmetric forms, with inert markers unfrozen."""
from pathlib import Path
from hashlib import sha256
from types import SimpleNamespace
from collections import Counter
import ast,gzip,importlib.util,json,sys,time
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
def digest(p):return sha256(Path(p).read_bytes()).hexdigest()
def need(ok,message):
    if not ok:raise ValueError(message)
def geometry(payload):
    path=HERE/'sources/mixed_gauge.py';tree=ast.parse(path.read_text(encoding='utf-8'))
    parts=[n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Union']+[
        n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='graph']
    need(len(parts)==2,'Exact geometry AST exports')
    env={'R':SimpleNamespace(need=need)}
    exec(compile(ast.fix_missing_locations(ast.Module(body=parts,type_ignores=[])),str(path),'exec'),env)
    old=env['graph'](payload)
    function=parts[1];returns=[n for n in function.body if isinstance(n,ast.Return)]
    need(len(returns)==1 and isinstance(returns[0].value,ast.Call),'Geometry return schema')
    for name,expression in [
        ('main_fixed',"sorted({comp[starts['L',i]] for i in range(224)}|{comp[ends['L',i]] for i in range(224)})"),
        ('owned_fixed','sorted({comp[i] for i in owned})'),
        ('zero_fixed','sorted({component for component,frame in compframe.items() if frame==0})')]:
        returns[0].value.keywords.append(ast.keyword(arg=name,value=ast.parse(expression,mode='eval').body))
    exec(compile(ast.fix_missing_locations(ast.Module(body=parts,type_ignores=[])),str(path),'exec'),env)
    expanded=env['graph'](payload)
    need({k:expanded[k] for k in old}==old,'Graph unchanged by return-only metadata')
    return expanded
def phase_module():
    path=HERE/'sources/phase_equations.py';spec=importlib.util.spec_from_file_location('credited_symmetric_forms',path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def gaussian(rows):
    basis={}
    for row in rows:
        while row:
            p=row.bit_length()-1
            if p not in basis:basis[p]=row;break
            row^=basis[p]
    return basis
def reduced(row,basis):
    while row:
        p=row.bit_length()-1
        if p not in basis:return row
        row^=basis[p]
    return 0

def evaluate(g,phase,mode):
    c=g['canonical'];frames=c['frames'];nodes=[0,0]+[g['component_frames'][i] for i in range(g['components'])]
    fixed=set(g['main_fixed'])|set(g['zero_fixed'])
    if mode=='main_and_owned':fixed.update(g['owned_fixed'])
    fixed={i+2 for i in fixed};forms=phase.Forms(frames,nodes,fixed);eq=phase.Equalities(forms.count)
    maps={w['op']:w['G_columns'] for w in c['warps']}
    maps.update({-op:phase.inverse(cols) for op,cols in list(maps.items())})
    equations=[];counts=Counter();paid=Counter()
    for e in g['edges']:
        a,b=e['source']+2,e['target']+2;U=tuple(frames[e['source_frame']]);V=tuple(frames[e['target_frame']])
        if e['kind']=='warp':
            image=tuple(phase.mv(maps[e['operator']],x) for x in U)
            need(phase.span(image)==phase.span(V),'Actual shared warp geometry')
        elif e['kind']=='center':
            need(not V and len(U)==8,'Actual owned center 8 to zero');U=();image=()
        else:
            need(phase.span(U)<=phase.span(V),'Actual nested climb');image=U
        if e['old_rank']:paid[e['old_rank']]+=1
        for i,x in enumerate(U):
            for j in range(i,len(U)):
                row=tuple(sorted(set(forms.at(a,x,U[j]))^set(forms.at(b,image[i],image[j]))))
                if row:counts[e['kind']]+=1;equations.append(row);eq.equation(row)
    need(paid==Counter({1:2201,2:412,3:510,4:127,5:40,8:8}),'Original paid profile')
    eq.finish();queries=[];helpers=Counter()
    for h in g['helpers']:
        a,b=h['source']+2,h['target']+2;U=tuple(frames[h['source_frame']]);V=tuple(frames[h['target_frame']])
        need(phase.span(U)<=phase.span(V),'Actual nested helper geometry');helpers[len(V)-len(U)]+=1
        for i,x in enumerate(U):
            for y in U[i:]:
                row=tuple(sorted(set(forms.at(a,x,y))^set(forms.at(b,x,y))))
                if row:queries.append((h['role'],row))
    need(helpers==Counter({4:28,7:7,8:47,9:326}),'Original helper profile')
    simplified=[(r,eq.simplify(row)) for r,row in queries]
    roots=sorted({x for row in eq.pending for x in eq.simplify(row)}|{x for _,row in simplified for x in row})
    pos={x:i for i,x in enumerate(roots)};bits=lambda row:sum(1<<pos[x] for x in row)
    basis=gaussian(bits(eq.simplify(row)) for row in eq.pending)
    useful=[(r,row) for r,row in simplified if reduced(bits(row),basis)]
    witnesses=[]
    if useful:
        for free in range(len(roots)):
            if free in basis:continue
            solution=1<<free
            for pivot,row in sorted(basis.items()):
                if (row&solution).bit_count()%2:solution|=1<<pivot
            if not any((bits(row)&solution).bit_count()%2 for _,row in useful):continue
            active={roots[i] for i in range(len(roots)) if solution>>i&1}
            value=lambda row:sum(eq.root(x) in active for x in row)%2
            need(all(value(row)==0 for row in equations),'Every original equation satisfied')
            support={}
            for n,f in enumerate(nodes):
                if n<2 or n in fixed:continue
                d=len(frames[f]);mask=sum((eq.root(forms.offsets[n]+i) in active)<<i for i in range(d*(d+1)//2))
                if mask:support[n-2]=mask
            gains=[]
            for h in g['helpers']:
                a,b=h['source']+2,h['target']+2;U=tuple(frames[h['source_frame']])
                matrix=[sum(value(set(forms.at(a,x,y))^set(forms.at(b,x,y)))<<j for j,y in enumerate(U)) for x in U]
                gain=len(gaussian(matrix))
                if gain:gains.append(dict(role=h['role'],old_rank=len(frames[h['target_frame']])-len(U),added_rank=gain))
            witnesses.append(dict(forms=support,gains=gains));break
    return dict(mode=mode,components=g['components'],fixed_components=len(fixed),form_coordinates=forms.count,
        equations=dict(counts),remaining_equations=len(eq.pending),residual_classes=len(roots),
        residual_linear_rank=len(basis),helper_queries=len(queries),useful_helper_roles=sorted({r for r,_ in useful}),
        witnesses=witnesses,unchanged_paid=dict(paid),unchanged_base_helpers=dict(helpers))

def main():
    began=time.monotonic();pins=json.loads((HERE/'SOURCES.json').read_text(encoding='utf-8'))
    for row in pins['files']:need(digest(HERE/'sources'/row['copy'])==row['sha256'],'Pinned source '+row['copy'])
    raw=(HERE/'sources/native-word.json.gz').read_bytes();data=gzip.decompress(raw)
    need(sha256(data).hexdigest()==pins['native_canonical_sha256'],'Exact canonical native payload')
    payload=json.loads(data);g=geometry(payload);phase=phase_module()
    results=[evaluate(g,phase,mode) for mode in ['main_and_owned','main_only_owned_relaxed']]
    report=dict(status='EXACT_ACTUAL_CONTACT_FULL_FORM_GATE',script_sha256=digest(__file__),
        sources_sha256=digest(HERE/'SOURCES.json'),actual_components=g['components'],
        original_residences=g['original_residences'],results=results,seconds=time.monotonic()-began,
        scope='Unchanged paid and warp ranks on actual residence graph, inert adapter markers impose no chart freeze. Main fixed in both modes; owned relaxed only in optimistic second mode. Phase witnesses still need native lowering and helper normalizers before admission.')
    (HERE/'FULL-FORM-GATE.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({k:report[k] for k in ['status','actual_components','seconds']}))
    for row in results:print(row['mode'],'variables',row['form_coordinates'],'useful_helpers',row['useful_helper_roles'])
if __name__=='__main__':main()
