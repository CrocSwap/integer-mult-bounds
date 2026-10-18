#!/usr/bin/env python3
"""Three fixed helper-shear compositions on the pinned 11,500-ADD R439 word.

Own exact F2, literal COPY/ERASE, positive bounds and frame-rank counting;
no predecessor executable or pending work is imported or run.
ToikY with substantial OpenAI Codex assistance. Apache-2.0.
"""
import argparse
from collections import Counter
import copy
import gzip
import hashlib
import json
from math import gcd
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = 'c4e06b3822987b4272c70ff82ae1c84773ee4426'
WORD = 'research/r439-bsection-stars-seed01/candidate.json.gz'
ORIGINAL = 'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz'
A, B = 277, 434
PROFILE = {1:1323, 2:1342, 3:79, 4:44, 5:102, 6:11, 7:19}


class Reject(ValueError):
    pass


def need(ok, message):
    if not ok:
        raise Reject(message)


def typed(x):
    if type(x) is dict:
        return ('dict', tuple((k, typed(v)) for k, v in sorted(x.items())))
    if type(x) is list:
        return ('list', tuple(typed(v) for v in x))
    need(type(x) in (str, int, bool, type(None)), 'exact JSON types')
    return type(x).__name__, x


def load_json(raw):
    def pairs(items):
        obj = {}
        for k, v in items:
            need(k not in obj, 'duplicate JSON key')
            obj[k] = v
        return obj
    obj = json.loads(raw, object_pairs_hook=pairs)
    typed(obj)
    return obj


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':')).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def digest(x):
    return sha(canonical(x))


def input_word():
    manifest = load_json((HERE/'SOURCES.json').read_bytes())
    need(type(manifest['schema_version']) is int and manifest['schema_version'] == 1 and manifest['base_commit'] == BASE, 'source schema/base')
    seen, raw = set(), {}
    for entry in manifest['files']:
        p = entry['path']
        need(p not in seen, 'unique source path')
        seen.add(p)
        if p in (WORD, ORIGINAL):
            need(entry['usage'] == 'input', 'required word source usage')
        if entry['usage'] == 'provenance':
            continue
        need(entry['usage'] == 'input', 'source usage')
        path = (ROOT/p).resolve()
        need(path.is_relative_to(ROOT), 'source path inside repository')
        data = path.read_bytes()
        blob = hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        need(sha(data) == entry['sha256'] and blob == entry['git_blob'], 'source SHA256/Git blob: '+p)
        raw[p] = data
    need(WORD in raw and ORIGINAL in raw, 'pinned baseline and original word inputs')
    return load_json(gzip.decompress(raw[WORD])), load_json(gzip.decompress(raw[ORIGINAL]))


def shear():
    return [0, A, [B]]


def correct_sources(gate):
    f, d, sources = gate
    ss = set(sources)
    if A in ss:
        ss.symmetric_difference_update({B})
    return [f, d, sorted(ss)]


def conjugated_body(word):
    out = []
    for f, d, sources in word['D']:
        if d != B:
            g = correct_sources([f, d, sources])
            if g[2]:
                out.append(g)
        else:
            for s in sources:
                if s == A:
                    # G E_(B,A) G is the two-role swap, not one ADD.
                    out.extend([[0,A,[B]], [0,B,[A]], [0,A,[B]]])
                else:
                    out.extend([[0,A,[s]], [0,B,[s]]])
    return out


def cuts(word):
    D, v = word['D'], word['v']
    n = 0
    while n < len(D) and D[n][1] >= 2*v:
        n += 1
    need(n == 236, '236 literal helper preparations')
    h, e, m, er, hr = D[:n], D[n:n+306], D[n+306:n+417], D[n+417:-n], D[-n:]
    need(len(m) == v and [g[1] for g in m] == list(range(v,2*v)), 'literal middle target rows')
    need(er == list(reversed(e)) and hr == list(reversed(h)), 'literal reverse target/helper restoration')
    need(all(d >= 2*v and len(ss) == 1 for _,d,ss in h), 'elementary helper preparations')
    need(all(v <= d < 2*v and all(v <= s < 2*v for s in ss) for _,d,ss in e), 'target basis preparations')
    need(all(all(s >= 2*v for s in ss) for _,_,ss in m), 'middle helper readers')
    return h, e, m, er, hr


