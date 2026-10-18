"""Prototype joint P104 word with delayed inputs and arbitrary dirty carriers.

Jose Manuel, with substantial OpenAI Codex assistance. This reads the pinned
selected side word through Ali Romman's source loader. No supplier admission.
"""

from collections import Counter, defaultdict
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse
import copy
import importlib.util
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
need_source = ROOT / "research/native-source-codes/source_data.py"
if sha256(need_source.read_bytes()).hexdigest() != "d23924511e3aed41e5e64511ca70126a636d91c8aa02e656cb61d6ceca1fe0a0":
    raise ValueError("selected source-loader pin")
spec = importlib.util.spec_from_file_location("p104_selected_source",ROOT / "research/native-source-codes/source_data.py")
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)


def need(ok,message):
    if not ok:
        raise ValueError(message)


def span(vs):
    out = {0}
    for v in vs:
        out |= {x^v for x in tuple(out)}
    return frozenset(out)


def add(row,other,q):
    S.add(row,other,q)


def touched(event):
    if event[0]=="scalar":
        op = event[1]
        return [reg(r) for r in (op[1:3] if op[0] in ("add","copy") else op[1:2])]
    if event[0] in ("climb","adapter","residual_adapter"):
        return [event[2]]
    return []


def reg(pair):
    return pair[1] + (704 if pair[0]=="C" else 0)


def scalar(event,state):
    if event[0]!="scalar":
        return
    op = event[1]
    t = reg(op[1])
    if op[0]=="clear":
        state[t] = {}
    elif op[0]=="scale":
        state[t] = {j:x*Q(op[2],op[3]) for j,x in state[t].items()}
    elif op[0]=="copy":
        state[t] = dict(state[reg(op[2])])
    else:
        need(op[0]=="add","scalar kind")
        add(state[t],state[reg(op[2])],Q(op[3],op[4]))


