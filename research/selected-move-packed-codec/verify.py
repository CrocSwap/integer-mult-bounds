"""Read-only exact checks; all decoded geometry below is oracle/fixture only."""
from pathlib import Path
from hashlib import sha1, sha256
import ast
import json
import importlib.util
import sys

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
spec=importlib.util.spec_from_file_location('packed_codec_machine',HERE/'machine.py')
m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m
exec(compile((HERE/'machine.py').read_bytes(),str(HERE/'machine.py'),'exec'),m.__dict__)


def need(ok,message):
    if not ok:raise ValueError(message)


def old_header(values):
    result=[]
    for name in m.SCHEMA:
        bits=list(map(int,bin(values[name])[2:][::-1]))
        result.extend([1]*len(bits)+[0]+bits)
    return result


def gamma(values):
    return [int(b) for n in values for b in '0'*(n.bit_length()-1)+bin(n)[2:]]


def old_data(values,b):
    result=[]
    for value in values:
        for bit in range(b):result.extend((0,0,(value>>bit)&1))
        result.extend((0,1,0))
    return result


def packed_data(values,b):
    return [value>>bit&1 for value in values for bit in range(b-1,-1,-1)]


def fixtures(a=9,u=0,K=1,rho=0,f=1,rows=1,r=1,b=2,cutoff=1):
    h=dict.fromkeys(m.SCHEMA,0)
    h.update(outer=1,rows=rows,row_bits=(1<<a)*6*r*(b+1),within_bits=a,
             record_bits=6*r*(b+1),f=f,K=K,rho=rho,active_start=u,cutoff=cutoff,
             G=1,H=1,back_start=a-1,selected_axes=9*f,d=9*f)
    values=[(j*13+(j>>2)*7+3)&((1<<b)-1) for j in range(rows*(1<<a)*2*r)]
    return h,values


def direct_indices(a,u,K,rho,g):
    selected=[u+k*K+rho for k in range(g)]
    order=list(range(u))+selected+[j for j in range(u,a) if j not in selected]
    need(sorted(order)==list(range(a)),'complete oracle permutation')
    result=[]
    for new in range(1<<a):
        old=0
        for j,position in enumerate(order):old|=((new>>(a-1-j))&1)<<(a-1-position)
        result.append(old)
    return result


def oracle_pack(values,h,r,b):
    a,u,K,rho,f=(h[k] for k in ('within_bits','active_start','K','rho','f'))
    order=direct_indices(a,u,K,rho,9*f); out=[]
    for row in range(h['outer']*h['rows']):
        for old in order:
            start=(row*(1<<a)+old)*2*r; out.extend(values[start:start+2*r])
    return out


def word(t,origin=1):
    end=origin
    while end<len(t.cells) and t.cells[end]!=m.BLANK:end+=1
    return t.cells[origin:end]


def new_tapes(data,header):
    origins=[1+(i%5) for i in range(len(m.NAMES))]
    tapes=[m.Tape.supplied(origin=o) for o in origins]
    tapes[0]=m.Tape.supplied(data,origins[0]);tapes[1]=m.Tape.supplied(header,origins[1])
    return tapes,origins


