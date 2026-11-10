"""Bind source-generated flat compiler events to charged #6878 routes.

This is finite template compilation, before runtime p, e, f and row counts.
Actual owner IDs and source tokens are retained. Prepared for @CubeJerry with
substantial OpenAI assistance. Apache-2.0.
"""
from dataclasses import dataclass
from pathlib import Path
import importlib.util
import sys

path=Path(__file__).resolve().parent/"row_programs.py"
spec=importlib.util.spec_from_file_location("compiler_row_programs",path)
r=importlib.util.module_from_spec(spec);sys.modules[spec.name]=r
exec(compile(path.read_bytes(),str(path),"exec"),r.__dict__)


@dataclass(frozen=True)
class Event:
    op: str
    fields: tuple
    token: tuple=()
    rank: int=0


def bind(unit,root_rank,raw_ambient,raw_roles):
    """Refine the exact lower() grammar; retain original native scalar services.

    Source complements target [s,n), exits canonical [0,n). Unit occurrences
    use actual rank*column and full ambient*column. Each terminal axis receives
    a prefix route/inverse at its explicit base-axis service boundaries. Original enter/
    return tokens become descriptor-only identities after these XOR records.
    They stay in the word so the independent ownership replay still applies.
    """
    r.need(type(root_rank) is int and root_rank>=2,"fixed uniform rank")
    r.need(raw_ambient>=max(raw_roles.values()),"complete raw ambient")
    fields={name for name,_ in unit.roles}|set(unit.owned)
    identity=tuple(range(root_rank))
    chart={field:identity for field in fields}
    scopes={field:[] for field in fields}
    output,bindings=[],[]
    serial=total_swaps=paid=0
    tags={}

    def xor_events(field,swaps,which,source_token,number):
        for a,b in swaps:
            for x,y in ((a,b),(b,a),(a,b)):
                output.append(Event("SERVICE",(field,),
                    ("selected-bit-xor",number,which,x,y,source_token)))

    def enter(field,positions,ambient,scope,source_token):
        nonlocal serial,total_swaps
        r.need(field in fields,"actual emitted physical field")
        layout=r.occurrence(root_rank,tuple(positions),ambient)
        before=chart[field]
        after=tuple(before[i] for i in layout['order'])
        number=serial;serial+=1
        scopes[field].append((scope,before,layout,number))
        chart[field]=after
        total_swaps+=len(layout['entry'])
        bindings.append(dict(id=number,field=field,source_token=source_token,
            kind=r.MATCHED,scope=scope,parent_order=before,order=layout['order'],
            active=tuple(positions),child_ambient=ambient,global_image=after[:ambient],
            entry=layout['entry'],inverse=layout['return'],row_divisor=1))
        xor_events(field,layout['entry'],"enter",source_token,number)

    def leave(field,scope,source_token):
        r.need(scopes[field] and scopes[field][-1][0]==scope,"source LIFO complete chart return")
        _,before,layout,number=scopes[field].pop()
        xor_events(field,layout['return'],"return",source_token,number)
        restored=list(chart[field])
        for a,b in layout['return']:
            restored[a],restored[b]=restored[b],restored[a]
        r.need(tuple(restored)==before,"actual inverse restores complete parent order")
        chart[field]=before

    for event in unit.events:
        token=event.token
        tag=token[0] if token else None
        r.need(tag!="selected-bit-xor","source word must not be routed twice")
        original=Event(event.op,event.fields,event.token,event.rank)
        if event.op=="SERVICE" and tag in ("program-enter","program-return"):
            r.need(len(event.fields)==1,"one actual program field")
            field=event.fields[0]
            binding,index=token[1:]
            r.need(binding[0]=="matched-program" and binding[2][index]==field,
                   "exact ordered matched-program owner")
            kind=binding[1]
            if kind[0]=="source-complement":
                parent=kind[1][1];n=kind[2];start=kind[3]
                r.need(start+n==parent<=root_rank,"source complement exact partition")
                positions=tuple(range(start,parent))
            else:
                r.need(kind[0]=="deepest-exit","retained compiler program kind")
                n=kind[3];positions=tuple(range(n))
            r.need(1<=n<=root_rank,"positive smaller complete program")
            scope=("program",binding,index)
            if tag=="program-enter":
                output.append(original);enter(field,positions,n,scope,token)
                tags[kind[0]]=tags.get(kind[0],0)+1
            else:
                leave(field,scope,token);output.append(original)
        elif event.op=="SERVICE" and tag in ("occurrence-enter","occurrence-return"):
            r.need(len(token)==9 and token[1]=="occurrence","actual source occurrence token")
            field,=event.fields
            column,n,name=token[6:9]
            r.need(name in raw_roles and type(column) is int and column>0,"source role/column")
            ambient=raw_ambient*column;target=raw_roles[name]*column
            r.need(target<=ambient<=n<=root_rank,"complete source unit fits program")
            scope=("occurrence",token[1:])
            if tag=="occurrence-enter":
                output.append(original)
                enter(field,tuple(range(target)),ambient,scope,token)
                tags["unit-occurrence"]=tags.get("unit-occurrence",0)+1
            else:
                leave(field,scope,token);output.append(original)
        elif event.op=="SERVICE" and tag in ("base-axis-enter","base-axis-return"):
            field,=event.fields
            ordinary=token[1:]
            r.need(len(ordinary)==7 and ordinary[0]=="ordinary-rank-one",
                   "explicit current elementary-axis source boundary")
            axis,n=ordinary[-2:]
            r.need(ordinary[2]==field and 0<=axis<n<=root_rank,"actual terminal axis/owner")
            scope=("paid-axis",ordinary)
            if tag=="base-axis-enter":
                output.append(original);enter(field,(axis,),1,scope,token)
                tags["terminal-rank-one"]=tags.get("terminal-rank-one",0)+1
            else:
                leave(field,scope,token);output.append(original)
        elif event.op=="PAID":
            field,=event.fields
            r.need(event.rank==1 and len(token)==7 and token[0]=="ordinary-rank-one",
                   "only actual terminal rank-one leaves consume rows")
            r.need(scopes[field] and scopes[field][-1][0]==("paid-axis",token),
                   "rank-one call occurs within its actual charged axis route")
            output.append(original)
            paid+=1
        else:
            if event.op in ("INIT","CLEAR"):
                field,=event.fields
                r.need(not scopes[field],"private lifetime after complete geometry return")
            output.append(original)
    r.need(not any(scopes.values()),"all finite compiler scopes return")
    r.need(all(order==identity for order in chart.values()),"all complete root charts restored")
    xor_count=sum(e.op=="SERVICE" and e.token and e.token[0]=="selected-bit-xor" for e in output)
    r.need(xor_count==6*total_swaps,"complete literal address tariff")
    r.need(sum(e.op=="PAID" for e in output)==paid,"paid profile unchanged")
    return tuple(output),dict(source_events=len(unit.events),emitted_events=len(output),
        route_pairs=serial,entry_swaps=total_swaps,selected_xor_records=xor_count,
        paid_sites=paid,scope_kinds=dict(sorted(tags.items())),matched_row_divisors=0),tuple(bindings)
