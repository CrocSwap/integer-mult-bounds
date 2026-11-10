"""Independent target-filter oracle and extra physical extraction cases.

Even source periods, four axes, unrelated hole bits and old backing.
Prepared for @CubeJerry with OpenAI assistance.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys
p=argparse.ArgumentParser();p.add_argument('package');p.add_argument('--output',required=True)
a=p.parse_args();root=Path(a.package).resolve();sys.path.insert(0,str(root))
from source_binding import opened

def target_filter(shape):
    maps=[{(2*(1<<ell)*j+s)//(2*s):j for j in range(s)} for ell,s in shape]
    total=1<<sum(ell for ell,s in shape)
    selected=[];ordinals=[]
    for address in range(total):
        residual=address;ordinal=0;stride=1;valid=True
        for (ell,s),inverse in zip(shape,maps):
            digit=residual%(1<<ell);residual>>=ell
            if digit not in inverse:valid=False;break
            ordinal+=inverse[digit]*stride;stride*=s
        if valid:selected.append(address);ordinals.append(ordinal)
    assert ordinals==list(range(len(ordinals)))
    return selected

cases=[]
with opened() as state:
    from extractor import Extract
    from cardinal_counts import Count
    from records import Tape
    from gaussian_rationals import write_count
    from session import erase_marker,initialize_marker
    from words import BLANK
    B=state.B
    for shape,qvalue in ((((3,6),),1),(((2,3),(4,9)),7),(((2,3),)*4,17)):
        desc=Tape();erase_marker(desc);initialize_marker(desc)
        for value in (len(shape),*(v for pair in shape for v in pair)):
            item=Count.literal(value);write_count(item,desc);item.close()
        desc.rewind();q=Count.literal(qvalue)
        descriptor_before=tuple(desc.cells),tuple(q.tape.cells)
        owner=Extract(B,desc,q)
        count=1<<sum(ell for ell,s in shape);width=2*(qvalue+3)
        records=[format((i*i*3217+997*i+11)%(1<<width),'0'+str(width)+'b')+'#' for i in range(count)]
        payload=''.join(records)
        source=B.Tape('old-backing-input','1'*(3*len(payload)+19))
        B.clear(source)
        for ch in payload:B.append(source,ch)
        B.home(source)
        before=dict(source._cells);old_high=source._high;old_actions=dict(source.actions)
        addresses=target_filter(shape);expected=''.join(records[i] for i in addresses)
        result=owner.run(source)
        assert result.inspect()==expected and source._cells==before
        assert source._high==old_high and source._head==1
        assert (tuple(desc.cells),tuple(q.tape.cells))==descriptor_before
        assert all(t.head==1 and all(ch==BLANK for ch in t.cells[1:]) for t in (owner.first,owner.second))
        assert all(t.head==1 and all(ch==BLANK for ch in t.cells) for t in owner.pool.tapes)
        owner.consume();assert owner.run(source).inspect()==expected;owner.consume()
        owner.close();q.close()
        measured={key:source.actions[key]-old_actions.get(key,0) for key in ('read','write','move')}
        assert measured['write']==0
        cases.append(dict(shape=shape,q=qvalue,T=count,S=len(addresses),input_current_cells=len(payload)+2,
                          input_retained_cells=old_high+1,selected_address_sha256=hashlib.sha256(json.dumps(addresses).encode()).hexdigest(),
                          exact_reuse=True,borrowed_old_backing_preserved=True,source_actions_for_two_runs=measured))
out=dict(status='pass',method='target-coordinate membership filtering and source ordinal reconstruction; actual unchanged native Count executor',
         cases=cases,scientific_sha256={name:hashlib.sha256((root/name).read_bytes()).hexdigest()
             for name in ('PROOF.md','extractor.py','source_binding.py')},
         limitations=['No Gaussian transform or numerical radius admission.',
                      'Historical input capacity is charged separately; test makes it larger than current extent.',
                      'No full caller, CRT/carry or new kappa.'])
Path(a.output).write_text(json.dumps(out,sort_keys=True,indent=2)+'\n');print(json.dumps(out,sort_keys=True))
