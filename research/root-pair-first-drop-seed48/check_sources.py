"""Cross-model and adversarial coverage tests; @woklerx, substantial OpenAI Codex assistance.

Apache-2.0. The main proof does not import predecessor code. This separate
compatibility check compares it against PR968's retained exact model.
"""
import copy
import importlib.util
from pathlib import Path
from unittest.mock import patch
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent


def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    check=load('first_drop',HERE/'verify.py')
    roots,pairing,_,_,_=check.model.setup()
    predecessor=load('credited_pr968',check.ROOT/'research/frame-pair-enumeration-production/baseline.py')
    mapping={max(r,tuple(-x for x in r)):i for i,r in enumerate(predecessor.LINES)}
    check.need(set(mapping)==set(roots),'same 120 root lines')
    order=[mapping[r] for r in roots]
    check.need(all(((pairing[i]>>j)&1)==((predecessor.NROW[order[i]]>>order[j])&1)
                   for i in range(120) for j in range(120)), 'all 14400 predecessor pairing entries')
    observed=check.run()
    check.need(check.canon(observed)==check.canon(check.read(HERE/'CERTIFICATE.json')),'exact retained certificate')
    original_read=check.read
    pins=copy.deepcopy(original_read(HERE/'SOURCES.json'))
    del pins['files']['research/complex-frame-pair-decoders/PROOF.md']
    rejected=[]
    def reject(label,fn,reason):
        try:fn()
        except ValueError as error:
            check.need(reason in str(error),'unexpected failure reason')
            rejected.append(label)
            return
        raise ValueError('accepted mutation: '+label)
    with patch.object(check,'read',side_effect=lambda path:pins if path.name=='SOURCES.json' else original_read(path)):
        reject('removed source pin',check.run,'exact source inventory')
    pins=copy.deepcopy(original_read(HERE/'SOURCES.json'))
    pins['files']['research/complex-frame-pair-decoders/PROOF.md']='0'*64
    with patch.object(check,'read',side_effect=lambda path:pins if path.name=='SOURCES.json' else original_read(path)):
        reject('altered source digest',check.run,'source pin:')
    bad=copy.deepcopy(observed)
    bad['witness_puncture'].pop()
    reject('changed certificate puncture',lambda:check.need(check.canon(bad)==check.canon(observed),'certificate mismatch'),'certificate mismatch')
    print('PASS_ROOT_PAIR_SOURCE_CROSSCHECK pairing_entries=14400 rejected=3')


if __name__=='__main__':main()
