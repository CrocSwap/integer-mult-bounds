"""Long-to-short calls on the same physical owners, retaining opaque tails."""
from pathlib import Path
import json
import random
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import check as c


def main():
    rng=random.Random(2026111206); records=[]
    for side in ('right','left'):
        large=(1,2,2,1,1);small=(1,1,1,1,1)
        old=''.join(str(rng.randrange(2)) for _ in range(c.extent(large)))
        new=''.join(str(rng.randrange(2)) for _ in range(c.extent(small)))
        tapes,origins=c.packet(large,old);owners=tuple(map(id,tapes))
        code=c.m.compile_linear(side)[0]
        first=c.m.Machine(code,tapes).run(2_000_000_000)
        c.require(all(t.head==u for t,u in zip(tapes,origins)),'large call return')
        initial_history=[(t.low,t.high) for t in tapes]
        # Caller prepares the next public prefix. Old tails remain opaque;
        # neither owned tapes nor history observers are reset/recreated.
        for t,text in ((c.m.HEADER,c.header(small)),(c.m.DATA,new)):
            tapes[t].cells.update({origins[t]+j:b for j,b in enumerate(text)})
        tapes[c.m.DATA].cells.pop(origins[c.m.DATA]+len(new),None)
        before=[dict(t.cells) for t in tapes]
        second=c.m.Machine(code,tapes).run(2_000_000_000)
        expected=c.oracle(new,small,c.m.MATRICES[side])
        c.require(tapes[1].cells==before[1]|{origins[1]+j:b for j,b in enumerate(expected)},'reused field/opaque tail')
        c.require(all(t.cells==before[i] for i,t in enumerate(tapes) if i!=1),'reused private/header/exterior')
        c.require(all(t.head==u for t,u in zip(tapes,origins)),'reused head return')
        c.require(tuple(map(id,tapes))==owners,'same owner identities')
        c.require([(t.low,t.high) for t in tapes]==initial_history,'history was reset or unexpectedly expanded')
        fresh=c.execute(side,small,new,code=code)
        c.require(second.steps==fresh,'current time depends on old erased capacity')
        records.append({'side':side,'large_shape':large,'small_shape':small,'large_steps':first.steps,'small_and_fresh_steps':second.steps,'retained_total_history':sum(b-a+1 for a,b in initial_history)})
    print(json.dumps({'status':'PASS_SELECTED_LINEAR_SAME_OWNER_REUSE','seed':2026111206,'records':records,
        'scope':'Same actual tape objects and intervals; old public payload/descriptor tails retained as opaque exterior. No failure-time retry claim.'},indent=2,sort_keys=True))


if __name__=='__main__':main()
