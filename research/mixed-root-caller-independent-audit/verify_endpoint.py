#!/usr/bin/env python3
"""Independent forward68-component rational caller endpoint for fixed PR6398.

The34complex inputs are arbitrary.68is a realification representation, not
additional physical fields. The author already supplies exact forward/reverse
checks; this is independent cold implementation evidence, not first validation.
No author, peer or local-predecessor program is imported or executed.
"""
import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
SOURCES={'CONTROLLER.json': ['4aa7ee4e1bc4853200cf97474695054057cc354bc1778f35b6554a365aac412c', '4f7d7a2f13b13966b10c7b583d28d1bed210364c'], 'ROOT.json': ['2f25684c24ae0e1d10d4f8f29430aed3cef584f82c8ae840e82be0a72baa048d', 'b59f1ea89aca17f0a76131743c12f2c724421df8'], 'upstream-PROOF.md': ['bfbe0b872f6ff14c858bff47c6e3ac0bb8e43bc8eeaec20253744e3f44720fcd', '510bf9dba012949ea0f37d9e087ce8778b1951d0'], 'NOTICE': ['b6026dd901f3cb2e6ec6d5f7b32a38aa998005c8a1df93392151ca1766d45b33', '03e4ac5937424ed9f0ae0e4b33d6b0df0c9ec8d9'], 'controller-source.py': ['e5671c66a4091f1b482a750baf5bedf9ac0750e577efbe3c5b3d2860d2fa8edc', '393524f903b44be54884475d11200f06ce1dfddb'], 'algebra-source.py': ['02eb3380715294334710edd3273f267dc048264555bd60fefb86022bc9eda835', 'a06d6f641685e96b2f150ea6b741930a9ec037f8'], 'normalization-PROOF.md': ['68be52ab098ff9dd6edfe938e5bf36d14d5f49aa1cac94a3d0784566c05363e9', 'f910b5fbf9a9d519fa7d7c7503de51df5a796368'], 'author-caller-reverse.py': ['6435f092e7f435aa30db3877237056cc00fcb206fd8c87a3bddf380dbb7e80e9', 'be84e58dc5c1836261441c1a58d4ffe51315c23f'], 'headroom-NOTICE': ['87d3cf335599cec76ede9e68e58fa13b077e823004aab60ad17b22196cdc3747', '081d5cea1467c7cecfe35a37608963dda4e483b7']}
FROZEN={'SOURCE-PINS.json': 'c74239713cbebdea38f0cca551a17606617878a83c82d4ef0a5cb689e8ce9cb0', 'verify_local.py': '1cff5ecc5af60a97aca7ddc425f56a2abdf42fa8def6a64b9bf9abed8d9f08d9', 'oracle_local.py': 'e6191d69f80612ba6b51e8d2963ebc80fe77f35c163ae4e526eefa05b6bce393', 'LOCAL-RESULT.json': 'cb82b5ff7ccb32971ef839974f9d43461f89d8bd738409e5c3577aa0aa9f2894', 'LOCAL-ORACLE.json': 'ea0bcc77e8a1b9a21e24c35a318f7523b4867272d294fc73c57967e44fb9c7eb', 'PROOF.md': 'a40f40fe7812d5e7503178a1789c7f84f9d70fd4ba49f24f0612877c3b025820', 'sources/CONTROLLER.json': '4aa7ee4e1bc4853200cf97474695054057cc354bc1778f35b6554a365aac412c', 'sources/NOTICE': 'b6026dd901f3cb2e6ec6d5f7b32a38aa998005c8a1df93392151ca1766d45b33', 'sources/ROOT.json': '2f25684c24ae0e1d10d4f8f29430aed3cef584f82c8ae840e82be0a72baa048d', 'sources/algebra-source.py': '02eb3380715294334710edd3273f267dc048264555bd60fefb86022bc9eda835', 'sources/author-caller-reverse.py': '6435f092e7f435aa30db3877237056cc00fcb206fd8c87a3bddf380dbb7e80e9', 'sources/controller-source.py': 'e5671c66a4091f1b482a750baf5bedf9ac0750e577efbe3c5b3d2860d2fa8edc', 'sources/headroom-NOTICE': '87d3cf335599cec76ede9e68e58fa13b077e823004aab60ad17b22196cdc3747', 'sources/normalization-PROOF.md': '68be52ab098ff9dd6edfe938e5bf36d14d5f49aa1cac94a3d0784566c05363e9', 'sources/upstream-PROOF.md': 'bfbe0b872f6ff14c858bff47c6e3ac0bb8e43bc8eeaec20253744e3f44720fcd'}
FIELDS,REAL,STAGES=34,68,18
UNIT=(0,)*19
COUNTS={"ADD":277,"SWAP":126,"SCALE":80,"LAMBDA":20,"QUERY":17,"IDLE":14,"LOCAL":18,"Q_POWER":16,"IDLE_ONE":2}
MAX_TERMS=200000
MAX_CELL_TERMS=32768
MAX_COEFFICIENT_BITS=4096
WORKING_STATE_ACCOUNTING_LIMIT=256*1024*1024


