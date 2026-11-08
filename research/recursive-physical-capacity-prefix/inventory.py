"""Proof-bound source inventory, not a general Python resource analyzer.

Every AST statement/call in named transition modules is recorded. Three
literal facts are extracted independently. Other effects belong to the written
source proof and credited prefix lemmas, not an inference from successful tests.
Prepared for @CubeJerry with substantial OpenAI Codex assistance. Apache-2.0.
"""
import ast
from hashlib import sha1, sha256
import json
import tarfile
from audit_sources import HERE, ROOT, need

ARCHIVE = 'research/physical-ordinary-interchange/inputs/pr2809.tar'
MODULES = ('macro_machine.py', 'macro_binding.py', 'residual_blocks.py', 'role_parking.py',
           'inputs/pr2769/codec.py', 'inputs/pr2753/packet_engine.py',
           'inputs/pr2753/layout.py', 'inputs/pr2753/trace.py', 'inputs/pr2753/peel.py')
COEFFICIENT_BLOBS = {
    'children.py': 'ce4935f838516e2b08d13bec767cb803786fbc6b',
    'controller.py': 'c631a9e77fbcccf0e8f448adc22978728aed7b60',
    'forms.py': '6667c0b772a63f0059c7caffec63e0d919a92398',
    'matrices.py': '5d497353efbb9eeaaf4facd96ab40ffb0f3aa20d',
    'numeric.py': '6d4ebca8398008375b8f4762d1a9f1514e8c2611',
    'records.py': '4f00467a0ff580954ad2fd0c7380240c753ddef3',
    'words.py': '8d4ba37e2778acb35b34e0719df2caf138fbeb50',
}


def functions(tree):
    result = {}
    def walk(node, prefix):
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
                name = prefix + child.name
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    result[name] = child
                walk(child, name + '.')
            else:
                walk(child, prefix)
    walk(tree, '')
    return result


def source_inventory(raw):
    rows = {}
    for name, node in functions(ast.parse(raw)).items():
        rows[name] = dict(
            ast_sha256=sha256(ast.dump(node, include_attributes=False).encode()).hexdigest(),
            statements=sorted(type(x).__name__ for x in ast.walk(node) if isinstance(x, ast.stmt)),
            calls=sorted(ast.unparse(x.func) for x in ast.walk(node) if isinstance(x, ast.Call)))
    return dict(sha256=sha256(raw).hexdigest(), functions=rows)


def extract_facts(sources):
    packet = functions(ast.parse(sources['inputs/pr2753/packet_engine.py']))['run_generator']
    copies = [n.value for n in ast.walk(packet) if isinstance(n, ast.Assign)
              and any(isinstance(t, ast.Name) and t.id == 'boundary_words' for t in n.targets)
              and isinstance(n.value, ast.ListComp)]
    need(len(copies) == 1, 'one saved child-boundary list')
    copied = copies[0]
    need(ast.unparse(copied.elt) == 'layout.geometry.index.copy(getattr(event, name))'
         and len(copied.generators) == 1 and isinstance(copied.generators[0].iter, ast.Tuple),
         'actual per-field numerical copy')
    fields = [x.value for x in copied.generators[0].iter.elts if isinstance(x, ast.Constant)]
    need(fields == ['first', 'second', 'width', 'depth'], 'all four saved boundary fields')
    layout = functions(ast.parse(sources['inputs/pr2753/layout.py']))['Layout.child_extents']
    named = [n.value for n in ast.walk(layout) if isinstance(n, ast.Assign)
             and any(isinstance(t, ast.Name) and t.id == 'words' for t in n.targets)]
    need(len(named) == 1 and isinstance(named[0], ast.Tuple), 'explicit child extent Word set')
    extents = [ast.unparse(x) for x in named[0].elts]
    need(extents == ['a', 'b', 'a_end', 'b_end', 'last_offset', 'first_last', 'second_last',
                     'mapped_first_last', 'mapped_second_last',
                     'expected_first_last', 'expected_second_last'], 'eleven coordinate Words')
    extra = {t.id: ast.unparse(n.value) for n in ast.walk(layout) if isinstance(n, ast.Assign)
             for t in n.targets if isinstance(t, ast.Name) and t.id in ('between', 'after')}
    need(extra == {'between': 'g.raw.subtract_exact(b, a_end)',
                   'after': 'g.raw.subtract_exact(self.total, b_end)'},
         'two further live projected-coordinate allocations')
    machine = functions(ast.parse(sources['macro_machine.py']))['Machine.prepare_child']
    returns = [n.value for n in ast.walk(machine) if isinstance(n, ast.Return)]
    need(len(returns) == 1 and isinstance(returns[0], ast.Tuple), 'one grant tuple')
    grants = [ast.unparse(x) for x in returns[0].elts]
    need(grants == ['self.arena.copy(self.context.ring.modulus)',
                    'self.indices.copy(event.width)', 'self.indices.copy(event.depth)'],
         'one fresh residue and two fresh index grants')
    return dict(saved_boundary_indices=len(fields), projected_coordinate_words=len(extents),
                projected_extra_between_after=len(extra), residue_grants=1, index_grants=2)


