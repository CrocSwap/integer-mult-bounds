#!/usr/bin/env python3
"""Forward rational endpoint certificate for frozen PR6375's literal word.

This transparently reuses this contribution's own PR6376 forward sparse-row method,
with no source/peer/predecessor executable imports. Public inputs are arbitrary;
INIT is blank activation and CLEAR is a formal reset, not physical erasure.
"""
import argparse
from fractions import Fraction as Q
import gzip
import hashlib
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
PUBLIC,OWNED,Z,OMEGA=770,29,3,127
ANCHORS=(472,520,544,624,655,671)
SOURCE_PINS={'sources/NEW-WORD.json.gz': ['9e31463a785c18a70f6ae6ef3d04a6560dbb965517109390fe820f9fac3371b3', 'b1cfd03abe9128cf5a3908fbd82652e5e8a2e292'], 'sources/OLD-WORD.json.gz': ['e3b6f1c25d672b8c85433be97ebad77ae6a6972352ce2ff63507d30835fcb491', '0af79e58172f85c302c35b193205c0b185b09393'], 'sources/LIFTS.json': ['38960b70a074888a2aeaf3b543629a7ae747c0c5d4f5c853371a6e7c483766c5', '2ee8cb78fd149f9aca8dd953c650b92495a56266'], 'sources/constructor-source.py': ['fe7dc1d9aa55da393465388ee90faaa687b1e5be48dfa816a421069fa3d2de08', 'c099995bef0e224cbb0ec61c06ed3d0b4d478b33'], 'sources/upstream-PROOF.md': ['769e0f87e6b85c557b48135d2d898bb485cf77ce9925540e0a3740e6283f41af', 'bd20fcaf2078691d914d6afbc5cb06a75f47770d'], 'sources/NOTICE': ['91f24d68004688bc0a56303a48edcb5ddabd66bfc2326950603bf98dec245bbe', '638a187d1417bda8976e945a2aeaed116a090e37'], 'sources/author-VALIDATION.md': ['cf33fe7acd32b1912bde7bf67abe1386eb042c6d269a9540cd28cdd076a7cac3', '0be8e7f1052628c34e24dfae6777cb3749b224a9']}
CHECKPOINT_SHA256={'SOURCE-PINS.json': '06514df0ebb826b6561b3fb8f349021240dbd76d0b249f86bf8a7ec5a16cc348', 'verify_preparation.py': 'b025336c2929281ff773fc07631bc00561fd0feddbe202a4e801666bae513bff', 'oracle_preparation.py': '9ef5a448a1337ded7e9e1e9b18bf4caba2670b7433cb10858a391676d89f35d1', 'PREP-RESULT.json': '3fe48cc86074cff29d7f98e793fc91f28021f8b1d9f901996f0daf44f4c28ee9', 'PREP-ORACLE.json': 'f308e045f563e10602e78ce23320f592b9748883541c815141da4aed042d3057', 'PROOF.md': '49175bd7d784d4b6b7b67b83e23dd2080b351b7c50291d62c61ed4d11ba0e212', 'sources/LIFTS.json': '38960b70a074888a2aeaf3b543629a7ae747c0c5d4f5c853371a6e7c483766c5', 'sources/NEW-WORD.json.gz': '9e31463a785c18a70f6ae6ef3d04a6560dbb965517109390fe820f9fac3371b3', 'sources/NOTICE': '91f24d68004688bc0a56303a48edcb5ddabd66bfc2326950603bf98dec245bbe', 'sources/OLD-WORD.json.gz': 'e3b6f1c25d672b8c85433be97ebad77ae6a6972352ce2ff63507d30835fcb491', 'sources/author-VALIDATION.md': 'cf33fe7acd32b1912bde7bf67abe1386eb042c6d269a9540cd28cdd076a7cac3', 'sources/constructor-source.py': 'fe7dc1d9aa55da393465388ee90faaa687b1e5be48dfa816a421069fa3d2de08', 'sources/upstream-PROOF.md': '769e0f87e6b85c557b48135d2d898bb485cf77ce9925540e0a3740e6283f41af'}


def need(ok,message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False)


def digest(value):
    return hashlib.sha256((canonical(value)+"\n").encode()).hexdigest()


def strict(raw):
    def pairs(items):
        value={}
        for key,item in items:
            need(key not in value,"duplicate JSON key")
            value[key]=item
        return value
    return json.loads(raw,object_pairs_hook=pairs,
                      parse_constant=lambda x:(_ for _ in ()).throw(ValueError("nonfinite JSON")))


def integer(value,limit,message):
    need(type(value) is int and 0<=value<limit,message)


def fraction(raw):
    need(type(raw) is str,"canonical rational coefficient string")
    value=Q(raw)
    need(value and str(value)==raw and value.denominator & (value.denominator-1)==0,
         "nonzero canonical dyadic coefficient")
    return value