def need(ok,message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False)


def digest(value):
    return hashlib.sha256((canonical(value)+"\n").encode()).hexdigest()


def strict(raw):
    def pairs(items):
        result={}
        for key,value in items:
            need(key not in result,"duplicate JSON key")
            result[key]=value
        return result
    return json.loads(raw,object_pairs_hook=pairs,
                      parse_constant=lambda x:(_ for _ in ()).throw(ValueError("nonfinite JSON")))


def authenticated():
    raw={}
    for name,sha in FROZEN.items():
        data=(HERE/name).read_bytes()
        need(hashlib.sha256(data).hexdigest()==sha,"SHA256 frozenR9file: "+name)
        raw[name]=data
    for name,(sha,blob) in SOURCES.items():
        data=raw["sources/"+name]
        need(hashlib.sha256(data).hexdigest()==sha,"SHA256 source: "+name)
        need(hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()==blob,"Git blob source: "+name)
    return strict(raw["sources/CONTROLLER.json"]),strict(raw["sources/ROOT.json"])


def integer(value,limit,label):
    need(type(value) is int and 0<=value<limit,label)


def coefficient(value):
    need(type(value) in (int,str),"rational coefficient literal")
    out=F(value)
    need(out and (type(value) is int or str(out)==value),"nonzero canonical rational coefficient")
    return out


def stage_list(values):
    need(type(values) is list and values,"nonempty stage list")
    for value in values:
        need(type(value) is int and 1<=value<=STAGES,"independent formal stage label")
    need(len(values)==len(set(values)),"distinct stages in oneidle")


def validate(events,fixed):
    need(type(events) is list,"caller events array")
    for event in events:
        need(type(event) is list and event and type(event[0]) is str and event[0] in COUNTS,"caller opcode")
        op=event[0]
        if op in ("ADD","QUERY"):
            need(len(event)==4,"binary operationarity")
            integer(event[1],FIELDS,"destination field")
            integer(event[2],FIELDS,"source field")
            need(event[1]!=event[2],"distinct source/destination")
            if op=="ADD":coefficient(event[3])
            else:need(type(event[3]) is int and event[3] in (-1,1),"QUERYcentralpower")
        elif op in ("SCALE","LAMBDA","Q_POWER"):
            need(len(event)==3,"unary operationarity")
            integer(event[1],FIELDS,"unary field")
            if op=="SCALE":coefficient(event[2])
            else:need(type(event[2]) is int and event[2] in ((-1,1) if op=="LAMBDA" else (-2,2)),"unary central sign")
        elif op=="SWAP":
            need(len(event)==3,"SWAP arity")
            integer(event[1],FIELDS,"SWAP field")
            integer(event[2],FIELDS,"SWAP field")
            need(event[1]!=event[2],"distinct SWAP fields")
        elif op=="LOCAL":
            need(len(event)==4 and type(event[1]) is int and 1<=event[1]<=STAGES,"LOCAL stage/arity")
            integer(event[2],FIELDS,"LOCALsource")
            integer(event[3],FIELDS,"LOCALdestination")
            need(event[2]!=event[3],"distinct LOCALfields")
        elif op=="IDLE":
            need(len(event)==4,"IDLE arity")
            integer(event[1],FIELDS,"IDLEfield")
            integer(event[2],FIELDS,"IDLEfield")
            need(event[1]!=event[2],"distinct IDLEfields")
            stage_list(event[3])
        else:
            need(len(event)==3,"IDLE_ONEarity")
            integer(event[1],FIELDS,"IDLE_ONEfield")
            stage_list(event[2])
    need(sorted(e[1] for e in events if e[0]=="LOCAL")==list(range(1,19)),"all18 distinct native stages exactly once")
    if fixed:
        need(len(events)==570 and dict(Counter(e[0] for e in events))==COUNTS,"fixed570event inventory")


