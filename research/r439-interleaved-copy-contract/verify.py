#!/usr/bin/env python3
"""Bind PR2407 to PR1627's ideal hosted-stream theorem, with explicit reuse.

Ross Richardson, with substantial OpenAI Codex assistance. Apache-2.0.
No compiler, recursive-work allocation, new generic theorem or kappa claim.
"""
import argparse
from collections import Counter
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import struct
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
AUDIT = 'research/pr589-five-helper-hosting/verify.py'
GEOMETRY_KEYS = ('v', 'R', 'h', 'lines', 'frames', 'start', 'final', 'ret')


def need(ok, message):
    if not ok:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def encoded(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':')).encode()


def pin_check():
    source = json.loads((HERE/'SOURCES.json').read_text())
    predecessor = json.loads((HERE/'PREDECESSOR.json').read_text())
    pins = [p for p in source['files'] if p['usage'] == 'input']
    pins += predecessor['pr2407_files']
    for p in pins:
        raw = (ROOT/p['path']).read_bytes()
        need(digest(raw) == p['sha256'], 'source SHA256: '+p['path'])
        blob = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        need(blob == p['git_blob'], 'source Git blob: '+p['path'])
    return {p['path']: p['sha256'] for p in pins}


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def programs(raw, dims):
    """Translate documented RAW6 to the predecessor's event schema."""
    answer = {}
    for rev in (False, True):
        es = []
        for op, a, b, c, f, phase in (reversed(raw) if rev else raw):
            if op == 0:
                es.append([0, a, c if rev else b, b if rev else c, f, int(rev)])
            elif op == 1:
                es.append([1, a, b, -c if rev else c, f, int(rev)])
            elif op == (3 if rev else 2):
                es.append([2, a, b, c, f, abs(dims[c]-dims[f]), int(rev)])
            elif op == (2 if rev else 3):
                es.append([3, a, b, c, f, phase, int(rev)])
            else:
                raise ValueError('unknown RAW6 opcode')
        answer['reverse' if rev else 'forward'] = es
    return answer


def window_contract(raw, w):
    """A stronger sufficient contract for this fixed witness, not an iff."""
    n = 2*w['v']+w['R']
    begin = next(i for i,e in enumerate(raw) if e[0] == 2 and e[1] == 472)
    end = next(i for i in range(begin+1,len(raw)) if raw[i][0] == 3)
    need(tuple(raw[begin]) == (2,472,n,510,0,7), 'exact COPY transport')
    need(tuple(raw[end]) == (3,472,n,510,0,0), 'exact ERASE transport')
    targets = set(range(w['v'],2*w['v']))
    touched, taps, undo = set(), [], []
    for op,dst,src,c,f,phase in raw[begin+1:end]:
        need(op == 1, 'interior has an address child or lifecycle event')
        need(dst in targets and src in targets | {n}, 'non-target write or non-snapshot read')
        need(dst != src and c == 1 and f == 0, 'interior common-frame elementary ADD')
        touched.add(dst)
        if src == n:
            need(phase == 3, 'tap provenance')
            taps.append([len(undo),dst-w['v']])
        else:
            need(phase == 4, 'undo provenance')
            touched.add(src)
            undo.append([dst,src])
    need(len(undo) == 303 and len(taps) == 10, 'complete window inventory')
    need({472,n}.isdisjoint(touched), 'reserved source/slot modified')
    return dict(copy_record_index=begin, erase_record_index=end,
                interior_records=end-begin-1, target_undo_ADDs=len(undo),
                snapshot_taps=taps, target_roles_touched=sorted(touched),
                copied_source=472, private_role=n, source_frame=510,
                temporary_frame=0, relative_copy_rank=7,
                interior_address_children=0, interior_source_or_slot_writes=0)


def rebind(template, progs, raw_hash):
    adapted = copy.deepcopy(template)
    adapted['local_programs'] = progs
    adapted['source_record_sha256'] = raw_hash
    hashes = {k:digest(json.dumps(es,separators=(',',':')).encode()) for k,es in progs.items()}
    for call in adapted['calls']:
        call['local_hash'] = hashes[call['orientation']]
    return adapted, hashes