def variants(word):
    need((word['v'],word['R'],word['h']) == (111,439,8), 'baseline dimensions')
    h,e,m,er,hr = cuts(word)
    naive = copy.deepcopy(word)
    naive['D'] = [shear()] + [correct_sources(g) if 111 <= g[1] < 222 else copy.deepcopy(g) for g in word['D']] + [shear()]
    whole = copy.deepcopy(word)
    whole['D'] = [shear()] + conjugated_body(word) + [shear()]
    middle = copy.deepcopy(word)
    middle['D'] = copy.deepcopy(h) + [shear()] + copy.deepcopy(e) + [correct_sources(g) for g in m] + copy.deepcopy(er) + [shear()] + copy.deepcopy(hr)
    return dict(baseline=word, naive_entry=naive, whole_prefix=whole, middle_wrap=middle)


def check_gates(word):
    n, v = 2*word['v']+word['R'], word['v']
    for section in ('D','A','B','C'):
        for f,d,ss in word[section]:
            need(type(f) is int and 0 <= f < len(word['frames']), 'valid gate frame')
            need(ss and all(type(r) is int and 0 <= r < n for r in [d]+ss), 'valid gate operands')
            need(len(set([d]+ss)) == len([d]+ss), 'distinct gate operands')
            if section == 'D':
                need(f == 0 and all(r >= v for r in [d]+ss), 'zero-frame target/helper D')
                if d >= 2*v:
                    need(all(s >= 2*v for s in ss), 'H2-sem forbids target-to-helper feedback in D')


def d_rows(word):
    check_gates(word)
    rows = [1 << r for r in range(2*word['v']+word['R'])]
    for _,d,ss in word['D']:
        for s in ss:
            rows[d] ^= rows[s]
    return rows


def stream(word):
    ops = [('add',d,s) for sec in ('D','A') for _,d,ss in word[sec] for s in ss]
    tmp = 2*word['v']+word['R']
    for j,c in enumerate(word['ret']):
        ops.append(('copy',tmp,c))
        ops.extend(('add',word['v']+t,tmp) for t,row in enumerate(word['scatter']) if j in row)
        ops.append(('erase',tmp,c))
    ops.extend(('add',d,s) for sec in ('B','C') for _,d,ss in word[sec] for s in ss)
    return ops


def execute(ops, n, reverse=False, positive=False):
    rows = [1]*n+[0] if positive else [1 << r for r in range(n)]+[0]
    peak = 1
    for kind,d,s in (reversed(ops) if reverse else ops):
        if reverse:
            kind = {'copy':'erase','erase':'copy'}.get(kind,kind)
        if kind == 'add':
            rows[d] = rows[d]+rows[s] if positive else rows[d]^rows[s]
        elif kind == 'copy':
            need(rows[d] == 0, 'COPY destination must be clear')
            rows[d] = rows[s]
        elif kind == 'erase':
            need(rows[d] == rows[s], 'ERASE copy must equal its source')
            rows[d] = 0
        else:
            raise Reject('literal opcode')
        if positive:
            peak = max(peak, rows[d])
    need(rows[-1] == 0, 'literal scratch restored')
    return peak if positive else rows[:-1]


def first_difference(actual, expected):
    need(len(actual) == len(expected), 'matrix shape equality')
    for output,(a,b) in enumerate(zip(actual,expected)):
        if a != b:
            column = ((a^b)&-(a^b)).bit_length()-1
            return dict(output_role=output, input_column=column, actual=(a >> column)&1, expected=(b >> column)&1)
    return None


