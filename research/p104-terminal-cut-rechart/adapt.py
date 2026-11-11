# Successor: Rohan Arun/OpenAI Codex global output rechart; predecessor attribution retained.
"""Counted adapters invalidate same-native reuse in Rohan Arun's #7113 checks.
All edits apply only to temporary copies of authenticated source. Apache-2.0.
Prepared for dillona with substantial OpenAI Codex assistance.
"""
from hashlib import sha256

def adapt(folder,claim,frac):
    changes=[]
    def patch(name,old,new):
        path=folder/name;raw=path.read_text()
        if raw.count(old)!=1:raise ValueError('Exact one-occurrence adapter: '+name+' '+old)
        path.write_text(raw.replace(old,new));changes.append(dict(file=name,old=old,new=new))
    patch('emit_odd_type_ab.py',
          'invoice=next(x for x in json.loads((root/"SHORT-CALLER-RAW-PRICE.json").read_text())["rows"] if tuple(x["shape"])==shape)',
          'invoice=json.loads((root/"COHORT-PRICE.json").read_text())')
    patch('check_odd_partial_admission.py',
          'previous=json.loads((root/"SHORT-ADMISSION-PARTIAL.json").read_text())\nassert previous["native_sha256"]==digest and not N["bad_inputs"]',
          'actual_native=ind.native(w)\nassert actual_native==N and not N["bad_inputs"], "Fresh complete native inventory and arbitrary-input adjoint"')
    patch('check_odd_partial_admission.py','claim=Q(".00363797977")','claim=Q('+repr(claim)+')')
    # ToikY's frozen exact_price() already shrinks this probe below the
    # certified crossing. Recompute that rule in the caller's separate gate.
    patch('check_odd_partial_admission.py',
          'tested=claim+Q(7,10**17)',
          'tested=claim+Q(7,10**17)\nwhile tested>=Q(reference["raw_bracket"][0]):\n    tested=claim+(tested-claim)/10')
    patch('check_odd_partial_admission.py',
          'g=gate(invoice,claim,tested,*bracket,r["gate"]["BIT_pin"])',
          'g=gate(invoice,claim,tested,*bracket,r["gate"]["BIT_pin"])\ntry:\n    gate(invoice,claim,Q(bracket[0]),*bracket,r["gate"]["BIT_pin"])\nexcept AssertionError:\n    crossing_probe_rejected=True\nelse:\n    raise AssertionError("Probe at lower crossing unexpectedly accepted")')
    patch('check_odd_partial_admission.py',
          '"scope":"Reuse exact same native word all-column adjoint;',
          '"crossing_probe_rejected":crossing_probe_rejected,"scope":"Fresh complete changed-native arbitrary-input adjoint;')
    patch('check_odd_precision.py', 'env=ModuleType("short_envelope")',
          'patch(\'(life, peak, owned_count) == (54, 43, 51)\',\'(life, peak, owned_count) == (70, 49, 67)\')\nenv=ModuleType("short_envelope")')
    patch('check_odd_precision.py','previous=json.loads((root/"SHORT-PRECISION.json").read_text())','')
    patch('check_odd_precision.py',
          'assert previous["native_sha256"]==sha and grid_receipt["caller_sha256"]==sha256(cpath.read_bytes()).hexdigest()',
          'assert grid_receipt["caller_sha256"]==sha256(cpath.read_bytes()).hexdigest()')
    patch('check_odd_precision.py',
          'wg=previous["native_grid"]\nwr=previous["rounded_native"]\nwp={key:(Q(v["exact"]),v["witness"]) for key,v in wr["bounds"].items()}',
          f'wg=grid.word_run(w, frac={frac})\nwp,wr=env.native_envelope(w)\nwg=json.loads(json.dumps(wg,default=str));wr=json.loads(json.dumps(wr,default=str))\nassert wg==r["precision"]["word"] and wr==r["precision"]["rounded_native"], "Fresh changed-native grid and envelope"')
    return dict(edits=changes,adapted_sha256={x['file']:sha256((folder/x['file']).read_bytes()).hexdigest() for x in changes})
