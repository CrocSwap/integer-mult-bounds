#!/usr/bin/env python3
"""One literal generated-caller calibration with a nonretaining lifetime observer."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
import tempfile

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from bundle import activate_component, materialize, need
from lifetime import Lifetime


def run(fault=None):
    with tempfile.TemporaryDirectory(prefix='qq16-root-') as folder:
        base=Path(folder)
        source_hashes, _outer=materialize(base)
        fixture=activate_component(base)
        observer=Lifetime(fault)
        with observer.instrument(fixture.Machine):
            physical=fixture.run()
        observed=observer.result()
        need(observed['new_contexts']==13 and observed['restorations']==12,'Complete original CALL/RETURN count')
        need(observed['registered_generations']==25,'Every root/child/restored generation')
        need(observed['dispatches']==5859,'Complete original dispatcher count')
        need(observed['terminal_dispatch_records']==observed['run_return_records']==5,'Closed machine retains its final generation')
        expected=json.loads((base/'RESULT.json').read_bytes())['macro_nested']['sha256']
        digest=sha256(json.dumps(physical,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        need(digest==expected,'Unchanged complete predecessor physical receipt')
        return {'status':'PASS_LITERAL_RESTORATION_GENERATION_CALIBRATION','source_hashes':source_hashes,
                'lifetime':observed,'predecessor_physical_receipt_sha256':digest,
                'physical_receipt':physical,
                'scope':'Literal generated toy caller and genuine constructors; no production supplier or full QQ16 ownership theorem.'}


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fault',choices=['binding_history','boundary_backedge','program_backedge'])
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    result=run(args.fault)
    raw=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.output:args.output.write_text(raw)
    else:print(raw,end='')
