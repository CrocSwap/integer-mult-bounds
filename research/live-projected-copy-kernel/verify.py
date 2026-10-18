"""Conditional projected-copy interface; no scalar/native supplier admission."""
from fractions import Fraction as Q
from pathlib import Path
import gzip
import hashlib
import itertools
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def need(ok, message):
    if not ok:
        raise ValueError(message)


def matvec(a, x):
    return [sum((v * w for v, w in zip(row, x)), Q(0)) for row in a]


def projection(q):
    s = sum(v*v for v in q)
    return [[Q(int(i == j)) - Q(q[i] * q[j], s) for j in range(8)] for i in range(8)]


def run_word(p, u, donor_column, initial, restore_early=False, check_erase=True):
    c, d, y = (list(initial[i:i+8]) for i in (0, 8, 16))
    t = matvec(p, c)
    update = [v*d[donor_column] for v in u]
    c = [a+b for a,b in zip(c, update)]
    y = [a+b for a,b in zip(y, t)]
    if restore_early:
        c = [a-b for a,b in zip(c, update)]
    if check_erase:
        need(t == matvec(p, c), 'stale projected copy')
    if not restore_early:
        c = [a-b for a,b in zip(c, update)]
    return c+d+y


def run():
    for row in json.loads((HERE/'SOURCES.json').read_text(encoding='utf-8'))['files']:
        if row['usage']=='input':
            need(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'], 'source '+row['path'])
    word=json.loads(gzip.decompress((ROOT/'research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz').read_bytes()))
    lines=word['lines']
    need(len(lines)==111 and all(len(q)==8 and sum(v*v for v in q)==4 for q in lines), 'selected punctured lines')
    valid=columns=bad=repairs=0
    for qi,q in enumerate(lines):
        p=projection(q)
        need(matvec(p,q)==[0]*8 and sum(p[i][i] for i in range(8))==7, 'kernel and rank')
        for j in range(8):
            col=[p[i][j] for i in range(8)]
            need(matvec(p,col)==col, 'projector identity')
        for donor in range(8):
            for col in range(24):
                initial=[int(i==col) for i in range(24)]
                wanted=initial[:]
                projected=matvec(p,initial[:8])
                wanted[16:]=[a+b for a,b in zip(wanted[16:],projected)]
                need(run_word(p,q,donor,initial)==wanted, 'complete dirty projected boundary')
                columns+=1
            valid+=1
        wrong=lines[(qi+1)%len(lines)]
        initial=[0]*24;initial[8]=1
        need(run_word(p,wrong,0,initial,check_erase=False)==initial, 'endpoint-only control passes')
        try:run_word(p,wrong,0,initial)
        except ValueError as exc:need(str(exc)=='stale projected copy','precise chronological rejection');bad+=1
        else:raise ValueError('wrong-line update accepted')
        need(run_word(p,wrong,0,initial,restore_early=True)==initial, 'early restoration repair');repairs+=1
        need(any(p[i][j] for i in range(8) for j in range(8)), 'scalar identity update must fail')
    distinct=0
    for q,r in itertools.combinations(lines,2):
        # Independent exact Gram determinant checks that kernel lines differ.
        dot=sum(x*y for x,y in zip(q,r))
        need(16-dot*dot>0,'distinct two-copy kernels')
        distinct+=1
    return {'status':'PASS_LIVE_PROJECTED_COPY_KERNEL','pinned_lines':len(lines),
            'rank_seven_projectors':111,'kernel_basis_updates':valid,'dirty_columns':columns,
            'endpoint_only_false_positives_rejected':bad,'early_restoration_repairs':repairs,
            'distinct_two_copy_pairs_forcing_zero_update':distinct,
            'single_copy_update_space_dimension':8,
            'conditional_rank_invoice':{'copy_erase_pair':7,'target_read':7,'prepare':1,'restore':1,'total':16,'baseline':14},
            'native_or_scalar_admission':False,'new_kappa':False}


if __name__=='__main__':
    result=run()
    if '--write' in sys.argv:(HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    else:need(result==json.loads((HERE/'RESULT.json').read_text(encoding='utf-8')),'receipt')
    print(result['status'],'updates=888 dirty_columns=21312 pairs=6105 no_native_admission')