def sparse(row):
    return [[i,str(value)] for i,value in sorted(row.items()) if value]


def matrix_payload(matrix):
    return [sparse(row) for row in matrix]


def add(destination,source,coefficient):
    for i,value in source.items():
        new=destination.get(i,Q(0))+coefficient*value
        if new:
            destination[i]=new
        else:
            destination.pop(i,None)
    need(len(destination)<=PUBLIC,"bounded rational row width")


def authenticated():
    raw={}
    for name,sha in CHECKPOINT_SHA256.items():
        value=(HERE/name).read_bytes()
        need(hashlib.sha256(value).hexdigest()==sha,"SHA256 immutable checkpoint file: "+name)
        raw[name]=value
    for name,(sha,blob) in SOURCE_PINS.items():
        need(name in raw,"source belongs to frozen checkpoint")
        value=raw[name]
        need(hashlib.sha256(value).hexdigest()==sha,"SHA256 source: "+name)
        need(hashlib.sha1(b"blob "+str(len(value)).encode()+b"\0"+value).hexdigest()==blob,
             "Git blob source: "+name)
    return (strict(gzip.decompress(raw["sources/OLD-WORD.json.gz"])),
            strict(gzip.decompress(raw["sources/NEW-WORD.json.gz"])),
            strict(raw["sources/LIFTS.json"]))


def frame_spaces(word):
    need(type(word) is dict and type(word.get("public")) is int and word["public"]==PUBLIC,
         "770 public inputs")
    need(type(word.get("owned_fields")) is int and word["owned_fields"]==OWNED,"29 owned labels")
    frames=word["frames"]
    need(type(frames) is list and frames,"frame array")
    spaces=[]
    for generators in frames:
        need(type(generators) is list and len(generators)<=9,"frame generator width")
        values={0}
        for vector in generators:
            integer(vector,512,"nine-bit frame generator")
            values|={x^vector for x in values}
        need(len(values)==1<<len(generators),"independent frame generators")
        spaces.append(frozenset(values))
    for name in ("initial","final"):
        need(type(word[name]) is list and len(word[name])==PUBLIC,"public frame boundary array")
        for value in word[name]:
            integer(value,len(frames),"public frame label")
    return spaces


def expected_maps(word,lifts):
    live=word["live"]
    need(type(live) is list and len(live)==len(set(live))==len(word["ports"])==104,"104 declared main pairs")
    for role in live:
        integer(role,PUBLIC-112,"main driving role")
    need(not(set(live)&{r+112 for r in live}),"disjoint main pairs")
    M=[{i:Q(1)} for i in range(PUBLIC)]
    for role in live:
        M[role+112][role]=Q(1)
    H={}
    need(type(lifts) is dict and type(lifts.get("schema_version")) is int and lifts["schema_version"]==1,
         "lift schema")
    tail=[]
    for rnd in lifts["rounds"]:
        for cluster in rnd["clusters"]:
            for raw,entry in cluster["anchors"].items():
                role=int(raw)
                need(str(role)==raw and role in ANCHORS and role not in H,"six unique anchor columns")
                column={}
                for raw_input,raw_value in entry["h"].items():
                    coordinate=int(raw_input)
                    need(str(coordinate)==raw_input,"canonical lift role key")
                    integer(coordinate,PUBLIC,"public lift input")
                    column[coordinate]=fraction(raw_value)
                H[role]=column
                for output,value in column.items():
                    if output!=role:
                        tail.append(["ADD",output,role,str(-value),OMEGA])
    need(tuple(sorted(H))==ANCHORS,"exact lift anchor set")
    N=[{} for _ in range(PUBLIC)]
    for q,column in H.items():
        need([column.get(r,Q(0)) for r in ANCHORS]==[Q(int(r==q)) for r in ANCHORS],"all-six raw anchor units")
        for output,value in column.items():
            delta=value-Q(int(output==q))
            if delta:
                N[output][q]=delta
    P=[dict(row) for row in M]
    for output,row in enumerate(N):
        add(P[output],row,Q(1))
    need(len(tail)==16,"16 literal restoration ADDs")
    return M,N,P,tail


def first_difference(actual,expected):
    for output,(a,b) in enumerate(zip(actual,expected)):
        for coordinate in sorted(a.keys()|b.keys()):
            if a.get(coordinate,Q(0))!=b.get(coordinate,Q(0)):
                return {"output":output,"input":coordinate,"actual":str(a.get(coordinate,Q(0))),
                        "expected":str(b.get(coordinate,Q(0)))}
    return None


def require_equal(actual,expected,label):
    witness=first_difference(actual,expected)
    need(witness is None,label+" public coefficient mismatch "+canonical(witness))


