#!/usr/bin/env python3
"""Actual descendant ingress joined to PR4732's Program/row handoff.

Setup/bind/handoff derived from PR4732, Brian with OpenAI Codex assistance.

Brian, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import ast
from hashlib import sha256
from fractions import Fraction
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


def run():
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
        s = physical.source('D')
        import words, records, directory, macro_binding, macro_machine, numeric, layout, residual_blocks, packet
        from cardinal_counts import Count
        ia, ra = words.Arena(13, 1024), words.Arena(3, 131072)
        ring = words.Ring(ra.literal(3))
        program = records.Program.fixture(ia, ra, 2048, 2, (), s.cat.codes.bits)
        old_fields = records.Fields.fixture(ia, ra, [], s.cat.codes.bits)
        context = directory.Context(ring, s.cat.codes)
        size, depth, columns = ia.literal(2048), ia.literal(0), ia.literal(32)
        rows = admission.numerical.stock_unit(3, 1)**admission.numerical.depth(2048)
        domain = admission.RootDomain(2048, 2048, 1, 0, 3, 13, s.cat.codes.bits, rows)
        root = Node(2048, rows, 3, 1)
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
        geometry = layout.Layout(page, size, ring, 3, Count.literal(1), Count.literal(1), Count.literal(1))
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
            require(observed['unused_rows'] == rows//row_factor(3,1), 'independent row factor')
            return observed, certificate

        (observed, certificate), entry = admission.checked_entry(s.cat,s.specs,s.handle,domain,continuation,
            mode='semantic', expected_key=s.handle.request_key, expected_common=True)
        require(len(reached)==1 and entry['numerical_admitted'] is False, 'one guarded semantic continuation')
        # The predecessor ends here. Everything below executes the child ingress.
        factor = row_factor(3, 1)
        prep=[[Fraction(x).numerator*pow(Fraction(x).denominator,-1,3)%3 for x in row] for row in s.spec.template.preparation]
        require(all(sum(s.spec.low[i][k]*prep[k][j] for k in range(64))%3==int(i==j)
                    for i in range(64) for j in range(64)), 'independent low times preparation is identity modulo3')
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
            if grants is None: grants=(ra.literal(3),ia.literal(64),ia.literal(1))
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
        dispose(child,child_roles)

        rejections=[]
        def rejected_ingress(name, changes=None, width=64, depth=1):
            mutant,mutant_roles=child_runtime(changes, (ra.literal(3),ia.literal(width),ia.literal(depth)))
            try:
                try:run_ingress(mutant)
                except ValueError as error:rejections.append({'name':name,'error':str(error)})
                else:raise RuntimeError('ingress accepted '+name)
            finally:dispose(mutant,mutant_roles)

        rejected_ingress('runtime_width65',width=65)
        rejected_ingress('runtime_depth0',depth=0)
        rejected_ingress('runtime_depth2',depth=2)
        bad_rank=records.Program.fixture(ia,ra,2048,2,((0,s.handle.code,3,0,0,0),),s.cat.codes.bits)
        rejected_ingress('STEP_rank3',{'program':bad_rank.tape});bad_rank.tape.clear()
        bad_unit=records.Program.fixture(ia,ra,2048,0,((0,s.handle.code,2,0,0,0),),s.cat.codes.bits)
        rejected_ingress('nonunit_root',{'program':bad_unit.tape});bad_unit.tape.clear()
        wrong_code=records.Fields.fixture(ia,ra,[(binding.ambient,[[0]*64 for _ in range(64)])],s.cat.codes.bits)
        rejected_ingress('directory_source_mismatch',{'old_directory':wrong_code.tape});wrong_code.tape.clear()
        high=[[0]*64 for _ in range(64)];high[0][0]=1
        wrong_high=records.Fields.fixture(ia,ra,[(s.handle.code,high)],s.cat.codes.bits)
        rejected_ingress('noncanonical_high_digit',{'old_directory':wrong_high.tape});wrong_high.tape.clear()
        for name,delta in [('rows_not_divisible',1),('unused_not_9475_compatible',factor)]:
            wrong_rows=Count.literal(rows//factor+delta)
            rejected_ingress(name,{'rows':wrong_rows.tape});wrong_rows.close()
        # A valid but unrelated doubled stock passes the local guard: exact ancestry remains separate.
        doubled=Count.literal(2*rows//factor)
        other,other_roles=child_runtime({'rows':doubled.tape})
        require(run_ingress(other)==[2] and physical.count_value(other.count('unused'))==2*unused,
                'unrelated divisible rows pass local guard')
        dispose(other,other_roles);doubled.close()
        require(all(bytes(capsule[name].cells)==raw for name,raw in capsule_bytes.items()),'original capsule unchanged after controls')
        trace.close()
        return {'status':'PASS_R437_DESCENDANT_INGRESS','live_input_count':inputs,
            'source':{'request':s.record['identifier'],'key':list(s.handle.request_key),'identity':s.cat.source_identity,
                      'rank':source['rank'],'code':integer_receipt(s.handle.code)},
            'root':{'width':2048,'unit':2,'q':3,'w':1,'rows':integer_receipt(rows),'numerical_admitted':False},
            'path':{'widths':[2048,64],'arithmetic_certificate':certificate},
            'actual_ingress':positive,'actual_ingress_rejections':rejections,'correspondence_rejections':rejected,
            'doubled_stock_passes_local_guard':True,
            'literal_node_prefix_statements':len(prefix),'literal_node_prefix_ast_sha256':digest(ast.dump(ast.Module(body=prefix,type_ignores=[])).encode()),
            'scope':'One actual child ingress through first generated coefficient and real Count quotient/9475 guard; no second STEP, payload, numerical admission or kappa.'}



def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    result=run(); serialized=json.dumps(result,sort_keys=True,indent=2)+'\n'
    if args.write:
        (HERE/'RESULT.json').write_text(serialized)
    else:
        require(json.loads((HERE/'RESULT.json').read_text())==result,'deterministic receipt')
    print(result['status'])


if __name__=='__main__':
    main()
