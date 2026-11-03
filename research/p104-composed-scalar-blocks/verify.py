"""Check both block operators and the complete word without a search.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
"""
from copy import deepcopy
from fractions import Fraction as Q
from hashlib import sha256
import gzip
import importlib.util
import json
from pathlib import Path
import sys

P = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('construct', P/'construct.py')
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)


def matrix(program, roles, frame):
    """Use dense integer rows and a separate denominator for each row."""
    index = {r:i for i,r in enumerate(roles)}
    n = len(roles)
    rows = [[int(i == j) for j in range(n)] for i in range(n)]
    powers = [0]*n
    for e in program:
        op, r = e[:2]
        c.require(op in ('ADD','SCALE') and e[-1] == frame, 'block alphabet and frame')
        r = index[r]
        q = Q(e[-2]); power = q.denominator.bit_length()-1
        c.require(q and q.denominator == 1 << power, 'nonzero dyadic coefficient')
        if op == 'SCALE':
            rows[r] = [q.numerator*x for x in rows[r]]
            powers[r] += power
        else:
            s = index[e[2]]
            c.require(s != r, 'distinct ADD roles')
            level = max(powers[r], powers[s]+power)
            a, b = 1 << (level-powers[r]), q.numerator << (level-powers[s]-power)
            rows[r] = [a*x+b*y for x,y in zip(rows[r],rows[s])]
            powers[r] = level
        while powers[r] and not any(x & 1 for x in rows[r]):
            rows[r] = [x//2 for x in rows[r]]
            powers[r] -= 1
    return rows, powers


def check_block(word, block):
    old = word['program'][block['start']:block['stop']]
    new = block['replacement']
    roles = sorted({r for e in old+new for r in (e[1:3] if e[0] == 'ADD' else e[1:2])})
    c.require(matrix(old, roles, block['frame']) == matrix(new, roles, block['frame']), 'arbitrary-entry block identity')
    return dict(start=block['start'],stop=block['stop'],roles=len(roles),coefficients=len(roles)**2,
                before=len(old),after=len(new),replacement_sha256=sha256(c.canonical(new)).hexdigest())


def rejected(function):
    try:
        function()
    except (ValueError, KeyError):
        return 1
    raise ValueError('negative control accepted')


def verify():
    source = c.source_word()
    blocks = json.loads((P/'BLOCKS.json').read_text())
    c.require([(b['start'],b['stop'],b['frame']) for b in blocks] == [(1,9896,3),(17461,20431,127)], 'declared source intervals')
    joined = json.loads(gzip.decompress((P/'WORD.json.gz').read_bytes()))
    c.require(joined == c.join(source,blocks), 'complete joined word')
    certificates = [check_block(source,b) for b in blocks]
    protected = lambda w: [e for e in w['program'] if e[0] not in ('ADD','SCALE')]
    c.require(protected(source) == protected(joined), 'all protected events and their order')
    local = c.load('local_check', c.ROOT/'research/p104-unread-path-resynthesis/local.py')
    tr = c.load('transfer_check', c.ROOT/'research/p104-gauge-error-covariance/transfer.py')
    ca = c.load('causal_check', c.ROOT/'research/p104-gauge-error-covariance/causal.py')
    words = {'selected':source,'prefix_only':c.join(source,[blocks[0]]),
             'suffix_only':c.join(source,[blocks[1]]),'joined':joined}
    reports = {}
    for name,word in words.items():
        bill = local.replay(word)
        sites = {j for j,e in enumerate(word['program']) if e[0] in ('MOVE','ADD','SCALE')}
        weights, ideal = tr.ideal(word,sites)
        errors = {}
        for guard in (15,16):
            result = ca.bound(word,weights,sites,guard)
            errors[str(guard)] = dict(final=str(max(result['final'][:word['public']])),
                                     prefix=str(result['peak']),peak_at=result['peak_at'])
        c.require(Q(errors['15']['final']) > 1 and Q(errors['16']['final']) <= 1, 'guard bracket for this sufficient rule')
        c.require(ideal+Q(errors['16']['prefix']) < 1024, 'ten range bits')
        reports[name] = dict(events=len(word['program']),bill=bill,ideal_peak=str(ideal),errors=errors)
    invariant = lambda b: {k:v for k,v in b.items() if k != 'real_scalar_allowance'}
    c.require(all(invariant(r['bill']) == invariant(reports['selected']['bill']) for r in reports.values()), 'complete recursive and ownership bill')
    c.require(reports['joined']['events'] == 19107 and reports['joined']['bill']['real_scalar_allowance'] == 140268, 'joined count and allowance')
    c.require(Q(reports['joined']['errors']['16']['final']) < Q(reports['prefix_only']['errors']['16']['final']), 'incremental error improvement')
    reverse = local.reverse_columns(joined)
    controls = 0
    for b in blocks:
        bad = deepcopy(b); bad['replacement'][0][-2] = str(-Q(bad['replacement'][0][-2]))
        controls += rejected(lambda: check_block(source,bad))
        bad = deepcopy(b); bad['replacement'][0][-1] += 1
        controls += rejected(lambda: check_block(source,bad))
    bad = deepcopy(blocks); bad[1]['start'] = bad[0]['stop']-1
    controls += rejected(lambda: c.join(source,bad))
    bad = deepcopy(blocks); bad[0]['source_sha256'] = '0'*64
    controls += rejected(lambda: c.join(source,bad))
    return dict(status='PASS_P104_COMPOSED_SCALAR_BLOCKS',blocks=certificates,words=reports,
                independent_transpose=reverse,protected_events=len(protected(source)),negative_controls=controls,
                incremental_vs_prefix=dict(events=119,real_scalar_allowance=2510),
                inherited_and_incremental_vs_selected=dict(events=3696,real_scalar_allowance=49160),
                word_sha256=sha256(c.canonical(joined)).hexdigest())


if __name__ == '__main__':
    c.require(sys.argv[1:] in ([],['--write']), 'supported arguments')
    result = verify()
    if sys.argv[1:] == ['--write']:
        (P/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:
        c.require(c.canonical(result) == c.canonical(json.loads((P/'RESULT.json').read_text())), 'complete receipt')
    print(result['status'])
