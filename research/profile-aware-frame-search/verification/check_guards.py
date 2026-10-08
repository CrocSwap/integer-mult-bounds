"""Adversarial controls for the literal word/cost boundary.

Run with a selected or frozen h23/h25 word. No source or word files are edited.
"""
from pathlib import Path
import argparse
import gzip
import json
from verify_words import check_word_structure


def run(path):
    raw=path.read_bytes()
    d=json.loads(gzip.decompress(raw) if str(path).endswith('.gz') else raw)
    check_word_structure(d)
    passed=[]

    def reject(name):
        try:
            check_word_structure(d)
        except (AssertionError,IndexError,KeyError):
            passed.append(name)
        else:
            raise AssertionError('negative control accepted: '+name)

    old=d['ops'][0][0]
    d['ops'][0][0]=-1
    reject('negative slot index cannot alias the final role')
    d['ops'][0][0]=old

    # Two identical extra scatter XORs cancel on every basis vector. A pure
    # endpoint replay would therefore accept them, but the cost certificate
    # only charges the canonical scatter, so the structural guard must reject.
    extra=d['scatter'][0].copy()
    d['scatter'].extend([extra,extra])
    reject('canceling but uncharged additional scatter XORs')
    del d['scatter'][-2:]

    old=d['scatter'][0][0]
    d['scatter'][0][0]=(old+1)%(2*d['v']+d['R'])
    reject('mismatched scatter destination')
    d['scatter'][0][0]=old

    check_word_structure(d)
    result=dict(status='PASS',positive_selected_word=True,negative_controls=passed,
                explanation='A canceling XOR pair preserves the complete binary map but invalidates an unchanged cost certificate.')
    print(json.dumps(result,indent=2))
    return result


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('word',type=Path)
    run(p.parse_args().word)