def integer_rank(rows):
    """Rational rank by integer elimination and primitive row normalization."""
    basis = []
    for original in rows:
        row = list(original)
        for p,b in basis:
            if row[p]:
                lead = row[p]
                row = [x*b[p]-y*lead for x,y in zip(row,b)]
                factor = 0
                for x in row:
                    factor = gcd(factor,abs(x))
                if factor:
                    row = [x//factor for x in row]
        p = next((i for i,x in enumerate(row) if x),None)
        if p is not None:
            basis.append((p,row))
    return len(basis)


def frame_bill(word):
    dimensions = [integer_rank([word['lines'][i] for i in f]) for f in word['frames']]
    frames = [set(f) for f in word['frames']]
    cur = list(word['start'])
    paths = [[f] for f in cur]
    counts = Counter()
    def move(r,f):
        if cur[r] != f:
            old = cur[r]
            need(frames[old] < frames[f] and dimensions[old] < dimensions[f], 'nested positive frame climb')
            counts[dimensions[f]-dimensions[old]] += 1
            paths[r].append(f)
            cur[r] = f
    def section(name):
        for f,d,ss in word[name]:
            for r in [d]+ss:
                move(r,f)
    section('D');section('A')
    copies = [dimensions[cur[r]] for r in word['ret']]
    counts.update(copies)
    section('B');section('C')
    for r,f in enumerate(word['final']):
        move(r,f)
    return dict(profile={str(k):v for k,v in sorted(counts.items())}, mass=sum(k*v for k,v in counts.items()), copy_ranks=copies, ordered_paths_sha256=digest(paths)), paths


def precision(F,B):
    local, nine = 64*F**3*B**2, (1 << 18)*F**5*B**4
    return dict(local_bound=str(local), nine_stage_bound=str(nine), local_bits=local.bit_length(), nine_stage_bits=nine.bit_length(), local_guard=local < 1 << 104, nine_stage_guard=nine < 1 << 192)


def price(word):
    ops, n = stream(word), 2*word['v']+word['R']
    F = execute(ops,n,positive=True)
    B_ = execute(ops,n,reverse=True,positive=True)
    return dict(ADDs=sum(k == 'add' for k,_,_ in ops), D_ADDs=sum(len(ss) for _,_,ss in word['D']), COPYs=sum(k == 'copy' for k,_,_ in ops), ERASEs=sum(k == 'erase' for k,_,_ in ops), F=F, B=B_, **precision(F,B_))


def virtual_flags(word):
    """Separate finite checks of the inherited scalar-interface premises."""
    v = word['v']
    is_y = lambda r: v <= r < 2*v
    full = next(i for i,f in enumerate(word['frames']) if integer_rank([word['lines'][j] for j in f]) == 8)
    raw = copy.deepcopy(word);raw['D']=[];raw['C']=[]
    rows = execute(stream(raw),661)
    ym = ((1 << v)-1) << v
    xm = (1 << v)-1
    hm = ((1 << word['R'])-1) << (2*v)
    D = d_rows(word)
    cleanup = [[full,d,list(ss)] for sec in ('A','B') for _,d,ss in word[sec] if not is_y(d)]
    flags = dict(
        H1_no_target_feeds_z=not any(not is_y(d) and any(is_y(s) for s in ss) for sec in ('D','A','B','C') for _,d,ss in word[sec]),
        H2_original_D=all(f == 0 and is_y(d) and all(s >= 2*v for s in ss) for f,d,ss in word['D']),
        H3_split=all(not is_y(d) for _,d,_ in word['A']) and all(r >= 2*v for r in word['ret']) and all(is_y(d) or not any(is_y(s) for s in ss) for _,d,ss in word['B']),
        H4_literal_cleanup=word['C'] == list(reversed(cleanup)),
        H5_target_identity=all(rows[v+t]&ym == 1 << (v+t) for t in range(v)),
        U_no_target_columns=all(rows[r]&ym == 0 for r in range(661) if not is_y(r)),
        J_source_identity=all(rows[v+t]&xm == 1 << t for t in range(v)),
        K_semantic_equals_original_D=all(rows[v+t]&hm == D[v+t]&hm for t in range(v)),
    )
    restored = list(rows)
    for _,d,ss in word['C']:
        for s in ss:
            restored[d] ^= restored[s]
    flags['C_restores_raw_z'] = all(restored[r] == 1 << r for r in range(661) if not is_y(r))
    need(all(flags.values()), 'virtual splice inherited scalar flags')
    return flags


def controls(word, built, expected):
    out = []
    def bad(name, changed):
        difference = first_difference(d_rows(changed),expected)
        need(difference is not None, 'ineffective boundary control: '+name)
        out.append(dict(name=name, rejected=True, witness=difference))
    bad('naive entry and target-only correction',built['naive_entry'])
    q = copy.deepcopy(built['whole_prefix']);q['D'].pop();bad('omitted exit shear',q)
    q = copy.deepcopy(built['whole_prefix']);q['D'][-1]=[0,A,[B+1]];bad('wrong exit donor',q)
    q = copy.deepcopy(built['whole_prefix'])
    body = q['D'];index = next(i for i in range(1,len(body)-2) if body[i][1] == A and body[i+1][1] == B and body[i][2] == body[i+1][2] and body[i][2] != [B])
    del body[index];bad('omitted conjugated helper correction',q)
    q = copy.deepcopy(built['whole_prefix']);index = next(i for i,g in enumerate(q['D']) if 111 <= g[1] < 222 and A in g[2])
    ss = set(q['D'][index][2]);ss.symmetric_difference_update({B});q['D'][index][2]=sorted(ss);bad('wrong target source correction',q)
    h,e,m,er,hr = cuts(word)
    q = copy.deepcopy(word);q['D']=h+[shear()]+e+[shear()]+[correct_sources(g) for g in m]+er+hr;bad('restoration before dependent middle reads',q)
    ops = stream(built['whole_prefix']);del ops[next(i for i,e in enumerate(ops) if e[0] == 'erase')]
    try:
        execute(ops,661)
    except Reject as error:
        out.append(dict(name='omitted literal ERASE',rejected=True,predicate=str(error)))
    else:
        raise Reject('omitted ERASE control accepted')
    return out


def compute():
    word, original = input_word()
    built = variants(word)
    base_d = d_rows(word)
    expected = [1 << r for r in range(661)]
    for t in range(111):
        expected[111+t] ^= 1 << t
    need(d_rows(original) == base_d, 'parent D equals original PR589 complete dirty map')
    virtual = copy.deepcopy(word);virtual['D']=copy.deepcopy(original['D'])
    need(all(virtual[k] == word[k] for k in word if k != 'D'), 'virtual continuation byte equality')
    need(execute(stream(virtual),661) == expected and execute(stream(virtual),661,reverse=True) == expected, 'virtual splice full dirty endpoints')
    flags = virtual_flags(virtual)
    base_frame, base_paths = frame_bill(word)
    need(base_frame['profile'] == {str(k):v for k,v in PROFILE.items()} and base_frame['mass'] == 5129 and base_frame['copy_ranks'] == [7]*9, 'baseline paid profile')
    report = {}
    for name,candidate in built.items():
        for key in word:
            if key != 'D':
                need(candidate[key] == word[key], 'only D may change')
        framed, paths = frame_bill(candidate)
        need(paths == base_paths and framed == base_frame, 'unchanged ordered frame paths/COPY profile')
        boundary = first_difference(d_rows(candidate),base_d)
        fwd = execute(stream(candidate),661)
        back = execute(stream(candidate),661,reverse=True)
        forward_difference, backward_difference = first_difference(fwd,expected), first_difference(back,expected)
        bill = price(candidate)
        need(bill['local_guard'] and bill['nine_stage_guard'], 'complete positive precision guards')
        if name == 'naive_entry':
            need(boundary is not None and forward_difference is not None and backward_difference is not None, 'naive variant must fail actual dirty operators')
        else:
            need(boundary is None and forward_difference is None and backward_difference is None, 'correct variant exact dirty endpoints')
        report[name] = dict(word_sha256=digest(candidate), d_boundary_equal=boundary is None, d_witness=boundary, forward_equal=forward_difference is None, backward_equal=backward_difference is None, forward_witness=forward_difference, backward_witness=backward_difference, all_input_columns=661, forward_matrix_sha256=digest(fwd), backward_matrix_sha256=digest(back), bill=bill, paid=framed)
    need(report['baseline']['bill']['ADDs'] == 11500 and report['baseline']['bill']['F'] == 25717 and report['baseline']['bill']['B'] == 5911840, 'literal baseline inventory')
    return dict(status='PASS_R439_FIXED_COPYSHARE_STAR_COMPOSITION', fixed_pair=[A,B], baseline_helper_preparations=236, virtual_original_D_splice=dict(original_word_sha256=digest(original), parent_D_equal=True, continuation_unchanged=True, scalar_flags=flags, full_dirty_columns=661, fresh_full_xcheck=False, root_lattice_geometry='REUSED_PREDECESSOR'), variants=report, controls=controls(word,built,base_d), scope='Three fixed zero-frame D substitutions; exact dirty scalar/COPY boundaries and inherited precision bills only. No new supplier, physical hosted replay, all-size compiler, optimum, or kappa.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-result',type=Path)
    args = parser.parse_args()
    if args.write_result is not None:
        need(not args.write_result.exists() and not args.write_result.resolve().is_relative_to(ROOT), 'fresh external result only')
    result = compute()
    if args.write_result is None:
        need(typed(load_json((HERE/'RESULT.json').read_bytes())) == typed(result), 'strict committed RESULT equality')
    else:
        with args.write_result.open('x') as f:
            f.write(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(result['status'],'correct_whole=+9','correct_middle=+3','naive=INVALID','columns=661','profile_mass=5129')


if __name__ == '__main__':
    main()