def replay(word,spaces,capture=None):
    current=word["initial"][:]+[None]*OWNED
    rows=[{i:Q(1)} for i in range(PUBLIC)]+[None]*OWNED
    active={}
    lifecycle=[]
    opcode_counts={}
    paid_count=0
    peak=0
    next_lifetime=0
    copy_checks=0
    maximum_terms=PUBLIC
    prefix=None
    for i,event in enumerate(word["program"]):
        need(type(event) is list and len(event)>=2,"literal event schema")
        op,role=event[:2]
        integer(role,PUBLIC+OWNED,"literal role")
        opcode_counts[op]=opcode_counts.get(op,0)+1
        if op=="MOVE":
            need(len(event)==5 and type(event[4]) is bool,"MOVE ownership flag")
            src,dst,owned=event[2:]
            integer(src,len(spaces),"MOVE source frame")
            integer(dst,len(spaces),"MOVE destination frame")
            need(current[role]==src and (role in active)==owned,
                 "literal MOVE source/ownership at event "+str(i))
            need(spaces[dst]<spaces[src] if owned else spaces[src]<spaces[dst],
                 "strict nested MOVE at event "+str(i))
            current[role]=dst
            paid_count+=1
        elif op=="INIT":
            need(len(event)==3 and role>=PUBLIC and role not in active,"owned blank INIT lifecycle")
            frame=event[2]
            integer(frame,len(spaces),"INIT frame")
            next_lifetime+=1
            active[role]=(next_lifetime,i,frame)
            rows[role]={}
            current[role]=frame
            peak=max(peak,len(active))
        elif op=="CLEAR":
            need(len(event)==3 and role in active and current[role]==event[2],"owned CLEAR lifecycle/frame")
            ordinal,birth,initial_frame=active.pop(role)
            coefficients=sparse(rows[role])
            lifecycle.append({"lifetime":ordinal,"role":role,"init_index":birth,"clear_index":i,
                              "init_frame":initial_frame,"clear_frame":event[2],
                              "support":len(coefficients),"public_functional":coefficients,
                              "functional_sha256":digest(coefficients)})
            rows[role]=None
            current[role]=None
        else:
            need(op in ("ADD","COPY","SCALE") and len(event)==(4 if op=="SCALE" else 5),"scalar opcode/schema")
            coefficient,frame=fraction(event[-2]),event[-1]
            integer(frame,len(spaces),"scalar frame")
            need(current[role]==frame and (role<PUBLIC or role in active),
                 "scalar destination frame/lifecycle at event "+str(i))
            if op=="SCALE":
                absolute=abs(coefficient.numerator)
                need(absolute & (absolute-1)==0,"dyadic unit SCALE")
                rows[role]={k:coefficient*v for k,v in rows[role].items()}
            else:
                source=event[2]
                integer(source,PUBLIC+OWNED,"scalar source role")
                need(source!=role and current[source]==frame and (source<PUBLIC or source in active),
                     "scalar common frame/lifecycle at event "+str(i))
                if op=="COPY":
                    need(role in active and not rows[role],"COPY into blank owned field at event "+str(i))
                    rows[role]={k:coefficient*v for k,v in rows[source].items()}
                    copy_checks+=1
                else:
                    add(rows[role],rows[source],coefficient)
        total_terms=sum(len(row) for row in rows if row is not None)
        maximum_terms=max(maximum_terms,total_terms)
        need(total_terms<=100000,"bounded sparse endpoint state")
        if capture==i+1:
            prefix=[dict(row) for row in rows[:PUBLIC]]
    need(not active and all(row is None for row in rows[PUBLIC:]) and current[:PUBLIC]==word["final"],
         "every public and owned final frame/lifecycle")
    need(capture is None or prefix is not None,"requested literal prefix boundary reached")
    need(next_lifetime==len(lifecycle)==43 and peak==13,"43 lifetimes and peak13")
    return {"matrix":[dict(row) for row in rows[:PUBLIC]],"prefix":prefix,"clears":lifecycle,
            "inventory":{"events":len(word["program"]),"public_inputs":PUBLIC,"owned_labels":OWNED,
                         "owned_lifetimes":next_lifetime,"peak_owned":peak,"COPY_zero_checks":copy_checks,
                         "paid_moves":paid_count,"opcode_counts":opcode_counts,"maximum_sparse_terms":maximum_terms}}


def summary(matrix):
    payload=matrix_payload(matrix)
    return {"rows":PUBLIC,"columns":PUBLIC,"coefficient_positions":PUBLIC*PUBLIC,
            "nonzero_coefficients":sum(map(len,matrix)),"sha256":digest(payload),"public_rows":payload}


