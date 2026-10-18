"""External conformance checks; this command does not compile or verify Lean."""
import argparse
import hashlib
from itertools import product
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE_SHA = '935a276dd172dd8d45b13612c24115a766fcaacb1c581450f5b46d917f475852'


def require(ok, why):
    if not ok:
        raise ValueError(why)


def read_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate JSON key: '+key)
            result[key] = value
        return result
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=pairs)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def bindings():
    result = {}
    rows = read_json(HERE/'SOURCES.json')['files']+read_json(HERE/'PREDECESSORS.json')['files']
    for row in rows:
        if row['usage'] != 'input':
            continue
        raw = (ROOT/row['path']).read_bytes()
        blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        require(sha(raw) == row['sha256'] and blob == row['git_blob'], 'source binding: '+row['path'])
        require(row['path'] not in result, 'duplicate source')
        result[row['path']] = sha(raw)
    require(len(result) == 5, 'five source inputs required')
    formal = read_json(HERE/'FORMAL.json')
    require(formal['status'] == 'EXTERNAL_RECEIPT_NOT_A_FRESH_COMPILATION', 'formal boundary')
    require(set(formal['files']) == {'RegularOrbit.lean','Controls.lean','formal_verify.py','FORMAL-RESULT.json'}, 'formal file set')
    for name, digest in formal['files'].items():
        require(sha((HERE/name).read_bytes()) == digest, 'formal artifact binding: '+name)
    receipt = read_json(HERE/'FORMAL-RESULT.json')
    require(receipt['status'] == 'PASS_FRESH_LEAN_REGULAR_ORBIT_INTERFACE', 'retained formal status')
    require(receipt['reused_candidate_olean'] is False, 'retained fresh build')
    require(len(receipt['axioms']) == 16, 'retained formal roots')
    require(len(receipt['negative_statements']) == 4, 'retained negative statements')
    for name in ('RegularOrbit.lean','Controls.lean'):
        require(receipt['sources_sha256'][name] == formal['files'][name], 'compiled source binding')
    for axioms in receipt['axioms'].values():
        require(set(axioms) <= {'propext','Quot.sound','Classical.choice'}, 'retained unexpected axiom')
    return {'sources':result,'formal':formal['files']}


def explicit_vector(rows, value):
    # Literal Boolean formula used by RegularOrbit.mv3 (independent of bit_count).
    out = 0
    for i in range(3):
        a, b, c = [(rows[i] >> j) & 1 for j in range(3)]
        x, y, z = [(value >> j) & 1 for j in range(3)]
        out |= ((a & x) ^ ((b & y) ^ (c & z))) << i
    return out


def explicit_tuple(rows, address):
    return sum(explicit_vector(rows,(address >> (3*j)) & 7) << (3*j) for j in range(3))


def calculate():
    pins = bindings()
    raw = (HERE/'source/pr2599/verify.py').read_bytes()
    require(sha(raw) == SOURCE_SHA, 'exact authenticated source code required')
    source = {'__name__':'authenticated_pr2599','__file__':str(HERE/'source/pr2599/verify.py')}
    exec(compile(raw, source['__file__'], 'exec'), source)
    # Independent invertibility: every one of the eight vectors has a distinct image.
    matrices = [m for m in product(range(8),repeat=3)
                if len({explicit_vector(m,x) for x in range(8)}) == 8]
    require(len(matrices) == 168, 'GL3 order')
    source_group, _, _ = source['group'](3,False)
    require(set(source_group) == {(m,0) for m in matrices}, 'source group conformance')
    basis = 1 | (2 << 3) | (4 << 6)
    images = []
    points = 0
    inverses = 0
    vector_cases = 0
    for m in matrices:
        inverse = next(n for n in matrices if all(explicit_vector(n,explicit_vector(m,x)) == x for x in range(8)))
        require(all(explicit_vector(m,explicit_vector(inverse,x)) == x for x in range(8)), 'two-sided inverse')
        for x in range(8):
            require(explicit_vector(m,x) == source['vector'](m,x), 'mv3 vector conformance')
            vector_cases += 1
        for x in range(512):
            y = explicit_tuple(m,x)
            require(y == source['act']((m,0),x,3,3), 'three-column action conformance')
            require(explicit_tuple(inverse,y) == x and explicit_tuple(m,explicit_tuple(inverse,x)) == x, 'full tuple inverse')
            points += 1
            inverses += 2
        images.append(explicit_tuple(m,basis))
    require(len(set(images)) == 168, 'separating basis tuple')
    # Nonconstant full coefficient matrix: apply the source forward action to
    # each role-delta input and recover all nine blocks, including off-diagonals.
    mixed = 0
    matrix = [[[int((5*h+3*i+j) % 11 < 4) for h in range(168)] for j in range(3)] for i in range(3)]
    for input_role in range(3):
        payload = [0,0,0]
        payload[input_role] = 1 << basis
        for i in range(3):
            output = 0
            for j in range(3):
                for h,m in enumerate(matrices):
                    if matrix[i][j][h]:
                        bits = payload[j]
                        while bits:
                            low = bits & -bits
                            x = low.bit_length()-1
                            output ^= 1 << source['act']((m,0),x,3,3)
                            bits ^= low
            require([(output >> y) & 1 for y in images] == matrix[i][input_role], 'mixed dirty-role coefficient extraction')
            mixed += 168
    # Actual inverse-pullback formula for every coefficient/output pair in a C2 action.
    c2 = 0
    for coeffs in product((0,1),repeat=2):
        for h in range(2):
            value = 0
            for g in range(2):
                value ^= coeffs[g] & int((h ^ g) == 0)
            require(value == coeffs[h], 'C2 inverse pullback coefficient extraction')
            c2 += 1
    # Source-width mismatch really collides: three columns are not one column.
    require(len({source['act']((m,0),1,3,1) for m in matrices}) == 7, 'short-width collision control')
    return {'schema_version':1,'status':'PASS_EXTERNAL_REGULAR_ORBIT_CONFORMANCE',
            'bindings':pins,'matrix_count':168,'vector_comparisons':vector_cases,
            'full_three_column_comparisons':points,'inverse_identities':inverses,
            'separating_point':basis,'separating_images':len(set(images)),
            'mixed_dirty_block_coefficients':mixed,
            'c2_inverse_pullback_cases':c2,'one_column_basis_images':7,
            'lean_compiled_by_this_command':False,
            'limits':'Finite conformance is external to Lean. Enumerators, code parsing, word translation, prior census, other widths and physical suppliers are not formalized.'}


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write-result',type=Path,help='write only a NEW result')
    args = ap.parse_args()
    if args.write_result:
        require(not args.write_result.exists(),'output already exists')
    result = calculate()
    if args.write_result:
        with args.write_result.open('x',encoding='utf-8',newline='\n') as f:
            json.dump(result,f,indent=2)
            f.write('\n')
    else:
        require(canonical(read_json(HERE/'RESULT.json')) == canonical(result),'typed exact receipt mismatch')
    print(result['status']+' matrices=168 full_columns=86016 Lean_compiled=False')


if __name__ == '__main__':
    main()
