"""Final rank-one control with supplied cutoff and explicit remainder hooks.

The credited frozen Builder/interpreter performs literal local tape steps.
No payload or external cutoff producer is included. Apache-2.0.
"""
from controller_reference import Builder,Machine,Tape,initial_tapes,BLANK,ONE,MARK,WIDTH,CHILD,STACK
CUTOFF=3

def remainder(a,m,prefix,event,next_state):
    a.mark(prefix);a.op('goto',prefix+'r0')
    for r in range(m):
        a.mark(prefix+f'r{r}');a.op('read',WIDTH,{ONE:prefix+f'b{r}',BLANK:prefix+f'e{r}'})
        a.mark(prefix+f'b{r}');a.op('move',WIDTH,1);a.op('goto',prefix+f'r{(r+1)%m}')
        a.mark(prefix+f'e{r}');a.rewind(WIDTH,(ONE,));a.op('emit',event+str(r));a.op('goto',next_state)

def compile_selected(m,sites):
    if type(m) is not int or m<2 or type(sites) is not int or sites<1:raise ValueError('invalid fixed template')
    tags=tuple(f't{i}' for i in range(sites));a=Builder();a.mark('enter');a.op('read',WIDTH,{ONE:'probe0'})
    for k in range(m):
        a.mark(f'probe{k}');a.op('read',WIDTH,{ONE:f'advance{k}',BLANK:f'leaf{k}'})
        a.mark(f'advance{k}');a.op('move',WIDTH,1);a.op('goto',f'probe{k+1}' if k+1<m else 'width_at_least_m')
        a.mark(f'leaf{k}');a.rewind(WIDTH,(ONE,));a.op('emit','L');a.op('goto','complete')
    a.mark('width_at_least_m');a.rewind(WIDTH,(ONE,))
    a.mark('compare');a.op('read',CUTOFF,{BLANK:'cutoff_reached',ONE:'width_probe'})
    a.mark('width_probe');a.op('read',WIDTH,{BLANK:'shorter_than_cutoff',ONE:'compare_bit'})
    a.mark('compare_bit');a.op('move',CUTOFF,1);a.op('move',WIDTH,1);a.op('goto','compare')
    for label,event,dest in [('cutoff_reached','E','before'),('shorter_than_cutoff','L','complete')]:
        a.mark(label);a.rewind(WIDTH,(ONE,));a.rewind(CUTOFF,(ONE,));a.op('emit',event);a.op('goto',dest)
    remainder(a,m,'before','B','child0')
    for i in range(sites):
        a.mark(f'child{i}');a.op('goto',f'build{i}_0')
        for r in range(m):
            a.mark(f'build{i}_{r}');a.op('read',WIDTH,{ONE:f'build{i}_{r}bit',BLANK:f'built{i}'})
            a.mark(f'build{i}_{r}bit')
            if r==m-1:a.op('write',CHILD,ONE);a.op('move',CHILD,1)
            a.op('move',WIDTH,1);a.op('goto',f'build{i}_{(r+1)%m}')
        a.mark(f'built{i}');a.rewind(WIDTH,(ONE,));a.rewind(CHILD,(ONE,))
        a.mark(f'push{i}');a.op('read',WIDTH,{ONE:f'push{i}bit',BLANK:f'pushed{i}'})
        a.mark(f'push{i}bit');a.op('write',STACK,ONE);a.op('write',WIDTH,BLANK);a.op('move',WIDTH,1);a.op('move',STACK,1);a.op('goto',f'push{i}')
        a.mark(f'pushed{i}');a.op('write',STACK,tags[i]);a.op('move',STACK,1);a.rewind(WIDTH,(BLANK,))
        a.mark(f'transfer{i}');a.op('read',CHILD,{ONE:f'transfer{i}bit',BLANK:f'transferred{i}'})
        a.mark(f'transfer{i}bit');a.op('write',WIDTH,ONE);a.op('write',CHILD,BLANK);a.op('move',WIDTH,1);a.op('move',CHILD,1);a.op('goto',f'transfer{i}')
        a.mark(f'transferred{i}');a.rewind(WIDTH,(ONE,));a.rewind(CHILD,(BLANK,));a.op('emit',f'D{i}');a.op('goto','enter')
    remainder(a,m,'after','A','complete')
    a.mark('complete');a.op('emit','X');a.op('move',STACK,-1);a.op('read',STACK,{MARK:'root_done',**{t:f'return{i}' for i,t in enumerate(tags)}})
    a.mark('root_done');a.op('move',STACK,1);a.op('halt')
    for i in range(sites):
        a.mark(f'return{i}');a.op('write',STACK,BLANK);a.op('move',STACK,-1)
        a.mark(f'erase{i}');a.op('read',WIDTH,{ONE:f'erase{i}bit',BLANK:f'erased{i}'})
        a.mark(f'erase{i}bit');a.op('write',WIDTH,BLANK);a.op('move',WIDTH,1);a.op('goto',f'erase{i}')
        a.mark(f'erased{i}');a.rewind(WIDTH,(BLANK,));a.mark(f'pop{i}')
        a.op('read',STACK,{ONE:f'pop{i}bit',MARK:f'popped{i}',**{t:f'popped{i}' for t in tags}})
        a.mark(f'pop{i}bit');a.op('write',WIDTH,ONE);a.op('write',STACK,BLANK);a.op('move',WIDTH,1);a.op('move',STACK,-1);a.op('goto',f'pop{i}')
        a.mark(f'popped{i}');a.op('move',STACK,1);a.rewind(WIDTH,(ONE,));a.op('emit',f'U{i}');a.op('goto',f'child{i+1}' if i+1<sites else 'after')
    return a.finish((BLANK,'0',ONE,MARK,*tags))

def inputs(width,cutoff,origins=(0,0,0,0)):
    if type(cutoff) is not int or cutoff<1:raise ValueError('positive supplied cutoff')
    t=initial_tapes(width,origins[:3]);o=origins[3];t.append(Tape({o-1:MARK,**{o+i:ONE for i in range(cutoff)}},o));return t
