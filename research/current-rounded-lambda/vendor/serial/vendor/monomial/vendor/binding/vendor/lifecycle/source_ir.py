"""Source-driven lifecycle IR and finite compiler lowering.

All recursion/dictionaries here belong to template construction, before runtime
input size varies. machine.py executes the resulting fixed finite program.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction


def need(ok, message):
    if not ok:
        raise ValueError(message)


@dataclass(frozen=True)
class Event:
    op: str
    fields: tuple
    token: tuple = ()
    rank: int = 0


@dataclass(frozen=True)
class Unit:
    name: str
    roles: tuple
    owned: tuple
    events: tuple

    def check(self):
        public = {name for name, rank in self.roles}
        private = set(self.owned)
        need(len(public) == len(self.roles) and len(private) == len(self.owned), "unique unit names")
        need(public.isdisjoint(private), "public/private name separation")
        need(all(type(r) is int and r >= 1 for _, r in self.roles), "positive target ranks")
        live = set()
        for e in self.events:
            need(e.op in ("INIT", "CLEAR", "COPY", "SERVICE", "PAID"), "unit opcode")
            if e.op == "INIT":
                need(len(e.fields) == 1 and e.fields[0] in private and e.fields[0] not in live, "fresh private INIT")
                live.add(e.fields[0])
            elif e.op == "CLEAR":
                need(len(e.fields) == 1 and e.fields[0] in live, "CLEAR only own live bank")
                live.remove(e.fields[0])
            else:
                need(e.fields and all(f in public or f in live for f in e.fields), "use outside private lifetime")
                if e.op == "COPY":
                    need(len(e.fields) == 2 and e.fields[0] in live
                         and e.fields[0] != e.fields[1], "private COPY ports")
                if e.op == "PAID":
                    need(len(e.fields) == 1 and type(e.rank) is int and e.rank > 0, "positive whole paid job")
        need(not live, "all private lifetimes end")
        return self

    def pieces(self):
        fragments, rounds = [[]], []
        for e in self.events:
            if e.op == "PAID":
                rounds.append(e)
                fragments.append([])
            else:
                fragments[-1].append(e)
        return tuple(tuple(f) for f in fragments), tuple(rounds)


def remap(event, names, context=(), rank_factor=1):
    return Event(event.op, tuple(names[f] for f in event.fields),
                 context + (event.token,), event.rank * rank_factor)


def product(left, right):
    """p7-TENSOR chronological substitution; never tensor an operator sum."""
    left.check(); right.check()
    lf, lr = left.pieces()
    roles = tuple(((i,j),k*h) for i,k in left.roles for j,h in right.roles)
    owned, maps, events = [], {}, []
    for j,h in right.roles:
        maps[j] = {i:(i,j) for i,_ in left.roles}
        for o in left.owned:
            fresh = ("left",j,o)
            owned.append(fresh); maps[j][o] = fresh
    for j,h in right.roles:
        for i,_ in left.roles:
            events.append(Event("SERVICE",((i,j),),("product-left-enter",j,h,i)))
    for ell in range(len(lr)+1):
        for j,h in right.roles:
            events += [remap(e,maps[j],("product-left",j,h)) for e in lf[ell]]
        if ell == len(lr):
            break
        issuing = lr[ell]
        names = {j:maps[j][issuing.fields[0]] for j,_ in right.roles}
        need(len(set(names.values())) == len(names), "distinct product request owners")
        for o in right.owned:
            fresh = ("right",ell,o)
            owned.append(fresh); names[o] = fresh
        events += [Event("SERVICE",(names[j],),("product-enter",ell,j,issuing.token)) for j,_ in right.roles]
        events += [remap(e,names,("product-right",ell,issuing.rank,issuing.token),issuing.rank) for e in right.events]
        events += [Event("SERVICE",(names[j],),("product-return",ell,j,issuing.token)) for j,_ in right.roles]
    for j,h in right.roles:
        for i,_ in left.roles:
            events.append(Event("SERVICE",((i,j),),("product-left-return",j,h,i)))
    return Unit(left.name+"*"+right.name,roles,tuple(owned),tuple(events)).check()


def completion_split(unit, cutoff, floor):
    unit.check()
    need(0 < cutoff < floor <= max(k for _,k in unit.roles), "completion/splitting domain")
    completed = [(name,k) for name,k in unit.roles if k < floor]
    events = [Event("SERVICE",(name,),("whole-job-in",k,floor)) for name,k in completed]
    extended = list(unit.events)
    for name,k in completed:
        extended.append(Event("PAID",(name,),("completion",k,floor),floor-k))
    for e in extended:
        if e.op != "PAID":
            events.append(e); continue
        start = 0
        while start < e.rank:
            size = min(cutoff,e.rank-start)
            token = ("piece",start,size,e.rank,e.token)
            events += [Event("SERVICE",e.fields,("piece-enter",)+token),
                       Event("PAID",e.fields,token,size),
                       Event("SERVICE",e.fields,("piece-return",)+token)]
            start += size
    events += [Event("SERVICE",(name,),("whole-job-out",k,floor)) for name,k in completed]
    return Unit(unit.name+"/pass",tuple((name,max(k,floor)) for name,k in unit.roles),
                unit.owned,tuple(events)).check()


def current_local(word):
    """Retain every current #6030 operand, chart, lifetime and paid position.

    No all-column algebra is redone. MOVE ranks are the dimension differences
    in the authenticated source rule, with their native meaning retained.
    """
    p,o = word["public"],word["owned_fields"]
    frames = word["frames"]
    current = list(word["initial"])+[None]*o
    live,untouched,starts,episodes = set(),set(),{},[]
    events,moves,peak = [],Counter(),0
    for pc,raw in enumerate(word["program"]):
        op,r = raw[:2]
        need(type(r) is int and 0 <= r < p+o,"current local role")
        token = ("local",pc,tuple(raw))
        if op == "INIT":
            need(p <= r and r not in live,"current fresh private INIT")
            live.add(r); untouched.add(r); starts[r] = pc
            current[r] = raw[2]; peak = max(peak,len(live))
            events.append(Event("INIT",(r,),token))
        elif op == "CLEAR":
            need(r in live and current[r] == raw[2],"current owned CLEAR chart")
            live.remove(r); untouched.discard(r)
            episodes.append((r,starts.pop(r),pc)); current[r] = None
            events.append(Event("CLEAR",(r,),token))
        elif op == "MOVE":
            need(len(raw) == 5 and type(raw[4]) is bool,"typed private MOVE flag")
            need(current[r] == raw[2] and (r in live) == raw[4],"current MOVE owner and chart")
            need(r < p or r in live,"live MOVE source")
            rank = abs(len(frames[raw[3]])-len(frames[raw[2]]))
            need(rank > 0,"current positive MOVE rank")
            current[r] = raw[3]; moves[rank] += 1
            untouched.discard(r)
            events += [Event("SERVICE",(r,),("move-in",)+token),
                       Event("PAID",(r,),token,rank),
                       Event("SERVICE",(r,),("move-out",)+token)]
        else:
            need(op in ("COPY","ADD","SCALE") and current[r] == raw[-1],"current scalar destination chart")
            need(r < p or r in live,"live scalar destination")
            coefficient = Fraction(raw[-2])
            need(coefficient != 0,"nonzero source coefficient")
            if op == "SCALE":
                fields = (r,)
            else:
                src = raw[2]
                need(type(src) is int and 0 <= src < p+o and src != r,"current distinct scalar source")
                need((src < p or src in live) and current[src] == raw[-1],"current common scalar chart")
                fields = (r,src)
            if op == "COPY":
                need(r in untouched and coefficient == 1,"current COPY follows untouched INIT with coefficient one")
                events.append(Event("COPY",fields,token))
            else:
                events.append(Event("SERVICE",fields,token))
            untouched.discard(r)
    need(not live and current[:p] == word["final"],"current complete local exit")
    return tuple(events),dict(events=len(word["program"]),owned_labels=o,
                              owned_lifetimes=len(episodes),peak_live=peak,
                              episodes=episodes,paid=dict(sorted(moves.items())))


def current_caller(word,caller):
    """Exact outer/local field maps and explicit copied-query lifetimes.

    Named contact/normalizer/query services retain source endpoint meanings.
    Every original scalar/MOVE token and its chronology are preserved.
    """
    local_events,report = current_local(word)
    ports = tuple(word["live"])
    need(len(ports) == len(set(ports)) == 104,"current 104 ports")
    need((caller["kind"],caller["pairs"],caller["prefix_pairs"],caller["ambient_rank"])
         == ("complex",16,7,145),"current physical caller family")
    main_local = set(ports)|{x+112 for x in ports}
    helpers = sorted(set(range(word["public"]))-main_local)
    locals_ = [e for e in caller["physical_events"] if e[0] == "LOCAL"]
    need(len(locals_) == 18 and all(not e[3] for e in locals_),"current forward local sites")
    public = 32*104+18*len(helpers)
    own_first,query_first = public,public+18*word["owned_fields"]
    owned = tuple(range(public,query_first+104))
    roles = []
    for i,term in enumerate(caller["diagonal"]):
        stages = term[1:]
        rank = (9 if stages[0] else 1)+8*sum(stages[1:])
        roles += [(i*104+j,rank) for j in range(104)]
    events,local_sites,query_sites = [],[],[]
    def scalar(raw,context):
        for j in range(104):
            fields = (raw[1]*104+j,) if raw[0] == "SCALE" else (raw[1]*104+j,raw[2]*104+j)
            events.append(Event("SERVICE",fields,context+(j,tuple(raw))))
    for raw in caller["boundaries"]["right_program"]:
        scalar(raw,("boundary-right",))
    local_number = 0
    for site,raw in enumerate(caller["physical_events"]):
        op = raw[0]
        if op == "LOCAL":
            _,stage,pair,reverse = raw
            need(not reverse,"all-forward local occurrence")
            names = {}
            for j,r in enumerate(ports):
                names[r] = 2*pair*104+j; names[r+112] = (2*pair+1)*104+j
            for j,r in enumerate(helpers):
                field = 32*104+local_number*len(helpers)+j
                names[r] = field
                rank = len(word["frames"][word["final"][r]])-len(word["frames"][word["initial"][r]])
                roles.append((field,rank))
            for j in range(word["owned_fields"]):
                names[word["public"]+j] = own_first+local_number*word["owned_fields"]+j
            need(len(names) == len(set(names.values())) == word["public"]+word["owned_fields"],
                 "injective complete current local grant")
            for r in range(word["public"]):
                events.append(Event("SERVICE",(names[r],),("local-entry",site,stage,r)))
            events += [remap(e,names,("caller-local",site,stage)) for e in local_events]
            for r in range(word["public"]):
                events.append(Event("SERVICE",(names[r],),("local-return",site,stage,r)))
            local_sites.append((site,stage,tuple(sorted(names.items())))); local_number += 1
        elif op == "QUERY_SHEAR":
            _,stage,pair,reverse = raw
            need(not reverse,"current forward query")
            for j in range(104):
                x,y,z = 2*pair*104+j,(2*pair+1)*104+j,query_first+j
                token = ("query",site,stage,j)
                events += [Event("INIT",(z,),token),Event("COPY",(z,x),token),
                           Event("SERVICE",(z,),("query-in",)+token),Event("PAID",(z,),token,1),
                           Event("SERVICE",(z,),("query-out",)+token),
                           Event("SERVICE",(y,z),("query-add",)+token),Event("CLEAR",(z,),token)]
                query_sites.append((site,j,x,y,z))
        elif op == "IDLE":
            for side in (0,1):
                for j in range(104):
                    field = (2*raw[1]+side)*104+j
                    token = ("idle",site,tuple(raw[2]),side,j)
                    events += [Event("SERVICE",(field,),("idle-in",)+token),
                               Event("PAID",(field,),token,8*len(raw[2])),
                               Event("SERVICE",(field,),("idle-out",)+token)]
        elif op == "Q_POWER":
            for j in range(104):
                events.append(Event("SERVICE",(raw[1]*104+j,),("central-square",site,j,raw[2])))
        else:
            need(op in ("ADD","SWAP","SIGNED_SWAP"),"current outer scalar opcode")
            scalar(raw,("outer",site))
    for raw in caller["boundaries"]["left_program"]:
        scalar(raw,("boundary-left",))
    roles = tuple(sorted(roles))
    need([r for r,_ in roles] == list(range(public)),"every productive field supplied once")
    # The pinned occurrence theorem supplies the complete 145-coordinate
    # whole-job canonicalizers. Each is a charged service, never a free name.
    events = ([Event("SERVICE",(r,),("raw-whole-job-enter",r,k)) for r,k in roles]
              +events+[Event("SERVICE",(r,),("raw-whole-job-return",r,k)) for r,k in roles])
    unit = Unit("selected6030",roles,owned,tuple(events)).check()
    report.update(public_count=public,raw_owned=len(owned),local_sites=len(local_sites),
                  query_lifetimes=len(query_sites),total_lifetimes=18*report["owned_lifetimes"]+len(query_sites),
                  raw_paid=dict(sorted(Counter(e.rank for e in events if e.op=="PAID").items())),
                  raw_targets=dict(sorted(Counter(k for _,k in roles).items())),raw_events=len(events))
    return unit,report


def lower(unit,rank,source):
    """Refine #5443's unchanged matching, with no partial/interface fallback.

    Insert all inter-round fragments before a class is suspended. Flatten
    finite compiler substitutions; only rank-one leaves make runtime children.
    """
    unit.check()
    fragments,rounds = unit.pieces()
    need(rounds,"nonempty paid word")
    need(max(e.rank for e in rounds)<min(k for _,k in unit.roles),"strict separated compiler rule")
    R = source.Rule(unit.name,unit.roles,tuple((e.rank,e.fields[0]) for e in rounds),unit.owned)
    public_names = {name for name,_ in unit.roles}

    class Lowerer(source.Compiler):
        def __init__(self):
            super().__init__(R,owned_policy="unit")
            self.code,self.indices,self.contexts = [],{},[]
            self.unit_context,self.unit_fields,self.occurrences = {},{},[]
            self.borrowed_private = 0
            self.program_frames,self.program_count = [],0

        def number(self,field):
            need(field in self.indices,"field has a static allocation")
            return self.indices[field]

        def append(self,event,names,context):
            self.code.append(remap(event,{key:self.number(value) for key,value in names.items()},context))

        def push(self,field,entry,expect_top):
            super().push(field,entry,expect_top)
            if isinstance(entry,tuple) and len(entry)==2 and type(entry[0]) is int:
                g,name = entry
                ctx = self.contexts[-1]
                if g not in self.unit_fields:
                    pos = len(ctx["gids"])
                    need(pos<len(ctx["metadata"]),"source class unit enumeration")
                    ctx["gids"].append(g)
                    self.unit_context[g],self.unit_fields[g] = ctx,{}
                self.unit_fields[g][name] = field
                if name in public_names:
                    pos = ctx["gids"].index(g)
                    copy,point,column = ctx["metadata"][pos]
                    context = ("occurrence",ctx["serial"],g,copy,point,column,ctx["n"],name)
                    self.code.append(Event("SERVICE",(self.number(field),),("occurrence-enter",)+context))
                    self.occurrences.append((context,self.number(field),expect_top))
                    if isinstance(field,tuple) and field and field[0]=="own":
                        self.borrowed_private += 1

        def pop(self,field,entry):
            if isinstance(entry,tuple) and len(entry)==2 and type(entry[0]) is int and entry[1] in public_names:
                g,name = entry
                ctx = self.unit_context[g]
                pos = ctx["gids"].index(g)
                copy,point,column = ctx["metadata"][pos]
                context = ("occurrence",ctx["serial"],g,copy,point,column,ctx["n"],name)
                self.code.append(Event("SERVICE",(self.number(field),),("occurrence-return",)+context))
            super().pop(field,entry)

        def alloc_bank(self,g,oname,frame,d):
            field = super().alloc_bank(g,oname,frame,d)
            need(field not in self.indices,"fresh occurrence bank identity")
            self.indices[field] = len(self.indices)
            return field

        def begin_round(self,ctx):
            j = ctx["round"]
            need(j<len(rounds),"source cannot advance beyond final round")
            need(len(ctx["gids"])==len(ctx["metadata"]),"complete class match before scalar contacts")
            for g,meta in zip(ctx["gids"],ctx["metadata"]):
                names = self.unit_fields[g]
                need(set(names)==public_names|set(unit.owned),"complete field map")
                for e in fragments[j]:
                    self.append(e,names,("unit-fragment",ctx["serial"],g,meta[2],j))
            ctx["round"] += 1
            return j

        def run_class(self,frame,n,a,G,d,dil,incoming,exits_iter):
            if incoming:
                parent = self.unit_context[incoming[0]["issuer"][0]]
                j = self.begin_round(parent)
                need(len(incoming)==len(parent["gids"]),"one request per parent unit")
                for job,g,meta in zip(incoming,parent["gids"],parent["metadata"]):
                    need(job["issuer"]==(g,rounds[j].fields[0]) and job["rank"]==rounds[j].rank*meta[2],
                         "literal incoming owner and rank")
            metadata = [(copy,point,dil*R.c(point)) for copy in range(a)
                        for point in R.lattice(n,dil) if sum(point)==G-d for _ in range(R.u(point))]
            ctx = dict(n=n,metadata=metadata,gids=[],round=0,pending=None,serial=len(self.occurrences))
            self.contexts.append(ctx)
            super().run_class(frame,n,a,G,d,dil,incoming,exits_iter)
            need(ctx["round"]==len(rounds) or not metadata,"complete source class chronology")
            need(self.contexts.pop() is ctx,"static compiler stack order")

        def free_class_banks(self,units):
            if units:
                ctx = self.unit_context[units[0][1]]
                need(ctx["round"]==len(rounds) and ctx["pending"] is None,"all exits returned before cleanup")
                for U in units:
                    _,g,_,column,_,_,_ = U
                    for e in fragments[-1]:
                        self.append(e,self.unit_fields[g],("unit-fragment",ctx["serial"],g,column,len(rounds)))
            super().free_class_banks(units)

        def sub(self,n,fields,tops):
            kind = ("source-complement",self.program_frames[-1],n,
                    self.program_frames[-1][1]-n)
            if tops and isinstance(tops[0],tuple) and len(tops[0])==2 and type(tops[0][0]) is int:
                ctx = self.unit_context[tops[0][0]]
                if ctx["pending"] is None:
                    j = self.begin_round(ctx)
                    ctx["pending"] = set(ctx["gids"])
                else:
                    j = ctx["round"]-1
                for field,top in zip(fields,tops):
                    g,name = top
                    need(self.unit_context[g] is ctx and g in ctx["pending"],"unique exit batch owner")
                    need(name==rounds[j].fields[0] and field==self.unit_fields[g][name],"exact exit binding")
                    ctx["pending"].remove(g)
                if not ctx["pending"]:
                    ctx["pending"] = None
                kind = ("deepest-exit",ctx["serial"],j,n,tuple(tops))
            ordered_fields = tuple(self.number(field) for field in fields)
            need(len(set(ordered_fields))==len(ordered_fields),"whole smaller-program distinct field binding")
            binding = ("matched-program",kind,ordered_fields)
            for index,field in enumerate(ordered_fields):
                self.code.append(Event("SERVICE",(field,),("program-enter",binding,index)))
            if n<R.m:
                self.blackbox(n,fields,tops)
                self.stats["base_rank_lt_m_fields"] += len(fields)
            else:
                need(len(fields)==self.compile(n)[0],"complete smaller-rank program; no interface-only fallback")
                self.uniform(n,fields,tops)
            for index in reversed(range(len(ordered_fields))):
                self.code.append(Event("SERVICE",(ordered_fields[index],),("program-return",binding,index)))

        def blackbox(self,n,fields,tops):
            need(n<R.m,"only elementary rank base may be opaque")
            super().blackbox(n,fields,tops)
            for field in fields:
                for axis in range(n):
                    token=("ordinary-rank-one",len(self.code),self.number(field),
                           tuple(self.program_frames),
                           tuple((c["serial"],c["round"]) for c in self.contexts),axis,n)
                    self.code.append(Event("SERVICE",(self.number(field),),("base-axis-enter",)+token))
                    self.code.append(Event("PAID",(self.number(field),),token,1))
                    self.code.append(Event("SERVICE",(self.number(field),),("base-axis-return",)+token))

        def uniform(self,n,fields,tops,top_level=False,copies=None):
            need(copies is None,"partial compiler execution forbidden")
            self.program_count += 1
            self.program_frames.append((self.program_count,n))
            super().uniform(n,fields,tops,top_level=top_level,copies=None)
            self.program_frames.pop()

    compiler = Lowerer()
    B,a,P,cost = compiler.compile(rank)
    fields = [("array",i) for i in range(B)]
    compiler.indices.update({field:i for i,field in enumerate(fields)})
    if rank<R.m:
        compiler.blackbox(rank,fields,[None]*B)
    else:
        compiler.uniform(rank,fields,[None]*B,top_level=True)
        need(all(compiler.received[f]==2 for f in fields),"every source plus complement occurs exactly once")
    need(all(not entries for entries in compiler.stack.values()),"source ownership stacks restored")
    need(sum(e.op=="PAID" for e in compiler.code)==P,"literal paid leaf count")
    result = Unit(unit.name+"/uniform",tuple((i,rank) for i in range(B)),
                  tuple(range(B,len(compiler.indices))),tuple(compiler.code)).check()
    summary = dict(rank=rank,width=B,replication=a,paid=P,source_cost=cost,
                   events=len(result.events),owned=len(result.owned),
                   occurrences=len(compiler.occurrences),borrowed_private=compiler.borrowed_private,
                   source_stats=dict(sorted(compiler.stats.items())))
    return result,summary,tuple(compiler.occurrences)


def check_flat_ownership(unit):
    """Independent flat-word permission replay; does not call the compiler."""
    public={i for i,_ in unit.roles};private=set(unit.owned)
    scopes={i:[] for i in public|private}
    owners={};max_depth=0;counts=Counter()
    for e in unit.events:
        token=e.token
        if e.op=="SERVICE" and token and token[0] in ("occurrence-enter","occurrence-return"):
            field,=e.fields;scope=("occurrence",token[1:])
            if token[0].endswith("enter"):
                need(field in public or field in owners,"borrow initialized actual private field")
                scopes[field].append(scope);counts["occurrence_entries"]+=1
                counts["private_occurrence_entries"]+=int(field in private)
            else:
                need(scopes[field] and scopes[field][-1]==scope,"exact occurrence inverse return")
                scopes[field].pop()
        elif e.op=="SERVICE" and token and token[0] in ("program-enter","program-return"):
            field,=e.fields;binding,index=token[1:]
            need(binding[0]=="matched-program" and binding[2][index]==field,"ordered complete subprogram field")
            scope=("program",binding,index)
            if token[0].endswith("enter"):
                need(field in public or field in owners,"subprogram borrows initialized field")
                scopes[field].append(scope);counts[binding[1][0]+"_fields"]+=1
            else:
                need(scopes[field] and scopes[field][-1]==scope,"exact whole-program inverse return")
                scopes[field].pop()
        elif e.op=="SERVICE" and token and token[0] in ("base-axis-enter","base-axis-return"):
            field,=e.fields;scope=("base-axis",token[1:])
            need(token[1]=="ordinary-rank-one" and token[3]==field,"actual elementary axis owner")
            if token[0].endswith("enter"):
                need(field in public or field in owners,"base axis borrows initialized field")
                scopes[field].append(scope);counts["base_axis_entries"]+=1
            else:
                need(scopes[field] and scopes[field][-1]==scope,"exact elementary axis inverse return")
                scopes[field].pop()
        else:
            actor=token[2] if token and token[0]=="unit-fragment" else None
            if e.op=="INIT":
                field,=e.fields
                need(actor is not None and field in private and field not in owners and not scopes[field],
                     "fresh unborrowed static private bank")
                owners[field]=actor;counts["physical_init_sites"]+=1
            elif e.op=="CLEAR":
                field,=e.fields
                need(field in owners and owners[field]==actor and not scopes[field],
                     "only actual owner clears after all child returns")
                del owners[field];counts["physical_clear_sites"]+=1
            else:
                for field in e.fields:
                    need(field in public or field in owners,"initialized emitted operand")
                    if actor is not None:
                        if scopes[field]:
                            top=scopes[field][-1]
                            need(top[0]=="occurrence" and top[1][2]==actor,
                                 "parent cannot resume through a pending borrow")
                        else:
                            need(owners.get(field)==actor,"unborrowed private actor")
                if e.op=="PAID":
                    need(e.rank==1,"only ordinary rank-one calls remain")
                    counts["ordinary_paid_sites"]+=1
                    counts["ordinary_private_paid_sites"]+=int(e.fields[0] in private)
        max_depth=max(max_depth,max((len(scopes[f]) for f in e.fields),default=0))
    need(not owners and not any(scopes.values()),"all static scopes and physical lifetimes close")
    return dict(max_borrow_depth=max_depth,counts=dict(sorted(counts.items())))