def check_binding(original, adapted, progs, raw_hash):
    need(adapted['local_programs'] == progs, 'local-program binding')
    need(adapted['source_record_sha256'] == raw_hash, 'RAW6 binding')
    for old,new in zip(original['calls'],adapted['calls'],strict=True):
        need({k:v for k,v in old.items() if k != 'local_hash'} ==
             {k:v for k,v in new.items() if k != 'local_hash'}, 'owner descriptor changed')
        expected = digest(json.dumps(progs[new['orientation']],separators=(',',':')).encode())
        need(new['local_hash'] == expected, 'stale call program hash')
    excluded = {'local_programs','source_record_sha256','calls'}
    need({k:v for k,v in original.items() if k not in excluded} ==
         {k:v for k,v in adapted.items() if k not in excluded}, 'host schedule or geometry changed')


def alias_control():
    """A restored borrowed snapshot can still corrupt an intervening read."""
    count, witness = 0, None
    for source in (0,1):
        for target in (0,1):
            for dirt in (0,1):
                private = source
                private ^= dirt
                out = target ^ private
                private ^= dirt
                private ^= source
                need(private == 0, 'alias control must still close work')
                if out != target ^ source:
                    count += 1
                    if witness is None:
                        witness = dict(source=source,target=target,dirt=dirt,
                                       actual=out,expected=target ^ source,final_private=private)
    need(count == 4, 'alias countermodel not discriminating')
    return dict(domain='all eight binary (source,target,dirt) inputs',
                failing_inputs=count,witness=witness,
                scope='weakened snapshot-preservation implication, not production acceptance')


