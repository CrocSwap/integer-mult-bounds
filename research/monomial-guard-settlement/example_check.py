"""Reachability and explicit attaining headers for the sharp examples."""
from pathlib import Path
import json,sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
from literal import literal_orders
from monomial import flat_rows, passing_permutations
from settlement import Field, add_row, witness
from state_oracle import neighbors


def orders(f, state, m):
    return literal_orders(f,state[:m],flat_rows(f,state[m:2*m],[state[2*m:]]))


def smaller_levels(f, initial, m, distance):
    """Every distinct raw state at every smaller shortest distance."""
    level = {initial}
    seen = set(level)
    records = []
    for step in range(distance):
        passing = sum(orders(f,s,m)>0 for s in level)
        records.append(dict(cost=step, unique_states=len(level), passing=passing))
        if passing:
            raise ValueError("found a cheaper actual passing header")
        if step+1 < distance:
            new = {p for s in level for p in neighbors(f,s,m,2)} - seen
            seen.update(new)
            level = new
    return records


def example(q,u,b,w,gates):
    f = Field(q)
    levels = smaller_levels(f,u+b+w,len(u),len(gates))
    u1,rows = u,(b,w)
    for i,j,a in gates:
        u1,rows = add_row(f,u1,rows,i,j,a)
    named = flat_rows(f,rows[0],[rows[1]])
    actual = literal_orders(f,u1,named)
    if not actual or actual != passing_permutations(f,u1,named):
        raise ValueError("word fails actual proper minors")
    return dict(q=q,u=u,b=b,w=w,minimum=len(gates),gates=gates,cheaper_levels=levels,
                final_u=u1,final_b=rows[0],final_w=rows[1],passing_final_orders=actual)


def collect():
    records=[]
    for w in ((1,4,2,3,0),(1,1,1,2,0)):
        u,b=(1,)*5,(0,0,0,0,1)
        proof=witness(Field(5),u,[w])
        records.append(example(5,u,b,w,proof["gates"]))
    records.append(example(3,(1,)*6,(0,0,1,1,1,1),(1,2,0,0,0,0),
                           [(0,1,2),(2,3,2)]))
    records.append(example(3,(1,1,1,1,0),(1,1,1,1,0),(0,0,0,0,1),[(0,1,2)]))
    records.append(example(3,(1,)*5,(2,2,1,1,1),(1,2,0,0,0),[(0,1,2),(2,3,2)]))
    return records


if __name__=="__main__":
    rows=collect()
    if json.loads(json.dumps(rows)) != json.loads((HERE/"EXAMPLES.json").read_text(encoding="utf8")):
        raise ValueError("frozen depth search")
    print(json.dumps(dict(status="PASS_SETTLEMENT_SHORTEST_EXAMPLES", minima=[r["minimum"] for r in rows],
                          cheaper_states=sum(t["unique_states"] for r in rows for t in r["cheaper_levels"]))))
