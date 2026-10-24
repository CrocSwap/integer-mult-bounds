"""One local-symbol instruction per step. No runtime assembly/source callbacks."""
from program import ROLES,BLANK

def validate(code,entries):
    for pc,row in enumerate(code):
        op,*a=row
        if op=='test':
            if len(a)!=4 or a[0] not in ROLES or type(a[1]) is not int or not 0<=a[1]<=4:raise ValueError('test domain')
            targets=a[2:]
        elif op=='write':
            if len(a)!=2 or a[0] not in ROLES or type(a[1]) is not int or not 0<=a[1]<=4:raise ValueError('write domain')
            targets=[]
        elif op=='move':
            if len(a)!=2 or a[0] not in ROLES or type(a[1]) is not int or a[1] not in (-1,1):raise ValueError('move domain')
            targets=[]
        elif op=='jump':
            if len(a)!=1:raise ValueError('jump arity')
            targets=a
        elif op=='halt':
            if len(a)!=1 or a[0] not in ('initialized','returned','consumed','installed','closed','rejected'):raise ValueError('halt domain')
            targets=[]
        else:raise ValueError('nonliteral instruction')
        if op in ('write','move') and pc+1>=len(code):raise ValueError('fallthrough boundary')
        if any(type(t) is not int or not 0<=t<len(code) for t in targets):raise ValueError('target domain')
    if any(type(v) is not int or not 0<=v<len(code) for v in entries.values()):raise ValueError('entry')
    # Jumps are the only zero-cell instructions; their induced graph must be acyclic.
    longest=0
    for start,row in enumerate(code):
        if row[0]!='jump':continue
        seen=set();pc=start
        while code[pc][0]=='jump':
            if pc in seen:raise ValueError('zero-cell cycle')
            seen.add(pc);pc=code[pc][1]
        longest=max(longest,len(seen))
    return longest+1

def execute(code,tapes,heads,entry,max_steps=1000000000):
    pc=entry;steps=reads=writes=moves=0
    while steps<max_steps:
        row=code[pc];op=row[0];steps+=1
        if op=='test':
            _,r,s,y,n=row;h=heads[r];cells=tapes[r];v=cells[h] if h<len(cells) else BLANK
            reads+=1;pc=y if v==s else n
        elif op=='write':
            _,r,s=row;h=heads[r];cells=tapes[r]
            if h>=len(cells):cells.extend([BLANK]*(h+1-len(cells)))
            cells[h]=s;writes+=1;pc+=1
        elif op=='move':
            _,r,d=row;h=heads[r]+d
            if h<0:raise ValueError('left boundary')
            heads[r]=h;moves+=1;pc+=1
        elif op=='jump':pc=row[1]
        elif op=='halt':return {'status':row[1],'steps':steps,'reads':reads,'writes':writes,'moves':moves}
        else:raise ValueError('invalid opcode')
    raise ValueError('observer watchdog')
