"""Source-bound portable replay. Apache-2.0.
Dugongue with substantial OpenAI Codex assistance.
"""
from pathlib import Path
import hashlib
import json

ROOT=Path(__file__).resolve().parent


def need(ok, why):
    if not ok:
        raise ValueError(why)


def load(name):
    path=ROOT/name
    namespace={'__name__':'checked_'+name.removesuffix('.py'),'__file__':str(path)}
    # Compile the authenticated bytes; do not import a potentially stale pyc.
    exec(compile(path.read_bytes(),str(path),'exec'),namespace)
    return namespace


def main():
    manifest=json.loads((ROOT/'CONTENT-HASHES.json').read_text(encoding='utf-8'))
    actual={p.name for p in ROOT.iterdir() if p.is_file() and p.name!='CONTENT-HASHES.json'}
    need(actual==set(manifest),'unexpected or missing package file')
    for name,want in manifest.items():
        need(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==want,'source hash mismatch: '+name)
    reports={}
    for name in ('root_seed.py','recover.py','phase_tables.py','exp_table.py','chirp_check.py','gaussian_block.py','band_solve.py','periodic_solve.py','gaussian_inverse.py','native_fft.py'):
        reports[name]=load(name)['check']()
        need(reports[name]['status']=='PASS','failed component: '+name)
    native=load('native_fft.py')
    def wrong_seed(order,p,width):
        return dict(real=1<<p,imag=0,charged_word_operations=0,largest_intermediate_bits=p+1)
    rejected=False
    try:
        out=native['multiply']([1]*9,[1]*9,9,wrong_seed)
        product=sum(x<<i for i,x in enumerate(out['digits']))
        rejected=product!=511*511
    except ValueError:
        rejected=True
    need(rejected,'wrong root control escaped independent product check')
    try:native['multiply']([2],[1],1)
    except ValueError:pass
    else:raise ValueError('invalid packed digit accepted')
    print(json.dumps(dict(status='PASS',source_hashes=len(manifest),reports=reports,
                          wrong_root_control=True,invalid_ABI_control=True,
                          scope='finite executable evidence; universal mathematical proofs are informal',
                          new_best_kappa=False,TM_subroutine_calls=0),indent=2))


if __name__=='__main__':main()
