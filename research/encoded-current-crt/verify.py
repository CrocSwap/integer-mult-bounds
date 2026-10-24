"""Independent source/current-state oracles and real encoded producer controls.

JoyboyBrian; substantial OpenAI Codex assistance. Apache-2.0.
All integer decoding and reference arithmetic below are observer-only.
"""
import argparse,ast,hashlib,json,math,sys,types
from pathlib import Path
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
def need(ok,message):
    if not ok:raise ValueError(message)
def load(name,path):
    m=types.ModuleType(name);m.__file__=str(path);sys.modules[name]=m
    exec(compile(path.read_bytes(),str(path),'exec'),m.__dict__);return m

def modules():
    for row in json.loads((P/'SOURCES.json').read_text())['files']:
        if row['usage']!='input':continue
        raw=(ROOT/row['path']).read_bytes()
        need(hashlib.sha256(raw).hexdigest()==row['sha256'],'source SHA256 drift')
        need(hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==row['git_blob'],'source Git blob drift')
    source=ROOT/'research/r437-preparation-composition/predecessor4025/source'
    w=load('words',source/'words.py');r=load('records',source/'records.py')
    return w,r,load('current_crt_producer',P/'producer.py'),load('current_crt_reference',ROOT/'research/unconditional-batched-crt/check_batched_crt.py')

def value(word):return sum(bit<<i for i,bit in enumerate(word.cells[1:-1]))
def encoded(arena,records,words,rows):
    out=records.Tape()
    for modulus,current in rows:
        out.append(records.ROOT)
        for number in(modulus,current):
            v=arena.literal(number);records.append_word(out,v);arena.free(v)
        out.append(records.RECORD_END)
    out.append(words.RIGHT);out.rewind();return out

def observe(stream,width,w,r):
    body=stream.cells;at=1;result=[]
    while body[at]!=w.RIGHT:
        need(body[at]==r.ROOT,'output tag');at+=1;row=[]
        for _ in range(2):
            bits=body[at:at+width];need(all(b in(0,1)for b in bits),'output binary digits')
            row.append(sum(bit<<i for i,bit in enumerate(bits)));at+=width
            need(body[at]==r.WORD_END,'output word terminator');at+=1
        need(body[at]==r.RECORD_END,'output record terminator');at+=1;result.append(row)
    return result

def original(left,right,ref,mode='correct'):
    moduli=[q for q,_ in left];values=[y for _,y in left]
    valid=all(y<q for q,y in left)
    lower=(ref.decode_group(values,moduli) if mode!='mixed_radix' else sum(y*math.prod(moduli[:i])for i,y in enumerate(values)))if valid else 0
    prefix=math.prod(moduli);result=[]
    for q,x in right:
        offset=lower*pow(prefix,-1,q)%q
        result.append([offset,ref.run_network(ref.benes(ref.rotation(1<<(q-1).bit_length(),q,offset)),x) if x<1<<(q-1).bit_length() else x])
        prefix*=q
    return lower,math.prod(moduli),result,valid

def case(w,r,p,ref,left_rows,right_rows,width=16,fault=None,expect_reject=None,mutate=None,dirty_count=8):
    arena=w.Arena(width,64);left=encoded(arena,r,w,left_rows);right=encoded(arena,r,w,right_rows)
    dirty=[arena.literal(17+i if width>=6 else 3)for i in range(dirty_count)]
    for i,word in enumerate(dirty):
        for _ in range(1+i%3):word.step(1)
    borrowed_dirty=[(bytes(word.cells),word.head)for word in dirty]
    template_before=(bytes(arena.template.cells),arena.template.head)
    protected=set(arena.live);backing=[];init=r.Tape.__init__
    def register(t):init(t);backing.append(t)
    r.Tape.__init__=register
    if mutate:mutate(left,right,w,r)
    observed_input=(bytes(left.cells),bytes(right.cells))
    old_inspect=w.Word.inspect;w.Word.inspect=lambda _:(_ for _ in()).throw(ValueError('runtime integer decode forbidden'))
    before=witness(arena)
    record_before={k:getattr(left.meter,k)+getattr(right.meter,k)for k in('reads','writes','moves')}
    try:
        try:out=p.produce(arena,left,right,w,r,fault=fault)
        except ValueError as error:
            if expect_reject is None:raise
            need(expect_reject in str(error),'named rejection '+str(error));out=None
        else:need(expect_reject is None,'invalid input accepted')
    finally:w.Word.inspect=old_inspect;r.Tape.__init__=init
    need((bytes(left.cells),bytes(right.cells))==observed_input and left.head==right.head==1,'borrowed descriptor bytes/heads')
    need([(bytes(word.cells),word.head)for word in dirty]==borrowed_dirty,'unrelated dirty numerical bytes/head')
    need((bytes(arena.template.cells),arena.template.head)==template_before,'borrowed initialization template restored')
    peak=arena.meter.peak_live
    traffic={k:getattr(arena.meter,k)-before[k]for k in('reads','writes','moves')}
    record_traffic={k:getattr(left.meter,k)+getattr(right.meter,k)-record_before[k]+sum(getattr(t.meter,k)for t in backing)for k in('reads','writes','moves')}
    need(sum(traffic.values())+sum(record_traffic.values())<=2**20*(width+2)**4,'proved local source-tape envelope')
    row=dict(left=left_rows,right=right_rows,width=width,peak_live=peak,numerical_traffic=traffic,record_traffic=record_traffic)
    if out is not None:
        actual=(value(out['lower']),value(out['product']),observe(out['stream'],width,w,r),out['left_valid'])
        expected=original(left_rows,right_rows,ref)
        need(actual==expected,'actual current-child/source padded rotation endpoint')
        row.update(lower=actual[0],product=actual[1],outputs=actual[2],left_valid=actual[3])
        need(set(arena.live)==protected|{out['lower'].slot,out['product'].slot},'only declared owned outputs remain')
        arena.free_many(out['lower'],out['product']);out['stream'].clear()
    else:row['rejection']=expect_reject
    need(set(arena.live)==protected,'numeric ownership restored')
    need(all(word.slot in protected or all(x==w.BLANK for x in word.cells[1:])for word in arena.words),'visited numerical backing erased')
    need(all(t.head==1 and all(x==w.BLANK for x in t.cells[1:])for t in backing),'all owned output backing erased')
    need(peak<=32,'constructive temporary inventory')
    arena.free_many(*dirty);left.clear();right.clear()
    need(not arena.live,'fixture cleanup')
    return row

