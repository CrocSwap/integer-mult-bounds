"""Independent certificate checker; arbitrary-real completeness is written proof."""
import argparse
import ast
from copy import deepcopy
from fractions import Fraction as Q
import hashlib
import itertools
import json
from pathlib import Path

P = Path(__file__).resolve().parent
ROOT = P.parents[1]
SOURCE = 'research/complex-frame-pair-decoders/verify.py'


def need(ok,message):
    if not ok:
        raise ValueError(message)


def authenticate():
    files = {}
    for row in json.loads((P/'SOURCES.json').read_text(encoding='utf-8'))['files']:
        data = (ROOT/row['path']).read_bytes()
        need(hashlib.sha256(data).hexdigest() == row['sha256'],'source SHA-256: '+row['path'])
        blob = b'blob '+str(len(data)).encode()+b'\0'+data
        need(hashlib.sha1(blob).hexdigest() == row['git_blob'],'source Git blob: '+row['path'])
        files[row['path']] = data
    return files


def source_geometry(data):
    """Evaluate only the authenticated root function and two constants."""
    tree = ast.parse(data,filename=SOURCE)
    wanted = []
    for node in tree.body:
        if isinstance(node,ast.FunctionDef) and node.name == 'e8_roots':
            wanted.append(node)
        elif isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id in {'SIMPLE','EXPECTED_TYPES'} for t in node.targets):
            wanted.append(node)
    need(len(wanted) == 3,'source geometry AST boundary')
    namespace = {'itertools':itertools}
    exec(compile(ast.Module(body=wanted,type_ignores=[]),SOURCE,'exec'),namespace)
    return sorted(map(list,namespace['e8_roots']())),list(map(list,namespace['SIMPLE'])),namespace['EXPECTED_TYPES']


def alphabet():
    # Independent sign-mask/pair loops; no producer import or solver reuse.
    answer = set()
    for i in range(8):
        for j in range(i):
            for mask in range(4):
                r = [0]*8
                r[i],r[j] = 2 if mask&1 else -2,2 if mask&2 else -2
                answer.add(tuple(r))
    for mask in range(256):
        if mask.bit_count()%2 == 0:
            answer.add(tuple(-1 if mask&(1<<i) else 1 for i in range(8)))
    return sorted(map(list,answer))


def dot(a,b):
    return sum(x*y for x,y in zip(a,b))


def rank(rows):
    # Fraction-free elimination; unlike the producer this never inverts a matrix.
    a = [list(row) for row in rows]
    pivot = 0
    for j in range(8):
        hit = next((i for i in range(pivot,len(a)) if a[i][j]),None)
        if hit is None:
            continue
        a[pivot],a[hit] = a[hit],a[pivot]
        for i in range(pivot+1,len(a)):
            if a[i][j]:
                x,y = a[pivot][j],a[i][j]
                a[i] = [x*s-y*t for s,t in zip(a[i],a[pivot])]
        pivot += 1
        if pivot == 8:
            break
    return pivot


def vector(row,size=8):
    return isinstance(row,list) and len(row) == size and all(type(x) is int for x in row)


