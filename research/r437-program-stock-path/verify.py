#!/usr/bin/env python3
"""One literal Program/row handoff joined to PR4685's arithmetic certificate.

Brian, with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
import ast
from dataclasses import replace
from hashlib import sha256
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
        rejected, boundary_controls = [], []

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

        binding = object.__new__(macro_binding.SelectedBinding)
        binding.specifications, binding.codes = s.specs, s.cat.codes
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
            ia.free_many(root_words[0], root_words[2], child_words[0], child_words[2], level, parent, width, grants[1], grants[2])
            ra.free_many(root_words[1], child_words[1], grants[0])
            require((set(ia.live),set(ra.live))==live, 'prepare and observation release temporary numerical words')
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
        for name, changes in [
            ('changed_root_rows', {'root_rows':rows*2}),
            ('changed_source_identity', {'source_identity':'0'*64}),
            ('changed_request', {'request_key':('IDLE',0,0,0)}),
            ('changed_source_code', {'source_code':s.handle.code+1}),
            ('changed_root_width', {'root_width':1024}),
            ('changed_root_depth', {'root_depth':1}),
            ('changed_root_unit', {'root_unit':1,'child_root':(2048,1,1)}),
            ('changed_field', {'q':5}),
            ('changed_precision', {'w':2}),
            ('changed_modulus', {'modulus':9}),
            ('changed_grant_modulus', {'grant_modulus':9}),
            ('changed_child_root_unit', {'child_root':(2048,1,1)}),
            ('changed_step_rank', {'step_metadata':(0,s.handle.code,3,0,0,0)}),
            ('changed_prepared_rows', {'handed_rows':observed['handed_rows']*2}),
            ('unrelated_divisible_rows', {'unused_rows':observed['unused_rows']*2,'handed_rows':observed['handed_rows']*2}),
        ]:
            reject(name, lambda changes=changes:bind(root,source,dict(observed,**changes)))
        require((observed['handed_rows']*2)%stock_divisor(64,3,1)==0, 'doubled child passes local divisibility')
        reject('foreign_parent_identity',lambda:handoff(replace(event,parent_identity=object())))
        reject('foreign_event_source',lambda:handoff(replace(event,source_code=s.handle.code+1)))
        for name,field,value in [('event_width_disagrees_with_program','width',63),('event_depth_disagrees_with_program','depth',2)]:
            word = ia.literal(value)
            changed = handoff(replace(event,**{field:word}))
            reject(name, lambda changed=changed:bind(root,source,changed))
            boundary_controls.append({'name':name,'prepare_child_accepts':True,
                                      'produced_width':changed['step_width'],'produced_depth':changed['child_root'][2],
                                      'grant_width':changed['grant_width'],'grant_depth':changed['grant_depth']})
            ia.free(word)
        # Reconstruct a final unmodified handoff; the protected parent is still reusable.
        require(bind(root,source,handoff(event))==certificate, 'positive control after mutations')
        trace.close()
        result = {'status':'PASS_R437_PROGRAM_STOCK_PATH', 'live_input_count':inputs,
            'source':{'request':s.record['identifier'],'request_key':list(s.handle.request_key),
                      'identity':s.cat.source_identity,'rank':source['rank'],'code_bits':s.cat.codes.bits,
                      'code':integer_receipt(s.handle.code)},
            'semantic_root':{'width':2048,'q':3,'w':1,'depth':0,'unit':2,'rows':integer_receipt(rows),
                             'numerical_admitted':False,'stock':'retained conservative K^D'},
            'path':{'widths':[2048,64],'depths':[0,1],'child_rows':integer_receipt(observed['handed_rows']),
                    'child_modulus':3,'arithmetic_certificate':certificate},
            'literal_boundaries':['semantic checked_entry continuation','directory.produce','Machine.node quotient/stock AST with real Count',
                'residual_blocks.events good branch','SelectedBinding.child_program / children.extend','Machine.prepare_child','Program.root/step'],
            'controls_rejected':rejected,'boundary_controls':boundary_controls,
            'scope':'One q=3,w=1 historical R437 semantic Program/row witness. No numerical admission, full payload, recursive execution, physical cost or kappa claim.'}
        return result


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
