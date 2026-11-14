#!/usr/bin/env python3
"""Independent original-source arithmetic census and outermost-meter audit.
No B12 interpreter, binder, oracle or checker is imported. Apache-2.0.
"""
from pathlib import Path
from hashlib import sha256
from collections import Counter
import argparse,ast,importlib.util,json,math,sys
PINS={
 'encoded-current-crt/producer.py':'88dab4ca02a92164a67826db361214fa1405e4b4a588f8c4279a21bcee95ab76',
 'encoded-crt-leaf-payload/frozen/inverse_producer.py':'6acdebee7134fbc8e2d121060286bd05e7282900da8a28a78c80937dde7ea178',
 'r437-preparation-composition/predecessor4025/source/words.py':'5c37f57708ba3131bdcb03139f9dbc29886bee44569c09cbba51b68f75acd7f9',
 'r437-preparation-composition/predecessor4025/source/records.py':'0c9c4b23e998597fb877bb1a29da69ac869b68262abe635b162b4dba9c69b372'}
PROVIDERS=('compare','add','subtract','divmod')
def require(value,message):
    if not value:raise ValueError(message)
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);sys.modules[name]=m
    spec.loader.exec_module(m);return m
def locate(root):
    found={}
    for suffix,digest in PINS.items():
        candidates=sorted(p for p in root.rglob(Path(suffix).name) if p.as_posix().endswith(suffix))
        require(candidates,'missing retained original '+suffix)
        for path in candidates:require(sha256(path.read_bytes()).hexdigest()==digest,'exact retained source '+suffix)
        found[suffix]=candidates[0]
    return found
def raw_calls(path):
    calls=[]
    for node in ast.walk(ast.parse(path.read_bytes())):
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute):
            base=node.func.value
            if isinstance(base,ast.Attribute) and base.attr=='raw':calls.append((node.lineno,node.func.attr,ast.unparse(node)))
    calls.sort();require(len(calls)==16,'all sixteen source raw call sites')
    require({row[1] for row in calls}=={'compare','add','subtract_exact','divmod'},'exact reached raw alphabet')
    return calls
def value(word):return sum(b<<i for i,b in enumerate(word.cells[1:-1]))
def stream(records,words,p,rows):
    t=records.Tape()
    for modulus,current in rows:
        t.append(records.ROOT)
        for x in (modulus,current):
            require(0<=x<1<<p,'fixture fits source word')
            for k in range(p):t.append((x>>k)&1)
            t.append(records.WORD_END)
        t.append(records.RECORD_END)
    t.append(words.RIGHT);t.rewind();return t
def parse_stream(t,records,words,p):
    data=t.cells;k=1;rows=[]
    while data[k]!=words.RIGHT:
        require(data[k]==records.ROOT,'output ROOT');k+=1;row=[]
        for _ in range(2):
            digits=data[k:k+p];require(len(digits)==p and set(digits)<={0,1},'output P digits')
            row.append(sum(x<<j for j,x in enumerate(digits)));k+=p
            require(data[k]==records.WORD_END,'output WORD_END');k+=1
        require(data[k]==records.RECORD_END,'output RECORD_END');k+=1;rows.append(row)
    return rows
def integer_reference(left,right,reverse):
    lower=0;prefix=1;euclid=0
    for modulus,current in left:
        x,y=modulus,prefix%modulus
        while y:x,y=y,x%y;euclid+=1
        require(x==1,'coprime source prefix')
        lower+=prefix*((current-lower*pow(prefix,-1,modulus))%modulus);prefix*=modulus
    if any(current>=modulus for modulus,current in left):lower=0
    product=prefix;rows=[]
    for modulus,current in right:
        x,y=modulus,prefix%modulus
        while y:x,y=y,x%y;euclid+=1
        require(x==1,'coprime right prefix')
        offset=lower*pow(prefix,-1,modulus)%modulus
        updated=(current+(-offset if reverse else offset))%modulus if current<modulus else current
        rows.append([offset,updated]);prefix*=modulus
    return lower,product,rows,euclid