def expected(word,root):
    need(word.get("schema")==root.get("schema")=="mixed-projector-query-root/2","fixedcaller schema")
    need(type(word.get("roles")) is int and word["roles"]==FIELDS and type(word.get("stages")) is int and word["stages"]==STAGES,
         "34complexfields/18stages")
    need(type(word.get("ambient_rank")) is int and word["ambient_rank"]==153,"source ambient header")
    need(type(root.get("fields")) is int and root["fields"]==6,"sixrootfields")
    stage=1
    next_field=6
    nodes=[]
    def leaves(tree):
        nonlocal stage
        if type(tree) is int:
            need(tree==1,"nativeleaf")
            out=[stage]
            stage+=1
            return {"stages":out}
        need(type(tree) is list and len(tree)==2,"binarytree")
        left,right=leaves(tree[0]),leaves(tree[1])
        return {"left":left,"right":right,"stages":left["stages"]+right["stages"]}
    def node_roles(tree,sign):
        nonlocal next_field
        if "left" not in tree:
            return
        roles=[next_field,next_field+1]
        next_field+=2
        nodes.append({"roles":roles,"stages":tree["stages"],"exponent":sign})
        node_roles(tree["left"],-sign)
        node_roles(tree["right"],sign)
    need(type(root["children"]) is list and len(root["children"])==4,"fourchildtrees")
    trees=[]
    for child in root["children"]:
        tree=leaves(child)
        trees.append(tree)
        node_roles(tree,1)
    need(stage==19 and next_field==34 and len(nodes)==14,"allfreshnative/stage/node fields")
    need([len(tree["stages"]) for tree in trees]==root["child_sizes"]==[7,2,2,7],"fourchildsizes")
    need(word["nodes"]==nodes,"independenttree/nodebinding")
    monomials=[None]*FIELDS
    need(type(root["masks"]) is list and len(root["masks"])==6,"sixrootmasks")
    for role,mask in enumerate(root["masks"]):
        need(type(mask) is list and len(mask)==4 and all(type(bit) is int and bit in (0,1) for bit in mask),"fourindependentrootbits")
        selected={s for bit,tree in zip(mask,trees) if bit for s in tree["stages"]}
        monomials[role]=[-1,0]+[int(s in selected) for s in range(1,19)]
    for node in nodes:
        for role,sign in zip(node["roles"],(-node["exponent"],node["exponent"])):
            need(monomials[role] is None,"unique binaryoutput")
            monomials[role]=[sign,0]+[int(s in node["stages"]) for s in range(1,19)]
    need(type(word["diagonal"]) is list and len(word["diagonal"])==FIELDS,"34declaredtargets")
    for raw in word["diagonal"]:
        need(type(raw) is list and len(raw)==20 and type(raw[0]) is int and raw[0] in (-1,1)
             and type(raw[1]) is int and raw[1]==0 and all(type(x) is int and x in (0,1) for x in raw[2:]),
             "central/dummy0/stage target typing")
    need(word["diagonal"]==monomials,"independentROOT/tree target declarations")
    matrix=[]
    for real in range(REAL):
        raw=monomials[real//2]
        key=(raw[0]%4,)+tuple(raw[2:])
        matrix.append({real:{key:F(1)}})
    return matrix,monomials


class Bounds:
    def __init__(self):
        self.peak_terms=0
        self.peak_cell_terms=0
        self.max_stage_exponent=0
        self.max_numerator_bits=1
        self.max_denominator_bits=1
    def value(self,x):
        self.max_numerator_bits=max(self.max_numerator_bits,abs(x.numerator).bit_length())
        self.max_denominator_bits=max(self.max_denominator_bits,x.denominator.bit_length())
        need(max(self.max_numerator_bits,self.max_denominator_bits)<=MAX_COEFFICIENT_BITS,"coefficient bitlength cap")
    def shifted(self,key,q,stages):
        out=list(key)
        out[0]=(out[0]+q)%4
        for stage in stages:
            out[stage]+=1
            self.max_stage_exponent=max(self.max_stage_exponent,out[stage])
        return tuple(out)
    def state(self,rows):
        cells=[poly for row in rows for poly in row.values()]
        total=sum(len(poly) for poly in cells)
        largest=max(map(len,cells),default=0)
        self.peak_terms=max(self.peak_terms,total)
        self.peak_cell_terms=max(self.peak_cell_terms,largest)
        need(total<=MAX_TERMS and largest<=MAX_CELL_TERMS,"sparse polynomial term cap")
        # Conservative working-state accounting, not a whole-process RSS claim.
        # Count shared small integers/monomials repeatedly and include all dict
        # allocations. OS RSS stays in external logs; this value is not retained.
        bitmax=max(self.max_numerator_bits,self.max_denominator_bits)
        intsize=sys.getsizeof((1<<bitmax)-1)
        stage_size=sys.getsizeof(self.max_stage_exponent)
        perterm=sys.getsizeof(UNIT)+19*stage_size+sys.getsizeof(F(1))+2*intsize+128
        accounting=sum(sys.getsizeof(row) for row in rows)+sum(sys.getsizeof(poly) for poly in cells)+total*perterm
        need(accounting<=WORKING_STATE_ACCOUNTING_LIMIT,"conservative working-state memory accounting cap")
    def receipt(self):
        return {"peak_terms":self.peak_terms,"peak_cell_terms":self.peak_cell_terms,
                "observed_max_stage_exponent":self.max_stage_exponent,
                "max_numerator_bits":self.max_numerator_bits,"max_denominator_bits":self.max_denominator_bits}


def add_row(dst,src,c,bounds,q=0,stages=()):
    for column,poly in src.items():
        target=dst.setdefault(column,{})
        for key,value in poly.items():
            shifted=bounds.shifted(key,q,stages) if q or stages else key
            new=target.get(shifted,F(0))+c*value
            bounds.value(new)
            if new:
                target[shifted]=new
            else:
                target.pop(shifted,None)
        if not target:
            dst.pop(column,None)


def shift_row(row,bounds,q=0,stages=()):
    return {column:{bounds.shifted(key,q,stages):value for key,value in poly.items()}
            for column,poly in row.items()}


def evaluate(events,fixed=True):
    validate(events,fixed)
    rows=[{i:{UNIT:F(1)}} for i in range(REAL)]
    bounds=Bounds()
    bounds.state(rows)
    for event in events:
        op=event[0]
        if op in ("ADD","QUERY"):
            dst,src=event[1:3]
            c=coefficient(event[3]) if op=="ADD" else F(1)
            q=0 if op=="ADD" else event[3]
            for part in (0,1):
                add_row(rows[2*dst+part],rows[2*src+part],c,bounds,q=q)
        elif op=="SCALE":
            role,c=event[1],coefficient(event[2])
            for part in (0,1):
                for poly in rows[2*role+part].values():
                    for key in poly:
                        poly[key]*=c
                        bounds.value(poly[key])
        elif op=="SWAP":
            a,b=event[1:]
            for part in (0,1):
                rows[2*a+part],rows[2*b+part]=rows[2*b+part],rows[2*a+part]
        elif op=="LOCAL":
            stage,src,dst=event[1:]
            for part in (0,1):
                add_row(rows[2*dst+part],rows[2*src+part],F(1),bounds,q=-1)
            for role in (src,dst):
                for part in (0,1):
                    rows[2*role+part]=shift_row(rows[2*role+part],bounds,stages=(stage,))
        elif op=="Q_POWER":
            role,q=event[1:]
            for part in (0,1):
                rows[2*role+part]=shift_row(rows[2*role+part],bounds,q=q)
        elif op=="LAMBDA":
            role,sign=event[1:]
            real,imag=rows[2*role],rows[2*role+1]
            new_real,new_imag={},{}
            for c,row,q in ((F(1,2),real,0),(F(1,2),real,2),(F(-sign,2),imag,0),(F(sign,2),imag,2)):
                add_row(new_real,row,c,bounds,q=q)
            for c,row,q in ((F(1,2),imag,0),(F(1,2),imag,2),(F(sign,2),real,0),(F(-sign,2),real,2)):
                add_row(new_imag,row,c,bounds,q=q)
            rows[2*role],rows[2*role+1]=new_real,new_imag
        else:
            roles,selected=([event[1],event[2]],event[3]) if op=="IDLE" else ([event[1]],event[2])
            for role in roles:
                for part in (0,1):
                    rows[2*role+part]=shift_row(rows[2*role+part],bounds,stages=selected)
        bounds.state(rows)
    return rows,bounds.receipt()


def payload(rows):
    return [[[[list(key),str(value)] for key,value in sorted(row.get(column,{}).items())]
             for column in range(REAL)] for row in rows]


def first_difference(actual,expected):
    for output in range(REAL):
        for column in range(REAL):
            a,b=actual[output].get(column,{}),expected[output].get(column,{})
            for key in sorted(a.keys()|b.keys()):
                if a.get(key,F(0))!=b.get(key,F(0)):
                    return {"output_real":output,"input_real":column,"monomial":list(key),
                            "actual":str(a.get(key,F(0))),"expected":str(b.get(key,F(0)))}
    return None


def equal(actual,expected,label):
    witness=first_difference(actual,expected)
    need(witness is None,label+" actual polynomial mismatch "+canonical(witness))


def negate(poly):
    return {key:-value for key,value in poly.items()}


def complex_blocks(rows):
    result=[]
    for r in range(FIELDS):
        line=[]
        for c in range(FIELDS):
            a=rows[2*r].get(2*c,{})
            b=rows[2*r+1].get(2*c,{})
            need(rows[2*r+1].get(2*c+1,{})==a and rows[2*r].get(2*c+1,{})==negate(b),
                 "faithful complex-linear realification block")
            line.append((a,b))
        result.append(line)
    return result


def character_residual(actual,expected):
    A,B=complex_blocks(actual),complex_blocks(expected)
    result={}
    for name,phase in (("1",0),("-1",2),("i",1),("-i",3)):
        witness=None
        for r in range(FIELDS):
            for c in range(FIELDS):
                a,im=A[r][c]
                b,jm=B[r][c]
                combined={}
                for key in sorted(a.keys()|im.keys()|b.keys()|jm.keys()):
                    re=a.get(key,F(0))-b.get(key,F(0))
                    imaginary=im.get(key,F(0))-jm.get(key,F(0))
                    turn=(phase*key[0])%4
                    re,imaginary=((re,imaginary),(-imaginary,re),(-re,-imaginary),(imaginary,-re))[turn]
                    old_re,old_im=combined.get(key[1:],(F(0),F(0)))
                    combined[key[1:]]=(old_re+re,old_im+imaginary)
                for stages,(re,imaginary) in sorted(combined.items()):
                    if re or imaginary:
                        witness={"output_complex":r,"input_complex":c,"stage_exponents":list(stages),
                                 "real_residual":str(re),"imaginary_residual":str(imaginary)}
                        break
                if witness is not None:break
            if witness is not None:break
        result[name]={"all_stage_polynomials_zero":witness is None,"first_residual":witness}
    return result


def controls(events,expected):
    specifications=[]
    i=564
    need(events[i]==["LAMBDA",0,-1],"actual finalnormalizer controlsite564")
    changed=deepcopy(events)
    changed[i][2]=1
    specifications.append(("flip_final_LAMBDA_sign",i,events[i],changed))
    i=229
    need(events[i]==["IDLE_ONE",2,[8,9]],"actual individualidle controlsite229")
    specifications.append(("omit_individual_idle",i,events[i],events[:i]+events[i+1:]))
    for op in ("QUERY","ADD"):
        i=next(i for i,event in enumerate(events) if event[0]==op)
        changed=deepcopy(events)
        changed[i][3]=(-changed[i][3] if op=="QUERY" else str(-coefficient(changed[i][3])))
        specifications.append(("flip_first_"+op+"_coefficient",i,events[i],changed))
    result={}
    for label,index,event,changed in specifications:
        actual,observed=evaluate(changed,fixed=False)
        witness=first_difference(actual,expected)
        need(witness is not None,"actual control must give a coefficient mismatch: "+label)
        entry={"event_index":index,"original_event":event,"first_coefficient_witness":witness,
               "actual_matrix_sha256":digest(payload(actual)),"observed_bounds":observed,
               "kind":"corrupted literal caller,not an accepted alternative algorithm; only fixed count checks bypassed"}
        if label=="flip_final_LAMBDA_sign":
            characters=character_residual(actual,expected)
            need(characters["1"]["all_stage_polynomials_zero"] and characters["-1"]["all_stage_polynomials_zero"]
                 and not characters["i"]["all_stage_polynomials_zero"] and not characters["-i"]["all_stage_polynomials_zero"],
                 "finalnormalizer fault requires allfourcentralcharacters")
            entry["character_residuals"]=characters
        result[label]=entry
    changed=deepcopy(events)
    i=next(i for i,event in enumerate(events) if event[0]=="Q_POWER")
    changed[i][2]*=-1
    actual,observed=evaluate(changed,fixed=False)
    equal(actual,expected,"benign+-2QPOWER")
    result["benign_Q_POWER_even_sign_flip"]={"event_index":i,"original_event":events[i],"mutated_event":changed[i],
                                           "all4624cells_equal":True,"observed_bounds":observed}
    changed=events[:-6]+list(reversed(events[-6:]))
    actual,observed=evaluate(changed,fixed=False)
    equal(actual,expected,"benignindependenttailnormalizerorder")
    result["benign_terminal_LAMBDA_order_reversal"]={"event_range":[564,569],"all4624cells_equal":True,"observed_bounds":observed}
    return result


def run():
    word,root=authenticated()
    expected_matrix,monomials=expected(word,root)
    actual,observed=evaluate(word["events"],fixed=True)
    equal(actual,expected_matrix,"full570caller")
    complex_blocks(actual)
    normalized=payload(actual)
    return {"schema_version":1,"scope":"All4624rational polynomial cells of the literal570eventcaller on68arbitrary real input components,representing34complex fields",
            "frozen_R9_sha256":FROZEN,"source_pins":SOURCES,
            "ring":"Q[Q,D1,...,D18]/(Q^4-1); complexi is represented by real2x2blocks",
            "representation":{"complex_fields":FIELDS,"real_components":REAL,"real_index":"2r=real,2r+1=imaginary",
                              "monomial":"[Q exponent modulo4,D1 exponent,...,D18 exponent]","term":"[monomial,str(Fraction)]",
                              "full_matrix_payload":"68rows each68cells; eachcell sortedterms; [] meanszero"},
            "events":len(word["events"]),"stages":STAGES,"real_polynomial_positions":REAL*REAL,
            "nonzero_real_cells":sum(len(row) for row in actual),
            "nonzero_real_terms":sum(len(poly) for row in actual for poly in row.values()),
            "actual_matrix_sha256":digest(normalized),"actual_matrix":normalized,
            "independently_ROOT_tree_derived_complex_diagonal":monomials,"observed_bounds":observed,
            "caps":{"total_terms":MAX_TERMS,"cell_terms":MAX_CELL_TERMS,"coefficient_bits":MAX_COEFFICIENT_BITS,
                    "working_state_conservative_accounting_bytes":WORKING_STATE_ACCOUNTING_LIMIT},
            "controls":controls(word["events"],expected_matrix),
            "credit":"AliRomman/OpenAICodex already publishes forwardGaussian quotient and reversecharacter exact checks; old6361methods and allretained6348/native/notices keepcredit. This is independent implementation evidence,not firstverification.",
            "limits":["68real components are an audit representation,not68physical complex fields or added productive inputs.",
                      "All18stage variables remain distinct formal variables; no stage powers were reduced or specialized.",
                      "Workingstate memory accounting is conservative; actual processRSS/time are separate external evidence.",
                      "Native q^2=X/absolutephase,physical allwidth caller/erasure,ordinary funding,precision/compiler/classification/price/outer assumptions remain.",
                      "No new root,normalization theorem,kappa,physical supplier or selected-frontier change."]}


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit",action="store_true")
    options=parser.parse_args()
    result=run()
    raw=(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n").encode()
    if options.emit:
        sys.stdout.buffer.write(raw)
    else:
        receipt=HERE/"ENDPOINT-RESULT.json"
        need(receipt.is_file(),"retained ENDPOINT-RESULT.json receipt required")
        observed=strict(receipt.read_bytes())
        need(type(observed) is dict and type(observed.get("schema_version")) is int and observed["schema_version"]==1,"typed endpoint receipt schema")
        need(canonical(observed)==canonical(result),"strict typed ENDPOINT-RESULT receipt")
        print("PASS complete realified mixed caller endpoint and retained receipt")
