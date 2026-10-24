#!/usr/bin/env python3
"""Source-bound main-output paths; Apache-2.0, Codex assistance.

No optimizer, constructor, interval enumerator or Clifford checker is imported.
"""
from collections import defaultdict
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import gzip
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = 'research/kappa-round3-warp-20261022/ACTUAL-WORD.json.gz'
SOURCE_SHA = '7679daa4ec6a40f56fc7f0202379a6f454310e94945aba4f48beaaaafb838d05'
PAYLOAD_SHA = 'cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd'


def need(ok, message):
    if not ok:
        raise ValueError(message)


def span(vectors):
    out = {0}
    for v in vectors:
        need(type(v) is int and 0 < v < 512 and v not in out, 'independent nine-bit basis')
        out |= {x ^ v for x in tuple(out)}
    return out


def authenticate(raw):
    need(sha256(raw).hexdigest() == SOURCE_SHA, 'immutable compressed source')
    data = gzip.decompress(raw)
    need(sha256(data).hexdigest() == PAYLOAD_SHA, 'canonical source payload')
    return json.loads(data)


def skeleton(payload, direction):
    """Cut EVERY warp; propagate only along persistent scalar contacts."""
    word = [e for e in payload['programs'][direction] if e[0] != 'climb']
    current = [('entry', r) for r in range(632)]
    links = defaultdict(set)
    for i, e in enumerate(word):
        if e[0] == 'scalar':
            gate = e[1]
            refs = gate[1:3] if gate[0] in ('add', 'copy') else gate[1:2]
            for typ, role in refs:
                if typ == 'L':
                    need(0 <= role < 632, 'persistent role')
                    target = ('scalar', i)
                    links[current[role], target].add(role)
                    current[role] = target
        elif e[0] == 'warp':
            need(e[1][0] == 'L', 'persistent native map')
            current[e[1][1]] = ('cut-warp', i)
        else:
            need(e[0] in ('phase', 'adapter', 'residual_adapter', 'center'), 'source marker')
    for role in range(112, 224):
        links[current[role], ('exit', role)].add(role)
    return word, links


def verify_certificate(payload, certificate):
    need(certificate['schema_version'] == 1 and
         certificate['payload_sha256'] == PAYLOAD_SHA, 'certificate source binding')
    cases = certificate['cases']
    need([c['operator'] for c in cases] == list(range(47, 59)), 'all twelve operators')
    c = payload['canonical']; frames = c['frames']; totals = {}
    for direction in ('forward', 'backward'):
        word, links = skeleton(payload, direction); checked = 0
        for case in cases:
            op, pre, first = case['operator'], case['prelude_event'], case['first_scalar_event']
            role, a = case['source_role'], case['input_vector']
            need(first == pre + 1, 'first contact immediately follows prelude')
            need(word[pre][0:3] == ['warp', ['L', role], op], 'actual positive prelude')
            need(role < 112 and span(frames[c['start'][role]]) == {0, a}, 'main input line')
            need(not any(e[0] == 'warp' and e[1] == ['L', role] for e in word[:pre]),
                 'no earlier warp on this main input')
            need(word[first][0] == 'scalar' and word[first][1][0] == 'add' and
                 ['L', role] in word[first][1][1:3], 'prelude meets first ADD')
            need(45 in span(frames[word[first][2]]), 'source realizes forced line')
            intersection = set(range(512)); normals = []
            need(len(case['witnesses']) == 8, 'eight output hyperplanes')
            for w in case['witnesses']:
                path = [tuple(n) for n in w['nodes']]; owners = w['roles']; end = w['output_role']
                need(112 <= end < 224, 'only fixed main Y exits')
                need(path[0] == ('scalar', first) and path[-1] == ('exit', end), 'path ends')
                need(len(owners) == len(path) - 1, 'one owner per link')
                for u, v, owner in zip(path, path[1:], owners):
                    need(owner in links.get((u, v), set()), 'literal consecutive-contact containment')
                    checked += 1
                b = frames[c['final'][end]]; n = w['normal']
                need(len(b) == 8 and 0 < n < 512 and
                     all((n & x).bit_count() % 2 == 0 for x in b), 'actual output normal')
                normals.append(n); intersection &= span(b)
            need(len(span(normals)) == 256, 'eight independent constraints')
            need(intersection == {0, 45}, 'forced first-contact line')
            need(case['forced_image_vector'] == 45, 'forced nonzero image')
        totals[direction] = dict(operators=12, paths=96, literal_containment_links=checked)
    return totals


def controls(payload, cert):
    rejected = []
    def reject(fn, name):
        try:
            fn()
        except (ValueError, KeyError, IndexError):
            rejected.append(name); return
        raise ValueError('corruption accepted: ' + name)
    bad = deepcopy(cert)
    bad['cases'][0]['witnesses'][0]['nodes'].pop(1)
    bad['cases'][0]['witnesses'][0]['roles'].pop(0)
    reject(lambda: verify_certificate(payload, bad), 'skipped contact')
    bad = deepcopy(cert); bad['cases'][0]['witnesses'][0]['roles'][0] = 900
    reject(lambda: verify_certificate(payload, bad), 'wrong path owner')
    bad = deepcopy(cert); bad['cases'][0]['witnesses'][0]['normal'] ^= 1
    reject(lambda: verify_certificate(payload, bad), 'wrong output normal')
    bad = deepcopy(cert); bad['cases'][0]['witnesses'].pop()
    reject(lambda: verify_certificate(payload, bad), 'omitted output constraint')
    bad = deepcopy(cert); bad['cases'][0]['forced_image_vector'] = 44
    reject(lambda: verify_certificate(payload, bad), 'wrong forced image')
    bad = deepcopy(cert); bad['cases'][0]['input_vector'] ^= 1
    reject(lambda: verify_certificate(payload, bad), 'changed main entrance')
    raw = bytearray((ROOT / SOURCE).read_bytes()); raw[10] ^= 1
    reject(lambda: authenticate(bytes(raw)), 'changed source bytes')
    # Separate all-vector arithmetic, using no subspace-closure routine.
    for case in cert['cases']:
        ns = [w['normal'] for w in case['witnesses']]
        need([v for v in range(512) if not any((v & n).bit_count() % 2 for n in ns)] == [0, 45],
             'all-vector evaluation of normal constraints')
        for i in range(8):
            rest = ns[:i] + ns[i + 1:]
            need(sum(not any((v & n).bit_count() % 2 for n in rest) for v in range(512)) == 4,
                 'each selected output constraint is independent')
    return rejected


def main():
    payload = authenticate((ROOT / SOURCE).read_bytes())
    cert = json.loads((HERE / 'CERTIFICATE.json').read_text())
    print(json.dumps(dict(status='PASS_ALL_TWELVE_PRELUDE_IMAGE_LINES_FORCED_NO_NEW_KAPPA',
                         coverage=verify_certificate(payload, cert),
                         controls_rejected=controls(payload, cert), source_payload_sha256=PAYLOAD_SHA,
                         scope='Fixed scalar chronology and ascending persistent contacts. '
                         'All warps cut; only main input lines and main Y exits used. '
                         'No helper endpoint, owned boundary, moment ceiling or supplier claim.'),
                     indent=2, sort_keys=True))


if __name__ == '__main__':
    main()