def complete_case(program,labels,params,change=False):
    h,values=fixtures(**params);b=params.get('b',2);r=params.get('r',1)
    data=old_data(values,b);header=old_header(h);tapes,origins=new_tapes(data,header)
    cpu=m.CPU(program,tapes);need(cpu.run()=='PACKED','complete entrance')
    packed=oracle_pack(values,h,r,b)
    need(word(tapes[m.PORT['PACK']],origins[m.PORT['PACK']])==packed_data(packed,b),'direct-index full packed image')
    P=h['outer']*h['rows']*(1<<h['active_start']);S=1<<(h['within_bits']-h['active_start']-9*h['f'])
    expected_header=gamma([h['f'],r,P,S,b,h['cutoff']])
    need(word(tapes[m.PORT['GAMMA']],origins[m.PORT['GAMMA']])==expected_header,'all six Gamma values')
    need(tapes[0].writes==0 and word(tapes[0],origins[0])==data,'protected old source')
    need(word(tapes[1],origins[1])==header and tapes[1].writes==0,'immutable old descriptor')
    need(tapes[0].head==origins[0] and tapes[1].head==origins[1],'public entry head returns')
    for name in ('PACK','GAMMA'):need(tapes[m.PORT[name]].head==origins[m.PORT[name]],'provider head origins')
    if change:
        # A same-width service fixture, NOT an executed native C operator.
        mask=(1<<b)-1; packed=[x^mask for x in packed]; values=[x^mask for x in values]
        t=tapes[m.PORT['PACK']];o=origins[m.PORT['PACK']]
        t.cells[o:o+len(packed)*b]=packed_data(packed,b)
    need(cpu.run(labels['EXIT'],limit=300_000_000)=='DONE','complete inverse return')
    need(word(tapes[0],origins[0])==old_data(values,b),'independent old-format return image')
    need(word(tapes[1],origins[1])==header,'descriptor returned exactly')
    for i,t in enumerate(tapes):
        need(t.head==origins[i] and t.low>=origins[i]-1,'every relative origin and left exterior')
        need(t.cells[origins[i]-1]==m.LEFT,'left guard preserved')
        if i>=2:need(all(v==m.BLANK for v in t.cells[origins[i]:]),'complete private retirement')
    V=len(data);E=len(header);g=9*h['f']
    need(cpu.steps<=2**20*((g+1)*V+E+1),'stated conservative complete time envelope')
    need(tapes[m.PORT['PACK']].writes>=4*g*len(packed)*b,'full-pass PACK-write lower bound')
    backing=sum(max(0,t.high-origins[i]) for i,t in enumerate(tapes) if i>=2)
    need(backing<=64*(V+E+1),'complete incremental history envelope')
    return {'geometry':params,'old_bits':V,'packed_bits':len(packed)*b,'header_bits':E,
            'transitions':cpu.steps,'packed_bank_writes':tapes[m.PORT['PACK']].writes,
            'incremental_history_cells':backing,'changed_service_fixture':change}


def shuffle_checks():
    b=m.Builder();b.label('FORWARD');b.shuffle();b.halt('PACKED');b.label('REVERSE');b.shuffle(True);b.halt('DONE')
    code,labels=b.finish();receipts=[]
    cases=[(4,0,1,0,3,1,3),(5,1,2,1,2,2,5),(8,1,2,1,3,3,2),(9,0,3,2,3,2,1),(7,2,1,0,4,2,7)]
    wrong_position_detected=False;global_partition_detected=False
    for a,u,K,rho,g,rows,L in cases:
        values=[(j*11+(j>>3)*5+1)&1 for j in range(rows*(1<<a)*L)]
        tapes=[m.Tape.supplied() for _ in m.NAMES]; tapes[m.PORT['PACK']]=m.Tape.supplied(values)
        guides={'G':g,'K':K,'KM1':K-1,'PREFIX':rows*(1<<u),'HALF':L*(1<<(a-u-1)),
                'RUN':L*(1<<(a-u-rho-1)),'CHUNKS':1<<rho}
        for name,n in guides.items():tapes[m.PORT[name]]=m.Tape.supplied([1]*n)
        cpu=m.CPU(code,tapes);need(cpu.run()=='PACKED','strided forward subprogram')
        perm=direct_indices(a,u,K,rho,g);expected=[]
        for row in range(rows):
            for old in perm:expected.extend(values[(row*(1<<a)+old)*L:(row*(1<<a)+old+1)*L])
        got=word(tapes[m.PORT['PACK']]);need(got==expected,'independent strided direct-index oracle')
        if rho:
            badperm=direct_indices(a,u,K,0,g);bad=[]
            for row in range(rows):
                for old in badperm:bad.extend(values[(row*(1<<a)+old)*L:(row*(1<<a)+old+1)*L])
            wrong_position_detected|=bad!=got
        if u:
            badperm=direct_indices(a,0,K,rho,g);bad=[]
            for row in range(rows):
                for old in badperm:bad.extend(values[(row*(1<<a)+old)*L:(row*(1<<a)+old+1)*L])
            global_partition_detected|=bad!=got
        need(cpu.run(labels['REVERSE'])=='DONE' and word(tapes[m.PORT['PACK']])==values,'strided inverse subprogram')
        for name in ('ZERO','ONE','OUT','TMP'):
            need(tapes[m.PORT[name]].head==1 and not word(tapes[m.PORT[name]]),'subprogram scratch retirement')
        receipts.append({'a':a,'u':u,'K':K,'rho':rho,'selected_bits':g,'rows':rows,'record_bits':L,'transitions':cpu.steps})
    need(wrong_position_detected,'wrong rho control discriminates')
    need(global_partition_detected,'global instead of per-prefix partition control discriminates')
    return receipts


