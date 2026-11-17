"""Dynamic rational/integer grid and literal forward endpoint leaf.

The integer engine is the #7480 retained audit_native.py, already authenticated
by the source archive loader. Its two literal height constants are replaced by
freshly derived per-word values with unique-anchor checks. No replay at import.
"""
import hashlib, json, sys
from fractions import Fraction as Q
from types import ModuleType

def need(ok,msg):
    if not ok:raise ValueError(msg)
def normalized(x):return json.loads(json.dumps(x,default=str))
def audit_engine(path,frac,name):
    need(type(frac) is int and 0<=frac<=256,'fraction bit bound')
    raw=path.read_bytes();src=raw.decode();changes=[]
    for old,new in (('2**24',f'2**{frac}'),('25 - (abs(value) & -abs(value)).bit_length()',f'{frac+1} - (abs(value) & -abs(value)).bit_length()')):
        need(src.count(old)==1,'integer audit adaptation anchor '+old)
        src=src.replace(old,new);changes.append({'before':old,'after':new,'count':1})
    obj=ModuleType(name);obj.__file__=str(path);sys.modules[name]=obj
    exec(compile(src,str(path),'exec'),obj.__dict__)
    return obj,{'source_sha256':hashlib.sha256(raw).hexdigest(),'adapted_sha256':hashlib.sha256(src.encode()).hexdigest(),'edits':changes}

def endpoint(word,rows,odd,frac):
    n=word['public'];unit=odd*2**frac
    target=[{r:Q(1)} if r<n else {} for r in range(n+word['owned_fields'])]
    hosted=word['hosted'];D=set(hosted['Dports'])
    for i,x in enumerate(word['live']):
        y=x+112
        if i in D:target[y][x]=Q(1)
        else:target[x][y]=Q(-1);target[y]={x:Q(1,2),y:Q(1,2)}
    for x,y in zip(hosted['X2'],hosted['Y2']):target[x][y]=Q(-1)
    need(len(rows)==len(target) and all(row=={k:v*unit for k,v in want.items()} for row,want in zip(rows,target)),'whole forward endpoint')
    return {'rows':len(rows),'coefficient_positions':len(rows)**2,'odd_scale':odd,'fractional_bits':frac}

def one(word,derive,audit_path,label):
    derived,_=derive(word);odd=derived['odd_scale'];frac=derived['fractional_bits']
    need(type(odd) is int and odd>0 and odd%2==1,'derived odd grid')
    engine,adapter=audit_engine(audit_path,frac,'e4_grid_'+label)
    forward,grid=engine.replay(word,list(enumerate(word['program'])),set(),grid=odd)
    receipt=endpoint(word,forward[0],odd,frac)
    receipt['copy_guards_checked']=len(forward[3]);receipt['owned_clear_rows_checked']=len(forward[2])
    need(grid['odd_grid_lcm']==odd and grid['dyadic_height']==frac and grid['maximum_scaled_mass']==derived['scaled_maximum_mass'],'independent rational/integer grid agreement')
    need(receipt['copy_guards_checked']==1 and receipt['owned_clear_rows_checked']==grid['owned_lifetimes'],'copy and clear inventory')
    return normalized({'derived_grid':derived,'grid':grid,'forward':receipt,'adapter':adapter})
