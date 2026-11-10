"""Independent integer/header oracle and actual literal-row exclusion controls.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent))
from hashlib import sha256
import json
from cutoff_sources import HERE,load,need
from cutoff_view import CutoffView,PositiveChild,PaidService,R,S,PRIVATE,RELEASE

H=load("cutoff_header_oracle",S.root/"check_view.py")


def fresh(rank):
    view=CutoffView(rank)
    work=[H.Tape(3+j%5) for j in range(view.port_count)]
    parent=H.Tape(11)
    view.bind(work,S.common.abi.BinaryContextPort(parent))
    return view,work,parent


def one(rank,values,bank=None):
    view,work,parent=fresh(rank) if bank is None else bank
    need(view.rank==rank,"fixed source-rank table reused")
    bits=H.encode(values); H.put(parent,bits)
    tapes=(*work,parent)
    old=[{i:v for i,v in t.data.items() if i<t.origin} for t in tapes]
    before=sum(t.actions for t in tapes)
    steps=view.prepare(); actual=H.body(view.context.tape)
    expected=dict(values,f=rank*values["f"],cutoff=rank*values["cutoff"])
    need(actual==H.encode(expected) and H.decode(actual)==expected,
         "exact two-field transport and all21 unchanged values")
    need(len(actual)<=len(bits)+12,"two self-delimited products add at most12bits")
    need((expected["f"]<=expected["cutoff"])==(values["f"]<=values["cutoff"]),
         "exact positive-integer cutoff equivalence")
    need(H.body(parent)==bits and all(t.head==t.origin for t in tapes),"prepared origins and unchanged parent")
    steps+=view.release()
    need(all(not H.body(t) and t.head==t.origin for t in work) and parent.head==parent.origin,
         "literal complete header retirement")
    need(all({i:v for i,v in t.data.items() if i<t.origin}==v for t,v in zip(tapes,old)),
         "protected caller ancestors")
    actions=sum(t.actions for t in tapes)-before
    need(actions<=steps<=2000*len(bits)+20000,"paid conservative instruction ceiling")
    extents=[max(t.visited)-t.origin+1 for t in work]
    return dict(rank=rank,f=values["f"],cutoff=values["cutoff"],
                parent_bits=len(bits),view_bits=len(actual),parent_leaf=values["f"]<=values["cutoff"],
                instructions=steps,physical_actions=actions,view_sha256=sha256(bytes(actual)).hexdigest(),
                historical_private_visited_extents=extents), (view,work,parent)


def row_choice(values):
    view,work,parent=fresh(2); bits=H.encode(values); H.put(parent,bits)
    decision,steps=R.run_choice(R.compile_leaf(145),view.ports)
    need(H.body(parent)==bits and all(t.head==t.origin for t in (*work,parent))
         and all(not H.body(t) for t in work),"actual public row predicate restores every port")
    return decision,steps


def excluded_consumers():
    # Canonical metadata only: this tests the exact row predicate and does not
    # assert that a global root producer supplied every other descriptor field.
    values=H.descriptor(1); values.update(f=146,cutoff=145)
    old,_=row_choice(values)
    cutoff_only,_=row_choice(dict(values,cutoff=290))
    both,_=row_choice(dict(values,f=292,cutoff=290))
    need((old,cutoff_only,both)==(False,True,False),
         "public cutoff-only mutation changes actual global branch")
    native=H.descriptor(3)
    need(native["selected_axes"]==9*native["f"]+native["remainder"]
         and native["selected_axes"]!=9*(2*native["f"])+native["remainder"],
         "private scaled width violates unchanged general native selected-axis relation")
    return dict(original_row_leaf=old,cutoff_only_mutant_leaf=cutoff_only,
                both_scaled_row_leaf=both,unchanged_native_relation_fails=True,
                descriptor_producer_admission=False)


def tables():
    result={}
    for rank in range(1,9):
        view=CutoffView(rank)
        for table in (view.table,RELEASE):
            for row in table:
                need(row[0] in ("read","write","move","goto","done","reject","quarantine"),"literal local vocabulary")
                if row[0] in ("read","write","move"):
                    need(type(row[1]) is int and 0<=row[1]<R.FIRST_ROLE,"fixed finite physical role")
                if row[0]=="write":
                    need(row[1]!=R.HEADER and row[2] in (R.ZERO,R.ONE,R.BLANK),"parent and markers never written")
                if row[0]=="move":
                    need(row[2] in (-1,1),"literal unit movement")
        result[rank]=dict(prepare=len(view.table),release=len(RELEASE),
                         sha256=sha256(json.dumps(view.table,separators=(",",":")).encode()).hexdigest())
    return result


def check():
    records=[]
    for rank in range(1,9):
        for f in (1,2,3,17):
            for t in sorted({max(1,f-1),f,f+1,145}):
                values=H.descriptor(f);values["cutoff"]=t
                record,_=one(rank,values);records.append(record)
    values=H.descriptor(1);values["f"]=(1<<257)-1;values["cutoff"]=(1<<1024)+3
    long_case,bank=one(8,values)
    short=H.descriptor(1);short["cutoff"]=1
    reused,bank=one(8,short,bank);fresh_case,_=one(8,short)
    need(reused["instructions"]==fresh_case["instructions"]
         and reused["physical_actions"]==fresh_case["physical_actions"]
         and sum(reused["historical_private_visited_extents"])>sum(fresh_case["historical_private_visited_extents"]),
         "old blank history remains charged without added short-call scans")
    zero_rejections=[]
    for name in ("f","cutoff"):
        view,work,parent=bank;bad=dict(short);bad[name]=0;bits=H.encode(bad);H.put(parent,bits)
        try:
            view.prepare()
        except ValueError:
            need(not view.active and H.body(parent)==bits and all(not H.body(t) for t in work)
                 and all(t.head==t.origin for t in (*work,parent)),"zero-field rejection cleans whole private bank")
            zero_rejections.append(name)
        else:
            raise ValueError("zero positive field accepted")
    recovered,_=one(8,short,bank)
    invalid=(0,9,True,1.0,-1)
    for rank in invalid:
        try: CutoffView(rank)
        except ValueError: pass
        else: raise ValueError("invalid static source rank accepted")
    # The predecessor's f-only table is an explicit mutation of the new claim.
    mutant,work,parent=fresh(2);mutant.table=S.view.LeafView(2).table
    try:
        one(2,short,(mutant,work,parent))
    except ValueError as error:
        need(str(error)=="exact two-field transport and all21 unchanged values","unscaled-cutoff mutant caught independently")
    else: raise ValueError("unscaled cutoff accepted by two-field oracle")
    finally:
        if mutant.active:mutant.release()
    entries=S.catalog.catalog()[1]
    representatives=[next(t for t in entries.values() if t[1].rank==r) for r in range(1,9)]
    services=[PaidService(t[1]) for t in representatives]
    need(all(s.port_count==388 and s.provider.view.port_count==39 for s in services),"unchanged complete private stock for every source rank")
    grants=0
    for rank in (1,8):
        child=PositiveChild(rank);work=[H.Tape() for _ in range(child.port_count)]
        parent=S.common.abi.BinaryContextPort(H.Tape())
        for bad in (work[:-1],work[:-1]+[work[0]],work[:-1]+[parent.tape]):
            try:child.bind(bad,parent)
            except ValueError:grants+=1
            else:raise ValueError("invalid translated child grant accepted")
    return dict(tables=tables(),cases=records,long_f_and_cutoff_syntax_only=long_case,
                history_reused=reused,history_fresh=fresh_case,recovery=recovered,
                invalid_ranks_rejected=len(invalid),zero_fields_rejected=zero_rejections,
                unscaled_cutoff_mutant_rejected=True,consumer_exclusions=excluded_consumers(),
                all_source_occurrences=len(entries),ranks_checked=8,private_ports=388,
                bad_grants_rejected=grants,full_producer_or_numeric_admission_claim=False)


if __name__=="__main__":
    print(json.dumps(check(),sort_keys=True))
