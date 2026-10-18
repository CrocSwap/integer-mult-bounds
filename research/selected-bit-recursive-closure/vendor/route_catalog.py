"""Compile the retained selected BIT data routes and hosted owner descriptors.

Exact arithmetic only. No predecessor Python imports or finite-cover expansion.
"""
from collections import Counter
from fractions import Fraction as F
from hashlib import sha256
import gzip
import json
from qadic_streams import need

BASE="research/community-hyperplane599-audit/pr589/bit589/v9/"
GEOMETRY=BASE+"nine/GEOMETRY.json"
TEMPLATE=BASE+"hosted/GLOBAL-TEMPLATE.json.gz"
GLOBAL=BASE+"hosted/GLOBAL.json"
WORD="research/e8-bit-p111-tuned/tune/bitE8mut-p111-tuned.json.gz"
EXPECTED="research/e8-bit-p111-tuned/tune/EXPECTED.json"
ASSEMBLY="research/community-frontier1094-audit/ASSEMBLY.json"


def canonical(value):return json.dumps(value,sort_keys=True,separators=(",",":"))
def digest(value):return sha256(canonical(value).encode()).hexdigest()
def identity(n):return [[F(i==j) for j in range(n)] for i in range(n)]
def transpose(a):return [list(x) for x in zip(*a)]
def multiply(a,b):
    n=len(a);out=[[F(0)]*n for _ in range(n)]
    for i,row in enumerate(a):
        for k,x in enumerate(row):
            if x:
                for j,y in enumerate(b[k]):
                    if y:out[i][j]+=x*y
    return out


def column_word(matrix):
    """Gauss reduction gives inverse column factors in the reduction order."""
    n=len(matrix);reduced=[list(row) for row in matrix];word=[]
    for col in range(n):
        pivot=next(row for row in range(col,n) if reduced[row][col])
        if pivot!=col:
            reduced[col],reduced[pivot]=reduced[pivot],reduced[col]
            word.append(("swap",pivot,col,F(1)))
        diagonal=reduced[col][col]
        if diagonal!=1:
            reduced[col]=[x/diagonal for x in reduced[col]]
            word.append(("scale",col,col,diagonal))
        for row in range(n):
            if row==col:continue
            coefficient=reduced[row][col]
            if coefficient:
                reduced[row]=[x-coefficient*y for x,y in zip(reduced[row],reduced[col])]
                word.append(("add",col,row,coefficient))
    need(reduced==identity(n),"Gaussian endpoint")
    need(replay(word,n)==matrix,"exact rational factor product")
    return word


def replay(word,n=64):
    matrix=identity(n)
    for kind,dest,src,c in word:
        for row in matrix:
            if kind=="swap":row[dest],row[src]=row[src],row[dest]
            elif kind=="scale":row[dest]*=c
            elif kind=="add":row[dest]+=c*row[src]
            else:raise ValueError("unknown column factor")
    return matrix


def embed(matrix,axes,n=64):
    out=identity(n)
    for i,a in enumerate(axes):
        for j,b in enumerate(axes):out[a][b]=matrix[i][j]
    return out


def encode(word):return [[k,i,j,str(c)] for k,i,j,c in word]
def remap(word,axes):return [(k,axes[i],axes[j],c) for k,i,j,c in word]


def bill(word):
    counts=Counter({"ordinary":0,"double_half":0,"negation":0,
                    "controlled_shift":0,"constant_shift":0,"low_permutation":len(word)})
    for kind,dest,src,c in word:
        a,d=abs(c.numerator),c.denominator
        need(a&(a-1)==0 and d&(d-1)==0,"dyadic unit alphabet")
        if kind=="swap":counts["ordinary"]+=64
        elif kind=="add":
            counts["ordinary"]+=128*(src>dest)
            counts["double_half"]+=128*(d.bit_length()-1)
            counts["controlled_shift"]+=64
        else:
            counts["double_half"]+=64*(a.bit_length()+d.bit_length()-2)
            counts["negation"]+=64*(c<0)
            counts["constant_shift"]+=64
    return dict(counts)


