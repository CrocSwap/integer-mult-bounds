"""Source-only replay of mandatory serial full-field passes. No native run.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
import ast
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent


def need(ok, message):
    if not ok:
        raise ValueError(message)


def authenticate():
    manifest = json.loads((HERE/'DEPENDENCIES.json').read_text())
    for row in manifest['files']:
        raw = (HERE/row['path']).read_bytes()
        need(len(raw) == row['bytes'] and hashlib.sha256(raw).hexdigest() == row['sha256']
             and hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest() == row['git_blob'],
             'immutable source '+row['path'])
    return len(manifest['files'])


def method(tree, cls, name):
    c = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == cls)
    return next(n for n in c.body if isinstance(n, ast.FunctionDef) and n.name == name)


def calls(node, name):
    return sorted((n for n in ast.walk(node) if isinstance(n, ast.Call)
                   and ast.unparse(n.func) == name), key=lambda n: n.lineno)


def four_traversals(tree):
    importer = method(tree, 'Provider', 'import_field')
    exporter = method(tree, 'Provider', 'export_field')
    rewind = method(tree, 'Provider', 'rewind_field')
    run = method(tree, 'Provider', 'run')
    for part in (importer, exporter):
        need(len(calls(part, 'self.rewind_field')) == 1, 'one complete return per codec direction')
        need(any(isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
                 and ast.unparse(n.value.func) == 'self.rewind_field' for n in part.body),
             'return outside the data loop')
        advance = calls(part, 'field.move')
        need(len(advance) == 2 and all(ast.literal_eval(n.args[0]) == 1 for n in advance),
             'data and delimiter forward movement')
    back = calls(rewind, 'field.move')
    need(len(back) == 1 and ast.literal_eval(back[0].args[0]) == -1,
         'per-guide-marker backward movement')
    keys = ('self.import_field', 'self.engine.run', 'self.export_field')
    ordered = [calls(run, key) for key in keys]
    need(all(len(v) == 1 for v in ordered)
         and [v[0].lineno for v in ordered] == sorted(v[0].lineno for v in ordered),
         'import, actual engine, export in fixed order')
    return True


def literal_coded_costs():
    tree = ast.parse((HERE/'source/machine.py').read_bytes())
    nodes = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef))
             and n.name in ('need', 'emit', 'CodedPort')]
    env = {'ZERO': 0, 'ONE': 1, 'LEFT': 2, 'BLANK': 6}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), '<pinned literal CodedPort>', 'exec'), env)

    class Meter:
        def __init__(self):
            self.cells = [2]+[0]*15
            self.head = 4
            self.count = [0, 0, 0]
        def read(self):
            self.count[0] += 1
            return self.cells[self.head]
        def write(self, value):
            self.count[1] += 1
            self.cells[self.head] = value
        def move(self, direction):
            need(direction in (-1, 1), 'unit primitive')
            self.count[2] += 1
            self.head += direction

    result = {}
    for label, op in [('forward', lambda p: p.move(1)),
                      ('backward', lambda p: p.move(-1)),
                      ('write', lambda p: p.write(2)),
                      ('read', lambda p: p.read())]:
        t = Meter();op(env['CodedPort'](t));result[label] = t.count
    need(result == dict(forward=[1,0,3], backward=[1,0,3], write=[0,3,6], read=[4,0,6]),
         'literal coded primitive costs')
    return result


def source_recipe():
    word = json.loads(gzip.decompress((HERE/'source/WORD.json.gz').read_bytes()))
    raw = ['MOVE', 236, 3, 7, False]
    need(word['program'][9896] == raw and type(word['program'][9896][-1]) is bool,
         'exact selected raw occurrence')
    spec = importlib.util.spec_from_file_location('serial_lower_retained_clifford', HERE/'source/clifford_exact.py')
    C = importlib.util.module_from_spec(spec);sys.modules[spec.name] = C;spec.loader.exec_module(C)
    a = C.canonical_frame(9, tuple(word['frames'][3]))
    b = C.canonical_frame(9, tuple(word['frames'][7]))
    rec, _ = C.lower_child(a.adjoint().then(b))
    recipe = rec['right']
    need(len(recipe['matrix_rows']) == 9 and recipe['phase'] == 1 and rec['rank'] == 1,
         'nontrivial actual right recipe; child rank differs from monomial rank')
    return dict(event=9896, raw=raw, monomial_rank=9, positive_child_rank=rec['rank'],
                right=recipe, recipe_sha256=hashlib.sha256(json.dumps(recipe, sort_keys=True,
                separators=(',', ':')).encode()).hexdigest())


def family(f):
    return dict(outer=1, rows=1, stock=1, h=2, d=9*f, selected_axes=9*f, p=9*f,
                D=9*f, remainder=0, K=1, G=1, rho=0, H=f,
                active_start=2*f, entry_start=2*f, back_start=11*f,
                within_bits=12*f, record_bits=18, row_bits=18 << (12*f),
                q0=0, qF=0, qB=0, cutoff=145, f=f)


def admitted(v):
    m = 9
    need(all(type(x) is int and x >= 0 for x in v.values()), 'nonnegative canonical integers')
    need(all(v[k] > 0 for k in ('outer','rows','row_bits','record_bits','f','K','G','H')),
         'positive consumed parameters')
    need(v['h'] >= 2 and v['rho'] < v['K'], 'signed width and residue')
    need((v['f']-1)*v['G'] <= v['H'] and 2*v['H'] <= v['active_start'], 'front reservations')
    need(v['active_start']+m*v['f']*v['K'] <= v['back_start'], 'active axis extent')
    need(v['back_start']+v['H'] <= v['within_bits'], 'entire back reservation')
    need(m*v['f']+v['remainder'] == v['selected_axes'] <= v['d']
         and v['remainder'] < m, 'selected dimensions')
    need(v['row_bits'] == v['record_bits'] << v['within_bits'], 'complete row')
    need(v['record_bits'] % (6*(v['h']+1)) == 0, 'whole positive coefficient records')
    return True


def main():
    retained = authenticate()
    phase = ast.parse((HERE/'source/phase_adapter.py').read_bytes())
    four_traversals(phase)
    serial = ast.parse((HERE/'source/column_view.py').read_bytes())
    run = method(serial, 'SerialProvider', 'run')
    need(len(calls(run, 'self.native.run')) == len(calls(run, 'self.view.advance')) == 1,
         'one native invocation per encoded iterator cycle')
    need(not any(isinstance(n, ast.Constant) and n.value == 'cutoff' for n in ast.walk(phase)),
         'monomial adapter does not consume cutoff')
    mutant = copy.deepcopy(phase)
    ex = method(mutant, 'Provider', 'export_field')
    ex.body = [n for n in ex.body if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
               and ast.unparse(n.value.func) == 'self.rewind_field')]
    controls = []
    try: four_traversals(mutant)
    except ValueError: controls.append('missing_export_rewind')
    else: raise ValueError('missing rewind escaped structure control')
    count = 0
    for f in list(range(128, 641))+[1024,2048,4096]:
        v=family(f);admitted(v)
        V=v['row_bits'];Vraw=4 << (12*f)
        need(2*V == 9*Vraw and v['d'] == 9*f, 'actual volume and dimension identities')
        need((1 << (f+2)) >= (12*f+5)**6, 'long-record member')
        for j in (0, f//2, f-1):
            child=dict(v,f=1,K=f,rho=j,selected_axes=9)
            admitted(child)
            need(all(child['active_start']+i*child['K']+child['rho']
                     == v['active_start']+(i*f+j)*v['K'] for i in range(9)), 'all9 coordinate positions')
        count += 1
    need(129**6 < 2*128**6 and (1 << 130) >= 1541**6,
         'exact induction base and uniform ratio premise')
    for key, bad in [('H',126),('active_start',255),('back_start',1407),
                     ('row_bits',18),('d',1151),('rho',1)]:
        v=family(128);v[key]=bad
        try: admitted(v)
        except ValueError: controls.append('invalid_'+key)
        else: raise ValueError(('invalid family escaped',key))
    v=family(146);admitted(v)
    need(v['f'] > v['cutoff'], 'local family does not imply fixed-cutoff MOVE admission')
    controls.append('fixed_cutoff_scope')
    need(family(128)['row_bits']//128 != family(128)['row_bits'], 'f-divided field is not complete volume')
    controls.append('false_f_divided_volume')
    result=dict(status='PASS_SERIAL_MANDATORY_FIELD_PASSES',retained_files=retained,
                source=source_recipe(),primitive_costs=literal_coded_costs(),
                family_members=count,controls=controls,
                lower_per_fV=dict(physical_moves='4',physical_reads='4/3',physical_writes='1'),
                numerical_native_execution=False,full_supplier_family_proved=False,
                fixed_leaf_budget_refuted=False,new_kappa=False)
    print(json.dumps(result,sort_keys=True))


if __name__ == '__main__':
    main()