def one_case(words,records,producer,p,left,right,reverse):
    require(math.prod(m for m,_ in left+right)<1<<(p-1),'source product reserve')
    arena=words.Arena(p,64);arena.words=[words.Word(arena,i) for i in range(64)]
    arena.available=list(range(63,-1,-1))
    guards=[arena.literal((5*i+3)% (1<<p)) for i in range(8)]
    for i,w in enumerate(guards):w.head=1+i%(p+1)
    guard_state=[(bytes(w.cells),w.head) for w in guards]
    l=stream(records,words,p,left);r=stream(records,words,p,right);borrowed=(bytes(l.cells),bytes(r.cells))
    stack=[];outer=Counter();all_calls=Counter();aliases=Counter()
    action_partition=Counter();outer_actions=Counter();inclusive_actions=Counter()
    original_raw={name:getattr(words.Unsigned,name) for name in PROVIDERS}
    original_word={name:getattr(words.Word,name) for name in ('read','write','step')};recording=False
    def meter():return arena.meter.reads+arena.meter.writes+arena.meter.moves
    def wrap_word(name,original):
        def action(obj,*args):
            result=original(obj,*args)
            if recording and obj.arena is arena:action_partition['inside' if stack else 'outside']+=1
            return result
        return action
    def wrap_raw(name,original):
        def call(obj,a,b):
            require(obj.arena is arena,'single source arena')
            top=not stack;before=meter();all_calls[name]+=1
            if top:
                outer[name]+=1
                if a is b:aliases[name]+=1
            stack.append(name)
            try:return original(obj,a,b)
            finally:
                stack.pop();used=meter()-before;inclusive_actions[name]+=used
                if top:outer_actions[name]+=used
        return call
    for name,method in original_word.items():setattr(words.Word,name,wrap_word(name,method))
    for name,method in original_raw.items():setattr(words.Unsigned,name,wrap_raw(name,method))
    before=meter()
    try:
        recording=True;result=producer.produce(arena,l,r,words,records);recording=False;produced=meter()-before
        require(not stack,'all old provider intervals closed')
        require(produced==sum(action_partition.values()),'independent action-level total')
        require(sum(outer_actions.values())==action_partition['inside'],'outermost intervals equal action-level inside partition')
        require(produced-sum(outer_actions.values())==action_partition['outside'],'exact retained-source residual')
        expected=integer_reference(left,right,reverse)
        require((value(result['lower']),value(result['product']),parse_stream(result['stream'],records,words,p))==expected[:3],'direct current-CRT oracle')
        require(result['left_valid']==all(c<m for m,c in left),'validity flag')
        require((bytes(l.cells),bytes(r.cells))==borrowed and l.head==r.head==1,'borrowed streams restored')
        require([(bytes(w.cells),w.head) for w in guards]==guard_state,'protected words and unrelated heads preserved')
        m,t=len(left),len(right);e=expected[3];v=sum(c<mod for mod,c in right)
        j=outer['divmod'];h=sum(outer[k] for k in PROVIDERS if k!='divmod')
        require(j==3*m+2*t+v+2*e,'exact J with both Euclidean divisions')
        h_cap=(6*p+3)*e+m*(10*p+7)+t*(8*p+6)
        require(h<=h_cap<12*(p+2)**3,'complete H count and cubic ceiling')
        require(e<=(m+t)*(2*p+1) and m+t<=p-2,'Euclid and record-count bounds')
        require(j<=(p-2)*(4*p+5),'complete J bound')
        require(sum(inclusive_actions.values())>sum(outer_actions.values()),'inclusive-sum double-counting control')
        require(j!=3*m+2*t+v+e,'omitted Euclidean qmod control')
        require(aliases['add']>0,'actual aliased doubling path')
        require(len(arena.live)==10,'eight borrowed and two returned words')
        before_close=meter();recording=True;arena.free_many(result['lower'],result['product']);recording=False
        close_actions=meter()-before_close
        require(close_actions==2*(5*p+8),'complete returned Word erasure bill')
        require(arena.live==set(range(8)),'caller retirement retains protected owners')
        require([(bytes(w.cells),w.head) for w in guards]==guard_state,'retirement preserves borrowed histories')
        require(all(w.head==1 and all(x==words.BLANK for x in w.cells[1:]) for w in arena.words[8:]),'all owned numerical histories blank')
        require(sum(outer_actions.values())==action_partition['inside'],'late output retirement remains outside providers')
        require(produced+close_actions-sum(outer_actions.values())==action_partition['outside'],'complete residual including output retirement')
        return {'P':p,'left':left,'right':right,'reverse':reverse,'E':e,'J':j,'H':h,'H_cap':h_cap,
                'outer_calls':dict(outer),'all_nested_calls':dict(all_calls),'aliases':dict(aliases),
                'producer_word_actions':produced,'removed_outer_actions':sum(outer_actions.values()),
                'incorrect_inclusive_actions':sum(inclusive_actions.values()),'retained_after_output_retirement':action_partition['outside'],
                'returned_output_retirement_actions':close_actions,'returned_values':list(expected[:2])}
    finally:
        for name,method in original_raw.items():setattr(words.Unsigned,name,method)
        for name,method in original_word.items():setattr(words.Word,name,method)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-root',type=Path,required=True);args=ap.parse_args()
    sources=locate(args.source_root.resolve());words=load('words',sources['r437-preparation-composition/predecessor4025/source/words.py'])
    records=load('independent_original_records',sources['r437-preparation-composition/predecessor4025/source/records.py'])
    fwd=sources['encoded-current-crt/producer.py'];inv=sources['encoded-crt-leaf-payload/frozen/inverse_producer.py']
    inventories=[raw_calls(fwd),raw_calls(inv)]
    require([r[1:] for r in inventories[0]]==[r[1:] for r in inventories[1]],'same exact raw source surfaces')
    producers=(load('independent_original_forward',fwd),load('independent_original_inverse',inv))
    fixtures=[(4,[(2,1)],[(3,2)]),(5,[(3,2)],[(5,4)]),
              (11,[(5,3),(7,2)],[(2,1),(3,1)]),(11,[(5,5),(7,6)],[(2,2),(3,3)]),
              (15,[(5,1),(7,2)],[(13,12),(8,7)]),(15,[(5,0),(7,0)],[(13,13),(8,9)]),
              (18,[(3,2),(5,4),(7,6)],[(11,10),(13,12)])]
    results=[one_case(words,records,producers[reverse],p,left,right,bool(reverse)) for p,left,right in fixtures for reverse in (0,1)]
    print(json.dumps({'status':'PASS_INDEPENDENT_CURRENT_ARITHMETIC_SOURCE_COST','source_sha256':PINS,
                     'source_raw_sites':inventories,'fixtures':results,'cases':len(results),
                     'total_outer_calls':sum(x['H']+x['J'] for x in results),
                     'scope':'Exact original source/count/action-partition review; no B12 graph or binder imported.'},indent=2,sort_keys=True))
if __name__=='__main__':main()
