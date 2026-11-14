"""Tiny exact-source Count/lease cleanup surfaces, not a scalar replay.

Only the frozen class/function ASTs are loaded; Meter is observer accounting.
Old capacity and invalid dirty-tail states are explicit input fixtures.
Apache-2.0; prepared for @CubeJerry with substantial OpenAI assistance.
"""
import argparse
import ast
from contextlib import contextmanager
from hashlib import sha256
import json
from pathlib import Path


def need(ok,message):
    if not ok:raise ValueError(message)


class Meter:
    def __init__(self):self.reads=self.writes=self.moves=0
    def total(self):return self.reads+self.writes+self.moves


def selected(path,names,namespace):
    raw=path.read_bytes();tree=ast.parse(raw)
    nodes=[node for node in tree.body if isinstance(node,(ast.ClassDef,ast.FunctionDef)) and node.name in names]
    need({node.name for node in nodes}==set(names),'complete exact-source AST selection')
    exec(compile(ast.Module(body=nodes,type_ignores=[]),str(path),'exec'),namespace)


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write',type=Path);args=ap.parse_args()
    root=Path(__file__).resolve().parent/'runtime-slices'
    pins={'records.py':'0c9c4b23e998597fb877bb1a29da69ac869b68262abe635b162b4dba9c69b372',
          'scratch_pool.py':'41f1eb93652b7174c3b02f95f70e1a9ce2e2aed0a729e725167c8f226e65d8db',
          'cardinality.py':'505d5e560c5a507e6184edcc19a87cf1fed243eb34a5cb21fbe1e4fe017e7f22',
          'session.py':'45ee809b27a69ca5576361922fd2760f568c9a98864d4c55c4fee3003ee3c9ad'}
    for name,digest in pins.items():need(sha256((root/name).read_bytes()).hexdigest()==digest,'frozen nested source '+name)
    ns=dict(Meter=Meter,need=need,ZERO=0,ONE=1,LEFT=2,RIGHT=3,BLANK=4,RETURN=13,contextmanager=contextmanager)
    selected(root/'records.py',{'Tape'},ns)
    selected(root/'scratch_pool.py',{'Lease','ScratchPool'},ns)
    selected(root/'cardinality.py',{'Natural'},ns)
    selected(root/'session.py',{'erase_marker'},ns)
    cases=[]
    for history in(1,257,65537):
        for digits in(1,7,31):
            pool=ns['ScratchPool'](2)
            for tape in pool.tapes:tape.cells.extend([4]*(history-len(tape.cells)))
            lease=pool.acquire();owner=lease.physical
            for bit in range(digits):lease.append(1 if bit==digits-1 else bit%2)
            lease.append(3);lease.rewind()
            current=digits+1;before=owner.meter.total();capacity=len(owner.cells)
            view=object.__new__(ns['Natural']);view.tape=lease;view.close()
            clear_cost=owner.meter.total()-before
            need(clear_cost==5*current+7,'exact active-prefix close invoice')
            need(owner.head==1 and len(owner.cells)==capacity==max(history,current+1),'physical capacity retained')
            need(not pool.live and all(x==4 for x in owner.cells[1:]),'whole admitted history blank after close')
            before=sum(t.meter.total() for t in pool.tapes);pool.empty()
            need(sum(t.meter.total() for t in pool.tapes)-before==8,'two-owner empty guard is origin-only')
            before=sum(t.meter.total() for t in pool.tapes)
            for tape in pool.tapes:ns['erase_marker'](tape)
            need(sum(t.meter.total() for t in pool.tapes)-before==10,'two markers have constant retirement cost')
            need(all(t.head==1 and all(x==4 for x in t.cells) for t in pool.tapes),'entire admitted capacity blank')
            cases.append(dict(entry_capacity=history,binary_digits=digits,clear_actions=clear_cost,
                              retained_capacity=capacity,empty_actions=8,marker_actions=10))
    for digits in(1,7,31):
        need(len({x['clear_actions'] for x in cases if x['binary_digits']==digits})==1,'no historical-capacity time scan')
    # A distant dirty cell is outside the blank-history premise and survives.
    pool=ns['ScratchPool'](1);tape=pool.tapes[0];tape.cells.extend([4]*256);tape.cells[-1]=1
    lease=pool.acquire();lease.append(1);lease.append(3);lease.rewind()
    view=object.__new__(ns['Natural']);view.tape=lease;view.close();pool.empty()
    need(tape.head==1 and tape.cells[-1]==1 and not all(x==4 for x in tape.cells[1:]),
         'origin-only empty guard does not establish arbitrary dirty-tail cleanup')
    # The exact retained ABI never promises that clearing releases old stock.
    need(cases[-1]['retained_capacity']>1000*(cases[-1]['binary_digits']+1),'short output cannot bound old stock')
    # Returned results do not own an unrelated borrowed live lease in the pool.
    pool=ns['ScratchPool'](2);borrowed=pool.acquire();borrowed.append(1);borrowed.append(3);borrowed.rewind()
    original=bytes(borrowed.physical.cells),borrowed.head
    result=pool.acquire();result.append(0);result.append(3);result.rewind()
    view=object.__new__(ns['Natural']);view.tape=result;view.close()
    try:pool.empty()
    except ValueError as error:need('closes all scratch leases' in str(error),'unreleased borrowed lease blocks pool empty')
    else:raise ValueError('output retirement incorrectly emptied a shared pool')
    need(borrowed.active and (bytes(borrowed.physical.cells),borrowed.head)==original,'borrowed live lease preserved')
    borrowed.clear();pool.empty()
    result=dict(status='PASS',source_pins=pins,cases=cases,
        controls=['distant-dirty-tail-survives-origin-empty-check','large-old-capacity-remains-after-short-clear',
                  'returned-output-retirement-does-not-release-borrowed-live-lease'],
        conclusion='Blank historical capacity contributes resident stock but is not rescanned by these cleanup methods; fresh or bounded histories justify the simplified current-parameter space bound.',
        scope='Exact retained cleanup methods plus accounting-only Meter; no exponential arithmetic, no full production replay, and no dirty-tail erasure claim.')
    text=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.write:args.write.write_text(text)
    print(text,end='')


if __name__=='__main__':main()