def rejecting_controls(code):
    h,values=fixtures();data=old_data(values,2);header=old_header(h);out=[]
    fixtures_bad=[('short-last-code',data[:-1],header),('extra-field-bit',data+[0],header),
                  ('bad-first-code',[1]+data[1:],header),('truncated-header',data,header[:-1]),
                  ('extra-header-bit',data,header+[0])]
    for name,key,value in [('wrong-row-size','row_bits',h['row_bits']-1),('nonintegral-r','record_bits',19),
                            ('rho-outside-K','rho',1),('selected-bits-outside-row','within_bits',8),('zero-f','f',0)]:
        hh=dict(h);hh[key]=value;fixtures_bad.append((name,data,old_header(hh)))
    for name,d,hh in fixtures_bad:
        tapes,origins=new_tapes(d,hh);cpu=m.CPU(code,tapes)
        need(cpu.run()=='REJECT',name+' must reject')
        need(tapes[0].writes==0 and word(tapes[0],origins[0])==d,'rejection preserves original source')
        out.append(name)
    tapes,_=new_tapes(data,header);tapes[-1]=tapes[0]
    try:m.CPU(code,tapes)
    except ValueError:out.append('binding-object-alias')
    else:raise ValueError('object alias accepted')
    packed_len=512*4
    need(len(data)>packed_len and data[packed_len] in (0,1),'header-only old DATA fails exact packed blank frontier')
    out.append('header-only-frontier')
    need(packed_data([1],2)!=[1,0],'unreversed component control')
    out.append('component-orientation')
    return out


def authenticate():
    manifest=HERE/'SOURCE-PINS.json'
    need(manifest.is_file(),'source manifest present')
    pins=json.loads(manifest.read_text());count=0
    def check(raw,item):
        need(sha256(raw).hexdigest()==item['sha256']
             and sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()==item['git_blob'],
             'source authentication '+item['local_path'])
    for item in pins['retained']:
        raw=(HERE/item['local_path']).read_bytes();check(raw,item);count+=1
        try:check(raw+b'\n',item)
        except ValueError:pass
        else:raise ValueError('source mutation accepted')
    module=ast.parse((HERE/'inputs/old-header-provider.py').read_text())
    schema=next(ast.literal_eval(n.value) for n in module.body if isinstance(n,ast.Assign)
                and any(isinstance(t,ast.Name) and t.id=='SCHEMA' for t in n.targets))
    need(schema==m.SCHEMA,'exact old source header schema')
    return {'authenticated_retained_files':count,'rejected_source_mutations':count,'source_schema_checked':True}


def main():
    code,labels=m.compile_bridge();again,_=m.compile_bridge();need(code==again,'input-independent deterministic graph')
    for pc,ins in enumerate(code):
        need(ins[0] in ('R','W','M','J','H'),'only literal operations')
        if ins[0]=='R':need(all(0<=q<len(code) for q in ins[2].values()),'resolved fixed branch')
        if ins[0]=='J':need(0<=ins[1]<len(code),'resolved fixed jump')
        if ins[0]=='M':need(ins[2] in (-1,1),'unit moves only')
        if ins[0]=='W':need(ins[1]!=m.PORT['CONTEXT'],'old descriptor never written')
        if ins[0]=='W' and ins[1]==m.PORT['OLD']:need(pc>labels['EXIT'],'public writes only in exit suffix')
    full=[complete_case(code,labels,{},True),
          complete_case(code,labels,{'a':12,'u':2,'b':2}),
          complete_case(code,labels,{'rows':2,'r':2,'b':3,'cutoff':(1<<200)+7},True),
          complete_case(code,labels,{'b':22})]
    print(json.dumps({'status':'PASS_SELECTED_MOVE_PACKED_CODEC','locations':len(code),'tapes':len(m.NAMES),
          'table_sha256':m.table_digest(code),'source_checks':authenticate(),'full_packets':full,
          'strided_subprograms':shuffle_checks(),'negative_controls':rejecting_controls(code),
          'scope':'No native C execution, f>1 full packet, recursive tariff or global assumption discharge.'},sort_keys=True,indent=2))


if __name__=='__main__':main()
