"""Selected low-packet separation, global scalar schedule and live-row layout."""
from collections import Counter,defaultdict
from fractions import Fraction as F
from itertools import combinations,product
from math import lcm
from ring_algebra import need,eye,reduce_matrix,chart,conjugate,weighted_swap,multiply,difference


def pending(event):
    a,b=event["source_level"],event["target_level"]
    return list(range(1 if a==-1 else 8+7*a,8+7*b))


def completion(axes,port):
    """PR2157's support completion; the full basis order is immaterial."""
    perm=list(range(64));domain=set(range(8));support=set(axes)
    for i,j in zip(sorted(domain-support),sorted(support-domain)):perm[i],perm[j]=j,i
    u=[tuple([F(port["q"][i],2)]+list(map(F,port["complement_columns"][i]))) for i in range(8)]
    def a_column(j):
        if j<8:return tuple(u[i][j] if i<8 else F(0) for i in range(64))
        return tuple(F(i==j) for i in range(64))
    local=bool(domain&support)
    actual=[a_column(perm[i]) if local else tuple(F(k==perm[i]) for k in range(64)) for i in range(8)]
    reference=[a_column(j) for j in axes]
    need(sorted(actual)==sorted(reference),"actual completion has the prescribed image basis")
    need(all(sum(x*y for x,y in zip(a,b))==int(i==j)
             for i,a in enumerate(actual) for j,b in enumerate(actual)),"unit orthogonal image basis")
    need(all(x.denominator&(x.denominator-1)==0 for col in actual for x in col),"dyadic completion")
    return tuple(perm),local


def owner_certificate(template,geometry):
    children={e["idx"]:e for e in template["schedule"] if e["kind"]=="idle"}
    pairs=occurrences=same_family_adds=0;types=set();sizes=Counter();first_add=None
    for call in template["calls"]:
        byfamily=defaultdict(list);owners=call["owners"]
        datafamilies={f for f,_ in owners[:222]}
        need(len(datafamilies)==222,"distinct live data families")
        role_support={}
        for role,(family,route) in enumerate(owners[222:],222):
            need(route[0]=="hosted" and family not in datafamilies,"hosted family outside the active pair")
            _,child,offset,width=route
            axes=pending(children[child])[offset:offset+width]
            need(len(axes)==width==8,"whole helper block")
            port=family%111;key=(tuple(axes),port if min(axes)<8 else None)
            if key not in types:completion(axes,geometry["ports"][port]);types.add(key)
            byfamily[family].append((role,tuple(axes),child));role_support[role]=axes
            occurrences+=1
        for family,roles in byfamily.items():
            sizes[len(roles)]+=1
            for a,b in combinations(roles,2):
                need(set(a[1]).isdisjoint(b[1]),"separation witness for complete low packets")
                pairs+=1
        for position,event in enumerate(template["local_programs"][call["orientation"]]):
            if event[0]!=1:continue
            target,source=event[1:3]
            if target<222 or source<222 or target>=661 or source>=661:continue
            if owners[target][0]==owners[source][0]:
                same_family_adds+=1
                if first_add is None:
                    first_add={"stage":call["stage"],"replica":call["replica"],"position":position,
                               "target_role":target,"source_role":source,"family":owners[target][0],
                               "target_support":role_support[target],"source_support":role_support[source]}
    need((occurrences,pairs,len(types),same_family_adds)==(126432,181056,124,11072),"selected owner inventory")
    need(first_add["position"]==19422 and first_add["family"]==451,"selected same-family ADD")
    return {"calls":len(template["calls"]),"helper_occurrences":occurrences,
            "same_family_pairs":pairs,"completion_types":len(types),
            "group_sizes":dict(sorted(sizes.items())),"same_family_ADDs":same_family_adds,
            "first_same_family_ADD":first_add,"private_family":template["live"]}


def global_scalar(schedule,skip=-1):
    values=[1<<i for i in range(8)];bridge=0
    for event in schedule:
        if event["kind"]=="local_cover_sweep":
            pair=event["pair"];target=2*pair+(0 if event["reverse"] else 1)
            source=2*pair+(1 if event["reverse"] else 0);values[target]^=values[source]
        elif event["kind"]=="bridge":
            d,s=event["dst"],event["src"]
            for target,source in ((2*d,2*s),(2*s+1,2*d+1)):
                if bridge!=skip:values[target]^=values[source]
                bridge+=1
        elif event["kind"]=="exchange":
            for j in range(4):values[2*j],values[2*j+1]=values[2*j+1],values[2*j]
        else:need(event["kind"]=="idle","known schedule operation")
    return values,bridge