def envelope(facts):
    need(all(type(value) is int for value in facts.values()), 'integer structural counts')
    m, rank = 64, 42
    candidates = [7*m*m + 4*m*r - r*r + 12 for r in range(1, rank+1)]
    need(all(b-a == 4*m-2*r-1 and b>a
             for r, (a, b) in enumerate(zip(candidates, candidates[1:]), 1)),
         'exact monotonicity across all selected ranks')
    good = max(candidates)
    fallback = m*m + 8*m*m - 2*m + 5 + 2
    evaluation = 9*m*m + 13
    coefficient = max(good, fallback, evaluation, 4*m*m+12, 12)
    need(coefficient == 37672, 'credited all-rank closed-coefficient maximum')
    need(facts == dict(saved_boundary_indices=4, projected_coordinate_words=11,
                       projected_extra_between_after=2, residue_grants=1, index_grants=2),
         'exact proof-bound structural facts')
    groups = dict(context=[3, 2], coefficient=[coefficient, 22], radix=[6, 0],
                  geometry=[0, 16], trace=[0, 16], saved_boundary=[0, facts['saved_boundary_indices']],
                  extents=[0, 16], grants=[facts['residue_grants'], facts['index_grants']])
    need(facts['projected_coordinate_words'] + facts['projected_extra_between_after'] <= 16,
         'physical extent allowance')
    total = [sum(row[j] for row in groups.values()) for j in range(2)]
    need(total == [37682, 78] and all(x <= 2**24 for x in total), 'complete declared capacity')
    return dict(groups=groups, total=total, sufficient_fixture_independent_pair=[65536, 128],
                production_pair=[2**24, 2**24], coefficient_candidates=[good, fallback, evaluation])


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False)


def build():
    with tarfile.open(ROOT / ARCHIVE, 'r:') as handle:
        sources = {name: handle.extractfile(name).read() for name in MODULES}
        compatible = {}
        for name, expected in COEFFICIENT_BLOBS.items():
            raw = handle.extractfile('inputs/pr2753/predecessor/vendor/' + name).read()
            actual = sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()
            need(actual == expected, 'credited exact coefficient implementation: ' + name)
            compatible[name] = actual
    facts = extract_facts(sources)
    rows = {name: source_inventory(raw) for name, raw in sources.items()}
    physical = 'research/physical-ordinary-interchange/physical_words.py'
    rows[physical] = source_inventory((ROOT / physical).read_bytes())
    return dict(schema_version=1,
                methodology='Complete syntax/call inventory binds the written proof; only specified literal structural facts are mechanically extracted. No generic resource analysis is claimed.',
                historical_dimension=64, maximum_rank=42, current_selected_admission=False,
                exact_coefficient_blobs=compatible, structural_facts=facts,
                envelope=envelope(facts), transition_modules=rows)


def verify_record(record, observed=None):
    actual = build() if observed is None else observed
    need(canonical(record) == canonical(actual), 'complete typed source/inventory record')


def controls(record):
    from copy import deepcopy
    outcomes = []
    for label, mutate in (
        ('omit_saved_boundary', lambda x: x['structural_facts'].__setitem__('saved_boundary_indices', 0)),
        ('omit_child_grant', lambda x: x['structural_facts'].__setitem__('residue_grants', 0)),
        ('boolean_structural_count', lambda x: x['structural_facts'].__setitem__('residue_grants', True)),
        ('wrong_total', lambda x: x['envelope']['total'].__setitem__(1, 74)),
        ('missing_transition', lambda x: x['transition_modules'].pop('macro_machine.py')),
    ):
        changed = deepcopy(record)
        mutate(changed)
        try:
            verify_record(changed, record)
        except ValueError:
            outcomes.append(label)
        else:
            raise ValueError('inventory corruption accepted: ' + label)
    try:
        envelope(dict(record['structural_facts'], residue_grants=True))
    except ValueError:
        outcomes.append('boolean_effect_rejected_directly')
    else:
        raise ValueError('boolean effect accepted')
    return outcomes