def counterfactuals(word,spaces,M):
    program=word["program"]
    targets={"omit_shared_carrier_624_response":["ADD",130,624,"-1/2",105],
             "omit_postponed_624_from_623":["ADD",624,623,"1",117],
             "omit_public205_restore":["ADD",205,624,"-1",OMEGA],
             "omit_dyadic732_restore":["ADD",732,624,"-1/2",OMEGA]}
    controls={}
    for label,target in targets.items():
        matches=[i for i,event in enumerate(program) if event==target]
        need(len(matches)==1,"unique actual endpoint control event")
        index=matches[0]
        mutated=dict(word)
        mutated["program"]=program[:index]+program[index+1:]
        try:
            result=replay(mutated,spaces)
        except ValueError as error:
            controls[label]={"kind":"one literal scalar ADD omitted; not an accepted alternative word",
                             "index":index,"event":target,"typing_rejection":str(error)}
        else:
            witness=first_difference(result["matrix"],M)
            need(witness is not None,"actual omitted scalar control must change a public coefficient")
            controls[label]={"kind":"one literal scalar ADD omitted; not an accepted alternative word",
                             "index":index,"event":target,"public_coefficient_witness":witness,
                             "all_frame_lifetime_COPY_guards_pass":True}
    return controls


def run():
    old,new,lifts=authenticated()
    spaces=frame_spaces(old)
    need(new["frames"]==old["frames"],"unchanged complete frame table")
    frame_spaces(new)
    need(all(old[key]==new[key] for key in old if key not in ("initial","program")),
         "unchanged other literal source metadata")
    need({r for r in range(PUBLIC) if old["initial"][r]!=new["initial"][r]}==set(ANCHORS),
         "six changed input frames only")
    M,N,P,tail=expected_maps(old,lifts)
    need(new["program"][-len(tail):]==tail,"actual16 restoration instructions and order")
    cut=len(new["program"])-len(tail)
    need(cut==17752,"literal prefix cut17752")
    baseline=replay(old,spaces)
    candidate=replay(new,spaces,capture=cut)
    require_equal(baseline["matrix"],M,"OLD=M")
    require_equal(candidate["prefix"],P,"actual NEW prefix=M+N")
    require_equal(candidate["matrix"],M,"final NEW=M")
    require_equal(candidate["matrix"],baseline["matrix"],"OLD/NEW exact equality")
    return {"schema_version":1,"scope":"literal OLD=M, NEW prefix=M+N and final NEW=M on arbitrary770 public inputs",
            "preserved_checkpoint_sha256":CHECKPOINT_SHA256,"source_pins":SOURCE_PINS,
            "declared_M":"identity plus output(r+112) receiving inputr for eachr in word.live",
            "scalar_model":{"MOVE":"identity", "INIT":"blank owned activation", "CLEAR":"formal reset after recording public functional",
                            "input_domain":"all770 public rational coordinates independently arbitrary under each word's own declared initial frame header; owned labels inactive beforeINIT"},
            "old_inventory":baseline["inventory"],"new_inventory":candidate["inventory"],
            "matrices":{"old":summary(baseline["matrix"]),"new_prefix":summary(candidate["prefix"]),"new":summary(candidate["matrix"])},
            "prefix_cut_t":cut,"restoration_tail":tail,"N_columns":{str(q):[[r,str(N[r][q])] for r in range(PUBLIC) if q in N[r]] for q in ANCHORS},
            "old_pre_CLEAR_functionals":baseline["clears"],"new_pre_CLEAR_functionals":candidate["clears"],
            "nonzero_pre_CLEAR_counts":{"old":sum(bool(item["public_functional"]) for item in baseline["clears"]),
                                         "new":sum(bool(item["public_functional"]) for item in candidate["clears"])},
            "controls":counterfactuals(new,spaces,M),
            "credit":"Own6376 forward sparse-row method reused transparently; author construction/checks and reported independent audit are predecessor evidence.",
            "limits":["The actual prefix equality closes delivery globally; no independent byte regeneration of the two-round author constructor is claimed.",
                      "OLD and NEW have six different initial frame charts; equal rational-coordinate maps do not identify their physical input embeddings.",
                      "All nonzero pre-CLEAR values are formal-model observations and supply no physical erasure permission.",
                      "Source native phases/all-width,physical caller,precision/compiler,complete budget/funding and all five framework assumptions remain.",
                      "No new tariff,kappa,selected frontier or physical supplier admission."]}


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit",action="store_true")
    options=parser.parse_args()
    result=run()
    payload=(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n").encode()
    if options.emit:
        sys.stdout.buffer.write(payload)
    else:
        receipt=HERE/"ENDPOINT-RESULT.json"
        need(receipt.is_file(),"retained ENDPOINT-RESULT.json receipt required")
        observed=strict(receipt.read_bytes())
        need(type(observed) is dict and type(observed.get("schema_version")) is int and observed["schema_version"]==1,
             "typed endpoint receipt schema")
        need(canonical(observed)==canonical(result),"strict typed ENDPOINT-RESULT receipt")
        print("PASS complete literal lift prefix/endpoint and retained receipt")