def global_endpoint(template,word,projectors):
    scalar,bridges=global_scalar(template["schedule"])
    need(scalar==[1<<i for i in range(8)] and bridges==18,"global scalar endpoint")
    for i in range(bridges):need(global_scalar(template["schedule"],i)[0]!=scalar,"omitted bridge shear")
    q,width,modulus=3,2,9;g,gi=chart(64,q,width)
    weights=[(1+i%2+3*(i+1))%modulus for i in range(64)]
    full=weighted_swap(eye(64),weights,modulus)
    for port in range(111):
        p=projectors[word["start"][port]]
        embedded=[[F(0)]*64 for _ in range(64)]
        for i in range(8):
            for j in range(8):embedded[i][j]=p[i][j]
        current=conjugate(reduce_matrix(embedded,modulus),g,gi,modulus)
        complement=difference(eye(64),current,modulus)
        a=weighted_swap(current,weights,modulus);b=weighted_swap(complement,weights,modulus)
        need(multiply(a,b,modulus)==full,"source entry and terminal-swapped gauge give F_A")
    return {"scalar_data_roles":8,"omitted_bridge_controls":bridges,
            "ambient_weighted_port_endpoints":111,"q":q,"width":width,
            "terminal_rule":"Exchange the two stream values together with their frame labels."}


def data_chart_boundaries(geometry):
    checks=0
    for modulus in (9,25):
        for port in geometry["ports"]:
            p=[[F(x*y,4) for y in port["q"]] for x in port["q"]]
            rho=reduce_matrix([[F(x) for x in row] for row in port["rho15"]],modulus)
            def block(local,exterior):
                out=[[F(0)]*15 for _ in range(15)]
                for i in range(8):
                    for j in range(8):out[i][j]=local[i][j]
                for i in range(8,15):out[i][i]=int(exterior)
                return reduce_matrix(out,modulus)
            complement=[[F(i==j)-p[i][j] for j in range(8)] for i in range(8)]
            zero=[[0]*8 for _ in range(8)]
            cases=((block(p,True),block(eye(8),False)),
                   (block(zero,True),block(complement,False)),
                   (block(eye(8),True),block(eye(8),True)),
                   (block(complement,True),block(complement,True)))
            for before,after in cases:
                need(multiply(multiply(rho,before,modulus),rho,modulus)==after,
                     "selected data entry/exit chart")
                checks+=1
    return {"ports":111,"projector_boundaries_per_port":4,"rings":[9,25],"checks":checks}


def depth(n):
    d=0
    while n>=64:n=42*(n//64);d+=1
    return d


def encode(family,low,high,unused,low_count,high_count,unused_count):
    return ((family*low_count+low)*high_count+high)*unused_count+unused


def decode(row,low_count,high_count,unused_count):
    row,unused=divmod(row,unused_count);row,high=divmod(row,high_count)
    family,low=divmod(row,low_count)
    return family,low,high,unused


def row_layout(template):
    live=template["live"];physical=live+template["private_centre_reserve"]
    compatible=lcm(live,physical);slack=compatible//live
    need((live,physical,compatible,slack)==(28416,28425,269241600,9475),"live/work compatibility count")
    need(compatible<2**80,"same logarithmic per-level envelope for eligible q")
    depth_checks=0
    for n in (0,1,63,64,65,127,128,1024,4096,10**6,10**9):
        if n<64:need(depth(n)==0,"leaf reserve");continue
        for rank in range(1,43):
            need(depth(rank*(n//64))<=depth(n)-1,"child compatible reserve divides unused quotient")
            depth_checks+=1
    # Exhaustive small complete-row model of the same mixed-radix layout.
    # W=2, P=3, q=3, GL1 low classes=2, high cardinality=3, depth=2.
    w,p,low_count,high_count=2,3,2,3
    packet=lcm(w,p)*low_count*high_count;rows=packet**2
    unused_count=rows//(w*low_count*high_count)
    seen=set()
    for fields in product(range(w),range(low_count),range(high_count),range(unused_count)):
        row=encode(*fields,low_count,high_count,unused_count)
        need(decode(row,low_count,high_count,unused_count)==fields,"exact row coordinate round trip")
        seen.add(row)
    need(seen==set(range(rows)),"every original live row belongs to the layout")
    batch=[encode(1,1,h,u,low_count,high_count,unused_count)
           for h,u in product(range(high_count),range(unused_count))]
    need(len(batch)*w*low_count==rows,"logical child volume denominator")
    need(len(batch)*p*low_count!=rows,"physical inventory is not the live denominator")
    need(unused_count%packet==0,"child reserve remains complete")
    for h in range(high_count):
        child_rows=[u%packet for u in range(unused_count)]
        need(Counter(child_rows)==Counter({r:unused_count//packet for r in range(packet)}),
             "fresh child row coverage independent of parent high coordinate")
    return {"live_families":live,"private_inventory":physical-live,"compatible_low_factor":compatible,
            "unused_compatibility_factor":slack,"physical_divisibility_factor":compatible//physical,
            "depth_checks":depth_checks,"toy_rows":rows,"toy_batch_rows":len(batch),
            "toy_child_reserve":packet,"toy_unused_quotient":unused_count,
            "volume_denominator_control":"REJECT_PHYSICAL_INVENTORY_SUBSTITUTION",
            "scope":"Explicit alternative packet layout; no numerical routing invoice or completed recursive scratch allocation."}
