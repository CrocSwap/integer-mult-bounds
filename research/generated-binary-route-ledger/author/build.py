"""Emit finite seed certificates and bounded constructor examples."""
from pathlib import Path
from fractions import Fraction as F
from hashlib import sha256
import gzip,json,sys
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import factor_words as fw
def mat(a):return [[F(x) for x in row] for row in a]
def packed(a):return [[str(x) for x in row] for row in a]
def main():
    manifest=json.loads((HERE/'INPUTS.json').read_text())
    for item in manifest['files']:
        fw.need(sha256((HERE/item['path']).read_bytes()).hexdigest()==item['sha256'],'source pin '+item['path'])
    native=json.loads(gzip.decompress((HERE/'retained/native.json.gz').read_bytes()))
    bases=json.loads((HERE/'retained/bases.json').read_text());finite=json.loads((HERE/'retained/ROUTE-CATALOGUE.json').read_text())
    receipt=json.loads((HERE/'retained/EFREE-RESULT.json').read_text());caller=json.loads(gzip.decompress((HERE/'retained/EFREE-CALLER.json.gz').read_bytes()))
    recipes={};seeds=[]
    def seed(label,matrix,source):
        r,stats=fw.euclidean_seed(mat(matrix),label);recipes[label]=r
        seeds.append(dict(label=label,source=source,matrix=packed(matrix),word=list(fw.emit(r)),count=r.count.json(),reducer=stats));return r
    for name,f in sorted(native['frames'].items(),key=lambda kv:int(kv[0])):
        seed('raw/'+name,list(map(list,zip(*(f['B']+f['A'])))),dict(kind='raw_frame',id=int(name),rank=f['dim']))
    bypair={tuple(row['pair']):row for row in bases};refs={}
    for row in finite['routes']:refs.setdefault(row['rank'],tuple(row['reference_pair']))
    for rank,pair in sorted(refs.items()):seed('reference/'+str(rank),bypair[pair]['alternative_basis'],dict(kind='reference_basis',rank=rank,pair=pair))
    for chart in receipt['source']['charts']:seed('port/'+str(chart['port']),chart['basis'],dict(kind='port_basis',port=chart['port'],input_frame=chart['input_frame'],output_frame=chart['output_frame']))
    source_seed_count=len(seeds);relative={};complete={}
    for row in finite['routes']:
        label='relative/'+','.join(map(str,row['pair']));r=fw.literal(8,[fw.invert_op(op) for op in reversed(row['elimination_word'])],label);relative[tuple(row['pair'])]=r
        complete[tuple(row['pair'])]=fw.Tagged(fw.multiply(r,recipes['reference/'+str(row['rank'])]),row['rank'])
    control=seed('control/nonorthogonal',[[1,F(1,2)],[0,1]],dict(kind='control'))
    diagonal=seed('control/diagonal',[[2,0],[0,F(1,2)]],dict(kind='control'))
    seed('control/short_repair_failure',[[7,17],[2,5]],dict(kind='control'))
    cases=[]
    def case(label,r,expected):
        word=list(fw.emit(r));fw.need(fw.recount(word)==r.count,'constructor count mismatch '+label)
        fw.need(fw.recount(fw.emit(r,True))==r.count,'inverse count mismatch '+label)
        cases.append(dict(label=label,n=r.n,recipe=r.json(),expected=expected,word=word,inverse_word=list(fw.emit(r,True)),ordered_word=list(fw.expanded_ordered_ops(r)),count=r.count.json(),physical_per_direction=r.count.physical(r.n)))
    for label in ('control/nonorthogonal','control/diagonal','control/short_repair_failure'):case(label,recipes[label],dict(kind='seed',label=label))
    p=complete[(11,266)];q=complete[(2,270)];s=relative[(11,266)]
    bp=dict(kind='basis',pair=[11,266]);sr=dict(kind='relative',pair=[11,266]);a=dict(kind='seed',label='control/nonorthogonal');b=dict(kind='seed',label='control/diagonal')
    case('actual_relative',s,sr);case('actual_complete_basis',p.basis,bp);case('matched_complete',fw.matcher(p,q),sr)
    case('noncommuting_product',fw.multiply(control,diagonal),dict(kind='multiply',children=[a,b]))
    case('noncommuting_inverse',fw.inverse(fw.multiply(control,diagonal)),dict(kind='inverse',child=dict(kind='multiply',children=[a,b])))
    case('source_direct_sum',fw.direct_sum(p.basis,control),dict(kind='direct_sum',children=[bp,a]))
    case('source_tensor',fw.tensor(p.basis,control),dict(kind='tensor',children=[bp,a]))
    case('identity_extension',fw.extend(s,13),dict(kind='extend',n=13,child=sr))
    order=[3,0,7,1,6,2,5,4];case('complete_permutation',fw.permutation(order),dict(kind='permutation',order=order))
    case('changed_basis',fw.conjugate(control,diagonal),dict(kind='conjugate',children=[a,b]))
    case('nonorthogonal_guard',fw.guarded(s,control,1),dict(kind='guard',children=[sr,a],rank=1))
    case('zero_sector_guard',fw.guarded(diagonal,control,0),dict(kind='guard',children=[b,a],rank=0))
    case('full_sector_guard',fw.guarded(diagonal,control,2),dict(kind='guard',children=[b,a],rank=2))
    t=fw.Tagged(control,1)
    summed=fw.tagged_sum(p,t);case('image_first_direct_sum',summed.basis,dict(kind='tagged_sum_basis',children=[bp,a],ranks=[p.rank,1]))
    tensored=fw.tagged_tensor(p,t);case('image_first_tensor',tensored.basis,dict(kind='tagged_tensor_basis',children=[bp,a],ranks=[p.rank,1]))
    selected=[2,0];split=fw.split(p,selected);case('ordered_image_split',split.basis,dict(kind='split_basis',child=bp,selected=selected,rank=p.rank))
    axes=[12,0,9,3,11,1,7,4];placed=fw.placed(p,axes,14);case('whole_coordinate_placement',placed.basis,dict(kind='placed_basis',child=bp,axes=axes,n=14))
    case('two_stage_guard',fw.guarded(fw.guarded(diagonal,control,1),control,1),dict(kind='guard',children=[dict(kind='guard',children=[b,a],rank=1),a],rank=1))
    # Source coupled-port route: preserve the actual U_i and the full seven-axis swap.
    for port in (0,17,53,110):
        u=fw.extend(recipes['port/'+str(port)],15);order=[0,*range(8,15),*range(1,8)]
        route=fw.conjugate(u,fw.permutation(order))
        case('actual_port/'+str(port),route,dict(kind='port_route',port=port))
    # Count every original U_i stage route and every caller target basis without
    # replacing a 134-dimensional route by its 15-dimensional test block.
    stage_counts=[]
    for port in range(111):
        c=recipes['port/'+str(port)].count*2+fw.Count(swaps=7)
        stage_counts.append(dict(port=port,per_stage_count=c.json(),physical_per_direction_134=c.physical(134)))
    target_counts=[]
    for port in range(111):
        for index,target in enumerate(caller['diagonal']):
            active=([0] if target['q'] else [])+[8+7*(j-1)+k for j in target['stages'] for k in range(7)]
            order=active+[j for j in range(134) if j not in set(active)]
            c=recipes['port/'+str(port)].count+fw.permutation(order).count
            target_counts.append(dict(port=port,target=index,rank=len(active),count=c.json()))
    fw.need(source_seed_count==755 and len(caller['diagonal'])==38 and len(target_counts)==4218,'complete primitive seed/caller inventory')
    derived=[]
    for pair,p in complete.items():derived.append(dict(pair=pair,rank=p.rank,word=list(fw.emit(p.basis)),count=p.basis.count.json()))
    additions=set();scalings=set()
    source_words=[row['word'] for row in seeds[:source_seed_count]]+[list(fw.emit(r)) for r in relative.values()]
    for word in source_words:
        for op in word:
            if op[0]=='add':additions.update((str(F(op[3])),str(-F(op[3]))))
            elif op[0]=='scale':scalings.update((str(F(op[2])),str(1/F(op[2]))))
    artifacts={'SEEDS.json':dict(schema='generated-route-ledger-seeds/1',source_seed_count=source_seed_count,seeds=seeds),'DERIVED-BASES.json':derived,'CASES.json':cases,'CALLER-LEDGER.json':dict(distinct_stage_symbols=111*18,directed_raw_port_occurrences=4*111*36,stage_counts=stage_counts,target_counts=target_counts),'ALPHABET.json':dict(addition_coefficients=sorted(additions,key=F),scale_coefficients=sorted(scalings,key=F),scope='linear elementary words only; low-controlled representative carries have their own coefficients and preparation cost')}
    for filename,data in artifacts.items():(HERE/filename).write_text(json.dumps(data,indent=2)+'\n')
    summary=dict(status='PASS_GENERATED_ROUTE_PRODUCTION',source_seeds=source_seed_count,raw_frames=636,rank_references=len(refs),coupled_port_bases=111,derived_complete_bases=len(derived),bounded_constructor_cases=len(cases),stage_symbols=111*18,caller_target_bases=len(target_counts),addition_alphabet=len(additions),scale_alphabet=len(scalings),files={name:sha256((HERE/name).read_bytes()).hexdigest() for name in artifacts})
    (HERE/'PRODUCTION.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps(summary,sort_keys=True))
if __name__=='__main__':main()