def run():
    pins = pin_check()
    parent = load_module('pr2407_source',HERE/'inputs/pr2407/verify.py')
    parent.ROOT = ROOT
    audit = load_module('pr1627_source',ROOT/AUDIT)
    data = parent.inputs()
    w = json.loads(gzip.decompress(data[parent.WORD]))
    selected = audit.read(audit.WORD)
    for key in GEOMETRY_KEYS:
        need(w[key] == selected[key], 'selected geometry mismatch: '+key)
    witness = json.loads((parent.HERE/'WITNESS.json').read_text())
    split,rest,matrix,_ = parent.decompose(w,witness)
    with tempfile.TemporaryDirectory(prefix='r439-copy-contract-') as tmp:
        fixed,_ = parent.export(split,data,Path(tmp)/'split')
        raw = parent.interleave(fixed,w,rest,matrix,witness)
    raw_hash = digest(b''.join(struct.pack('<6i',*e) for e in raw))
    previous = json.loads((parent.HERE/'RESULT.json').read_text())
    need(raw_hash == previous['schedules']['interleaved88']['record_sha256'], 'PR2407 exact stream')
    footprint = window_contract(raw,w)
    need(footprint['snapshot_taps'] == witness['taps'], 'ordered tap binding')

    # Explicitly reused PR1627 exact engines, not newly independent code.
    projected = [audit.projection([w['lines'][i] for i in f]) for f in w['frames']]
    ps = [p for p,d in projected]
    dims = [d for p,d in projected]
    need(all(audit.dyadic(p) for p in ps), 'specialization denominator')
    progs = programs(raw,dims)
    local = {ori:audit.local_replay(es,w,ps,dims,ori == 'reverse') for ori,es in progs.items()}
    t,g = audit.read(audit.HOST),audit.read(audit.GEO)
    need(t['geometry_sha256'] == digest((ROOT/audit.GEO).read_bytes()), 'host geometry binding')
    owners,remainder = audit.ownership(t,w,g)
    old_receipt = json.loads((ROOT/'research/pr589-five-helper-hosting/RESULT.json').read_text())
    need(json.loads(json.dumps(owners)) == old_receipt['ownership'], 'unchanged owner census')
    adapted,hashes = rebind(t,progs,raw_hash)
    check_binding(t,adapted,progs,raw_hash)
    total = Counter(remainder)
    for call in adapted['calls']:
        total.update(local[call['orientation']]['profile'])
    need({str(k):v for k,v in sorted(total.items())} == old_receipt['profile'], 'global paid profile')
    need(sum(k*v for k,v in total.items()) == 1808352, 'global rank mass')

    controls = []
    def rejects(name,action,fragments):
        try:
            action()
        except (ValueError,audit.Reject) as exc:
            need(any(f in str(exc) for f in fragments),name+' wrong rejection: '+str(exc))
            controls.append(dict(name=name,reason=str(exc)))
        else:
            raise ValueError('control accepted: '+name)
    start,end = footprint['copy_record_index'],footprint['erase_record_index']
    bad = raw.copy(); gate=list(bad[start+1]); gate[1]=661; bad[start+1]=tuple(gate)
    rejects('write live private snapshot',lambda:window_contract(bad,w),['non-target write'])
    bad = raw.copy(); gate=list(bad[start+1]); gate[1]=472; bad[start+1]=tuple(gate)
    rejects('write copied original',lambda:window_contract(bad,w),['non-target write'])
    bad = raw.copy(); bad.insert(start+1,(0,111,0,1,8,0))
    rejects('unpriced address child inside window',lambda:window_contract(bad,w),['address child'])
    bad = list(raw)
    last_tap = max(i for i in range(start+1,end) if bad[i][0] == 1 and bad[i][2] == 661)
    bad.insert(start+1,bad.pop(last_tap))
    bp = programs(bad,dims)
    rejects('count-preserving tap moved to wrong cut',
            lambda:audit.local_replay(bp['forward'],w,ps,dims),['dirty endpoint'])
    bad = copy.deepcopy(progs['forward']); bad[start][3]=511
    rejects('wrong rank-seven COPY projector',
            lambda:audit.local_replay(bad,w,ps,dims),['stale COPY frame'])
    bad = copy.deepcopy(adapted); bad['calls'][0]['local_hash']=t['calls'][0]['local_hash']
    rejects('stale selected local program bound to new call',
            lambda:check_binding(t,bad,progs,raw_hash),['stale call program hash'])
    bad = copy.deepcopy(adapted); bad['calls'][0]['owners'][111]=bad['calls'][0]['owners'][472]
    rejects('target aliased to copied helper owner',
            lambda:audit.ownership(bad,w,g),['wrong data owner'])
    bad = copy.deepcopy(adapted); bad['private_centre_reserve']=0
    rejects('private reserve silently removed',
            lambda:audit.ownership(bad,w,g),['bank stock'])
    # Seven cut-zero taps commute; their order is not a theorem premise.
    equivalent = list(raw)
    equivalent[start+1:start+8] = list(reversed(equivalent[start+1:start+8]))
    ep = programs(equivalent,dims)
    for ori,es in ep.items():
        audit.local_replay(es,w,ps,dims,ori == 'reverse')
    return dict(status='PASS_R439_INTERLEAVED_COPY_CONTRACT',
        domain='PR1627 ideal complete finite-orthogonal-group stream model over finite fields of odd characteristic',
        theorem='credited applicability of PR1627 sections 3-4, not a new generic theorem',
        sources=pins,geometry_keys_equal=list(GEOMETRY_KEYS),record_sha256=raw_hash,
        local_program_sha256=hashes,adapted_template_canonical_sha256=digest(encoded(adapted)),
        local=local,copy_window=footprint,ownership=owners,
        complete_global_paid_profile=dict(sorted(total.items())),
        paid_rank_mass=sum(k*v for k,v in total.items()),
        rank_deficit=64*t['live']-sum(k*v for k,v in total.items()),
        unchanged_private_centre_reserve=t['private_centre_reserve'],controls=controls,
        snapshot_alias_countermodel=alias_control(),equivalent_cut_zero_order_passes=True,
        actual_compiler_or_recursive_scratch_implementation=False,
        local_ring_high_packet_admission=False,no_new_kappa=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--write-receipt',type=Path)
    args = ap.parse_args()
    result = run()
    if args.write_receipt:
        with args.write_receipt.open('x') as f:
            f.write(json.dumps(result,indent=2)+'\n')
    else:
        need(json.loads((HERE/'RESULT.json').read_text()) == json.loads(json.dumps(result)), 'stale result receipt')
    print('PASS_R439_INTERLEAVED_COPY_CONTRACT records=13990 columns=661 orientations=2 '
          'calls=288 window=303+10 controls='+str(len(result['controls']))+
          ' no_new_kappa ideal_stream_model_only')


if __name__ == '__main__':
    main()