def check(cert,expected_simple=None):
    need(type(cert.get('schema_version')) is int and cert['schema_version'] == 1,'certificate schema')
    rr,aa = cert['roots'],cert['simple']
    need(all(vector(r) for r in rr) and rr == alphabet(),'exact 240-root alphabet')
    need(len(aa) == 8 and all(vector(a) and a in rr for a in aa),'eight root basis vectors')
    if expected_simple is not None:
        need(aa == expected_simple,'source simple basis')
    need(rank(aa) == 8,'simple basis full rank')
    need(all(dot(r,r) == 8 for r in rr),'root norm')
    cc = cert['coefficients']
    need(len(cc) == 240 and all(vector(c) for c in cc),'240 integer expansions')
    for r,c in zip(rr,cc):
        need([sum(c[i]*aa[i][j] for i in range(8)) for j in range(8)] == r,'simple expansion reconstructs root')
        need(all(x >= 0 for x in c) or all(x <= 0 for x in c),'sign-coherent simple expansion')
    perms = cert['reflections']
    need(len(perms) == 8,'eight reflections')
    for a,perm in zip(aa,perms):
        need(vector(perm,240) and sorted(perm) == list(range(240)),'root permutation')
        for i,r in enumerate(rr):
            need([4*x-dot(r,a)*y for x,y in zip(r,a)] == [4*x for x in rr[perm[i]]],'exact reflection image')
            need(perm[perm[i]] == i,'reflection involution')
    weights = cert['fundamental_rays']
    need(len(weights) == 8 and all(vector(w) for w in weights),'eight integer fundamental rays')
    for j,w in enumerate(weights):
        need(all(dot(a,w) == 0 if i != j else dot(a,w) > 0 for i,a in enumerate(aa)),'positive dual ray')
    flats = cert['flat_roots']
    need(len(flats) == 8,'eight flat representatives')
    counts = []
    for j,w in enumerate(weights):
        indices = [i for i,r in enumerate(rr) if dot(r,w) == 0]
        need(vector(flats[j],len(indices)) and flats[j] == indices,'exact flat root set')
        need(rank([rr[i] for i in indices]) == 7,'root-spanned hyperplane')
        need(len(indices)%2 == 0,'antipodal flat roots')
        counts.append(len(indices)//2)
    need(sorted(counts) == [14,16,22,23,28,37,42,63],'eight distinct flat line counts')
    return counts


def reflect(x,a):
    return [v-Q(dot(x,a),4)*b for v,b in zip(x,a)]


def chamber_fixture(x,cert):
    aa,rr,weights = cert['simple'],cert['roots'],cert['fundamental_rays']
    rho = [sum(Q(w[k],dot(aa[j],w)) for j,w in enumerate(weights)) for k in range(8)]
    y,seen,steps = list(map(Q,x)),set(),0
    original_rank = rank([r for r in rr if dot(r,x) == 0])
    while any(dot(a,y) < 0 for a in aa):
        need(tuple(y) not in seen,'strict ascent never revisits a state')
        seen.add(tuple(y))
        j = next(j for j,a in enumerate(aa) if dot(a,y) < 0)
        z = reflect(y,aa[j])
        need(dot(rho,z) > dot(rho,y),'strict chamber potential')
        need(dot(z,z) == dot(y,y),'orthogonal reflection')
        y,steps = z,steps+1
        need(steps < 1000,'finite test fixture budget; not a universal algorithm bound')
    zero = [j for j,a in enumerate(aa) if dot(a,y) == 0]
    zero_roots = [r for r in rr if dot(r,y) == 0]
    need(rank(zero_roots) == original_rank == len(zero),'zero-root rank equals chamber face dimension')
    if original_rank == 7:
        j = next(i for i in range(8) if i not in zero)
        w = weights[j]
        factor = Q(dot(aa[j],y),dot(aa[j],w))
        need(factor > 0 and y == [factor*v for v in w],'hyperplane normal reaches one fundamental ray')
    return dict(zero_rank=original_rank,reflections=steps,zero_lines=len(zero_roots)//2)


def controls(cert):
    out = []
    def reject(label,mutant,expected):
        try:
            check(mutant)
        except ValueError as error:
            need(expected in str(error),label+': wrong failure boundary: '+str(error))
            out.append(label)
        else:
            raise ValueError(label+': mutant accepted')
    m = deepcopy(cert); m['roots'].pop()
    reject('missing_root',m,'240-root alphabet')
    # Flipping one basis root preserves its reflection and every reconstruction,
    # but is not a positive system: some valid root expansions have mixed signs.
    m = deepcopy(cert); m['simple'][0] = [-x for x in m['simple'][0]]
    for c in m['coefficients']: c[0] *= -1
    reject('basis_is_not_a_positive_system',m,'sign-coherent')
    m = deepcopy(cert); m['coefficients'][0][0] += 1
    reject('false_root_expansion',m,'reconstructs root')
    m = deepcopy(cert); m['reflections'][0][0],m['reflections'][0][1] = m['reflections'][0][1],m['reflections'][0][0]
    reject('wrong_but_bijective_root_permutation',m,'reflection image')
    m = deepcopy(cert); m['fundamental_rays'][0] = [-x for x in m['fundamental_rays'][0]]
    reject('negative_dual_ray',m,'positive dual ray')
    m = deepcopy(cert); m['flat_roots'].pop()
    reject('missing_representative',m,'eight flat representatives')
    m = deepcopy(cert); m['coefficients'][0][0] = bool(m['coefficients'][0][0])
    reject('boolean_is_not_integer_evidence',m,'integer expansions')
    return out


def run(cert,files):
    source_roots,simple,types = source_geometry(files[SOURCE])
    need(source_roots == alphabet(),'source/root-alphabet binding')
    counts = check(cert,simple)
    need(set(counts) == set(types),'F6 census representative binding')
    fixtures = []
    for face_size in range(8):
        for seed in range(8):
            omitted = {(seed+k)%8 for k in range(face_size)}
            x = [sum((j+1)*w[k] for j,w in enumerate(cert['fundamental_rays']) if j not in omitted) for k in range(8)]
            for step in range(19+seed):
                x = reflect(x,simple[(step*step+3*seed+step)%8])
            result = chamber_fixture(x,cert)
            need(result['zero_rank'] == face_size,'proper-face fixture rank')
            fixtures.append(result)
    zero = chamber_fixture([0]*8,cert)
    need(zero['zero_rank'] == 8 and zero['zero_lines'] == 120,'zero-normal exclusion')
    return dict(status='PASS_E8_FLAT_CHAMBER_CERTIFICATE',roots=240,positive_roots=120,
                simple_reflection_images=1920,simple_rank=8,flat_line_counts=counts,
                rational_chamber_fixtures=fixtures,zero_normal_control=zero,rejected_mutants=controls(cert),
                scope='Finite hypotheses and rational fixtures; arbitrary-real completeness is the README proof.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--certificate',type=Path,default=P/'certificate.json')
    parser.add_argument('--out',type=Path)
    args = parser.parse_args()
    files = authenticate()  # before evaluating any upstream AST
    result = run(json.loads(args.certificate.read_text(encoding='utf-8')),files)
    if args.out:
        with args.out.open('x',encoding='utf-8',newline='\n') as stream:
            json.dump(result,stream,indent=2)
            stream.write('\n')
    else:
        saved = json.loads((P/'RESULT.json').read_text(encoding='utf-8'))
        need(json.dumps(saved,sort_keys=True) == json.dumps(result,sort_keys=True),'committed receipt replay')
    print(result['status'])
    print(json.dumps({k:v for k,v in result.items() if k != 'rational_chamber_fixtures'},separators=(',',':')))


if __name__ == '__main__':
    main()