def slot_permutation(slots):
    """Exchange the two set differences; preserve the residual projector."""
    need(len(slots)==8 and len(set(slots))==8,"eight distinct residual axes")
    permutation=list(range(64))
    domain=set(range(8));image=set(slots)
    for i,s in zip(sorted(domain-image),sorted(image-domain)):
        permutation[i],permutation[s]=s,i
    need(sorted(permutation)==list(range(64)),"completed axis bijection")
    desired=[permutation.index(j) for j in range(64)]
    columns=list(range(64));word=[]
    for j in range(64):
        if columns[j]==desired[j]:continue
        k=columns.index(desired[j]);columns[j],columns[k]=columns[k],columns[j]
        word.append(("swap",j,k,F(1)))
    need(len(word)==len(domain-image),"minimal set-image completion")
    pi=[[F(i==permutation[j]) for j in range(64)] for i in range(64)]
    need(replay(word)==transpose(pi),"inverse permutation convention")
    return permutation,pi,word


def compile_catalog(data):
    geometry=json.loads(data[GEOMETRY]);template=json.loads(gzip.decompress(data[TEMPLATE]))
    global_receipt=json.loads(data[GLOBAL]);word=json.loads(gzip.decompress(data[WORD]))
    expected=json.loads(data[EXPECTED]);assembly=json.loads(data[ASSEMBLY])
    need(assembly["bit_supplier"]["pr"]==589,"selected producer")
    import hashlib
    blob=hashlib.sha1(b"blob "+str(len(data[EXPECTED])).encode()+b"\0"+data[EXPECTED]).hexdigest()
    need(assembly["bit_supplier"]["git_blob_sha1"]==blob,"selected EXPECTED binding")
    need(expected["word"]["file_sha256"]==sha256(data[WORD]).hexdigest(),"selected word binding")
    need(global_receipt["template_sha256"]==sha256(gzip.decompress(data[TEMPLATE])).hexdigest(),"decoded template binding")
    need(template["geometry_sha256"]==sha256(data[GEOMETRY]).hexdigest(),"geometry binding")
    need((template["m"],template["stages"],template["replicas"],template["live"])==(64,9,32,28416),"selected nine-stage parameters")
    need(expected["nine"]["bit"]["physical"]==28425 and not sum(template["banks_per_stage"].values()),"selected physical stock")
    need(word["R"]==439 and len(geometry["ports"])==111,"port/helper inventory")
    residuals=template["residual_isometries"]
    need(len(residuals)==1,"one selected helper residual chart")
    residual=residuals[0]
    need(residual["entrance_rank"]==0 and residual["entrance_basis"]==[]
         and residual["residual_basis"]==list(range(8)),"full width-eight residual")
    need([[F(x,residual["denominator"]) for x in row]
          for row in residual["orthogonal_rows_numerator"]]==identity(8),"identity residual basis")
    catalogue={};bases={};data_totals=Counter();census=[]
    for p,port in enumerate(geometry["ports"]):
        q=port["q"];a=[[F(x) for x in row] for row in port["complement_columns"]]
        need(q==word["lines"][p] and sum(x*x for x in q)==4,"selected root")
        u=[[F(q[i],2)]+a[i] for i in range(8)];bases[p]=u
        need(multiply(transpose(u),u)==identity(8),"orthogonal root basis")
        rho=[[F(x) for x in row] for row in port["rho15"]]
        formula=[[F(q[i]*q[j],4) for j in range(8)]+a[i] for i in range(8)]
        formula += [[a[i][j] for i in range(8)]+[F(0)]*7 for j in range(7)]
        need(rho==formula and multiply(rho,rho)==identity(15),"selected rho reflection")
        local=column_word(rho)
        counts=Counter(k for k,_,_,_ in local)
        late=sum(k=="add" and j>i for k,i,j,_ in local)
        census.append([p,word["ports_geom"][p],len(local),counts["swap"],counts["add"],counts["scale"],late,bill(local)["ordinary"]])
        need(len(port["routes"])==9,"nine route embeddings")
        for stage,route in enumerate(port["routes"]):
            axes=list(range(8))+(list(range(8+7*(stage-1),8+7*stage)) if stage else [])
            need(route["stage"]==stage and route["axes"]==axes,"selected stage axes")
            ops=remap(local,axes) if stage else []
            record={"family":"data","port":p,"stage":stage,"word":encode(ops),"bill":bill(ops)}
            catalogue[f"data:{p}:{stage}"]=record;data_totals.update(record["bill"])
    children={x["idx"]:x for x in template["schedule"] if x["kind"]=="idle"}
    assignments={(stage,helper):(child,copy,offset,width) for child,copy,offset,width,stage,helper in template["hosting"]["slots"]}
    need(len(assignments)==3951,"one fixed helper slot per stage")
    incidences=Counter();data_incidences=Counter()
    for call in template["calls"]:
        stage,replica=call["stage"],call["replica"]
        need(len(call["owners"])==661,"local owner count")
        for owner_index,(family,owner) in enumerate(call["owners"]):
            if owner_index<222:
                port=owner_index%111
                need(owner==["data",stage,port],"data owner descriptor")
                side=owner_index//111
                if call["orientation"]=="reverse":side=1-side
                need(family==replica*888+call["pair"]*222+side*111+port,"data physical family")
                data_incidences[f"data:{port}:{stage}"]+=1;continue
            helper=owner_index-222
            need(owner[0]=="hosted","zero-bank selected helper")
            child,offset,width=owner[1:];entry=children[child]
            prescribed=assignments[stage,helper]
            need((child,offset,width)==(prescribed[0],prescribed[2],prescribed[3]),"slot assignment binding")
            need(family==replica*888+entry["pair"]*222+prescribed[1],"host family binding")
            start,end=entry["source_level"],entry["target_level"]
            pending=list(range(1 if start==-1 else 8+7*start,8+7*end))
            slots=pending[offset:offset+width]
            need(width==8 and len(slots)==8,"complete hosted residual")
            local=any(s<8 for s in slots);port=family%111
            key="host:"+",".join(map(str,slots))+(f":{port}" if local else "")
            if key not in catalogue:
                permutation,pi,ops=slot_permutation(slots)
                if local:
                    need(slots==list(range(1,9)),"selected local-block slot")
                    ops+=column_word(transpose(bases[port]))
                    matrix=multiply(transpose(pi),embed(transpose(bases[port]),list(range(8))))
                    sigma=multiply(embed(bases[port],list(range(8))),pi)
                else:matrix=transpose(pi);sigma=pi
                need(replay(ops)==matrix and multiply(sigma,matrix)==identity(64),"hosted inverse route")
                # The residual depends on the span, not the order of its basis.
                chart=embed(bases[port],list(range(8))) if local else identity(64)
                need(set(permutation[:8])==set(slots),"slot image set")
                need(all(sigma[r][i]==chart[r][permutation[i]] for r in range(64) for i in range(8)),"residual image")
                catalogue[key]={"family":"hosted","slots":slots,"port":port if local else None,
                                "permutation":permutation,"word":encode(ops),"bill":bill(ops)}
            incidences[key]+=1
    need(len(catalogue)==1123 and len(incidences)==124 and sum(incidences.values())==126432,"complete selected route coverage")
    need(len(data_incidences)==999 and set(data_incidences.values())=={64},"data call incidence multiplicity")
    hosted_totals=Counter()
    for key,count in incidences.items():
        catalogue[key]["occurrences"]=count
        hosted_totals.update({k:count*v for k,v in catalogue[key]["bill"].items()})
    for key,count in data_incidences.items():catalogue[key]["occurrences"]=count
    return catalogue,{"data_types":999,"hosted_types":124,"hosted_occurrences":sum(incidences.values()),
                      "data_census_sha256":digest(census),"data_type_total":dict(data_totals),
                      "data_occurrence_total":{k:64*v for k,v in data_totals.items()},
                      "hosted_occurrence_total":dict(hosted_totals),
                      "max_data_ordinary":max(x["bill"]["ordinary"] for x in catalogue.values() if x["family"]=="data"),
                      "max_hosted_ordinary":max(x["bill"]["ordinary"] for x in catalogue.values() if x["family"]=="hosted"),
                      "catalogue_sha256":digest(catalogue)}
