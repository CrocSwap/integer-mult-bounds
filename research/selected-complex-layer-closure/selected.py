"""Authenticate in verify.py before calling the retained finite interfaces."""
import ast
from collections import Counter,defaultdict
from fractions import Fraction as Q
import copy
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tarfile

from streams import need

ARCHIVE="research/community-frontier1094-audit/selected-replay.tar.gz"
PREFIX="candidate/strict/global/"


def normal(value):return json.loads(json.dumps(value))


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(spec);sys.modules[name]=result
    spec.loader.exec_module(result);return result


def load(root):
    names={"template":"hosted/GLOBAL-TEMPLATE.json.gz",
           "parent":"base/split-centres/GLOBAL-TEMPLATE.json.gz",
           "sigmas":"hosted/ACTUAL-SIGMAS.json.gz",
           "phases":"base/work/complex-nine-native/DATA-PHASES.json",
           "word":"base/providers/gauge44/CANONICAL-WORD.json.gz",
           "programs":"base/providers/gauge44/LOCAL-PROGRAMS.json.gz",
           "clifford":"base/providers/gauge44/CLIFFORD-RECIPES.json",
           "wrappers":"base/providers/gauge44/RESIDUAL-ADAPTERS.json",
           "clifford_review":"base/providers/gauge44/CLIFFORD-REVIEW.json",
           "wrapper_review":"base/providers/gauge44/WRAPPER-CHECKS.json",
           "local_review":"base/providers/gauge44/INDEPENDENT-LOCAL-REPLAY.json",
           "invoice":"audit/PREFIX-AND-INVOICE.json"}
    data={};pins={}
    with tarfile.open(root/ARCHIVE,"r:gz") as archive:
        entries=archive.getmembers()
        for key,suffix in names.items():
            name=PREFIX+suffix;matches=[m for m in entries if m.name==name]
            need(len(matches)==1 and matches[0].isfile(),"one regular selected member")
            raw=archive.extractfile(matches[0]).read();pins[name]=hashlib.sha256(raw).hexdigest()
            data[key]=json.loads(gzip.decompress(raw) if name.endswith(".gz") else raw)
    need(data["template"]["local_providers"]["gauge44"]["local_programs"]==data["programs"],
         "actual selected local programs")
    artifacts=data["invoice"]["providers"]["gauge44"]["artifacts"]
    for name,digest in pins.items():
        if "/providers/gauge44/" in name:
            need(artifacts[name.rsplit("/",1)[1]]==digest,"selected invoice member binding")
    data["member_pins"]=pins
    return data


def native_binding(data):
    c=data["word"];frames=c["frames"];recipes=data["clifford"]
    directed={(r["old"],r["new"]):r for r in recipes["children"]}
    endpoints={(r["role"],r["port"]):r for r in recipes["endpoint_adapters"]}
    wrappers=data["wrappers"]["recipes"]
    need(len(directed)==2896 and len(endpoints)==224 and len(wrappers)==36,"retained native domains")
    review=data["clifford_review"]
    need(review["status"]=="PASS_NEW_WORD_EXACT_LOCAL_PHASE_RECIPES" and
         review["all_child_equalities_include_global_phase"] and
         review["directed_edges"]==len(directed) and review["endpoint_adapters"]==len(endpoints),
         "retained exact unary equality certificate")
    need(data["wrapper_review"]["status"]=="PASS_RESIDUAL_WRAPPERS_ARE_EXACT", "retained normalized endpoints")
    inventory={}
    for direction,events in data["programs"].items():
        counts=Counter()
        for event in events:
            tag=event[0]
            if tag in ("climb","center"):
                a,b,r=event[-3:];record=directed[a,b]
                need(record["rank"]==r and 0<r<73,"directed child binding")
                need(record["left"] is not None and record["right"] is not None,"two paid native adapters")
                counts["directed_children"]+=1
            elif tag=="residual_adapter":
                _,kind,role,entrance,*end=event;terminal=end[0] if end else 1
                key=f"{entrance}:{terminal}" if end else str(entrance)
                record=wrappers[key]
                need(record["frame"]==entrance and record["rank"]==len(frames[terminal])-len(frames[entrance]),
                     "actual normalized helper endpoint")
                need(kind in ("pre","post") and record["right" if kind=="pre" else "left"] is not None,
                     "inverse right/left wrapper")
                counts[kind+"_wrappers"]+=1
            elif tag=="adapter":
                _,kind,role,frame=event
                if frame in (0,1):counts["identity_endpoint_adapters"]+=1;continue
                side,port=("source",role) if role<112 else ("target",role-112)
                record=endpoints[side,port]
                need(record["frame"]==frame and record["rank"]==0,"exact endpoint monomial")
                need(kind in ("old_to_new","new_to_old"),"directed endpoint convention")
                counts["nontrivial_endpoint_adapters"]+=1
            elif tag=="scalar":counts["unchanged_role_scalars"]+=1
            else:need(tag=="phase","closed native event alphabet");counts["section_markers"]+=1
        inventory[direction]=dict(counts)
    return {"directed_recipe_count":len(directed),"endpoint_recipe_count":len(endpoints),
            "normalized_wrapper_keys":len(wrappers),"inventory":inventory,
            "scope":"Binding to retained exact unary/phase certificates; their producer is not rerun."}