def witness(arena):return {k:getattr(arena.meter,k)for k in('reads','writes','moves')}

def arithmetic(w,r,p):
    arena=w.Arena(7,64);a=p.Arithmetic(arena,w);cases=0;inverses=0
    for modulus in range(2,16):
        m=arena.literal(modulus);a.admit(m)
        for x in range(modulus):
            left=arena.literal(x)
            inv=a.inverse(left,m)
            need((inv is not None)==(math.gcd(x,modulus)==1),'all unit/nonunit inverses')
            if inv is not None:need(value(inv)*x%modulus==1,'encoded inverse value');arena.free(inv)
            inverses+=1
            for y in range(modulus):
                right=arena.literal(y)
                for function,expected in [(a.add,(x+y)%modulus),(a.subtract,(x-y)%modulus),(a.multiply,x*y%modulus)]:
                    result=function(left,right,m);need(value(result)==expected,'new loose-width modular arithmetic');arena.free(result)
                arena.free(right);cases+=1
            arena.free(left)
        arena.free(m)
    original_modulus=arena.literal(5)
    try:w.Ring(original_modulus)
    except ValueError:pass
    else:raise ValueError('frozen Ring canonical-width gate unexpectedly changed')
    a.admit(original_modulus);arena.free_many(original_modulus,a.one)
    need(not arena.live,'arithmetic cleanup')
    return dict(pair_cases=cases,inverse_cases=inverses,original_ring_rejects_wide_modulus=True,new_interface_admits_it=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--write-result',action='store_true');args=ap.parse_args();w,r,p,ref=modules()
    tree=ast.parse((P/'producer.py').read_text())
    need(not any(isinstance(n,ast.Attribute)and n.attr in('cells','inspect','bit_length','times_small')for n in ast.walk(tree)),'no runtime decoded-word/backing oracle')
    need(all(isinstance(n.args[0],ast.Constant)and n.args[0].value==1 for n in ast.walk(tree)if isinstance(n,ast.Call)and isinstance(n.func,ast.Attribute)and n.func.attr=='literal'),'only compiled literal one')
    checks=arithmetic(w,r,p);rows=[]
    mixed=load('actual_mixed_current_crt',ROOT/'research/crt-mixed-width-caller/verify.py')
    rows.append(case(w,r,p,ref,[(5,1),(7,5)],[(13,4),(17,16)]))
    correct=original([(5,1),(7,5)],[(13,4)],ref);wrong=original([(5,1),(7,5)],[(13,4)],ref,'mixed_radix')
    need(correct[0]==11 and correct[2][0][0]==7 and wrong[0]==26 and wrong[2][0][0]==0,'actual transformed-child discriminator')
    for x in range(8):
        for y in range(8):rows.append(case(w,r,p,ref,[(5,x),(7,y)],[(13,15),(17,7)]))
    # Actual complete balanced-root connection: transform both children first.
    full=[]
    for values in [(1,2,3,4),(4,6,12,16),(5,2,3,20),(7,7,15,31)]:
        mods=(5,7,13,17)
        current=ref.balanced(values[:2],mods[:2])+ref.balanced(values[2:],mods[2:])
        row=case(w,r,p,ref,list(zip(mods[:2],current[:2])),list(zip(mods[2:],current[2:])))
        need(tuple(z for c,z in row['outputs'])==ref.balanced(values,mods)[2:],'whole original balanced caller root')
        full.append(row)
    varied=[case(w,r,p,ref,[(2,1)],[(3,2)],width=4),case(w,r,p,ref,[(3,2)],[(5,4),(7,6)],width=8),case(w,r,p,ref,[(3,1),(5,2)],[(7,6),(11,10)],width=12),case(w,r,p,ref,[(3,1),(5,3),(7,2)],[(11,4),(13,5),(17,6)],width=20),case(w,r,p,ref,[(257,201),(263,101)],[(269,202)],width=32)]
    mixed_roots=[]
    for initial in[(1,2,3,4),(4,6,12,16),(5,2,3,20),(15,15,15,31)]:
        mods=(5,7,13,17);caller=mixed.Caller(mods,(4,4,4,5),5,ref);state=caller.state(initial);node_rows=[]
        for level in(1,2):
            offsets=caller.offsets(state,level);predicted=list(state);size=1<<level
            for start in range(0,4,size):
                middle=start+size//2;stop=start+size
                row=case(w,r,p,ref,list(zip(mods[start:middle],state[start:middle])),list(zip(mods[middle:stop],state[middle:stop])))
                need([z[0]for z in row['outputs']]==[offsets[i]for i in range(middle,stop)],'literal mixed-width caller offset port')
                predicted[middle:stop]=[z[1]for z in row['outputs']];node_rows.append(row)
            for global_row in range(2*caller.ell-1):state=caller.apply(state,caller.row(state,level,global_row,offsets))
            need(state==tuple(predicted),'original mixed-width row consumer vs encoded whole-node endpoint')
        need(state==caller.run(initial),'complete original mixed-width caller connection')
        mixed_roots.append(dict(initial=initial,endpoint=state,nodes=node_rows,declared_widths=[4,4,4,5]))
    rejected=[case(w,r,p,ref,[(5,1),(5,2)],[(13,4)],expect_reject='pairwise coprime'),case(w,r,p,ref,[(5,1)],[(5,2)],expect_reject='pairwise coprime'),case(w,r,p,ref,[(1,0)],[(13,4)],expect_reject='modulus exceeds one'),case(w,r,p,ref,[(5,1),(7,5)],[(13,4)],width=8,expect_reject='product'),case(w,r,p,ref,[],[(13,4)],expect_reject='nonempty'),case(w,r,p,ref,[(5,1)],[],expect_reject='nonempty')]
    controls=[]
    for fault in('treat_current_as_original','omit_right_prefix','rotate_padding'):
        try:case(w,r,p,ref,[(5,1),(7,5)],[(13,15),(17,7)],fault=fault)
        except ValueError:controls.append(fault)
        else:raise ValueError('behavior fault escaped '+fault)
    malformed=lambda left,right,w,r:left.cells.__setitem__(1,r.STEP)
    rejected.append(case(w,r,p,ref,[(5,1)],[(13,4)],mutate=malformed,expect_reject='paired descriptor tag'))
    rejected.append(case(w,r,p,ref,[(129,1)],[(3,2)],width=8,expect_reject='modulus high-bit'))
    rejected.append(case(w,r,p,ref,[(5,1)],[(13,4)],dirty_count=9,expect_reject='entry inventory'))
    short_word=lambda left,right,w,r:left.cells.__setitem__(2,r.WORD_END)
    rejected.append(case(w,r,p,ref,[(5,1)],[(13,4)],mutate=short_word,expect_reject='complete encoded word'))
    late_bad_tag=lambda left,right,w,r:right.cells.__setitem__(37,r.STEP)
    rejected.append(case(w,r,p,ref,[(5,1),(7,5)],[(13,4),(17,7)],mutate=late_bad_tag,expect_reject='paired descriptor tag'))
    result=dict(status='PASS_ENCODED_CURRENT_CRT',arithmetic=checks,current_child_discriminator=dict(encoded_current=[1,5],correct_lower=11,correct_offset=7,wrong_original_digit_lower=26,wrong_original_digit_offset=0),complete_cases=rows,actual_balanced_roots=full,varied_groups_and_widths=varied,actual_mixed_width_callers=mixed_roots,rejections=rejected,behavior_controls=controls,producer_sha256=hashlib.sha256((P/'producer.py').read_bytes()).hexdigest())
    if args.write_result:(P/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(json.dumps(result,sort_keys=True)==json.dumps(json.loads((P/'RESULT.json').read_text()),sort_keys=True),'typed frozen result drift')
    print(json.dumps(dict(status=result['status'],arithmetic=checks,complete_cases=len(rows),balanced_roots=len(full),mixed_width_callers=len(mixed_roots),varied_widths=[x['width']for x in varied],rejections=len(rejected),controls=controls)))

if __name__=='__main__':main()
