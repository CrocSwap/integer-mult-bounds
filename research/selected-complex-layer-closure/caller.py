"""Source-bound chronological macroplan; it does not enumerate the full cover."""
from collections import Counter,defaultdict
import copy
import hashlib
import json

from streams import need


def depth(e):
    d=0
    while e>=73:e=48*(e//73);d+=1
    return d


def global_scalar(recipe):
    def execute(events):
        rows=[[int(i==j) for j in range(8)] for i in range(8)]
        for event in events:
            kind=event["kind"]
            if kind=="local":
                x,y=2*event["pair"],2*event["pair"]+1
                if event["reverse"]:rows[x]=[a-b for a,b in zip(rows[x],rows[y])]
                else:rows[y]=[a+b for a,b in zip(rows[y],rows[x])]
            elif kind=="bridge":
                i,j,c=2*event["dst"],2*event["src"],event["coefficient"]
                rows[i]=[a+c*b for a,b in zip(rows[i],rows[j])]
                rows[j+1]=[a-c*b for a,b in zip(rows[j+1],rows[i+1])]
            else:
                need(kind=="terminal","scalar controller alphabet")
                for pair in range(4):
                    x,y=2*pair,2*pair+1;rows[x],rows[y]=rows[y],[-a for a in rows[x]]
        return rows
    identity=[[int(i==j) for j in range(8)] for i in range(8)]
    need(execute(recipe)==identity,"whole signed scalar controller")
    rejected=0
    for i,event in enumerate(recipe):
        if event["kind"]=="bridge":
            need(execute(recipe[:i]+recipe[i+1:])!=identity,"omitted bridge control")
            rejected+=1
    return {"scalar_columns":8,"endpoint":"identity","omitted_bridge_controls":rejected}


def schedule(data,profiles):
    t=data["template"];parent=data["parent"];ph=data["phases"];c=data["word"]
    need((t["m"],t["live"],t["physical"])==(73,14336,14826),"selected caller dimensions")
    need(t["hosting"]["max_helpers_per_physical_family_per_call"]==1,"one helper per family per call")
    source=parent["execution_schedule"];perrep=defaultdict(list);global_events=[];callpos={};last={};windows={}
    order=[(z["stage"],z["replica"]) for z in t["calls"]];block=-1;counts=Counter()
    pair_at={(z["stage"],z["replica"]):z["pair"] for z in t["calls"]}
    levels={(rep,pair):-1 for rep in range(16) for pair in range(4)}
    for position,event in enumerate(t["execution_schedule"]):
        j=event["source_event"];old=copy.deepcopy(source[j]);kind=event["kind"];counts[kind]+=1
        if "replica" in event:
            rep=event["replica"];perrep[rep].append(j)
            expected=old|dict(source_event=j,replica=rep,replicas=[rep],time=event["time"])
            if kind=="local_cover_sweep":expected["provider_id"]="gauge44";block+=1
            need(event==expected and event["time"]==block,"literal indivisible chronological block")
            if kind=="local_cover_sweep":
                need(order[block]==(event["stage"],rep),"ordered call dispatch")
                pair=pair_at[event["stage"],rep]
                need(levels[rep,pair]==event["stage"]-1,"native local entry level")
                levels[rep,pair]=event["stage"]
                callpos[event["stage"],rep]=position;last[rep,pair]=position
            elif kind=="bridge":
                need(levels[rep,event["src"]]==levels[rep,event["dst"]],"common global bridge levels")
                last[rep,event["src"]]=last[rep,event["dst"]]=position
            elif kind=="idle_cover_sweep":
                need(levels[rep,event["pair"]]==event["from_level"],"native idle entry level")
                levels[rep,event["pair"]]=event["to_level"]
                for side,child in enumerate(event["child_indices"]):
                    windows[rep,child]=(last.get((rep,event["pair"]),-1),position,event["pair"],side)
            else:
                need(kind in ("terminal_Y_translations","terminal") and
                     all(levels[rep,pair]==8 for pair in range(4)),"full terminal levels")
        else:
            global_events.append(j);expected=old|dict(source_event=j)
            if kind=="bank_padding_cover_sweep":expected["families"]=[14336,14336]
            if kind=="translate_every_live_family":expected.update(families=[0,14336],charged_calls_per_cover=14336)
            need(event==expected,"final global event binding")
    need(len(order)==144 and all(perrep[r]==list(range(30)) for r in range(16)) and global_events==[30,31],
         "complete per-replica and terminal schedule")
    need(not t["bank_padding"]["children"],"selected has no external bank children")
    used=defaultdict(set);roles=set();paid=Counter()
    stages={e["stage"]:e for e in t["recipe"] if e["kind"]=="local"}
    for call in t["calls"]:
        owners=call["owners"];st,rep=call["stage"],call["replica"]
        need(len(owners)==704 and len({f for f,_ in owners})==704 and
             all(0<=f<14336 for f,_ in owners),"distinct live whole-call owners")
        stage=stages[st]
        need(call["pair"]==stage["pair"] and call["orientation"]==
             ("backward" if stage["reverse"] else "forward"),"native stage orientation")
        expected_data=[[896*rep+224*call["pair"]+112*side+port,[1,st,port]]
                       for side in range(2) for port in range(112)]
        need(owners[:224]==expected_data,"paired data owners and common cover class")
        need(call["window"]=={"local_axes":list(range(9)),"prefix_axes":list(range(9,9+8*st))},
             "common exterior window factor")
        paid.update(profiles[call["orientation"]])
        for helper,(family,route) in enumerate(owners[224:]):
            owner_rep,sub=divmod(family,896);pair,sub=divmod(sub,224);side,port=divmod(sub,112)
            typ,child,offset=route[:3];width=len(c["frames"][c["final"][224+helper]])-len(c["frames"][c["start"][224+helper]])
            before,deadline,w_pair,w_side=windows[owner_rep,child]
            need(before<callpos[st,rep]<deadline and (pair,side)==(w_pair,w_side),"actual untouched hosting window")
            need((typ==3 and width==9) or (typ==4 and route[3]==width),"actual helper width")
            cells=set(range(offset,offset+width));key=(owner_rep,child,port)
            need(not used[key]&cells,"disjoint pending pieces");used[key].update(cells)
            roles.add((st,rep,helper))
    need(len(roles)==69120,"complete hosted role domain")
    remainders={(z["replica"],z["child"],z["port"]):z for z in t["idle_children"]}
    need(len(remainders)==len(t["idle_children"])==7526,"unique positive idle requests")
    translations=[];zero_nonzero=[];idleprofile=Counter();seen=set()
    for event in t["execution_schedule"]:
        if event["kind"]!="idle_cover_sweep":continue
        rep=event["replica"]
        for side,child in enumerate(event["child_indices"]):
            for port in range(112):
                key=(rep,child,port);original=ph["recipes"][port]["idle_children"][child]
                axes=original["orthogonal_axes"];taken=used[key]
                need(taken==set(range(len(taken))) and len(taken)<=len(axes),"prefix tiling of actual pending axes")
                rank=len(axes)-len(taken);family=896*rep+112*(2*event["pair"]+side)+port
                if rank:
                    z=remainders[key];seen.add(key)
                    need((z["family"],z["rank"],z["pending_offset"])==(family,rank,len(taken)),"actual idle child binding")
                    idleprofile[rank]+=1;paid[rank]+=1
                else:need(key not in remainders,"zero-rank child needs no callee")
                item=[rep,child,port,family,rank,original["translation_after"]]
                translations.append(item)
                if rank==0 and item[-1]:zero_nonzero.append(item)
    need(seen==set(remainders) and len(translations)==35840,"dispatch original phase deadlines")
    need(len(zero_nonzero)==6822 and [0,0,0,224,0,15] in zero_nonzero,"fully hosted phase witness")
    expected={1:349604,2:60192,3:62585,4:20448,5:11808,7:7,8:1152,48:4866}
    need(dict(paid)==expected and sum(r*n for r,n in paid.items())==1041408,"complete selected paid profile")
    return {"event_counts":dict(counts),"calls":144,"hosted_occurrences":len(roles),
            "global_scalar":global_scalar(t["recipe"]),"terminal_data_level":8,
            "idle_profile":dict(sorted(idleprofile.items())),"profile":dict(sorted(paid.items())),
            "original_idle_phase_calls":len(translations),"fully_hosted_nonzero_translations":len(zero_nonzero),
            "phase_dispatch_sha256":hashlib.sha256(json.dumps(translations,separators=(",",":")).encode()).hexdigest(),
            "zero_remainder_witness":{"replica":0,"child":0,"port":0,"family":224,"mask":15,
                                      "post_child_delta0_expected":15,"omitted_translation_result":0},
            "caller_scope":"Symbolic chronological and source binding; full-cover payload execution remains a written algorithm."}
