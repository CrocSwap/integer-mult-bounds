"""Independent sparse Graph CPU and direct XOR-address oracle for arbitrary fixed affine translation."""
from pathlib import Path
from fractions import Fraction
import hashlib,json,sys,time
P=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).with_name('source').resolve()
sys.path.insert(0,str(P))
import adapter as a
def require(ok,why):
    if not ok:raise ValueError(why)
def word(x,w):return format(x%(1<<w),f'0{w}b')
def gamma(x):
    b=bin(x)[2:];return '0'*(len(b)-1)+b

def interpret(graph,fields,stages,budget=150000000):
    origins=[-31+7*t for t in range(a.TAPES)];heads=origins.copy()
    text=['^'+'|'.join(fields)+'|$']+['^']*(a.TAPES-1)
    tapes=[{o+i:c for i,c in enumerate(s)} for o,s in zip(origins,text)]
    for t,o in enumerate(origins):tapes[t][o-4]='1';tapes[t][o+1000000]='0'
    low=origins.copy();high=[o+len(s)-1 for o,s in zip(origins,text)];high[-1]+=100003
    entry=sum(y-x+1 for x,y in zip(low,high));pc=graph.start;steps=writes=early=0
    returned=False;checkpoints={}
    while pc!='HALT':
        if pc==stages['primitive_return']:returned=True
        if pc in (stages['core_entry'],stages['core_return'],stages['primitive_return']):
            checkpoints[pc]=dict(steps=steps,home_writes=writes)
        found=None
        for rule in graph.rules[pc]:
            if all(tapes[t].get(heads[t],'_')==c for t,c in rule.tests):
                require(found is None,'ambiguous transition');found=rule
        require(found is not None,'literal rejection in valid fresh fixture')
        for t,c in found.writes:
            require(heads[t]!=origins[t] or c=='^','origin changed')
            if c=='_':tapes[t].pop(heads[t],None)
            else:tapes[t][heads[t]]=c
            if t==0:writes+=1;early+=not returned
        for t,d in found.moves:
            require(d in (-1,0,1),'nonunit head');heads[t]+=d
            low[t]=min(low[t],heads[t]);high[t]=max(high[t],heads[t])
        pc=found.target;steps+=1;require(steps<=budget,'bounded sparse CPU exhausted')
    require(heads==origins,'head restoration')
    for t,o in enumerate(origins):
        require(tapes[t].get(o)=='^' and tapes[t].get(o-4)=='1' and tapes[t].get(o+1000000)=='0','origin/exterior')
        if t:require(set(tapes[t])=={o,o-4,o+1000000},'private retirement')
    raw=''.join(tapes[0].get(origins[0]+i,'_') for i in range(len(text[0])))
    require(raw.startswith('^') and raw.endswith('|$'),'HOME framing')
    return raw[1:-2].split('|'),dict(steps=steps,HOME_writes=writes,early_HOME_writes=early,
        entry_head_history=entry,final_head_history=sum(y-x+1 for x,y in zip(low,high)),checkpoints=checkpoints)



def body_and_image(mask,outer,spectators,coefficients,width):
    physical_mask=sum(((mask>>slot)&1)<<(8-slot) for slot in range(9))
    blocks={}
    for p in range(outer):
        for address in range(512):
            bits=[]
            for spectator in range(spectators):
                for coefficient in range(coefficients):
                    for component in range(2):
                        value=((address^(address>>3)^(address>>6))+3*p+5*spectator+2*coefficient+3*component)% (1<<width)
                        bits.append(word(value,width))
            blocks[p,address]=''.join(bits)
    original=''.join(blocks[p,address] for p in range(outer) for address in range(512))
    expected=''.join(blocks[p,address^physical_mask] for p in range(outer) for address in range(512))
    wrong_endian=''.join(blocks[p,address^mask] for p in range(outer) for address in range(512))
    return original,expected,wrong_endian,physical_mask

def check_embedding(graph,stages,core,offset):
    labels=[s for s in graph.rules if s.startswith('AFFINE_B'+str(offset)+'.')]
    require(len(labels)==len(core),'complete affine state count')
    for i,(op,*args) in enumerate(core):
        nxt=labels[i+1] if i+1<len(labels) else stages['core_return']
        if op=='read':expected=[a.D.Rule(((a.CORE_BASE+args[0],c),),(),(),labels[j]) for c,j in args[1].items()]
        elif op=='write':expected=[a.D.Rule((),((a.CORE_BASE+args[0],args[1]),),(),nxt)]
        elif op=='move':expected=[a.D.Rule((),(),((a.CORE_BASE+args[0],args[1]),),nxt)]
        elif op=='goto':expected=[a.D.Rule((),(),(),labels[args[0]])]
        else:
            require(op=='halt','literal affine operation')
            expected=[a.D.Rule((),(),(),stages['core_return'])]
        require(graph.rules[labels[i]]==expected,'exact affine core embedding')

def main():
    offset=(1<<8)|(1<<5)|(1<<2)
    graph,stages=a.compile_home(offset);core=a.core(offset)
    check_embedding(graph,stages,core,offset)
    outer=spectators=coefficients=2;width=3;cutoff=(1<<129)+1
    body,expected_body,wrong_body,physical_mask=body_and_image(offset,outer,spectators,coefficients,width)
    require(expected_body!=body and expected_body!=wrong_body,'nontrivial orientation fixture')
    omitted=body_and_image(offset^(1<<8),outer,spectators,coefficients,width)[1]
    require(omitted!=expected_body,'omitted far-slot fixture')
    header=''.join(gamma(n) for n in (1,coefficients,outer,spectators,width,cutoff))
    packet=header+body;expected=header+expected_body
    parked=('001101011'*((len(packet)+8)//9))[:len(packet)]
    actual,receipt=interpret(graph,(parked,packet),stages)
    require(actual==[parked,expected],'complete address-XOR output and parked owner')
    require(receipt['HOME_writes']==len(packet) and not receipt['early_HOME_writes'],'one complete post-return HOME scatter')
    V=len(body);E=len(header);F=V+E
    require(V==2*outer*spectators*coefficients*512*width,'complete external spectator volume')
    require(receipt['steps']<=128*(F+1)+(1<<20)*(V+E+1),'stated complete affine time envelope')
    require(receipt['final_head_history']<=receipt['entry_head_history']+320*(F+1),'stated historical envelope')
    print(json.dumps({'status':'PASS_ROOT_AFFINE_HOME','offset':offset,'physical_stream_xor':physical_mask,
        'shape':{'f':1,'coefficients':coefficients,'outer':outer,'spectators':spectators,'width':width,'cutoff_bit_length':cutoff.bit_length()},
        'V':V,'E':E,'F':F,'states':len(graph.rules),'tapes':a.TAPES,'core_instructions':len(core),
        'core_sha256':hashlib.sha256(repr(core).encode()).hexdigest(),'receipt':receipt,
        'input_sha256':hashlib.sha256(packet.encode()).hexdigest(),'output_sha256':hashlib.sha256(expected.encode()).hexdigest(),
        'controls':['host mask used without slot-endian conversion changes expected output','omitted far-slot offset changes expected output'],
        'oracle':'Independent direct address XOR on complete P/native/S/coefficient/component records; no emitted conjugator or author oracle imported',
        'scope':'One full f1 shifted-origin call with external multiplicities, minimum signed bit patterns and a130-bit unused cutoff; all-f theorem and complete cost proof remain separate.'},indent=2,sort_keys=True))

if __name__=='__main__':main()
