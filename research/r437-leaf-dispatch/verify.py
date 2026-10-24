#!/usr/bin/env python3
"""Root-produced child to actual leaf dispatcher: metadata chronology audit.

Setup/bind/handoff/ingress derived from PR4732/4741; no full payload execution.

Brian, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import ast
from hashlib import sha256
from fractions import Fraction
from dataclasses import replace
import json
from pathlib import Path
import shutil
import sys
from tempfile import TemporaryDirectory
from types import SimpleNamespace as NS

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]

def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return sha256(data).hexdigest()


def integer_receipt(value):
    return {'bits': value.bit_length(), 'sha256': digest(value.to_bytes(max(1, (value.bit_length()+7)//8), 'big'))}


def authenticate():
    manifest = json.loads((HERE/'SOURCES.json').read_text())
    for row in manifest['files']:
        if row['usage'] == 'input':
            path = ROOT/row['path']
            require(path.is_file() and not path.is_symlink(), 'regular input '+row['path'])
            require(digest(path.read_bytes()) == row['sha256'], 'source hash '+row['path'])
    for row in manifest['retained']:
        require(digest((HERE/row['path']).read_bytes()) == row['sha256'], 'retained bytes '+row['path'])
    return len([r for r in manifest['files'] if r['usage']=='input'])


def bind(root, source, observed):
    """Checker for this one good-child witness; not installed runtime admission."""
    require(observed['source_identity'] == source['identity'], 'source identity')
    require(observed['request_key'] == source['key'], 'caller request key')
    require(observed['source_code'] == source['code'], 'literal source code')
    require((observed['q'], observed['w'], observed['modulus']) == (root.q, root.w, root.q**root.w),
            'actual root field and precision')
    require(observed['root_width'] == root.width and observed['root_depth'] == 0, 'original root Program')
    require(observed['runtime_width'] == root.width and observed['runtime_depth'] == 0, 'original root runtime')
    require(observed['root_rows'] == root.rows, 'authenticated root rows')
    require(observed['root_unit'] == source['root_unit'], 'authenticated root unit')
    require(observed['child_root'] == (root.width, source['root_unit'], 1), 'preserved root and chronological depth')
    require(observed['step_metadata'] == (0, source['code'], source['rank'], 0, 0, 0), 'produced chronological STEP')
    require(observed['step_parent'] == root.width, 'STEP parent width')
    width = source['rank']*(root.width//64)
    require(observed['step_width'] == observed['event_width'] == observed['grant_width'] == width,
            'event, STEP and grant widths agree')
    require(observed['event_depth'] == observed['grant_depth'] == 1, 'event and grant depth agree')
    require(observed['grant_modulus'] == root.q**root.w, 'inherited modulus')
    require(observed['handed_rows'] == observed['unused_rows'], 'rows port carries unused quotient')
    child = Node(width, observed['handed_rows'], observed['q'], observed['w'])
    return certify_path(root, [root, child])


def run(probe=False):
    inputs = authenticate()
    global Node, certify_path, row_factor, stock_divisor
    sys.path.insert(0, str(HERE/'retained'))
    from stock import Node, certify_path, row_factor, stock_divisor
    sys.path.insert(0, str(ROOT/'research/selected-bit-physical-caller'))
    import loader
    # The frozen runtime accepts its historical complete selected record only.
    with TemporaryDirectory(prefix='r437-stock-source-') as temporary:
        projection = Path(temporary)
        for row in json.loads((loader.CALLER/'SOURCES.json').read_text())['files']:
            if row['usage'] != 'input':
                continue
            target = projection/row['path']
            target.parent.mkdir(parents=True, exist_ok=True)
            source = HERE/'retained/selected-result.json' if row['path']=='certificates/selected-result.json' else ROOT/row['path']
            shutil.copyfile(source, target)
        loader.REPOSITORY = projection
        loader.compatibility_controls()
        sys.path.insert(0, str(ROOT/'research/r437-carrier-integration'))
        import physical, admission
        cat,top=physical.compiler.load('D',7)
        from catalogue import Specifications
        import oracle
        record=physical.compiler.early_source87(cat,top,0)
        low=tuple(map(tuple,oracle.inverse(oracle.reduce_rational(cat.template_for(record['identifier'],True).preparation,7),7)))
        specs=Specifications(cat);handle=physical.compiler.source_handle(cat,record['identifier'],True,low)
        spec=physical.compiler.resolve_handle(cat,specs,handle)
        s=NS(cat=cat,top=top,record=record,low=low,specs=specs,handle=handle,spec=spec,plan=specs.plan(handle.code))
        import words, records, directory, macro_binding, macro_machine, numeric, layout, residual_blocks, packet
        from cardinal_counts import Count
        ia, ra = words.Arena(13, 1024), words.Arena(4, 131072)
        ring = words.Ring(ra.literal(7))
        program = records.Program.fixture(ia, ra, 2048, 2, (), s.cat.codes.bits)
        old_fields = records.Fields.fixture(ia, ra, [], s.cat.codes.bits)
        context = directory.Context(ring, s.cat.codes)
        size, depth, columns = ia.literal(2048), ia.literal(0), ia.literal(32)
        rows = admission.numerical.stock_unit(7, 1)**admission.numerical.depth(2048)
        domain = admission.RootDomain(2048, 2048, 1, 0, 4, 13, s.cat.codes.bits, rows)
        root = Node(2048, rows, 7, 1)
        source = {'identity':s.cat.source_identity, 'key':s.handle.request_key,
                  'code':s.handle.code, 'rank':s.spec.template.rank, 'root_unit':2}
        rejected = []

        def reject(name, fn):
            try:
                fn()
            except (ValueError, KeyError):
                rejected.append(name)
            else:
                raise ValueError('control accepted: '+name)

        def count_view(tape):
            out = object.__new__(Count); out.tape = tape
            return out

        binding = macro_binding.SelectedBinding(s.specs)
        roles = {label:records.Tape() for label in ('current','directory','prefixes','rows','unused','before')}
        roles['rows'], roles['before'] = Count.literal(rows).tape, Count.literal(1).tape
        runtime = NS(indices=ia, arena=ra, context=context, program=program, size=size, depth=depth,
                     binding=binding, topology=s.top, handoff={label:records.Tape() for label in macro_machine.CAPSULE},
                     tape=lambda label:roles[label], count=lambda label:count_view(roles[label]))
        runtime.commit = lambda result,label:macro_machine.Machine.commit(runtime,result,label)
        runtime.save_count = lambda value,label:macro_machine.Machine.save_count(runtime,value,label)
        definition = NS(code=s.handle.code, plan=s.plan)
        page = numeric.Geometry(s.plan, ia, columns, depth, s.handle.code, program)
        trace = residual_blocks.events(page, ('good', 1, 0))
        event = next(trace)
        field_count = ia.literal(1)
        geometry = layout.Layout(page, size, ring, 7, Count.literal(1), Count.literal(1), Count.literal(1))
        powers, extent_method = physical.shared_geometry()
        geometry.child_extents = lambda first,second,width,before:extent_method(geometry,first,second,width,before=before)

        def handoff(used_event):
            for tape in runtime.handoff.values():
                tape.clear()
            saved = {name:(bytes(tape.cells), tape.head) for name,tape in roles.items()}
            saved_program = bytes(program.tape.cells), program.tape.head
            live = set(ia.live), set(ra.live)
            old_inspect = words.Word.inspect
            words.Word.inspect = lambda _self:(_ for _ in ()).throw(ValueError('runtime Word decoding forbidden'))
            try:
                grants = macro_machine.Machine.prepare_child(runtime, definition, used_event, geometry, field_count)
            finally:
                words.Word.inspect = old_inspect
            require(all((bytes(roles[name].cells), roles[name].head)==value for name,value in saved.items()),
                    'prepare_child preserves parent tapes and heads')
            require((bytes(program.tape.cells), program.tape.head)==saved_program, 'parent Program preserved')
            child = macro_binding.view(records.Program, runtime, runtime.handoff['program'])
            root_words = program.root(); child_words = child.root()
            level = ia.literal(1)
            metadata, parent, width = child.step(level)
            observed = {
                'source_identity':s.handle.identity, 'request_key':s.handle.request_key, 'source_code':definition.code,
                'q':context.q, 'w':domain.w, 'modulus':ring.modulus.inspect(),
                'root_width':root_words[0].inspect(), 'root_unit':root_words[1].inspect(), 'root_depth':root_words[2].inspect(),
                'runtime_width':size.inspect(), 'runtime_depth':depth.inspect(),
                'root_rows':physical.count_value(runtime.count('rows')),
                'child_root':tuple(word.inspect() for word in child_words),
                'step_metadata':metadata, 'step_parent':parent.inspect(), 'step_width':width.inspect(),
                'event_width':used_event.width.inspect(), 'event_depth':used_event.depth.inspect(),
                'grant_modulus':grants[0].inspect(), 'grant_width':grants[1].inspect(), 'grant_depth':grants[2].inspect(),
                'unused_rows':physical.count_value(runtime.count('unused')),
                'handed_rows':physical.count_value(count_view(runtime.handoff['rows']))}
            ia.free_many(root_words[0], root_words[2], child_words[0], child_words[2], level, parent, width)
            ra.free_many(root_words[1], child_words[1])
            runtime.grants = grants
            require((set(ia.live)-{grants[1].slot,grants[2].slot},set(ra.live)-{grants[0].slot})==live, 'handoff owns only declared grant words')
            return observed

        reached = []
        def continuation():
            reached.append(True)
            old_count = Count.literal(1)
            produced, prefixes = directory.produce(old_fields.tape, depth, old_count, s.handle.code, context)
            old_count.close()
            roles['directory'], roles['prefixes'] = produced, prefixes.tape
            expected = records.Fields.fixture(ia, ra, [(s.handle.code, [[0]*64 for _ in range(64)])], s.cat.codes.bits)
            require(bytes(produced.cells)==bytes(expected.tape.cells), 'literal current-prefix production at w=1')
            expected.tape.clear()
            # Execute exactly the unchanged quotient/save/guard block with real Count tapes.
            tree = ast.parse(Path(macro_machine.__file__).read_text())
            machine = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name=='Machine')
            node = next(n for n in machine.body if isinstance(n, ast.FunctionDef) and n.name=='node')
            start = next(i for i,n in enumerate(node.body) if isinstance(n, ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id=='unused')
            block = node.body[start:start+4]
            require([type(n).__name__ for n in block]==['Assign','Expr','Assign','Try'], 'literal quotient block shape')
            exec(compile(ast.Module(body=block,type_ignores=[]),str(macro_machine.__file__),'exec'),dict(vars(macro_machine),self=runtime))
            observed = handoff(event)
            certificate = bind(root, source, observed)
            require(observed['unused_rows'] == rows//row_factor(7,1), 'independent row factor')
            return observed, certificate

        (observed, certificate), entry = admission.checked_entry(s.cat,s.specs,s.handle,domain,continuation,
            mode='semantic', expected_key=s.handle.request_key, expected_common=True)
        require(len(reached)==1 and entry['numerical_admitted'] is False, 'one guarded semantic continuation')
        # The predecessor ends here. Everything below executes the child ingress.
        factor = row_factor(7, 1)
        prep=[[Fraction(x).numerator*pow(Fraction(x).denominator,-1,7)%7 for x in row] for row in s.spec.template.preparation]
        require(all(sum(s.spec.low[i][k]*prep[k][j] for k in range(64))%7==int(i==j)
                    for i in range(64) for j in range(64)), 'independent low times preparation is identity modulo7')
        require(observed['handed_rows'] == rows//factor, 'original row port')
        capsule = runtime.handoff
        capsule_bytes = {name:bytes(tape.cells) for name,tape in capsule.items()}

        tree = ast.parse(Path(macro_machine.__file__).read_text())
        machine = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name=='Machine')
        node = next(n for n in machine.body if isinstance(n, ast.FunctionDef) and n.name=='node')
        start = next(i for i,n in enumerate(node.body) if isinstance(n, ast.Assign) and isinstance(n.targets[0],ast.Name) and n.targets[0].id=='unused')
        prefix = node.body[:start+4]
        require(isinstance(prefix[-1], ast.Try) and len(prefix[-1].finalbody)==1,
                'ingress ends at exact stock guard finally')
        require(ast.unparse(prefix[-1].finalbody[0]) == 'stock.close()', 'stock boundary')
        code = compile(ast.Module(body=prefix,type_ignores=[]), str(macro_machine.__file__), 'exec')

        def clone_tape(original):
            copied=records.Tape(); directory.append_tape(original,copied); copied.rewind(); return copied

        def child_runtime(changes=None, grants=None):
            child_roles={name:clone_tape(tape) for name,tape in capsule.items()}
            child_roles.update(unused=records.Tape(),highs=records.Tape())
            child=NS(indices=ia, arena=ra, binding=binding, topology=s.top,
                     tape=lambda label:child_roles[label], count=lambda label:count_view(child_roles[label]))
            child.commit=lambda value,label:macro_machine.Machine.commit(child,value,label)
            child.save_count=lambda value,label:macro_machine.Machine.save_count(child,value,label)
            if changes:
                for name,tape in changes.items():
                    child_roles[name].clear(); child_roles[name]=clone_tape(tape)
            if grants is None: grants=(ra.literal(7),ia.literal(64),ia.literal(1))
            macro_machine.Machine.new_context(child,*grants)
            return child,child_roles

        def dispose(child,child_roles):
            child.context.close()
            child.context.ring.close()
            ra.free(child.context.ring.modulus)
            ia.free_many(child.size,child.depth)
            for tape in child_roles.values(): tape.clear()

        def run_ingress(child):
            values=[]
            original=macro_binding.SelectedBinding.incoming
            old_inspect=words.Word.inspect
            def observed_incoming(runtime):
                receiver=original(binding,runtime)
                def coefficient(fields,request):
                    value=receiver.coefficient(fields,request)
                    values.append(old_inspect(value))  # observer only, never fed to runtime
                    return value
                return NS(coefficient=coefficient)
            binding.incoming=observed_incoming
            words.Word.inspect=lambda _self:(_ for _ in ()).throw(ValueError('runtime Word decoding forbidden'))
            try: exec(code,dict(vars(macro_machine),self=child))
            finally:
                words.Word.inspect=old_inspect
                del binding.incoming
            return values

        child,child_roles=child_runtime(grants=runtime.grants)
        count_labels=('old_count','rows','before','gap','suffix')
        before={name:(bytes(child_roles[name].cells),child_roles[name].head) for name in capsule}
        count_values={name:physical.count_value(child.count(name)) for name in count_labels}
        live=(set(ia.live),set(ra.live))
        values=run_ingress(child)
        require(values==[2], 'identity preparation pivots preserve inherited root unit2')
        unused=physical.count_value(child.count('unused'))
        require(physical.count_value(child.count('rows'))==rows//factor and unused==rows//factor**2,
                'actual child ingress and exact second local quotient')
        require(unused%9475==0, 'child local stock guard')
        require((set(ia.live),set(ra.live))==live,'ingress numerical ownership restored')
        normalized=[name for name in count_labels if bytes(child_roles[name].cells)!=before[name][0]]
        require(normalized==['before','gap','suffix'], 'exact padded Count normalizations')
        require(all(physical.count_value(child.count(name))==value for name,value in count_values.items()),
                'all inherited Count values preserved')
        require(all((bytes(child_roles[name].cells),child_roles[name].head)==saved
                    for name,saved in before.items() if name not in count_labels),
                'non-Count capsule bytes and heads preserved')
        require(all(child_roles[name].head==before[name][1] for name in count_labels),'Count heads preserved')
        # The inherited row identity is a correspondence check, not a guard installed in the caller.
        def anchor_rows(candidate):
            require(candidate==observed['handed_rows'], 'authenticated inherited row port')
        reject('doubled_rows_break_parent_correspondence',lambda:anchor_rows(2*observed['handed_rows']))
        positive={'coefficient':values[0],'rows':integer_receipt(observed['handed_rows']),
                  'unused':integer_receipt(unused),'source_payload_symbols':len(capsule_bytes['source'])-1,
                  'program_sha256':digest(capsule_bytes['program']),
                  'old_directory_sha256':digest(capsule_bytes['old_directory']),
                  'non_count_capsule_bytes_and_heads_preserved':True,'inherited_count_values_and_heads_preserved':True,
                  'counts_normalized':normalized,'numerical_live_set_restored':True}
        # New task begins at the actual next below-cutoff block. Full payload is not built.
        import children,stream,fresh_rows
        from plan import Request
        stock_before={name:physical.count_value(child.count(name)) for name in count_labels}
        next_directory,next_prefixes=directory.produce(child_roles['old_directory'],child.depth,child.count('old_count'),s.handle.code,child.context)
        child_roles['directory'],child_roles['prefixes']=next_directory,next_prefixes.tape
        child_roles['current']=records.Tape()
        child_roles['leading']=Count.product(child.count('unused'),child.count('before')).tape
        child.geometry_state=None
        child.geometry=lambda definition:macro_machine.Machine.geometry(child,definition)
        child.close_geometry=lambda:macro_machine.Machine.close_geometry(child)
        child.prepare_child=lambda *args:(_ for _ in ()).throw(ValueError('leaf must not prepare internal capsule'))
        child.call=lambda *args:(_ for _ in ()).throw(ValueError('leaf must not dispatch internal call'))
        # Authenticate the literal split/merge request multiplicity; payload loops remain unexecuted.
        stree=ast.parse(Path(stream.__file__).read_text())
        add_pass=next(n for n in stree.body if isinstance(n,ast.FunctionDef) and n.name=='add_pass')
        traverse_calls=[n for n in add_pass.body if isinstance(n,ast.Expr) and isinstance(n.value,ast.Call)
                        and isinstance(n.value.func,ast.Name) and n.value.func.id=='traverse']
        require([ast.literal_eval(n.value.args[0]) for n in traverse_calls]==[False,True],'literal split and merge visits')
        nested=next(n for n in add_pass.body if isinstance(n,ast.FunctionDef) and n.name=='traverse')
        require(sum(isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='prepare_coefficient' for n in ast.walk(nested))==1,
                'one preparation per split or merge traversal')
        require(ast.dump(nested.body[0])==ast.dump(ast.parse('coefficient = prepare_coefficient()').body[0]),
                'preparation starts traversal before payload loops')
        programs=[];requests=[];events=[];failures=[]
        real_extend=children.extend
        class ProbeComplete(Exception):pass
        mutate_step=[False]
        def observe_extend(frame,request):
            extended=real_extend(frame,request)
            root_words=extended.root();level=ia.literal(2)
            metadata,parent,width=extended.step(level)
            observed_program={'root':tuple(x.inspect() for x in root_words),'metadata':metadata,
                              'parent':parent.inspect(),'width':width.inspect(),'sha256':digest(bytes(extended.tape.cells))}
            require(observed_program['root']==(2048,2,2) and metadata==(0,s.handle.code,2,0,0,0)
                    and observed_program['parent']==64 and observed_program['width']==2,'actual chronological second STEP')
            ia.free_many(root_words[0],root_words[2],level,parent,width);ra.free(root_words[1])
            if mutate_step[0]:
                positions=[i for i,v in enumerate(extended.tape.cells) if v==records.STEP]
                at=positions[-1]+1+(records.FINITE_BITS+1)+(s.cat.codes.bits+1)
                extended.tape.cells[at]=1
            real_clear=extended.tape.clear
            def clear():
                real_clear()
                require(extended.tape.head==1 and all(v==words.BLANK for v in extended.tape.cells[1:]),'temporary Program erased')
                observed_program['erased']=True
            extended.tape.clear=clear
            programs.append(observed_program)
            return extended
        children.extend=observe_extend
        saved_run=macro_machine.packet_engine.run
        saved_quotient=fresh_rows.quotient
        current_field_count=[None]
        captured_coefficient=[None]
        def boundary_observer(payload,trace,layout,fields,prefixes,field_count,coefficient):
            # Explicit metadata observer replacing the entire unexecuted packet interpreter.
            require(payload is child_roles['current'] and len(payload.cells)==1,'empty payload explicitly unexecuted')
            require(layout.geometry.parent_identity is child.program and layout.geometry.source_code==s.handle.code,'literal block geometry binding')
            require(physical.count_value(prefixes)==1 and field_count.inspect()==2,'complete w1 next prefix count')
            current_field_count[0]=field_count.inspect();captured_coefficient[0]=coefficient
            active=False
            for item in trace:
                events.append(item.kind)
                if item.kind in ('enter','return'):
                    require(item.parent_identity is child.program and item.source_code==s.handle.code,'source-produced leaf boundary')
                    require((item.first.inspect(),item.second.inspect(),item.width.inspect(),item.depth.inspect())==(0,126,2,2),'actual leaf extent and chronology')
                    active=item.kind=='enter'
                elif item.kind=='add':
                    require(active and item.request.kind=='child','leaf coefficient grammar')
                    for phase in ('split','merge'):
                        prefix=packet.read_prefix(fields,field_count);fields.rewind()
                        numerical_before=(set(ia.live),set(ra.live));program_before=(bytes(child.program.tape.cells),child.program.tape.head)
                        field_before=(bytes(prefix.cells),prefix.head)
                        try:
                            value=coefficient(prefix,item.request)
                            expected=3 if item.request.negative_inverse else 2
                            require(value.inspect()==expected,'non-involutory generated coefficient and negative inverse')
                            requests.append({'coordinate':item.request.coordinate.inspect(),'negative_inverse':item.request.negative_inverse,
                                             'phase':phase,'value':value.inspect()})
                            ra.free(value)
                            require((set(ia.live),set(ra.live))==numerical_before,'coefficient numerical ownership restored')
                            require((bytes(child.program.tape.cells),child.program.tape.head)==program_before and
                                    (bytes(prefix.cells),prefix.head)==field_before,'coefficient borrowed Program and fields preserved')
                        finally:prefix.clear()
                        if probe:raise ProbeComplete()
                else:require(active and item.kind in ('atom_swap','sign'),'only literal leaf primitive grammar')
            require(not active,'closed source-produced leaf lifetime')
            return payload
        macro_machine.packet_engine.run=boundary_observer
        fresh_rows.quotient=lambda *a,**k:(_ for _ in ()).throw(ValueError('leaf must not consume fresh stock'))
        try:
            try:
                returned=macro_machine.Machine.block(child,definition,('good',1,0))
            except ProbeComplete:
                return {'status':'PROBE_R437_LEAF_FIRST_REQUEST','requests':requests,'programs':len(programs)}
            require(returned is False,'literal Machine.block takes non-recursive leaf branch')
            require(events==['enter']+['atom_swap','add','atom_swap','add','atom_swap','add','atom_swap','sign']*2+['return'],
                    'complete literal leaf event chronology')
            require(len(requests)==12 and [x['coordinate'] for x in requests]==[0]*6+[1]*6 and
                    [x['value'] for x in requests]==[2,2,3,3,2,2]*2,'all split/merge leaf requests')
            require(len(programs)==12 and all(item.get('erased') for item in programs),'all twelve temporary second-STEP Programs erased')
            require(len({item['sha256'] for item in programs})==1,'same complete generated Program per unchanged source prefix')
            def reject_leaf(name,operation):
                try:operation()
                except ValueError as error:failures.append({'name':name,'error':str(error)})
                else:raise ValueError('accepted leaf control '+name)
            def leaf_request(coordinate,negative=False,directory_tape=None):
                coord=ia.literal(coordinate);count=ia.literal(2)
                fields=packet.read_prefix(next_directory if directory_tape is None else directory_tape,count)
                (next_directory if directory_tape is None else directory_tape).rewind()
                try:
                    result=captured_coefficient[0](fields,Request('child',coord,child_kind='good',negative_inverse=negative))
                    value=result.inspect();ra.free(result);return value
                finally:fields.clear();ia.free_many(coord,count)
            reject_leaf('coordinate_out_of_range',lambda:leaf_request(2))
            mutate_step[0]=True
            try:reject_leaf('generated_second_STEP_rank_changed',lambda:leaf_request(0))
            finally:mutate_step[0]=False
            wrong=records.Fields.fixture(ia,ra,[(s.handle.code,[[0]*64 for _ in range(64)]),(binding.ambient,[[0]*64 for _ in range(64)])],s.cat.codes.bits)
            try:reject_leaf('current_field_source_changed',lambda:leaf_request(0,directory_tape=wrong.tape))
            finally:wrong.tape.clear()
            require(stock_before=={name:physical.count_value(child.count(name)) for name in count_labels},'leaf dispatch preserves all inherited stock values')
        finally:
            macro_machine.packet_engine.run=saved_run;fresh_rows.quotient=saved_quotient;children.extend=real_extend
            child.close_geometry()
        result={'status':'PASS_R437_LEAF_DISPATCH','live_input_count':inputs,'q':7,'w':1,'root_unit':2,
                'root_source':{'request':s.record['identifier'],'identity':s.cat.source_identity,'rank':2},
                'path_widths':[2048,64,2],'stored_depths':[0,1,2],'events':events,'coefficient_requests':requests,
                'second_STEP_program_sha256':programs[0]['sha256'],'positive_programs_created_and_erased':12,
                'rejections':failures,'leaf_internal_dispatch':False,'leaf_additional_fresh_quotient':False,
                'all_inherited_stock_values_preserved':True,
                'add_pass_ast_sha256':digest(ast.dump(add_pass).encode()),
                'ingress_prefix_ast_sha256':digest(ast.dump(ast.Module(body=prefix,type_ignores=[])).encode()),
                'scope':'Literal Machine.block branch and actual generated-coefficient lifecycle with explicit packet metadata observer; full parent packet and leaf primitive payload passes are unexecuted. No numerical admission or kappa.'}
        dispose(child,child_roles);trace.close()
        return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');parser.add_argument('--probe',action='store_true');args=parser.parse_args()
    result=run(probe=args.probe)
    if args.probe:print(json.dumps(result,sort_keys=True));return
    if args.write:(HERE/'RESULT.json').write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    else:require(json.dumps(json.loads((HERE/'RESULT.json').read_text()),sort_keys=True)==json.dumps(result,sort_keys=True),'typed deterministic receipt')
    print(result['status'])


if __name__=='__main__':main()
