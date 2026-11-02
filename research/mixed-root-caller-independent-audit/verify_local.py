#!/usr/bin/env python3
"""Independent real-block local normalization/source-binding audit of PR6398.

The author already proves these normalization identities and checks the full
caller twice. This publishes separate local arithmetic/bindings, not a first
verification, full570-event transfer, native admission or new saving.
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
PINS={'CONTROLLER.json': ['4aa7ee4e1bc4853200cf97474695054057cc354bc1778f35b6554a365aac412c', '4f7d7a2f13b13966b10c7b583d28d1bed210364c'], 'ROOT.json': ['2f25684c24ae0e1d10d4f8f29430aed3cef584f82c8ae840e82be0a72baa048d', 'b59f1ea89aca17f0a76131743c12f2c724421df8'], 'upstream-PROOF.md': ['bfbe0b872f6ff14c858bff47c6e3ac0bb8e43bc8eeaec20253744e3f44720fcd', '510bf9dba012949ea0f37d9e087ce8778b1951d0'], 'NOTICE': ['b6026dd901f3cb2e6ec6d5f7b32a38aa998005c8a1df93392151ca1766d45b33', '03e4ac5937424ed9f0ae0e4b33d6b0df0c9ec8d9'], 'controller-source.py': ['e5671c66a4091f1b482a750baf5bedf9ac0750e577efbe3c5b3d2860d2fa8edc', '393524f903b44be54884475d11200f06ce1dfddb'], 'algebra-source.py': ['02eb3380715294334710edd3273f267dc048264555bd60fefb86022bc9eda835', 'a06d6f641685e96b2f150ea6b741930a9ec037f8'], 'normalization-PROOF.md': ['68be52ab098ff9dd6edfe938e5bf36d14d5f49aa1cac94a3d0784566c05363e9', 'f910b5fbf9a9d519fa7d7c7503de51df5a796368'], 'author-caller-reverse.py': ['6435f092e7f435aa30db3877237056cc00fcb206fd8c87a3bddf380dbb7e80e9', 'be84e58dc5c1836261441c1a58d4ffe51315c23f'], 'headroom-NOTICE': ['87d3cf335599cec76ede9e68e58fa13b077e823004aab60ad17b22196cdc3747', '081d5cea1467c7cecfe35a37608963dda4e483b7']}
MANIFEST_SHA256='c74239713cbebdea38f0cca551a17606617878a83c82d4ef0a5cb689e8ce9cb0'
ROLES,STAGES=34,18
COUNTS={"ADD":277,"SWAP":126,"SCALE":80,"LAMBDA":20,"QUERY":17,"IDLE":14,"LOCAL":18,"Q_POWER":16,"IDLE_ONE":2}


def need(ok,message):
    if not ok:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value,sort_keys=True,separators=(",",":"),allow_nan=False)


def strict(raw):
    def pairs(items):
        result={}
        for key,value in items:
            need(key not in result,"duplicate JSON key")
            result[key]=value
        return result
    return json.loads(raw,object_pairs_hook=pairs,
                      parse_constant=lambda x:(_ for _ in ()).throw(ValueError("nonfinite JSON")))


def authenticate():
    manifest=(HERE/"SOURCE-PINS.json").read_bytes()
    need(hashlib.sha256(manifest).hexdigest()==MANIFEST_SHA256,"SHA256 SOURCE-PINS manifest")
    raw={}
    for name,(sha,blob) in PINS.items():
        data=(HERE/"sources"/name).read_bytes()
        need(hashlib.sha256(data).hexdigest()==sha,"SHA256 source: "+name)
        need(hashlib.sha1(b"blob "+str(len(data)).encode()+b"\0"+data).hexdigest()==blob,"Git blob source: "+name)
        raw[name]=data
    return strict(raw["CONTROLLER.json"]),strict(raw["ROOT.json"])


def plus(a,b,scale=F(1)):
    out=dict(a)
    for exponent,value in b.items():
        new=out.get(exponent,F(0))+scale*value
        if new:
            out[exponent]=new
        else:
            out.pop(exponent,None)
    return out


def times(a,b):
    out={}
    for i,x in a.items():
        for j,y in b.items():
            k=(i+j)%4
            new=out.get(k,F(0))+x*y
            if new:
                out[k]=new
            else:
                out.pop(k,None)
    return out


def shifted(a,exponent):
    return {(i+exponent)%4:value for i,value in a.items()}


def zero(n):
    return [[{} for _ in range(n)] for _ in range(n)]


def identity(n):
    out=zero(n)
    for i in range(n):
        out[i][i]={0:F(1)}
    return out


def madd(a,b,scale=F(1)):
    return [[plus(x,y,scale) for x,y in zip(row,other)] for row,other in zip(a,b)]


def mmul(a,b):
    n=len(a)
    out=zero(n)
    for i in range(n):
        for j in range(n):
            for k in range(n):
                if a[i][k] and b[k][j]:
                    out[i][j]=plus(out[i][j],times(a[i][k],b[k][j]))
    return out


def mshift(a,exponent):
    return [[shifted(cell,exponent) for cell in row] for row in a]


def encode(a):
    return [[[[exponent,str(value)] for exponent,value in sorted(cell.items())] for cell in row] for row in a]


def matrix_difference(a,b):
    for i,(row,other) in enumerate(zip(a,b)):
        for j,(x,y) in enumerate(zip(row,other)):
            for exponent in sorted(x.keys()|y.keys()):
                if x.get(exponent,F(0))!=y.get(exponent,F(0)):
                    return {"output_component":i,"input_component":j,"central_exponent":exponent,
                            "actual":str(x.get(exponent,F(0))),"expected":str(y.get(exponent,F(0)))}
    return None


def equal(a,b,label):
    witness=matrix_difference(a,b)
    need(witness is None,label+" coefficient residual "+canonical(witness))


def embedded(block,start,n=4):
    out=identity(n)
    for i in range(len(block)):
        for j in range(len(block)):
            out[start+i][start+j]=dict(block[i][j])
    return out


def blocks(a,b,c,d):
    out=zero(4)
    for block,r,s in ((a,0,0),(b,0,2),(c,2,0),(d,2,2)):
        for i in range(2):
            for j in range(2):
                out[r+i][s+j]=dict(block[i][j])
    return out


def constant(rows):
    return [[{0:F(value)} if value else {} for value in row] for row in rows]


def evaluate(matrix,q):
    # Evaluate the central formal Q in a2x2 rational real representation.
    out=zero(2)
    power=identity(2)
    for exponent in range(4):
        coefficient=constant([[cell.get(exponent,F(0)) for cell in row] for row in matrix])
        out=madd(out,mmul(coefficient,power))
        power=mmul(power,q)
    return out


def local_arithmetic():
    I=identity(2)
    J=constant([[0,-1],[1,0]])
    negative_I=constant([[-1,0],[0,-1]])
    equal(mmul(J,J),negative_I,"realification i squared")
    A=madd(I,J,F(1))
    A=[[{k:v/2 for k,v in cell.items()} for cell in row] for row in A]
    B=madd(I,J,F(-1))
    B=[[{k:v/2 for k,v in cell.items()} for cell in row] for row in B]
    lam=madd(madd(I,mshift(I,2)),madd(J,mshift(J,2),F(-1)))
    lam=[[{k:v/2 for k,v in cell.items()} for cell in row] for row in lam]
    inv=madd(madd(I,mshift(I,2)),madd(J,mshift(J,2),F(-1)),F(-1))
    inv=[[{k:v/2 for k,v in cell.items()} for cell in row] for row in inv]
    S=mshift(lam,-1)
    equal(mmul(inv,lam),I,"lambda inverse")
    equal(mmul(lam,lam),mshift(I,2),"lambda squared=Q squared")
    equal(mmul(S,S),I,"S squared=I")
    equal(mmul(inv,S),mshift(I,-1),"lambda inverse S=Q inverse")
    # Source wrapper chronology: entrylambda-, U(Q^-1), exitlambda+,
    # then ordinaryADD0<-1 with coefficient-1.
    nothing=zero(2)
    Uq=blocks(I,mshift(I,-1),nothing,I)
    Uminus=blocks(I,negative_I,nothing,I)
    wrapper=mmul(Uminus,mmul(embedded(lam,0),mmul(Uq,embedded(inv,0))))
    expected=blocks(I,madd(S,I,F(-1)),nothing,I)
    equal(wrapper,expected,"literal local wrapper=U(S-I)")
    # Displayed four in-place ordinary operations on one translation orbit.
    minusJ=constant([[0,1],[-1,0]])
    E1=blocks(I,minusJ,nothing,I)
    E2=embedded(A,0)
    E3=embedded(madd(I,J),2)
    E4=blocks(I,nothing,minusJ,I)
    operations=[E1,E2,E3,E4]
    product=identity(4)
    for operation in operations:
        product=mmul(operation,product)
    desired=blocks(A,B,B,A)
    equal(product,desired,"four displayed ordinary operations")
    def conjugate(matrix):
        signs=[1,-1,1,-1]
        return [[{k:v*signs[i]*signs[j] for k,v in cell.items()} for j,cell in enumerate(row)] for i,row in enumerate(matrix)]
    inverse_product=identity(4)
    for operation in operations:
        inverse_product=mmul(conjugate(operation),inverse_product)
    equal(mmul(inverse_product,product),identity(4),"conjugated primitive sequence is inverse")
    real_bounds=[]
    for operation in operations:
        need(all(set(cell)<= {0} for row in operation for cell in row),"ordinary maps have no central dependence")
        bound=max(sum(abs(cell.get(0,F(0))) for cell in row) for row in operation)
        need(bound<=2,"componentwise real infinity step bound")
        real_bounds.append(str(bound))
    # A deliberately incomplete real-only normalizer is invisible atQ=+-1.
    real_only=madd(I,mshift(I,2))
    real_only=[[{k:v/2 for k,v in cell.items()} for cell in row] for row in real_only]
    bad=mmul(inv,real_only)
    residual=madd(bad,I,F(-1))
    need(matrix_difference(bad,I) is not None,"missing imaginary contribution must be detected")
    characters={"1":I,"-1":negative_I,"i":J,"-i":minusJ}
    character_residuals={name:encode(evaluate(residual,q)) for name,q in characters.items()}
    for name in ("1","-1"):
        equal(evaluate(residual,characters[name]),zero(2),"two-character blind control")
    for name in ("i","-i"):
        need(matrix_difference(evaluate(residual,characters[name]),zero(2)) is not None,"fourth-root character detects fault")
    # Reproduce the published warning: two q=-i factors have localS=+1,
    # but their combinedq=-1 has globalS=-1.
    one=evaluate(S,J)
    whole=evaluate(S,negative_I)
    equal(one,I,"published one-column character example")
    equal(whole,negative_I,"published whole-field character example")
    need(mmul(one,one)!=whole,"tensoring one-column normalization is not global normalization")
    equal(mshift(I,-2),mshift(I,2),"benign central even-power sign control")
    return {"ring":"Mat_2(Q[Q]/(Q^4-1)), complexi represented byJ", "i_matrix":encode(J),
            "lambda":encode(lam),"lambda_inverse":encode(inv),"S":encode(S),"wrapper":encode(wrapper),
            "identities":["lambda_inverse*lambda=I","lambda^2=Q^2I","S^2=I","lambda_inverse*S=Q^-1I","entrylambda-/U(Q^-1)/exitlambda+/ADD-1=U(S-I)"],
            "ordinary_orbit_product":encode(product),"ordinary_orbit_inverse_product":encode(inverse_product),
            "four_primitive_maps":list(map(encode,operations)),"componentwise_real_linf_step_bounds":real_bounds,
            "complex_modulus_max_step_bounds":["2","1","2","2"],
            "complex_bound_reason":"Triangle inequality,|i|=1,|(1+i)/2|^2=1/2<=1,|1+i|^2=2<=4; the real row-sum bound alone is not this complex-modulus statement.",
            "controls":{"missing_imaginary_part":{"first_inverse_residual":matrix_difference(bad,I),"full_residual":encode(residual),"character_residuals":character_residuals,"kind":"corrupted local normalizer,not a valid alternative implementation"},
                        "published_global_vs_tensor_character":{"local_S":encode(one),"tensor_product_character":encode(mmul(one,one)),"global_S":encode(whole),"kind":"already published source counterexample independently recalculated"},
                        "benign_Q_POWER_sign_flip":{"minus2":encode(mshift(I,-2)),"plus2":encode(mshift(I,2)),"equal":True}},
            "limit":"Formal local identities and the displayed two-address primitive specification; no native phase,address-loop implementation or fullcaller transfer."}


def integer(value,limit,message):
    need(type(value) is int and 0<=value<limit,message)


def scalar(value):
    need(type(value) in (int,str),"scalar rational literal type")
    q=F(value)
    need(q and (type(value) is int or str(q)==value),"nonzero canonical rational scalar")
    return q


def stage_set(values):
    need(type(values) is list and values and len(set(values))==len(values),"nonempty distinct stage set")
    for value in values:
        need(type(value) is int and 1<=value<=STAGES,"formal stage label")


def validate(word):
    need(type(word) is dict and word.get("schema")=="mixed-projector-query-root/2","literal caller schema")
    need(type(word.get("roles")) is int and word["roles"]==ROLES and type(word.get("stages")) is int and word["stages"]==STAGES,
         "34complex fields and18stages")
    need(type(word.get("ambient_rank")) is int and word["ambient_rank"]==9+8*STAGES,"declared ambient rank153")
    events=word["events"]
    need(type(events) is list and len(events)==570,"literal570eventcount")
    for event in events:
        need(type(event) is list and event and event[0] in COUNTS,"caller opcode")
        op=event[0]
        if op in ("ADD","QUERY"):
            need(len(event)==4,"ADD/QUERY arity")
            integer(event[1],ROLES,"destination role")
            integer(event[2],ROLES,"source role")
            need(event[1]!=event[2],"distinct source anddestination")
            if op=="ADD":scalar(event[3])
            else:need(type(event[3]) is int and event[3] in (-1,1),"query central exponent")
        elif op=="SCALE":
            need(len(event)==3,"SCALEarity")
            integer(event[1],ROLES,"SCALErole")
            scalar(event[2])
        elif op=="SWAP":
            need(len(event)==3,"SWAParity")
            integer(event[1],ROLES,"SWAProle")
            integer(event[2],ROLES,"SWAProle")
            need(event[1]!=event[2],"distinct SWAProles")
        elif op=="LOCAL":
            need(len(event)==4 and type(event[1]) is int and 1<=event[1]<=STAGES,"LOCALstage/arity")
            integer(event[2],ROLES,"LOCALsource")
            integer(event[3],ROLES,"LOCALdestination")
            need(event[2]!=event[3],"LOCALdistinct roles")
        elif op in ("Q_POWER","LAMBDA"):
            need(len(event)==3,"central unaryarity")
            integer(event[1],ROLES,"central unaryrole")
            need(type(event[2]) is int and event[2] in ((-2,2) if op=="Q_POWER" else (-1,1)),"central unaryexponent/sign")
        elif op=="IDLE":
            need(len(event)==4,"pairedIDLEarity")
            integer(event[1],ROLES,"IDLErole")
            integer(event[2],ROLES,"IDLErole")
            need(event[1]!=event[2],"IDLEdistinct roles")
            stage_set(event[3])
        else:
            need(len(event)==3,"IDLE_ONEarity")
            integer(event[1],ROLES,"IDLE_ONErole")
            stage_set(event[2])
    need(dict(Counter(event[0] for event in events))==COUNTS,"literal opcode inventory")
    need(sorted(event[1] for event in events if event[0]=="LOCAL")==list(range(1,STAGES+1)),"all18native stages once")
    return events


def bind(word,root):
    events=validate(word)
    need(root["schema"]==word["schema"] and type(root["fields"]) is int and root["fields"]==6,"sixfield ROOTspec")
    sites=root["sites"]
    need(len(sites)==7 and [site["site"] for site in sites]==list(range(7)),"seven chronological root sites")
    full=[i for i,site in enumerate(sites) if site["full"] is True]
    thin=[i for i,site in enumerate(sites) if site["full"] is False]
    need(full==root["full_sites"]==[0,1,5,6] and thin==root["thin_sites"]==[2,3,4],"fourfull/threethin sites")
    for site in sites:
        need(type(site["stage_rank"]) is int and site["stage_rank"] in (2,3),"declared stage projector rank")
    next_stage,next_role=1,6
    nodes,leaves,trees=[],[],[]
    def label(tree):
        nonlocal next_stage
        if type(tree) is int:
            need(tree==1,"one native leaf")
            result={"stage":next_stage,"stages":[next_stage]}
            next_stage+=1
            return result
        need(type(tree) is list and len(tree)==2,"binary child tree")
        left,right=label(tree[0]),label(tree[1])
        return {"left":left,"right":right,"stages":left["stages"]+right["stages"]}
    def allocate(tree,x,y,exponent):
        nonlocal next_role
        if "stage" in tree:
            leaves.append({"stage":tree["stage"],"source":x,"destination":y,"exponent":exponent})
            return
        a,b=next_role,next_role+1
        next_role+=2
        nodes.append({"roles":[a,b],"stages":tree["stages"],"exponent":exponent})
        allocate(tree["left"],y,x,-exponent)
        allocate(tree["right"],x,y,exponent)
    need(type(root["children"]) is list and len(root["children"])==4,"four declared children")
    for child in root["children"]:
        tree=label(child)
        startnode,startleaf=len(nodes),len(leaves)
        allocate(tree,0,1,1)
        trees.append({"stages":tree["stages"],"nodes":nodes[startnode:],"leaves":leaves[startleaf:]})
    sizes=[len(tree["stages"]) for tree in trees]
    need(sizes==root["child_sizes"]==[7,2,2,7] and next_stage==19 and next_role==ROLES,"fourtree dimensions/fresh roles")
    need(word["nodes"]==nodes and len(nodes)==14,"node roles/exponents/stages from independent tree walk")
    monomials=[None]*ROLES
    masks=root["masks"]
    need(type(masks) is list and len(masks)==6,"six root masks")
    for role,mask in enumerate(masks):
        need(type(mask) is list and len(mask)==4 and all(type(bit) is int and bit in (0,1) for bit in mask),"fourindependent stage bits")
        selected={stage for bit,tree in zip(mask,trees) if bit for stage in tree["stages"]}
        monomials[role]=[-1,0]+[int(stage in selected) for stage in range(1,19)]
    for node in nodes:
        a,b=node["roles"]
        for role,exponent in ((a,-node["exponent"]),(b,node["exponent"])):
            need(monomials[role] is None,"fresh binary output role")
            monomials[role]=[exponent,0]+[int(stage in node["stages"]) for stage in range(1,19)]
    for monomial in word["diagonal"]:
        need(type(monomial) is list and len(monomial)==20 and type(monomial[0]) is int and monomial[0] in (-1,1)
             and type(monomial[1]) is int and monomial[1]==0 and all(type(x) is int and x in (0,1) for x in monomial[2:]),
             "declared monomial schema/stagezero")
    need(word["diagonal"]==monomials,"ROOT/node derived declared34monomials")
    normalizers=[i for i,event in enumerate(events) if event[0]=="LAMBDA"]
    need(len(normalizers)==20 and [events[i] for i in normalizers[:14]]==[["LAMBDA",0,s] for _ in range(7) for s in (-1,1)],
         "seven entryminus/exitplus wrappers")
    need(normalizers[14:]==list(range(564,570)) and events[564:]==[["LAMBDA",r,-1] for r in range(6)],"six inverse outputnormalizers")
    bindings=[]
    covered=set(normalizers)
    full_index=0
    for site_index,site in enumerate(sites):
        start,end=normalizers[2*site_index:2*site_index+2]
        body=events[start+1:end]
        covered.update(range(start,end+1))
        need(events[end+1]==["ADD",0,1,-1],"ordinary subtractone after each normalized query")
        locals_in_body=[e[1] for e in body if e[0]=="LOCAL"]
        idle_one=[e for e in body if e[0]=="IDLE_ONE"]
        if site_index in full:
            tree=trees[full_index]
            full_index+=1
            need(sorted(locals_in_body)==tree["stages"],"wrapper assigned independent childstages")
            expected_idle=[["IDLE",node["roles"][0],node["roles"][1],node["stages"]] for node in tree["nodes"]]
            need([e for e in body if e[0]=="IDLE"]==expected_idle,"all paired wholeidles in correct child")
            need([e for e in body if e[0]=="QUERY"]==[["QUERY",node["roles"][0],node["roles"][1],-node["exponent"]] for node in tree["nodes"]],
                 "all binary childqueries in correct wrapper")
            expected_one=[["IDLE_ONE",r,tree["stages"]] for r in range(2,site["stage_rank"])]
            need(idle_one==expected_one,"rankthree individualidle binding")
            native_windows=[]
            for leaf in tree["leaves"]:
                target=["LOCAL",leaf["stage"],leaf["source"],leaf["destination"]]
                positions=[i for i in range(start+1,end) if events[i]==target]
                need(len(positions)==1,"literal native leaf source/destination")
                i=positions[0]
                swap=["SWAP",leaf["source"],leaf["destination"]]
                need(events[i-1]==events[i+1]==swap,"native leaf interchange wrappers")
                if leaf["exponent"]==-1:
                    need(events[i-2]==["Q_POWER",leaf["source"],-2] and events[i+2]==["Q_POWER",leaf["source"],2],
                         "negative leaf ordinary translation wrappers")
                native_windows.append({**leaf,"LOCAL_index":i})
            selected=tree["stages"]
        else:
            need(body==[["QUERY",0,1,-1]] and not idle_one,"single normalized thinquery body")
            native_windows=[]
            selected=[]
        bindings.append({"site":site_index,"full":site["full"],"stage_rank":site["stage_rank"],
                         "entry_index":start,"exit_index":end,"subtract_one_index":end+1,
                         "child_stages":selected,"native_windows":native_windows,"individual_idles":idle_one})
    need(all(i in covered or event[0] in ("ADD","SCALE","SWAP") for i,event in enumerate(events)),
         "all nonordinary calleroperations are bound to wrappers")
    return {"schema":word["schema"],"complex_fields":ROLES,"optional_realified_coordinates":2*ROLES,
            "stages":STAGES,"events":len(events),"opcode_counts":COUNTS,"arbitrary_caller_inputs":ROLES,
            "owned_or_initialized_caller_fields":0,"child_sizes":sizes,"child_stage_sets":[x["stages"] for x in trees],
            "nodes_from_tree":nodes,"expected_monomials_from_ROOT_nodes":monomials,
            "root_output_support_order":["ABCD","AB","CD","empty","C","B"],
            "wrapper_bindings":bindings,"output_normalizer_indices":normalizers[14:],
            "scope":"Literal source/target declarations and wrapper placement; not a computed570event endpoint."}


def rejected(action):
    try:
        action()
    except ValueError as error:
        return str(error)
    raise ValueError("counterfactual source binding accepted")


def binding_controls(word,root):
    controls={}
    bad=deepcopy(word)
    index=next(i for i,e in enumerate(bad["events"]) if e[0]=="LAMBDA")
    bad["events"][index][2]*=-1
    controls["single_wrapper_sign_changed"]={"index":index,"rejection":rejected(lambda:bind(bad,root)),"kind":"source binding failure,not a full endpoint calculation"}
    bad=deepcopy(word)
    index=next(i for i,e in enumerate(bad["events"]) if e[0]=="IDLE_ONE")
    bad["events"][index][2]=[1,2]
    controls["individual_idle_wrong_child"]={"index":index,"rejection":rejected(lambda:bind(bad,root)),"kind":"source binding failure,not a complete price or endpoint calculation"}
    bad=deepcopy(word)
    bad["diagonal"][0][0]=1
    controls["wrong_declared_central_endpoint"]={"rejection":rejected(lambda:bind(bad,root)),"kind":"independent ROOT/node declaration mismatch"}
    return controls


def run():
    word,root=authenticate()
    normalization=local_arithmetic()
    binding=bind(word,root)
    return {"schema_version":1,"scope":"Local real-block normalization and exact6398caller source/declaration binding only",
            "source_manifest_sha256":MANIFEST_SHA256,"source_pins":PINS,
            "normalization":normalization,"literal_binding":binding,"binding_controls":binding_controls(word,root),
            "credit":"Ali Romman/OpenAI Codex already publishes normalization proofs and two exact caller checks;6348/Cinna Davis and all retained notices keep credit. This is separate local implementation evidence,not first verification.",
            "remaining":["No complete570event transfer was propagated here; the realified68x68 endpoint and independent reverse replay remain pairedR10 work.",
                         "ROOT basis/projector identities and broad classification are referenced author evidence,not re-proved by this source-binding check.",
                         "Whole-field source q^2=X absolutephase/native premise,address-loop implementation,physical erasure,ordinary/precision/compiler/fullbudget assumptions remain.",
                         "No physical68field caller,newproductive target,tariff,kappa or selected-frontier change."]}


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--emit",action="store_true")
    options=parser.parse_args()
    result=run()
    payload=(json.dumps(result,sort_keys=True,indent=2,allow_nan=False)+"\n").encode()
    if options.emit:
        sys.stdout.buffer.write(payload)
    else:
        receipt=HERE/"LOCAL-RESULT.json"
        need(receipt.is_file(),"retained LOCAL-RESULT.json receipt required")
        observed=strict(receipt.read_bytes())
        need(type(observed) is dict and type(observed.get("schema_version")) is int and observed["schema_version"]==1,
             "typed local receipt schema")
        need(canonical(observed)==canonical(result),"strict typed LOCAL-RESULT receipt")
        print("PASS local mixed-root normalization and retained receipt")
