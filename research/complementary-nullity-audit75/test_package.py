"""Mathematical hypothesis and immutable-package rejection controls.
@woklerx with substantial OpenAI Codex assistance; Apache-2.0.
"""
import copy
import importlib.util
import json
from pathlib import Path
import tempfile

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('kernel_check', HERE / 'independent.py')
check = importlib.util.module_from_spec(spec); spec.loader.exec_module(check)
source = check.sources
need = source.need


def rejects(action, name):
    try:
        action()
    except ValueError:
        return name
    raise RuntimeError('accepted negative control: ' + name)


def main():
    source.pins()
    expected = json.loads((HERE / 'EXPECTED.json').read_text(encoding='utf-8'))
    witness = expected['finite_census']['wrong_complement_control']
    a,b,i,j = (witness[k] for k in ('A','B','I','J'))
    ic,jc = [k for k in range(3) if k not in i], [k for k in range(3) if k not in j]
    controls = []
    controls.append(rejects(lambda: need(source.small_rank(a,i,j)-source.small_rank(b,ic,jc) == len(i)+len(j)-3,
                                          'row/column complements must swap'), 'unswapped inverse complements'))
    identity = [[int(i == j) for j in range(3)] for i in range(3)]
    controls.append(rejects(lambda: need(source.small_rank(identity,[0],[0]) == source.small_rank(identity,[1,2],[1,2]),
                                          'rectangular dimension offset'), 'omit dimension offset'))
    controls.append(rejects(lambda: source.inverse3([[1,0,0],[0,0,0],[0,0,1]]), 'singular whole matrix'))
    raw, _ = source.source_matrix()
    inv = check.inverse(raw)
    bad = copy.deepcopy(inv); bad[0][1] += 1
    controls.append(rejects(lambda: check.check_inverse(raw,bad), 'corrupted source inverse'))
    controls.append(rejects(lambda: check.correspondence(raw,inv,[0,0],[1]), 'duplicate subset index'))
    vectors, rank = check.kernel([[0,0]], 2)
    controls.append(rejects(lambda: need(len(vectors[:-1])+rank == 2, 'full kernel dimension'), 'omit kernel basis vector'))
    # D is invertible, but X is singular. One complement cannot prove both conclusions.
    example = [[0,1],[1,1]]
    inv2 = check.inverse(example)
    need(check.rref([example[1][1:]],1)[1] == [0] and inv2[0][0] != 0, 'one-complement positive premise')
    controls.append(rejects(lambda: need(example[0][0] != 0, 'both complementary hypotheses needed'), 'drop second complementary hypothesis'))
    controls.append(rejects(lambda: need(source.canonical({'rank':2}) == source.canonical({'rank':2.0}), 'typed receipt'), 'float rank receipt'))
    pins = json.loads((HERE / 'SOURCES.json').read_text(encoding='utf-8'))
    package_controls = []
    with tempfile.TemporaryDirectory(prefix='nullity75-controls-', dir=source.ROOT) as tmp:
        package = Path(tmp)
        (package/'BASE-SELECTED.json').write_bytes((HERE/'BASE-SELECTED.json').read_bytes())
        mutations = []
        p = copy.deepcopy(pins); p['files'].pop(next(iter(p['files']))); mutations.append(('missing pin',p))
        p = copy.deepcopy(pins); p['files']['extra'] = '0'*64; mutations.append(('extra pin',p))
        p = copy.deepcopy(pins); p['base'] = '0'*40; mutations.append(('wrong base',p))
        p = copy.deepcopy(pins); p['files'][source.FILES[2]] = '0'*64; mutations.append(('wrong source digest',p))
        p = copy.deepcopy(pins); p['selected_snapshot_sha256'] = '0'*64; mutations.append(('wrong snapshot digest',p))
        for name,p in mutations:
            (package/'SOURCES.json').write_text(json.dumps(p),encoding='utf-8')
            package_controls.append(rejects(lambda:source.pins(package=package),name))
    print('PASS_COMPLEMENTARY_NULLITY_CONTROLS mathematical='+str(len(controls))+' package='+str(len(package_controls)))


if __name__ == '__main__':
    main()