def local_replay(root,data):
    """Reuse two authenticated pure functions; never execute their writing CLI."""
    path=root/"research/complex-sw4-frame8/local/hpe_audit_local.py"
    tree=ast.parse(path.read_bytes(),filename=str(path))
    functions=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in ("contains","local")]
    need({n.name for n in functions}=={"contains","local"},"retained checker API")
    c=data["word"];v,R,h=c["v"],c["R"],c["h"];n=2*v+R;frames=c["frames"]
    entering=[r for r,f in enumerate(c["start"]) if r>=2*v and f!=0]
    hpe={r for r in range(2*v,n) if c["final"][r]!=1}
    need(all(len(frames[c["final"][r]])<h for r in hpe),"proper low helper endpoints")
    wrapped=sorted(set(entering)|hpe)
    scope=dict(c=c,v=v,R=R,h=h,n=n,frames=frames,Counter=Counter,Q=Q,hashlib=hashlib,
               levels={int(t):f for t,f in c.get("target_levels",{}).items()},entering=entering,
               hpe=hpe,cold=sorted(hpe-set(entering)),wrapped=wrapped,plain=set(range(n))-set(wrapped))
    # Keep inherited assertions active even when our caller runs with -O.
    exec(compile(ast.Module(body=functions,type_ignores=[]),str(path),"exec",optimize=0),scope)
    result={};profiles={}
    for direction,events in data["programs"].items():
        profile,receipt=scope["local"](events,direction=="backward")
        old=data["invoice"]["providers"]["gauge44"]["local"][direction]
        need(receipt["prefix_l1_upper"]==old["prefix_l1"] and receipt["all_exact_columns"]==704,
             "retained literal receipt equality")
        profiles[direction]=profile;result[direction]=receipt
    controls=[]
    for label,change in (
        ("wrong_common_frame",lambda es:next(e for e in es if e[0]=="scalar" and e[2]!=0).__setitem__(2,0)),
        ("missing_post_wrapper",lambda es:es.pop(next(i for i,e in enumerate(es) if e[0]=="residual_adapter" and e[1]=="post"))),
        ("missing_private_final_clear",lambda es:es.pop(next(i for i,e in enumerate(es) if e[0]=="scalar" and e[1][0]=="clear" and e[1][1][0]=="C" and i>next(j for j,z in enumerate(es) if z[0]=="center"))))):
        events=copy.deepcopy(data["programs"]["forward"]);change(events)
        try:scope["local"](events,False)
        except (AssertionError,KeyError):controls.append(label)
        else:raise ValueError("retained label control accepted: "+label)
    return profiles,{"credited_checker":"retained hpe_audit_local.contains/local, optimize=0",
                     "orientations":result,"controls":controls,"wrapped_helpers":len(wrapped)}


def chart_replay(root):
    path=root/"research/selected1094-chart-phase/verify.py"
    old=module("retained_selected_chart_phase",path)
    data,_=old.inputs(root);receipt=old.audit_selected(data)
    expected=json.loads((path.parent/"EXPECTED.json").read_bytes())["selected"]
    need(normal(receipt)==expected,"retained selected chart and phase receipt")
    return {"roles":receipt["roles"],"full_charts":receipt["full_charts"],
            "kernel_coefficients_both_signs":receipt["kernel_coefficients_both_signs"],
            "chart_stream_sha256":receipt["chart_stream_sha256"],
            "kernel_stream_sha256":receipt["kernel_stream_sha256"],
            "scope":"Reuse of Gareth Davidson's selected audit; its separate orthogonal census is not rerun."}


def private_episodes(data):
    out={}
    for direction,events in data["programs"].items():
        episodes=[];active=None
        for position,event in enumerate(events):
            if event[0]=="scalar":
                op=event[1];target=op[1]
                if target[0]=="C" and op[0]=="clear":
                    if active is None:
                        active={"centre":target[1],"first":position,"last":None,
                                "copy":0,"gather":0,"transport":[],"initial_frame":event[2]}
                    else:
                        need(target[1]==active["centre"],"private clear closes its own episode")
                        active["last"]=position;active["final_frame"]=event[2]
                        episodes.append(active);active=None
                elif target[0]=="C":
                    need(active is not None and target[1]==active["centre"],"fresh private input")
                    active["copy" if op[0]=="copy" else "gather"]+=1
            elif event[0]=="center":
                need(active is not None and active["centre"]==event[1],"private centre transport")
                active["transport"].append(event[2:])
        need(active is None and len(episodes)==8,"complete private lifetimes")
        for episode in episodes:
            need(sum(t[2] for t in episode["transport"])==8,"rank-eight centre chain")
            if direction=="forward":need(episode["copy"]==1 and episode["gather"]==0,"forward copy/scatter")
            else:need(episode["copy"]==0 and episode["gather"]>0,"backward fresh gather")
        out[direction]=episodes
    return out
