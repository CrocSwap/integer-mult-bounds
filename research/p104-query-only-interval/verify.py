"""Bounded registered replay and deterministic complete caller generation."""
from pathlib import Path
import argparse
import json
import sys

sys.path.insert(0,str(Path(__file__).resolve().parent))
from source_binding import ROOT,authenticate,inputs,module,need
from replacement import START,STOP,transform
import interval_certificate
import complete_invoice


def interval():
    old,root,word=inputs();new=transform(old)
    return interval_certificate.verify(old,new)


def formal():
    old,root,word=inputs();new=transform(old)
    fwd=module('operator_ring');dual=module('dual_certificate')
    # The source validator also checks every new literal event's old opcode ABI.
    fwd.validate(new)
    return dict(forward=fwd.replay(new),backward_covectors=dual.certificate(new),
        claim='All 76 independent input/output coefficients; all 18 D variables formal; q^4=1.',
        credit='Unchanged public forward/backward engines from 4e2fd1b6; independent interval engine supplied here.')


def invoice():
    old,root,word=inputs()
    return complete_invoice.verify(old,transform(old),root,word)


def controls():
    old,root,word=inputs();new=transform(old)
    return interval_certificate.controls(old,new)


SUITES={'interval':interval,'formal':formal,'invoice':invoice,'controls':controls}


def normalized(value):
    return json.loads(json.dumps(value,sort_keys=True))


def main():
    p=argparse.ArgumentParser();p.add_argument('--suite',choices=SUITES)
    p.add_argument('--regenerate',action='store_true');a=p.parse_args()
    n=authenticate();old,root,word=inputs();new=transform(old)
    patch=dict(source_interval_half_open=[START,STOP],replacement_events=new['events'][START:START+223],
               old_event_count=2991,new_event_count=3095,scope='Exact formal caller source, no installed physical provider.')
    if a.regenerate:
        need(a.suite is None,'regenerate all suites together')
        results={key:normalized(fn()) for key,fn in SUITES.items()}
        results['authenticated_source_files']=n
        (ROOT/'RESULT.json').write_text(json.dumps(results,indent=2,sort_keys=True)+'\n')
        (ROOT/'QUERY-ONLY-CALLER.json').write_text(json.dumps(new,separators=(',',':'))+'\n')
        (ROOT/'PATCH.json').write_text(json.dumps(patch,indent=2)+'\n')
        print('WROTE_QUERY_ONLY_INTERVAL_RECEIPTS')
        return
    need(a.suite is not None,'choose an explicit bounded suite')
    result=normalized(SUITES[a.suite]())
    expected=json.loads((ROOT/'RESULT.json').read_bytes())
    need(result == expected[a.suite] and n == expected['authenticated_source_files'],
         'exact stored scoped receipt')
    need(new == json.loads((ROOT/'QUERY-ONLY-CALLER.json').read_bytes()),'exact whole generated caller')
    need(patch == json.loads((ROOT/'PATCH.json').read_bytes()),'exact complete interval patch')
    print(json.dumps(result,sort_keys=True))
    print('PASS_QUERY_ONLY_INTERVAL_'+a.suite.upper())


if __name__ == '__main__':
    main()