def sc(t,s,q,f):
    ref = lambda x:["C",x-704] if 704<=x<712 else ["L",x]
    return ["scalar",["add",ref(t),ref(s),Q(q).numerator,Q(q).denominator],f]


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--native",action="store_true")
    args=parser.parse_args()
    data = S.reconstruct(ROOT)
    w,p,R = data["word"],data["programs"]["forward"],data["R"]
    frames = list(map(span,w["frames"]))
    frame_bases = list(w["frames"])
    full,zero = 1,0
    need(len(frames[full])==512 and frames[zero]=={0},"frame anchors")
    n = len(w["start"])
    need(n==704,"selected width")
    a_cut = p.index(["phase","centers"])
    b_start = p.index(["phase","B"])
    cleanup = p.index(["phase","full_frame_cleanup"])
    need((a_cut,b_start,cleanup)==(12550,12759,17845),"pinned source cuts")
    old = [i for i in range(len(p)) if not a_cut<=i<b_start]
    cports = {110,106,81,86,8,50,54,25}
    live = [i for i in range(112) if i not in cports]
    early = [(81,3,224),(86,4,11),(54,5,240),(25,6,9)]
    late = [(7,110),(2,106),(1,8),(0,50)]
    fixture_path=ROOT/"research/p104-native-channel/inputs/P104-FIXTURE.json"
    fixture_bytes=fixture_path.read_bytes()
    need(sha256(fixture_bytes).hexdigest()=="516c06f6ec3cb84be588c546108de897650288576dd5fbf5fe44b9c5546ad8a4","P104 fixture pin")
    fixture=json.loads(fixture_bytes)["section4_explicit_P104"]
    source_roots=[tuple(R[k].get(j,Q(0)) for k in range(8)) for j in range(112)]
    def hamming(root):
        return tuple(Q(v,2) for i in range(0,8,2) for v in (root[i]+root[i+1],root[i]-root[i+1]))
    def root_id(root):
        v=hamming(root)
        ids=[i for i,r in enumerate(source_roots) if r==v or r==tuple(-x for x in v)]
        need(len(ids)==1,"standard root to selected source binding")
        return ids[0]
    need({root_id(root) for root in fixture["C"]}==cports,"actual P104 puncture")
    pairs=fixture["pairs_doubled_coordinates"]
    need([root_id(pairs[k][0]) for k in (2,3,4,6)]==[a for a,_,_ in early],"early pseudo-source roots")
    need([root_id(pairs[k][1]) for k in (0,1,5,7)]==[b for _,b in late],"late query roots")
    injection = [
        (81,27,{233:Q(1),239:Q(1,2)}),(81,29,{231:Q(1)}),
        (81,31,{230:Q(1)}),(81,34,{7:Q(1,2)}),(81,36,{238:Q(1,2)}),
        (86,230,{345:Q(1),351:Q(1,2)}),(86,232,{343:Q(1)}),
        (86,234,{342:Q(1)}),(86,237,{28:Q(1,2)}),(86,239,{350:Q(1,2)}),
        (54,136,{54:Q(1),102:Q(-1,2)}),(54,146,{290:Q(1)}),
        (54,147,{294:Q(1)}),(54,150,{19:Q(-1,2)}),(54,151,{300:Q(-1,2)}),
        (25,78,{2:Q(1),25:Q(1,2)}),(25,87,{263:Q(1)}),
        (25,90,{260:Q(1)}),(25,91,{264:Q(-1,2)}),(25,94,{270:Q(-1,2)})]
    # Strict per-register access order, including reads.
    previous,preds = {},{}
    for i in old:
        regs = touched(p[i])
        preds[i] = {previous[r] for r in regs if r in previous}
        for r in regs:
            previous[r] = i
    last_writes = {}
    for axis,b in late:
        last_writes[b] = max(i for i in old if p[i][0]=="scalar" and reg(p[i][1][1])==112+b)
    ideal = set(range(a_cut))
    stack = list(last_writes.values())
    while stack:
        i = stack.pop()
        if i in ideal:
            continue
        ideal.add(i)
        stack.extend(preds[i])
    order = sorted(ideal)+[i for i in old if i not in ideal]
    need(len(order)==24558 and len(ideal)==13412,"retimed query-ready cut")
    digest = lambda v:sha256(json.dumps(v,separators=(",",":")).encode()).hexdigest()
    need(digest(sorted(ideal))=="3f90133dd605cbbdbd2c2a34fbdb4160e6365f0dbca3b3dbe5aaf2be41694152","cut certificate")
    need(digest(order)=="5eec1caa341cd66afa1363dbe4688e19e6122819d81d132c26b2640457586056","order certificate")
    # Safe target reads after the target's last target-basis operation.
    threshold = defaultdict(lambda:-1)
    for i in old:
        if p[i][0]!="scalar":
            continue
        op = p[i][1]
        rr = touched(p[i])
        if op[0]=="scale" and 112<=rr[0]<224:
            threshold[rr[0]] = i
        elif op[0]=="add" and all(112<=r<224 for r in rr):
            for r in rr:
                threshold[r] = i
    normals = {}
    for axis,b in late:
        candidates = [q for q in range(1,512) if all(((q&w["ports"][j]).bit_count()%2)==((int(R[axis].get(j,0))+1)%2) for j in range(112))]
        need(len(candidates)==1,"coordinate root label")
        normals[axis] = candidates[0]
    intervals = defaultdict(list)
    current = w["start"].copy()
    entered = [-1]*n
    for i in old:
        e = p[i]
        if e[0]=="climb":
            r,oldf,newf = e[2:5]
            need(current[r]==oldf,"original frame itinerary")
            if 112<=r<224:
                intervals[r].append((entered[r],i,oldf))
            current[r],entered[r] = newf,i
    deliveries = defaultdict(list)
    group_ids = {}
    for axis,b in late:
        for t in live:
            coefficient = R[axis].get(t,Q(0))
            if not coefficient:
                continue
            candidates = [(start,end,f) for start,end,f in intervals[112+t]
                          if end>threshold[112+t] and normals[axis] in frames[f]
                          and f!=w["final"][112+t]]
            need(candidates,"safe nonterminal query read")
            start,end,f = min(candidates,key=lambda z:max(z[0],threshold[112+t]))
            need(len(frames[f])==128 and end not in ideal,"safe rank-seven read after queries")
            key = (axis,f)
            if key not in group_ids:
                group_ids[key] = 732+len(group_ids)
            deliveries[end].append((group_ids[key],112+t,coefficient,f))
    need(len(group_ids)==112 and sum(map(len,deliveries.values()))==208,"late delivery invoice")
    total = 844
    # Derive the twenty independent injection responses at the FULL repair cut.
    response = [{} for _ in range(total)]
    for j,(_,f,items) in enumerate(injection):
        for r,q in items.items():
            response[r][j] = q
    response_frames = w["start"].copy()
    for i in order:
        if i<a_cut:
            if p[i][0]=="climb":response_frames[p[i][2]]=p[i][4]
            continue
        if i==cleanup:
            break
        scalar(p[i],response)
        if p[i][0]=="climb":response_frames[p[i][2]]=p[i][4]
        if i==16592:
            add(response[341],{5:Q(1)},Q(-1))
    repairs = [(r,j,q) for r in range(n) if not 112<=r<224 for j,q in response[r].items()]
    need(len(repairs)==135,"FULL repair count")
    need(all(response_frames[r]==full for r,j,q in repairs),"all repairs use FULL")
    need(all(not response[q] for _,_,q in early),"queries survive injection")
    need(all(not response[112+t] for t in cports),"dummy query outputs survive injection")
    # Build the literal candidate, keeping scalar/native annotations separately.
    actions = []
    cur = w["start"].copy()+[0]*(total-n)
    for t in cports:cur[t]=0
    paid = Counter()

    def emit(e):
        if e[0]=="scalar":
            for r in touched(e):need(cur[r]==e[2],("common frame",r,cur[r],e))
        elif e[0]=="climb":
            r,o,f,k = e[2:6]
            need(cur[r]==o,"old transport entry")
            cur[r]=f;paid[k]+=1
        elif e[0]=="owned_init":
            cur[e[1]]=e[2]
        actions.append(e)

    def climb(r,f,kind="joint"):
        oldf = cur[r]
        if oldf==f:return
        a,b=frames[oldf],frames[f]
        need(a<=b or b<=a,"nested new transport")
        emit(["climb",kind,r,oldf,f,abs((len(a).bit_length()-1)-(len(b).bit_length()-1))])

    def singleton(q):
        f=span([q])
        if f not in frames:
            frames.append(f);frame_bases.append([q])
        return frames.index(f)

    def copy_query(q,scale,to):
        emit(["owned_init",704,cur[q]])
        emit(sc(704,q,scale,cur[q]))
        climb(704,to)

    def clear_copy():
        emit(["owned_init",704,0])

    for t in cports:climb(t,w["start"][t],"source_pad_entry")
    # New rows receive their dirty-response compensation in a later replay.
    prefix = S.corrected_program(p,data["H"],data["D"],False)[1]
    for pos,i in enumerate(order):
        if i==p.index(["phase","A"]):
            for e in prefix:emit(e)
        if pos==a_cut:
            for a,axis,q in early:
                f=singleton(w["ports"][a]);g=R[axis][a]
                need(g in (-1,1),"early pivot sign")
                copy_query(q,-1/g,f)
                for j,(aa,ff,items) in enumerate(injection):
                    if aa==a:
                        climb(712+j,f);emit(sc(712+j,704,1,f))
                clear_copy()
            for j,(a,f,items) in enumerate(injection):
                carrier=712+j;climb(carrier,f)
                for r,q in items.items():emit(sc(r,carrier,q,f))
                if j!=5:climb(carrier,full)
        if pos==len(ideal):
            for axis,b in late:
                f=singleton(normals[axis]);g=R[axis][b]
                need(g in (-1,1),"late pivot sign")
                copy_query(112+b,-1/g,f)
                for (aa,ff),carrier in group_ids.items():
                    if aa==axis:
                        climb(carrier,f);emit(sc(carrier,704,1,f))
                clear_copy()
        for carrier,target,q,f in deliveries.get(i,[]):
            climb(carrier,f);emit(sc(target,carrier,q,f))
        if i==cleanup:
            for carrier in group_ids.values():climb(carrier,full)
            for t in cports:climb(112+t,full,"target_pad_exit")
            for r,j,q in repairs:emit(sc(r,712+j,-q,full))
            for j,(a,f,items) in enumerate(injection):
                axis,q = next((axis,q) for aa,axis,q in early if aa==a)
                emit(sc(712+j,q,1/R[axis][a],full))
            for (axis,f),carrier in group_ids.items():
                b=next(b for aa,b in late if aa==axis)
                emit(sc(carrier,112+b,1/R[axis][b],full))
        emit(p[i])
        if i==16592:
            climb(717,240);emit(sc(341,717,-1,240));climb(717,full)
    # All omitted target outputs are helpers. Remove their side increment.
    for t in cports:
        for s,q in data["J"][t].items():emit(sc(112+t,s,-q,full))

    def replay(prelude=(),events=None):
        state=[{i:Q(1)} for i in range(total)]
        for target,source,q in prelude:add(state[target],state[source],q)
        for e in actions if events is None else events:
            if e[0]=="owned_init":state[e[1]]={}
            else:scalar(e,state)
        return state

    raw = replay()
    compensation=[]
    initial=w["start"].copy()+[0]*(total-n)
    for t in cports:initial[t]=0
    for t in live:
        row=raw[112+t].copy()
        add(row,{112+t:Q(1),t:Q(1)},Q(-1))
        need(not any(j in live for j in row),"real-input coefficient is identity")
        for j,q in row.items():
            need(initial[j]==0 and initial[112+t]==0 and j not in [112+s for s in live],("available baseline",j,initial[j]))
            compensation.append((112+t,j,-q))
    final=replay(compensation)
    for r,row in enumerate(final):
        expected={} if 704<=r<712 else {r:Q(1)}
        if 112<=r<224 and r-112 in live:expected[r-112]=Q(1)
        need(row==expected,("complete endpoint",r,row,expected))
    controls={}
    repair=sc(341,717,-1,240)
    need(actions.count(repair)==1,"unique scheduled low-frame repair")
    bad=list(actions);bad.remove(repair)
    controls["omitted_low_frame_repair"]=replay(compensation,bad)!=final
    restore=sc(712,224,1/R[3][81],full)
    need(actions.count(restore)==1,"unique carrier restoration")
    bad=list(actions);bad.remove(restore)
    controls["omitted_dirty_carrier_restoration"]=replay(compensation,bad)!=final
    controls["omitted_baseline_compensation"]=raw!=final
    need(all(controls.values()),"semantic controls")
    need(dict(paid)=={1:2564,2:547,3:432,4:142,5:83,6:128,7:11},"complete fixed child profile")
    drops=[e for e in actions if e[0]=="climb" and len(frames[e[3]])>len(frames[e[4]])]
    need(len(drops)==8 and all(e[2]==704 and e[5]==7 for e in drops),"eight owned private descents and COPY56")
    native={"status":"NOT_RUN"}
    if args.native:
        def load(name,path,pin):
            need(sha256(path.read_bytes()).hexdigest()==pin,"native source pin")
            sp=importlib.util.spec_from_file_location(name,path)
            module=importlib.util.module_from_spec(sp);sys.modules[name]=module;sp.loader.exec_module(module)
            return module
        CE=load("p104_delayed_compiler",ROOT/"research/p104-native-channel/vendor/clifford_exact.py",
                "2982ead07721e83358dc67c6f49c2b4c16a236a6bebdfd72f58221be1f5d0962")
        N=load("p104_delayed_independent",ROOT/"research/p104-native-channel/vendor/native_verify.py",
               "3049471905b47b385c88378a1a3be7a18b8858aadd035b8a6da2f4a03b470f38")
        charts={}
        def chart(f):
            if f not in charts:charts[f]=CE.canonical_frame(9,frame_bases[f])
            return charts[f]
        checked={};uses=0;phase_control=False
        for e in actions:
            if e[0]!="climb" or e[1] not in ("joint","source_pad_entry","target_pad_exit"):continue
            _,kind,r,a,b,rank=e;uses+=1
            normal=w["ports"][r if kind=="source_pad_entry" else r-112] if kind!="joint" else None
            key=(kind,a,b,normal)
            if key in checked:continue
            if kind=="joint":
                op=chart(a).adjoint().then(chart(b))
                expected=N.adjoint(N.frame(tuple(frame_bases[a]),9))+N.frame(tuple(frame_bases[b]),9)
            else:
                # Padding enters BEFORE the retained source adapter and exits
                # AFTER the retained target adapter; both need intrinsic C_q.
                op=CE.cgate(9,normal,1);expected=(("C",normal,1),)
            recipe,_=CE.lower_child(op)
            need(recipe["rank"]==rank,"new positive child rank")
            N.equal(N.recipe(recipe),expected,"new joint-side native transport")
            if not phase_control:
                bad=copy.deepcopy(recipe);bad["left"]["phase"]=(bad["left"]["phase"]+1)%4
                try:N.equal(N.recipe(bad),expected,"mutated global phase")
                except ValueError:phase_control=True
                else:raise ValueError("accepted wrong native phase")
            checked[key]=rank
        need(phase_control,"native phase control ran")
        native={"status":"PASS_NEW_NATIVE_RECIPES","distinct_recipes":len(checked),"paid_occurrences":uses,"global_phase_control":"REJECT"}
    print(json.dumps({"status":"PASS_CANONICAL_P104_DELAYED_SIDE_PROTOTYPE",
                      "persistent_columns":total-8,"private_columns":8,"actions":len(actions),
                      "baseline_compensation_adds":len(compensation),"paid_profile":dict(sorted(paid.items())),
                      "paid_mass":sum(r*c for r,c in paid.items()),"early_dirty_carriers":20,
                      "late_dirty_carriers":112,"query_cut":len(ideal),"native_new_recipe_check":native,
                      "controls":controls,
                      "scope":"Exact finite forward endpoint and canonical common frames. Native recipes are checked only with --native. Global hosting, dual orientation, precision and supplier admission remain separate."},indent=2))


if __name__=="__main__":main()
