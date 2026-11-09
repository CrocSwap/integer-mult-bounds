"""Exact proposed-source convention, finite family and typed binder checks.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
import ast,json
from collections import Counter
from copy import deepcopy
from dataclasses import replace
from hashlib import sha256
from types import SimpleNamespace
from port_sources import HERE,authenticate,activate,base,provider_class,load,need

B=base();S=activate();C=S.catalog
cert=load('proposal6936_certificate',Path(B.catalog.__file__).parent/'clifford_certificate.py')
V=load('proposal6936_semantics',HERE/'vendor/proposal/native_verify.py')

def digest(value):return sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def admit_record(record):
    """All literal shape obligations of the unchanged physical recipe."""
    need(type(record['rank']) is int and 1<=record['rank']<=8,'positive typed recipe rank')
    for name in ('right','left'):
        literal=record[name];rows=literal['matrix_rows'];quad=literal['quadratic_rows'];linear=literal['linear_Z4']
        need(len(rows)==len(quad)==len(linear)==9 and
             all(type(x) is int and 0<=x<512 for x in (*rows,*quad)) and
             all(type(x) is int and 0<=x<4 for x in linear),'full nine-axis finite recipe')
        need(all(((quad[i]>>j)&1)==((quad[j]>>i)&1) for i in range(9) for j in range(9))
             and all(linear[i]%2==((quad[i]>>i)&1) for i in range(9)),'unit quadratic phase parity')
        need(type(literal['offset']) is int and 0<=literal['offset']<512 and
             type(literal['phase']) is int and 0<=literal['phase']<4,'typed finite affine phase')
        cert.inverse(rows)
        actual=B.common.monomial.S.engine.Recipe(literal,tuple('v'+str(i) for i in range(9)))
        need(actual.matrix==tuple(rows) and actual.constant==literal['phase'],
             'unchanged actual physical recipe constructor admits this chart')

def convention():
    # The upstream #6936 checker explicitly calls these files and this order.
    # Exact copies prove more than equality of the frame label tables.
    original=Path(C.S.clifford.__file__)
    need(original.read_bytes()==(HERE/'vendor/proposal/clifford_exact.py').read_bytes(),
         'exact actual proposed Clifford compiler byte identity')
    old_v=Path(B.catalog.S.selected)/'native_verify.py'
    need(old_v.read_bytes()==(HERE/'vendor/proposal/native_verify.py').read_bytes(),
         'exact actual proposed independent native convention byte identity')
    word=C.catalog()[0];frames=[]
    for i,basis in enumerate(word['frames']):
        left=C.frame(i).circuit;right=V.frame(basis,9)
        need(digest(left)==digest(right),'literal canonical frame circuit and absolute convention')
        frames.append(digest(right))
    native=(HERE/'vendor/proposal/native.py').read_text()
    need('C.lower_child(chart(a).adjoint().then(chart(b)))' in native
         and "V.adjoint(V.frame(w['frames'][a],9)) + V.frame(w['frames'][b],9)" in native,
         'upstream actual source operator order')
    return dict(frames=len(frames),frame_circuit_sha256=digest(frames),
                compiler_and_verifier_exact_bytes=True,operator='T_b T_a^-1',
                selected_word_equality_claim=False)

def controls():
    word,entries,pairs,_report=C.catalog();triple=next(t for t in entries.values() if t[1].rank==2)
    event=triple[1];rank1=next(t[1] for t in entries.values() if t[1].rank==1)
    old_event=next(iter(B.catalog.catalog()[1].values()))[1]
    raw=event.token[3];as_int=tuple(int(x) if type(x) is bool else x for x in raw)
    wrong=[replace(event,rank=True),replace(event,rank=1),replace(rank1,rank=True),
           replace(event,fields=(event.fields[0]+1,)),replace(event,op='SERVICE'),
           replace(event,token=(C.NAMESPACE,C.WORD_SHA,True,raw)),
           replace(event,token=(C.NAMESPACE,C.WORD_SHA,event.token[2],as_int)),
           replace(event,token=(C.NAMESPACE,'0'*64,event.token[2],raw)),
           replace(event,token=('local',event.token[2],raw)),old_event,
           replace(event,token=('caller-local',0,event.token))]
    for bad in wrong:
        try:C.bind_paid(bad)
        except (ValueError,TypeError):pass
        else:raise ValueError('wrong word/owner/type/rank token accepted')
    for bad in ((triple[2],triple[1],triple[0]),triple[:2]):
        try:C.bind_move(bad)
        except ValueError:pass
        else:raise ValueError('wrong chronology accepted')
    selected=(B.catalog.S.selected/'WORD.json.gz').read_bytes()
    for raw_bytes in (selected,(HERE/'data/word.json.gz').read_bytes()+b' '):
        try:C.checked_word(raw_bytes)
        except ValueError:pass
        else:raise ValueError('unbound source bytes accepted')
    original,record=C.chart(word['program'][event.token[2]][2],word['program'][event.token[2]][3])
    wrong_phase=deepcopy(record);wrong_phase['left']['phase']=(wrong_phase['left']['phase']+1)%4
    wrong_z=deepcopy(record)
    z=list(wrong_z['right']['linear_Z4']);z[0]=(z[0]+2)%4;wrong_z['right']['linear_Z4']=z
    wrong_rank=deepcopy(record);wrong_rank['rank']=1
    need(cert.generators(original.circuit)==cert.generators(cert.lowered_circuit(wrong_phase)),
         'Pauli-only certificate cannot see global phase')
    need(cert.zero_column(original.circuit)==cert.zero_column(cert.lowered_circuit(wrong_z)),
         'single-column certificate cannot see input Z')
    for bad in (wrong_phase,wrong_z,wrong_rank):
        try:cert.certify(original,bad)
        except ValueError:pass
        else:raise ValueError('bad absolute-phase/Pauli/rank certificate accepted')
    # The scan is deliberately distinct from source authentication. These
    # malformed shapes must fail even if supplied as already-decoded data.
    mutants=[]
    first_init=next(i for i,row in enumerate(word['program']) if row[0]=='INIT')
    first_clear=next(i for i,row in enumerate(word['program']) if row[0]=='CLEAR')
    for mode in ('alias','missing-clear','wrong-frame','boolean-flag'):
        mutant=deepcopy(word)
        if mode=='alias':mutant['program'][first_init][1]=0
        elif mode=='missing-clear':mutant['program'].pop(first_clear)
        elif mode=='wrong-frame':mutant['program'][event.token[2]][2]=(raw[2]+1)%len(word['frames'])
        else:mutant['program'][event.token[2]][4]=int(mutant['program'][event.token[2]][4])
        try:C.source_scan(mutant)
        except ValueError:mutants.append(mode)
        else:raise ValueError('bad source lifetime accepted: '+mode)
    return dict(typed_token_rejections=len(wrong),chronology_rejections=2,wrong_word_rejections=2,
                factorization_rejections=3,lifetime_rejections=mutants,
                Pauli_only_misses_phase=True,column_only_misses_input_Z=True)

def catalog_check(progress=None):
    convention_result=convention();word,entries,pairs,report=C.catalog();rows=[];ranks=Counter()
    for i,(a,b) in enumerate(pairs,1):
        original,record=C.chart(a,b);admit_record(record);paulis,column=cert.certify(original,record)
        # Independent native expected order is authenticated and literal.
        expected=V.adjoint(V.frame(word['frames'][a],9))+V.frame(word['frames'][b],9)
        need(digest(original.circuit)==digest(expected),'actual proposed expected chronological operator')
        ranks[record['rank']]+=1;rows.append([a,b,record['rank'],digest(record),digest(paulis),digest(column)])
        if progress and (i%128==0 or i==len(pairs)):
            progress.write_text(json.dumps(dict(complete=i,total=len(pairs),remaining=len(pairs)-i))+'\n')
    for triple in entries.values():C.bind_move(triple)
    return dict(source=report,convention=convention_result,certificates=rows,
                chart_rank_counts=dict(sorted(ranks.items())),Pauli_images=18*len(rows),
                absolute_column_positions=512*len(rows),all_typed_occurrences_bound=len(entries),
                controls=controls(),numerical_whole_MOVE=False,no_new_kappa=True)

def bindings_check():
    from ordinary import Ordinary
    from macro_code import Code
    from check_rounded import Tape
    def factory():
        return Ordinary(2,SimpleNamespace(codes=SimpleNamespace(q=2)),SimpleNamespace(families=0),
                        (Code((("unreachable",),),0),),capacity=64)
    cls=provider_class();api=load('proposal6936_public_api',HERE/'rounded_move.py')
    need(api.RoundedMove is cls,'actual exported public provider class')
    bound=[]
    for rank in range(1,9):
        triple=next(t for t in C.catalog()[1].values() if t[1].rank==rank)
        provider=cls(triple,factory);work=[Tape(3+j%5) for j in range(provider.port_count)]
        field,header=Tape(7),Tape(9);provider.bind(work,{provider.owner:S.abi.CodedPort(field)},S.abi.BinaryContextPort(header))
        need(field.actions()==0 and header.actions()==0,'fixed source binding does not inspect numerical input or header')
        need(provider.rank==rank and provider.port_count==4368 and provider.owner==triple[1].fields[0],
             'actual proposed source constructor and owner binding')
        need(provider.child.engine.field.tape is provider.expanded.tape
             and provider.child.engine.context.tape is provider.wide_context.tape
             and provider.child.engine.child.view.__class__ is B.prior.cutoff.CutoffView,
             'same expanded field/header and LEAF-private cutoff child')
        bound.append(dict(rank=rank,pc=triple[1].token[2],owner=provider.owner,ports=provider.port_count))
    # Compare the complete AST after removing only the declared import line.
    import_checks=[]
    for path,old,new in (
        (HERE/'vendor/rounded-source/vendor/direct/direct_move.py','from direct_sources import activate, need','from port_sources import direct_activate as activate, need'),
        (HERE/'vendor/rounded-source/rounded_move.py','from rounded_move_sources import activate,need','from port_sources import activate,need')):
        before=path.read_text();need(before.count(old)==1,'one exact import rewrite');after=before.replace(old,new)
        def body(text):
            tree=ast.parse(text);tree.body=[n for n in tree.body if not (isinstance(n,ast.ImportFrom) and n.module in ('direct_sources','rounded_move_sources','port_sources'))]
            return ast.dump(tree,include_attributes=False)
        need(body(before)==body(after),'all computational AST bodies remain exact')
        import_checks.append(dict(path=str(path.relative_to(HERE)),before_sha256=sha256(before.encode()).hexdigest(),after_sha256=sha256(after.encode()).hexdigest(),only_import_changed=True))
    need(S.direct.S.catalog is C and B.direct.S.catalog is B.catalog and S.catalog is not B.catalog,
         'isolated new catalogue does not mutate selected source objects')
    return dict(retained_files=authenticate(),ranks_bound=bound,import_checks=import_checks,
                source_controls=controls(),old_catalogue_unchanged=True,physical_input_read=False,
                numerical_whole_MOVE=False,no_new_kappa=True)

if __name__=='__main__':
    from argparse import ArgumentParser
    p=ArgumentParser();p.add_argument('--suite',choices=('catalog','bindings'),required=True)
    p.add_argument('--emit',action='store_true');p.add_argument('--progress',type=Path);args=p.parse_args()
    result=catalog_check(args.progress) if args.suite=='catalog' else bindings_check()
    file=HERE/(args.suite.upper()+'-RESULT.json')
    if args.emit:file.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(digest(result)==digest(json.loads(file.read_text())),'exact proposed-source replay receipt')
    print('PASS_6936_ROUNDED_MOVE_'+args.suite.upper(),json.dumps(dict(new_kappa=False,numerical_whole_MOVE=False,
        raw_moves=6323,charts=2961,ports=4368),sort_keys=True))
