"""Compare the independent forward result to the exact sealed R55 lead receipt."""
from argparse import ArgumentParser
from hashlib import sha256
import json
from pathlib import Path

LEAD = '2ea6101e185bf2fd792c5d18530b878fa61a5ddb61403782d05034ab33ff2b00'


def main():
    p=ArgumentParser()
    p.add_argument('forward',type=Path)
    p.add_argument('lead',type=Path)
    a=p.parse_args()
    raw=a.lead.read_bytes()
    assert sha256(raw).hexdigest()==LEAD
    local,peer=json.loads(a.forward.read_bytes()),json.loads(raw)
    assert local['head']==peer['head'] and local['pins']['CALLER.json']==peer['caller_sha256']
    assert local['cases_visited']==peer['cases_visited']==9568
    assert not local['unvisited'] and not peer['unvisited']
    assert local['counts']==peer['counts'] and not local['survivors'] and not peer['survivors']

    def keyed(report):
        rows={(r['root'],r['boundary']):r for r in report['records']}
        assert len(rows)==len(report['records'])==9568
        return rows

    observed,expected=keyed(local),keyed(peer)
    assert observed.keys()==expected.keys()
    for key,row in observed.items():
        assert all(row[k]==expected[key][k] for k in (
            'status','column_rows','terms','body','central_parity','ranks') if k in row), key
    print(json.dumps({'matched_case_keys':len(observed),'counts':local['counts'],
                      'lead_support_sha256':LEAD},sort_keys=True))


if __name__=='__main__':
    assert __debug__
    main()
