"""Width-one event9896 in-place numerical child with clean swap scratch.

The actual Gaussian pair implementation belongs to Ali Romman/PR6509 and
its retained lineage. The new interface binds selected event9896 and6499.
This is an indexed bounded-word reference, not a fixed-tape bit circuit.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import types

HERE = Path(__file__).resolve().parent
MANIFEST = 'c9847104b61030a74b416a550f72dfa24a3fda660fa7d21fef4593e7fb307936'
SIZE = 512


def need(condition, message):
    if not condition:
        raise ValueError(message)


def strict(data):
    def pairs(items):
        out = {}
        for k,v in items:
            need(k not in out,'duplicate JSON key')
            out[k] = v
        return out
    def bad(value):
        raise ValueError('nonfinite JSON '+value)
    return json.loads(data,object_pairs_hook=pairs,parse_constant=bad)


def authenticate():
    raw = (HERE/'SOURCE-PINS.json').read_bytes()
    need(hashlib.sha256(raw).hexdigest() == MANIFEST,'SOURCE-PINS digest')
    pins = strict(raw)
    need(type(pins['schema_version']) is int and pins['schema_version'] == 1,'pin schema')
    need(len(pins['files']) == 6,'six source files')
    out = {}
    for row in pins['files']:
        path = row['path']
        need(path.startswith('inputs/') and '..' not in path and path not in out,'source path')
        data = (HERE/path).read_bytes()
        need(type(row['bytes']) is int and len(data) == row['bytes'],'source bytes')
        need(hashlib.sha256(data).hexdigest() == row['sha256'],'source SHA256')
        need(hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest() == row['git_blob'],'source Git blob')
        out[path] = data
    return out


def load_source(path, name, files):
    module = types.ModuleType(name)
    module.__file__ = str(HERE/path)
    sys.modules[name] = module
    # Execute the authenticated bytes, never a stale source-adjacent pyc.
    exec(compile(files[path],module.__file__,'exec',optimize=0),module.__dict__)
    return module


def prefix_binding(data):
    w = strict(gzip.decompress(data))
    need(type(w['public']) is int and w['public'] == 770,'public input count')
    need(w['initial'][236] == w['initial'][720] == 3,'public initial frame')
    need(w['frames'][3] == [] and w['frames'][7] == [21],'literal frames')
    need(w['program'][9896] == ['MOVE',236,3,7,False],'literal selected MOVE')
    prefix = w['program'][:9896]
    need(set(e[0] for e in prefix) == {'ADD','INIT','SCALE'},'complete prefix opcode/write grammar')
    prefix_grammar(w,prefix)
    a = [[i,e] for i,e in enumerate(prefix) if e[1] == 236]
    b = [[i,e] for i,e in enumerate(prefix) if e[1] == 720]
    need(a == [[8203,['ADD',236,720,'-2',3]]] and b == [],'complete public write census')
    need(all(e[1] >= 770 for e in prefix if e[0] == 'INIT'),'owned/public disjoint')
    return {'event':9896,'literal_event':['MOVE',236,3,7,0],
            'prefix_opcodes':['ADD','INIT','SCALE'],'writes236':a,'writes720':b,
            'entrance':'initial236-2*initial720','source_frame':[],'target_frame':[21]}


def prefix_grammar(w,prefix):
    from fractions import Fraction as F
    owned = w['owned_fields']
    need(type(owned) is int and 0 < owned <= 29,'owned/public role inventory')
    need(len(w['initial']) == 770,'complete public initial header')
    frame_ok = lambda f:type(f) is int and 0 <= f < len(w['frames'])
    need(all(frame_ok(f) for f in w['initial']),'initial frame types')
    need(all(type(b) is list and all(type(x) is int and 0<x<512 for x in b) for b in w['frames']),'frame basis grammar')
    current = list(w['initial'])+[None]*owned
    for e in prefix:
        need(type(e) is list and e[0] in ('ADD','INIT','SCALE'),'prefix record grammar')
        op,r = e[:2]
        need(type(r) is int and 0 <= r < 770+owned,'destination role type/range')
        need(len(e) == {'ADD':5,'SCALE':4,'INIT':3}[op],'prefix record length')
        need(frame_ok(e[-1]),'prefix frame type/range')
        if op == 'INIT':
            need(r >= 770 and current[r] is None,'fresh owned initialization')
            current[r] = e[-1]
            continue
        need(current[r] == e[-1],'prefix destination common frame')
        need(type(e[-2]) is str and str(F(e[-2])) == e[-2] and F(e[-2]) != 0,'literal nonzero exact coefficient')
        if op == 'ADD':
            s = e[2]
            need(type(s) is int and 0 <= s < 770+owned and s != r,'source role type/range')
            need(current[s] == e[-1],'prefix source common frame')
    need(current[236] == current[720] == 3,'actual child entrance frames')


def rotate(pair, phase):
    a,b = pair
    return ((a,b),(-b,a),(-a,-b),(b,-a))[phase%4]


def address(rows, value):
    return sum(((r&value).bit_count()&1)<<j for j,r in enumerate(rows))


def quadratic(Q, alpha, value):
    out = sum(alpha[j] for j in range(9) if value>>j&1)
    out += 2*sum(((Q[i]>>j)&1) for i in range(9) for j in range(i+1,9)
                 if value>>i&1 and value>>j&1)
    return out%4


def source_plan(files):
    need(sys.flags.optimize == 0,'frozen compiler must run in normal child Python')
    c = load_source('inputs/clifford_exact.py','event9896_frozen_compiler',files)
    op = c.canonical_frame(9,[21])
    circuit = op.circuit
    need([e[0] for e in circuit] == ['D','P','C','P','D'],'literal canonical circuit shape')
    G,Q,alpha = list(circuit[3][1]),list(circuit[4][1]),list(circuit[4][2])
    need(G == [3,4,9,16,1,32,64,128,256],'source monomial G')
    need(Q == [16,0,16,0,5,0,0,0,0] and alpha == [0]*9,'source monomial phase')
    need(circuit[2] == ('C',1,1),'positive bit-zero Gaussian')
    need(list(circuit[1][1]) == [16,17,2,20,8,32,64,128,256],'source inverse permutation')
    columns = []
    from fractions import Fraction as F
    for z in range(SIZE):
        vector,den = op.zero_state(z)
        eta = -1 if ((z&5).bit_count()&1) else 1
        expected = {z:(F(1,2),F(1,2)),z^21:(F(eta,2),F(-eta,2))}
        actual = {i:(F(a,1<<den),F(b,1<<den)) for i,(a,b) in enumerate(vector) if a or b}
        need(actual == expected,'all512 ideal columns including global phase')
        columns.append([[i,[str(v[0]),str(v[1])]] for i,v in sorted(actual.items())])
    encoded = json.dumps(columns,sort_keys=True,separators=(',',':'))+'\n'
    routes = route_descriptor(G,Q,alpha)
    return {'G':G,'Q':Q,'alpha':alpha,'routes':routes,'ideal_columns_sha256':hashlib.sha256(encoded.encode()).hexdigest(),
            'ideal_columns':512,'compiler_optimization':0,'binding':prefix_binding(files['inputs/WORD.json.gz'])}


def get_plan():
    result = subprocess.run([sys.executable,'-I','-Werror','-B',str(HERE/'child.py'),'--source-plan'],
                            check=True,capture_output=True,timeout=40)
    need(not result.stderr,'source-plan stderr')
    return strict(result.stdout)


def bump(trace,key,amount=1):
    trace[key] = trace.get(key,0)+amount


def word(value,width,trace):
    need(type(value) is int and -(1<<(width-1)) <= value < 1<<(width-1),'bounded signed word')
    bump(trace,'interface_signed_checks')
    return value


def route_descriptor(G,Q,alpha):
    permutation = [address(G,x) for x in range(SIZE)]
    need(sorted(permutation) == list(range(SIZE)),'source monomial permutation')
    seen,cycles = set(),[]
    for start in range(SIZE):
        if start in seen:
            continue
        cycle,x = [],start
        while x not in seen:
            seen.add(x);cycle.append(x);x=permutation[x]
        need(x == start,'closed permutation cycle')
        cycles.append(cycle)
    forward = [quadratic(Q,alpha,permutation[x]) for x in range(SIZE)]
    inverse = [(-quadratic(Q,alpha,x))%4 for x in range(SIZE)]
    return {'cycles_G':cycles,'phase_K':forward,'phase_Kdag':inverse}


def monomial_inplace(values,routes,inverse,width,trace,omit_final_swap=False):
    bump(trace,'monomial_passes')
    phases = routes['phase_Kdag'] if inverse else routes['phase_K']
    for i,phase in enumerate(phases):
        a,b = values[i]
        value = rotate((a,b),phase)
        values[i] = tuple(word(v,width,trace) for v in value)
        bump(trace,'phase_coordinate_visits')
        bump(trace,'phase_program_reads')
        bump(trace,'phase_component_reads',2);bump(trace,'phase_component_writes',2)
        bump(trace,'phase_component_negations',int(phase in (1,2))+int(phase in (2,3)))
    scratch = (0,0)
    for original in routes['cycles_G']:
        bump(trace,'cycle_header_reads')
        length = len(original)
        if length == 1:
            bump(trace,'route_index_reads')
            continue
        for position in range(length if omit_final_swap else length+1):
            index = original[(-position if inverse else position)%length]
            values[index],scratch = scratch,values[index]
            bump(trace,'gaussian_swaps')
            bump(trace,'route_index_reads')
            bump(trace,'swap_component_reads',4);bump(trace,'swap_component_writes',4)
        need(scratch == (0,0),'Gaussian swap scratch returned zero after each cycle')
    return scratch


def conversion(values,p,to_coarse,trace):
    for i,pair in enumerate(values):
        out = []
        for v in pair:
            if to_coarse:
                word(v,p+16,trace)
                need(v%32 == 0,'actual entrance must be coarse-grid aligned')
                v //= 32
                bump(trace,'exact_input_right_shifts')
                word(v,p+21,trace)
            else:
                v = word(v<<5,p+16,trace)
                bump(trace,'exact_output_left_shifts')
            out.append(v)
        values[i] = tuple(out)
        bump(trace,'conversion_component_reads',2);bump(trace,'conversion_component_writes',2)


def execute(fine,p,plan,kernel,adjoint=False,fault=None):
    need(type(p) is int and p >= 14,'p=t+14 with t nonnegative')
    need(type(adjoint) is bool,'literal forward or inverse direction')
    need(type(fine) is list and len(fine) == SIZE and all(len(z)==2 for z in fine),'512 complex input records')
    need(all(type(v) is int for z in fine for v in z),'integer input records')
    need(all(-(1<<(p+15)) <= v < 1<<(p+15) for z in fine for v in z),'incoming record range')
    need(all(v%32 == 0 for z in fine for v in z),'coarse aligned entrance')
    accumulator = 0
    for z in fine:
        for v in z:
            product = (v//32)**2
            need(0 <= product < 1<<(2*p+21),'finite norm product width')
            accumulator += product
            need(0 <= accumulator < 1<<(2*p+31),'finite norm accumulator width')
    limit_square = (3*(1<<p)+(64 if adjoint else 48))**2
    need(0 <= limit_square < 1<<(2*p+31),'finite norm cap-square width')
    need(accumulator <= limit_square,'actual entrance norm bound')
    trace = {'workspace_word_bits':p+21,'record_word_bits':p+16,
             'clean_scratch_field_banks':0,'clean_return_field_banks':0,
             'swap_scratch_words':2,'swap_initialization_bits':2*(p+21),
             'pair_temporary_word_stock':8,'pair_temporary_control_bits':'constant',
             'pair_temporary_cleanup':'retained indexed arithmetic bit-write model; no reversible bit circuit',
             'admission_component_range_tests':1024,'admission_component_alignment_tests':1024,
             'admission_component_exact_right_shifts':1024,'admission_component_squares':1024,
             'admission_norm_accumulator_additions':1024,
             'admission_norm_product_bits':2*p+21,'admission_norm_accumulator_bits':2*p+31,
             'admission_norm_cap_squares':1,'admission_norm_cap_additions':1,
             'admission_norm_cap_constant_multiplications':1,
             'guarded_reference_bit_work_bound':'O(512*(p+21)^2); core transform O(512*(p+21))',
             'read_only_route_phase_descriptor_bits_bound':21504,
             'read_only_G_Q_alpha_bits_bound':243,
             'route_generation_address_parities':512*9,
             'route_generation_phase_pair_tests':2*512*36,
             'route_generation_phase_linear_tests':2*512*9,
             'route_generation_and_decode':'charged fixed descriptor preparation; no free route oracle'}
    width = p+21
    conversion(fine,p,True,trace)
    scratch = monomial_inplace(fine,plan['routes'],True,width,trace,fault=='omit-final-swap')
    native = {}
    kernel.layer(fine,0,width,-1 if adjoint else 1,native)
    if fault != 'omit-K':
        scratch = monomial_inplace(fine,plan['routes'],False,width,trace)
    conversion(fine,p,False,trace)
    need(scratch == (0,0),'final swap scratch zero')
    trace['swap_scratch_final'] = list(scratch)
    trace['kernel'] = native
    trace['pair_real_reads'] = trace['pair_real_writes'] = 4*native['butterflies']
    trace['pair_temporary_initialization_and_clear_bit_writes_bound'] = 16*width*native['butterflies']
    return fine,trace


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-plan',action='store_true')
    args = parser.parse_args()
    files = authenticate()
    need(args.source_plan,'use verify.py for the numerical contract')
    print(json.dumps(source_plan(files),sort_keys=True,indent=2))


if __name__ == '__main__':
    main()
