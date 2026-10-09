"""Independent exact scalar sink protocol; stdlib only, no producer imports.

Sparse integer numerator vectors carry an adaptive exact denominator per row.
Both input banks and every retained dirty slot have disjoint formal variables.
Frame eligibility of sinks is checked; this is not a complete phase/frame proof.
Apache-2.0. Prepared with Codex assistance.
"""
from hashlib import sha256
import json
from math import lcm
from pathlib import Path
import sys
import time


class IdentityError(ValueError): pass


def need(condition, message):
    if not condition: raise ValueError(message)


class Meter:
    def __init__(self, seconds=300):
        self.start=time.monotonic(); self.seconds=seconds; self.operations=0
    def check(self):
        if time.monotonic()-self.start>self.seconds: raise TimeoutError('exact audit wall budget')


class Row:
    def __init__(self, data=None, denominator=1):
        need(type(denominator) is int and denominator>0, 'positive exact denominator')
        need(data is None or (type(data) is dict and all(type(k) is int and k>=0 and type(v) is int and v!=0
              for k,v in data.items())), 'exact sparse integer row')
        self.data={} if data is None else data
        self.denominator=denominator
    def add(self, source, factor, meter):
        need(self is not source, 'distinct row ports')
        numerator, denominator=factor
        need(type(numerator) is int and type(denominator) is int and denominator>0, 'exact factor')
        if not numerator or not source.data: return
        new=lcm(self.denominator, source.denominator*denominator)
        multiplier=new//self.denominator
        if multiplier!=1:
            for column in self.data: self.data[column]*=multiplier
        self.denominator=new
        multiplier=numerator*(new//(source.denominator*denominator))
        for count,(column,value) in enumerate(source.data.items()):
            new_value=self.data.get(column,0)+multiplier*value
            if new_value: self.data[column]=new_value
            else: self.data.pop(column,None)
            if not count%4096: meter.check()
        meter.operations+=len(source.data)
    def equals(self, coefficients):
        return self.data=={k:self.denominator*v for k,v in coefficients.items() if v}


def binary_basis(rows):
    pivots={}
    for value in rows:
        need(type(value) is int and value>=0, 'binary frame vector')
        for pivot in sorted(pivots,reverse=True):
            if value>>pivot&1: value^=pivots[pivot]
        if value:
            pivot=value.bit_length()-1
            for other in list(pivots):
                if pivots[other]>>pivot&1: pivots[other]^=value
            pivots[pivot]=value
    return tuple(pivots[p] for p in sorted(pivots,reverse=True))


def complement(rows,h):
    pivots={r.bit_length()-1:r for r in binary_basis(rows)}
    out=[]
    for j in range(h):
        if j not in pivots:
            value=1<<j
            for pivot,row in pivots.items():
                if row>>j&1: value|=1<<pivot
            out.append(value)
    return binary_basis(out)


def subspace(a,b): return len(binary_basis(tuple(a)+tuple(b)))==len(binary_basis(b))


def add_integer(target,source,factor):
    need(target is not source, 'distinct response rows')
    for k,v in source.items():
        total=target.get(k,0)+factor*v
        if total: target[k]=total
        else: target.pop(k,None)


def check_response_correspondence(ops,coef,order,cs,ds,actual_c,actual_d,R):
    """Compare the native raw-operation adjoint with the execution adjoint."""
    need(all(type(i) is int for i in order) and sorted(order)==list(range(len(ops))), 'operation order permutation')
    raw={}; reordered={}
    for i,(a,b,_) in enumerate(ops):
        raw.setdefault(a,[]).append(i);raw.setdefault(b,[]).append(i)
    for i in order:
        a,b,_=ops[i]
        reordered.setdefault(a,[]).append(i);reordered.setdefault(b,[]).append(i)
    need(raw==reordered,'native per-role operation order preservation')
    c=[dict(cs.get(s,{})) for s in range(R)]
    d=[dict(ds.get(s,{})) for s in range(R)]
    for i in reversed(range(len(ops))):
        a,b,_=ops[i];ca,cb=coef[i]
        need(type(ca) is int and ca==1 and type(cb) is int and cb in (-1,1),'response shear coefficient')
        add_integer(c[b],c[a],cb);add_integer(d[b],d[a],cb)
    need(c==actual_c and d==actual_d,'native raw/phase adjoint responses equal')
    return {'per_role_order_preserved':True,'exact_all_center_and_side_responses_equal':True,
            'roles':R,'operations':len(ops),
            'response_sha256':sha256(json.dumps({'c':c,'d':d},sort_keys=True,separators=(',',':')).encode()).hexdigest()}


class Protocol:
    def __init__(self,graph,word,witness,frames,pairs,sinks,meter):
        self.meter=meter; self.g=graph; self.w=word
        self.inputs=graph['inputs']; self.h=graph['h']; self.v=len(self.inputs)
        need(type(self.h) is int and self.h>0 and self.v and self.v%8==0,'dimensions')
        need(all(type(q) is int and 0<=q<2**self.h for q in self.inputs),'source addresses')
        labels=graph.get('labels',[])
        need(len(labels)==self.v and all(all(type(i) is int for i in label) and
             set(label)=={i for i in range(self.h) if address>>i&1}
             for label,address in zip(labels,self.inputs)), 'labels and source addresses agree')
        self.ops=[tuple(o) for o in word['ops']]
        self.coef=[tuple(o) for o in word['opcoeff']]
        need(len(self.ops)==len(self.coef) and all(len(o)==3 and all(type(x) is int and x>=0 for x in o) for o in self.ops),'operation schema')
        need(all(ca==1 and type(ca) is int and type(cb) is int and cb in (-1,1) for ca,cb in self.coef),'selected sink word must use shear gates')
        self.phase=sorted(word['phase1'])
        need(len(set(self.phase))==len(self.phase) and all(type(i) is int and 0<=i<len(self.ops) for i in self.phase),'phase schema')
        phase=set(self.phase)
        self.rest=[i for i in range(len(self.ops)) if i not in phase]
        need(self.rest,'nonempty second phase')
        self.order=self.phase+self.rest
        self.position={i:p for p,i in enumerate(self.order)}
        self.sources={int(x)-1:s for x,s in word['sources'].items()}
        need(set(self.sources)==set(range(self.v)) and all(type(s) is int and s>=0 for s in self.sources.values()) and
             len(set(self.sources.values()))==self.v,'source bijection')
        self.selected=[z['role'] for z in word['selected']]
        need(all(type(s) is int and s>=0 for s in self.selected) and len(set(self.selected))==len(self.selected),'deferred role uniqueness')
        deferred=set(self.selected)
        self.roots=graph['roots']; self.rootroles=word['rootroles']
        need(all(type(s) is int and s>=0 for s in self.rootroles) and len(self.roots)==len(self.rootroles)==len(set(self.rootroles)),'root role bijection')
        roles=set(self.sources.values())|deferred|set(self.rootroles)
        for a,b,_ in self.ops:
            need(a!=b,'equal gate ports'); roles.update((a,b))
        need(roles and all(type(s) is int and s>=0 for s in roles),'role schema')
        self.R=max(roles)+1
        need(all(len(p)==3 and type(p[0]) is int and type(p[1]) is int and p[0]>=0 and p[1]>=0 and
             (p[2] is None or type(p[2]) is int and p[2]>=0) for p in pairs),'pair exact schema')
        self.merge={b:a for a,b,_ in pairs}
        donors={a:b for a,b,_ in pairs}
        need(len(self.merge)==len(donors)==len(pairs) and not set(donors)&set(self.merge),'pair matching')
        self.deadlines={b:t for _,b,t in pairs}
        first,last={},{}
        for i in self.order:
            for role in self.ops[i][:2]: first.setdefault(role,i); last[role]=i
        for a,b,t in pairs:
            need(a in last and b in first and a not in deferred and a not in self.rootroles and b in deferred,'pair kinds')
            need(b not in self.sources.values(),'source recipient')
            if t is None:
                need(last[a] in phase and first[b] not in phase,'early alias chronology')
            else:
                need(type(t) is int and t==first[b] and t in self.rest and self.position[last[a]]<self.position[t],'late alias chronology')
        self.read_at={s:self.deadlines.get(s) if self.deadlines.get(s) is not None else self.rest[0] for s in self.selected}
        self.cs,self.ds={},{}
        for root,role in zip(self.roots,self.rootroles):
            if root['kind']=='center':
                coordinate=root['coordinate']
                need(type(coordinate) is int and 0<=coordinate<self.h,'center coordinate')
                self.cs[role]={coordinate:1}
            else:
                need(root['kind']=='side' and len(root['targets'])==len(root['coefficients']),'side root schema')
                need(len(set(root['targets']))==len(root['targets']),'side targets unique')
                weights={}
                for target,coefficient in zip(root['targets'],root['coefficients']):
                    need(type(target) is int and 0<=target<self.v and coefficient in ('1/2','-1/2'),'side coefficient schema')
                    weights[target]=1 if coefficient=='1/2' else -1
                self.ds[role]=weights
        self.c=[dict(self.cs.get(s,{})) for s in range(self.R)]
        self.d=[dict(self.ds.get(s,{})) for s in range(self.R)]
        for i in reversed(self.order):
            a,b,_=self.ops[i]; cb=self.coef[i][1]
            add_integer(self.c[b],self.c[a],cb); add_integer(self.d[b],self.d[a],cb)
        self.response_correspondence=check_response_correspondence(self.ops,self.coef,self.order,
                                      self.cs,self.ds,self.c,self.d,self.R)
        ann=witness['annihilators']
        operation_frames=[complement(ann[x],self.h) for _,_,x in self.ops]
        seen=set()
        for i,frame in frames:
            need(type(i) is int and 0<=i<len(self.ops) and i not in seen,'physical frame override schema')
            seen.add(i); operation_frames[i]=binary_basis(frame)
        first_correction={}
        for z in word['selected']:
            for t in z['targets']:
                first_correction[t]=min(first_correction.get(t,len(self.order)),self.position[self.read_at[z['role']]])
        self.sinks={}
        target_set=set()
        for s,pivot in sinks:
            need(type(s) is int and type(pivot) is int and s not in self.sinks,'sink schema')
            need(s in self.rootroles,'sink root exists')
            root=self.roots[self.rootroles.index(s)]
            targets=root.get('targets',[])
            need(root['kind']=='side' and targets and pivot in targets and len(set(root['coefficients']))==1,'sink root uniform coefficient')
            need(s not in self.merge and s not in donors and s not in deferred and s not in self.sources.values() and s not in self.cs,'sink has no alias, gauge or injection')
            writes=[i for i in self.order if self.ops[i][0]==s]
            need(writes and not any(b==s for _,b,_ in self.ops) and not set(writes)&phase,'sink destination-only second-phase writes')
            U=complement(binary_basis(self.inputs[t] for t in targets),self.h)
            chain=[()]+[operation_frames[i] for i in writes]+[U]
            need(all(subspace(a,b) for a,b in zip(chain,chain[1:])),'sink nested write frame')
            need(not self.c[s] and self.d[s]==self.ds[s],'sink response is root seed')
            need(first_correction.get(pivot,len(self.order))>self.position[writes[-1]],'sink pivot deadline')
            need(not target_set&set(targets),'sink target groups disjoint')
            target_set.update(targets)
            self.sinks[s]={'pivot':pivot,'targets':targets,'writes':writes,'coefficient':1 if root['coefficients'][0]=='1/2' else -1,'rank':len(U)}
        self.live=[s for s in range(self.R) if s not in self.merge and s not in self.sinks]
        self.slots={s:i for i,s in enumerate(self.live)}
        meter.check()

    def port(self,role):
        role=self.merge.get(role,role)
        need(role in self.slots,'access to removed sink')
        return ('Z',self.slots[role])

    def events(self):
        events=[]; retained=[]
        def addition(dest,source,factor,tag,identity=None):
            need(dest!=source,'distinct event ports')
            events.append({'kind':'add','dest':dest,'source':source,'factor':factor,'tag':tag,'identity':identity})
        def read(s,sign,seed=False):
            events.append({'kind':'read','source':self.port(s),'role':s,'sign':sign,'seed':seed,'bank':'Y'})
        def gate(i):
            a,b,_=self.ops[i]
            addition(self.port(a),self.port(b),(self.coef[i][1],1),'gate',i)
            retained.append(i)
        for s in range(self.R):
            if s not in self.selected and s not in self.merge and s not in self.sinks: read(s,-1)
        for x,s in sorted(self.sources.items()): addition(self.port(s),('X',x),(1,1),'injection',x)
        for i in self.phase: gate(i)
        for s in self.cs: read(s,1,True)
        events.append({'kind':'flush','bank':'Y'})
        for s,z in self.sinks.items():
            for t in z['targets']:
                if t!=z['pivot']: addition(('Y',t),('Y',z['pivot']),(-1,1),'sink_pre',s)
        due={}
        for s in reversed(self.selected): due.setdefault(self.read_at[s],[]).append(s)
        redirected={i:s for s,z in self.sinks.items() for i in z['writes']}
        final={z['writes'][-1]:s for s,z in self.sinks.items()}
        for i in self.rest:
            for s in due.get(i,[]): read(s,-1)
            if i in redirected:
                s=redirected[i]; z=self.sinks[s]
                addition(('Y',z['pivot']),self.port(self.ops[i][1]),(z['coefficient']*self.coef[i][1],2),'sink_pivot',s)
            else: gate(i)
            if i in final:
                s=final[i]; z=self.sinks[s]
                for t in z['targets']:
                    if t!=z['pivot']: addition(('Y',t),('Y',z['pivot']),(1,1),'sink_post',s)
        for root,s in zip(self.roots,self.rootroles):
            if root['kind']=='side' and s not in self.sinks: read(s,1,True)
        for base in range(0,self.v,8):
            for parity in (0,1):
                indices=[k for k in range(8) if k.bit_count()%2==parity]
                targets=[k^7 for k in indices]
                matrix=[]
                for t in targets:
                    row=[]
                    for source in indices:
                        distance=(self.inputs[base+t]^self.inputs[base+source]).bit_count()
                        row.append((1 if distance==6 else -1 if distance==2 else 0,2))
                    matrix.append(row)
                ports=[('X',base+k) for k in indices]
                events.append({'kind':'linear4','ports':ports,'matrix':matrix})
                for j,t in enumerate(targets): addition(('Y',base+t),ports[j],(1,1),'K_delivery')
                events.append({'kind':'linear4','ports':ports,'matrix':[list(c) for c in zip(*matrix)]})
        for i in reversed(retained):
            a,b,_=self.ops[i]
            addition(self.port(a),self.port(b),(-self.coef[i][1],1),'gate_inverse',i)
        for x,s in sorted(self.sources.items(),reverse=True): addition(self.port(s),('X',x),(-1,1),'uninjection',x)
        return events

    def reflected(self,events):
        swap=lambda port: ('Y' if port[0]=='X' else 'X' if port[0]=='Y' else 'Z',port[1])
        output=[]
        for original in reversed(events):
            e=dict(original)
            if e['kind']=='add':
                e['dest']=swap(e['dest']); e['source']=swap(e['source'])
                n,d=e['factor']; e['factor']=(-n,d)
            elif e['kind']=='read': e['bank']='X' if e['bank']=='Y' else 'Y'; e['sign']=-e['sign']
            elif e['kind']=='linear4':
                e['ports']=[swap(p) for p in e['ports']]
                e['matrix']=[list(c) for c in zip(*e['matrix'])]
            elif e['kind']=='flush': e['bank']='X' if e['bank']=='Y' else 'Y'
            else: raise ValueError('unknown reflected event')
            output.append(e)
        return output

    def replay(self,events,reflected=False):
        v=self.v; meter=self.meter
        banks={'X':[Row({t:1}) for t in range(v)],'Y':[Row({v+t:1}) for t in range(v)],
               'Z':[Row({2*v+j:1}) for j in range(len(self.live))]}
        pending={bank:[Row() for _ in range(self.h)] for bank in ('X','Y')}
        def flush(bank):
            for coordinate,row in enumerate(pending[bank]):
                if row.data:
                    for t,address in enumerate(self.inputs):
                        factor=(1,3) if address>>coordinate&1 else (-1,6)
                        banks[bank][t].add(row,factor,meter)
                    pending[bank][coordinate]=Row()
        def get(port):
            if port[0]!='Z': flush(port[0])
            return banks[port[0]][port[1]]
        for count,e in enumerate(events):
            kind=e['kind']
            if kind=='add':
                source=get(e['source'])
                banks[e['dest'][0]][e['dest'][1]].add(source,e['factor'],meter)
            elif kind=='read':
                value=get(e['source']); sign=e['sign']; role=e['role']; bank=e['bank']
                c=self.cs.get(role,{}) if e['seed'] else self.c[role]
                d=self.ds.get(role,{}) if e['seed'] else self.d[role]
                for coordinate,coefficient in c.items(): pending[bank][coordinate].add(value,(sign*coefficient,1),meter)
                for target,coefficient in d.items(): banks[bank][target].add(value,(sign*coefficient,2),meter)
            elif kind=='linear4':
                old=[get(port) for port in e['ports']]
                new=[Row() for _ in old]
                for j,row in enumerate(e['matrix']):
                    for source,factor in zip(old,row): new[j].add(source,factor,meter)
                for port,row in zip(e['ports'],new): banks[port[0]][port[1]]=row
            elif kind=='flush': flush(e['bank'])
            else: raise ValueError('unknown event kind')
            if not count%128: meter.check()
        flush('X'); flush('Y')
        for t in range(v):
            expect_x={t:1,v+t:-1} if reflected else {t:1}
            expect_y={v+t:1} if reflected else {v+t:1,t:1}
            if not banks['X'][t].equals(expect_x): raise IdentityError('source bank row '+str(t))
            if not banks['Y'][t].equals(expect_y): raise IdentityError('target bank row '+str(t))
        for j,row in enumerate(banks['Z']):
            if not row.equals({2*v+j:1}): raise IdentityError('dirty restore row '+str(j))
        return {'forward':not reflected,'reflected':reflected,'source_rows':v,'target_rows':v,'dirty_rows':len(self.live),
                'formal_basis':2*v+len(self.live),'events':len(events),'ring':'Q via integer numerators/adaptive denominators',
                'all_absent_coefficients_checked':True,'largest_final_denominator':max(r.denominator for bank in banks.values() for r in bank)}


def audit_raw(graph,word,witness,frames,pairs,sinks,*,seconds=300):
    """Pure entry point: raw data only, no producer/repository modules or I/O."""
    meter=Meter(seconds)
    protocol=Protocol(graph,word,witness,frames,pairs,sinks,meter)
    events=protocol.events()
    positive={'forward':protocol.replay(events),'reflected':protocol.replay(protocol.reflected(events),True)}
    controls={}
    for name in ('omit_post_shear','wrong_pivot_sign','omit_compensated_read','wrong_dirty_inverse'):
        changed=list(events)
        if name=='omit_post_shear':
            index=next(i for i,e in enumerate(changed) if e.get('tag')=='sink_post')
            del changed[index]
        elif name=='wrong_pivot_sign':
            index=next(i for i,e in enumerate(changed) if e.get('tag')=='sink_pivot')
            changed[index]=dict(changed[index]); n,d=changed[index]['factor']; changed[index]['factor']=(-n,d)
        elif name=='omit_compensated_read':
            recipient=next(b for b in protocol.merge if protocol.c[b] or protocol.d[b])
            index=next(i for i,e in enumerate(changed) if e['kind']=='read' and e['role']==recipient and e['sign']==-1)
            del changed[index]
        else:
            index=next(i for i,e in enumerate(changed) if e.get('tag')=='gate_inverse')
            changed[index]=dict(changed[index]); n,d=changed[index]['factor']; changed[index]['factor']=(-n,d)
        try: protocol.replay(changed)
        except IdentityError as error: controls[name]={'rejected':True,'reason':str(error)}
        else: raise ValueError('mathematical negative control accepted: '+name)
    return {'status':'computed_pass','event_sha256':sha256(json.dumps(events,sort_keys=True,separators=(',',':')).encode()).hexdigest(),
            'positive':positive,'controls':controls,'sink_count':len(protocol.sinks),'role_count':protocol.R,
            'retained_dirty':len(protocol.live),'aliases':len(protocol.merge),
            'native_response_correspondence':protocol.response_correspondence,
            'elapsed_seconds':time.monotonic()-meter.start,'sparse_term_additions':meter.operations,
            'limits':{'seconds':seconds,'workers':1,'required_external_memory_limit_bytes':4*1024**3},
            'scope':'Exact finite scalar maps on the full source, target and retained dirty basis; sink eligibility checks. Full frame/phase/all-size proof not certified.'}


def audit(folder):
    folder=Path(folder)
    data=lambda p: json.loads(p.read_text())
    work=folder/'producer-1'; repo=folder/'repo'
    files={'graph':work/'graph.json','word':work/'selection.json','witness':work/'frames.json',
           'physical_frames':repo/'references/paired-cube/physical/frames.json',
           'physical_pairs':repo/'references/paired-cube/physical/pairs.json',
           'sinks':repo/'research/terminal-sinks/sinks.json'}
    result=audit_raw(data(files['graph']),data(files['word']),data(files['witness']),
                     data(files['physical_frames'])['frames'],data(files['physical_pairs'])['pairs'],data(files['sinks'])['sinks'])
    result['source_input_sha256']={k:sha256(p.read_bytes()).hexdigest() for k,p in files.items()}
    result['checker_sha256']=sha256(Path(__file__).read_bytes()).hexdigest()
    return result


if __name__=='__main__':
    result=audit(sys.argv[1])
    target=Path(sys.argv[1])/(sys.argv[2] if len(sys.argv)>2 else 'exact-sinks-result.json')
    with target.open('x') as stream: json.dump(result,stream,indent=2,sort_keys=True); stream.write('\n')
    print(json.dumps(result,indent=2,sort_keys=True))
