#!/usr/bin/env python3
"""Sequential table replay, exact tape counters and conservative tariff checks."""
import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from check import Service,supplied_calendar,authenticate
from codec import Codec,Limits,Reader
from source_loader import load,need
from tapes import Meter,Table,byte_image
from controller import Controller
from registers import Registers




def opcode_checks():
    codec=Codec(Limits(128,20,100,20,40,2,1));ctrl=Controller(codec)
    job=load()['Job'](3,(2,0,1));requests=[];original_clear=ctrl.request.clear
    def capture():
        if ctrl.request.cells:requests.append(tuple(ctrl.request.cells))
        original_clear()
    ctrl.request.clear=capture
    returned=ctrl.call(0,lambda x:x,job)
    ctrl.call(4,lambda x:None,job)
    need(returned==job,'request/reply Job roundtrip')
    need(len(requests)==2,'two captured callback requests')
    w=ctrl.m.width
    def field(bits):
        value=0
        for b in bits[:w]:value=2*value+b
        return value
    need(field(requests[0])==0 and field(requests[1])==4,'explicit distinct service action tags')
    need(requests[0][w:]==requests[1][w:],'negative control differs only by action opcode')
    need(requests[0]!=requests[1],'zero and retire cannot share an untagged request')
    return dict(controls=['zero-and-retire-need-distinct-opcodes'],request_count=2)


def register_checks():
    cases=0;largest_ratio_num=0
    for width in (4,8,16):
        regs=Registers(width)
        values=sorted({0,1,2,3,(1<<(width//2))-1,(1<<width)-1})
        for a in values:
            for b in values:
                regs.load(0,a);regs.load(1,b)
                before=regs.meter.cells;regs.copy(0,2)
                need(regs.value(2)==a,'bitwise copy');cases+=1
                need(regs.compare(0,1)==(a>b)-(a<b),'bitwise compare');cases+=1
                if a+b<1<<width:
                    regs.add(0,1,2);need(regs.value(2)==a+b,'ripple add');cases+=1
                if a>=b:
                    regs.sub(0,1,2);need(regs.value(2)==a-b,'ripple subtract');cases+=1
                if a*b<1<<width:
                    regs.mul(0,1,2);need(regs.value(2)==a*b,'bitwise product');cases+=1
                if b:
                    regs.divide(0,1,2,3)
                    need((regs.value(2),regs.value(3))==divmod(a,b),'restoring division');cases+=1
                elapsed=regs.meter.cells-before
                need(elapsed<2**20*(2*width+1)**4,'register lowering envelope')
                largest_ratio_num=max(largest_ratio_num,elapsed)
    return dict(cases=cases,largest_batched_cell_actions=largest_ratio_num,
                scope='Finite witnesses for explicitly proved fixed-width algorithms; not an exhaustive macro proof.')


def table_checks():
    cases=0;controls=[]
    for width in (4,7,12):
        meter=Meter(width);table=Table(meter,[(1,[0,1]),(3,[1,0,1])])
        oracle={1:[0,1],3:[1,0,1]}
        for key,value in ((2,[1]),(3,[0]*7),(0,[]),(7,[1]*9),(2,[0,1,0])):
            before=meter.cells;table.rewrite(key,value);oracle[key]=value
            need(list(table.walk())==sorted(oracle.items()),'sequential table update')
            need(meter.cells>before,'charged table traversal');cases+=1
        for key in (3,0,7,1,2):
            need(table.pop(key)==oracle.pop(key),'sequential table delete')
            need(list(table.walk())==sorted(oracle.items()),'sequential table suffix copy');cases+=1
        need(table.empty(),'table final emptiness');peak=table.historical_bits();table.close()
        need(table.historical_bits()==peak and peak>0,'history survives clear')
        source=Table(meter,[(i,[i%2]*7) for i in range(8)])
        before=meter.cells;source.get(7);travel=meter.cells-before
        need(travel>=len(source.a.cells),'lookup is not free random access');controls.append('lookup-distance-'+str(width))
        source.close()
    return dict(operations=cases,controls=controls)


def controller_checks():
    result=[]
    for q,ticks,replicas in ((2,1,1),(3,2,1),(2,2,2)):
        plan=supplied_calendar(q,ticks,replicas);ns=load()
        rows=[ns['Job'](i,tuple(range(plan.n))) for i in range(plan.width)]
        C=sum(plan.count[e]*(q*plan.delay[e]+1) for e in plan.bands)
        codec=Codec(Limits(plan.n,20,plan.width+10*C,C,q*C,len(plan.targets),plan.width))
        for group,round_no in ((0,0),(1,plan.rounds-1)):
            direct=Service(plan);plan.decode(rows,round_no,group,direct,plan.events())
            other=Service(plan);ctrl=Controller(codec)
            receipt=ctrl.decode(plan,rows,round_no,group,other,list(plan.events()))
            need(direct.events==other.events,'literal source vs sequential service trace')
            need(direct.live==other.live==set(range(plan.width)),'sequential caller return')
            need(receipt['table_sweeps']>0 and receipt['tape_cell_actions']>0,'physical scans observed')
            need(receipt['lowered_bit_step_upper']>receipt['tape_cell_actions'],'register lowering is charged')
            result.append(dict(q=q,ticks=ticks,replicas=replicas,group=group,round_no=round_no,
                               trace_sha256=sha256(json.dumps(direct.events,separators=(',',':')).encode()).hexdigest(),**receipt))
    return result



def complete_run_check():
    plan=supplied_calendar(2,1,1);plan.rounds=4;ns=load()
    rows=[ns['Job'](i,tuple(range(plan.n))) for i in range(plan.width)]
    C=sum(plan.count[e]*(2*plan.delay[e]+1) for e in plan.bands)
    codec=Codec(Limits(plan.n,20,plan.width+10*C,C,2*C,len(plan.targets),plan.width))
    original=Service(plan);plan.run(rows,original)
    sequential=Service(plan);ctrl=Controller(codec)
    receipt=ctrl.run(plan,rows,sequential,list(plan.events()))
    need(original.events==sequential.events,'all source groups and rounds')
    groups=(plan.width+plan.source_width-1)//plan.source_width
    need(receipt['decode_calls']==groups*plan.rounds,'all decode repetitions counted')
    need(receipt['row_records_written']==plan.width*groups*plan.rounds,'all row initialization repeated')
    need(receipt['calendar_copies']==1,'immutable event tape reused across rounds')
    saved=Reader(*byte_image(ctrl.input_rows.cells));returned_rows=[]
    need(saved.get(ctrl.m.width)==len(rows),'returned immutable row count')
    for _ in rows:
        bits=[saved.get(1) for _ in range(saved.get(ctrl.m.width))]
        item=Reader(*byte_image(bits));returned_rows.append(codec.get_job(item));item.finish()
    saved.finish();need(returned_rows==rows,'immutable caller rows preserved at return')
    peaks=tuple(t.historical_bits() for t in ctrl.tables);event_peak=ctrl.calendar.peak
    warm=Service(plan);second=ctrl.run(plan,rows,warm,list(plan.events()))
    need(warm.events==original.events,'warm sequential replay')
    need(tuple(t.historical_bits() for t in ctrl.tables)==peaks,'fixed table roles reused across calls')
    need(ctrl.calendar.peak==event_peak>0,'calendar history retained after retirement')
    need(second['row_records_written']==2*plan.width*groups*plan.rounds,'warm initializations charged')
    # The mistaken one-round interpretation loses actual source callbacks.
    once=Service(plan)
    for group in range(groups):plan.decode(rows,0,group,once,plan.events())
    need(once.events!=original.events,'omitting rounds changes the source trace')
    return dict(groups=groups,rounds=plan.rounds,per_run_decodes=groups*plan.rounds,
                row_initializations=receipt['row_records_written'],warm_receipt=second,
                controls=['omitting-rounds-changes-trace','warm-history-not-erased','caller-rows-preserved-at-return'],
                trace_sha256=sha256(json.dumps(original.events,separators=(',',':')).encode()).hexdigest())


def tariff_checks():
    n0=2**16
    need(9**n0>=n0**512,'effective exponential base')
    need(2*512<=n0,'ratio denominator')
    h=3000;N=1<<h;B=N**92;C=2*N**83;P=18906;q=104904;w=128*h;J=4*w+1+N*h
    state=3*w+B*(2*w+J)+C*(4*w+P*J)+q*C*(2*w+J)
    event=w+2*N**88*(5+4*P+5*q)*w
    bridge=(10*P+32)*J+(16*P+256)*w+1024*N*h
    input_rows=w+B*(w+J)
    logical=2*state+input_rows+event+bridge+2**21+512*w+2048
    total=2*logical
    need(state<3*B*N*h and input_rows<2*B*N*h and event<B*N*h and bridge<B*N*h,'explicit historical components')
    need(total<32*B*N*h and total<N**96,'sequential historical role allowances')
    local_passes=64*(C+P*N+N*N+N+1)
    primitive=2**20*(2*w+1)**4
    need(local_passes<N**128 and primitive<N**16,'per-event and register envelopes')
    adapter=2**32*(N+1)**4
    need(adapter<N**5,'bounded local adapter envelope')
    need(64*N**96*(adapter+128)*(primitive+32)<N**128,'full scan bound')
    need((q+2)*N**82*(2*N**6)<N**90,'event count bound')
    need(2*N**348+N**200<N**350 and N**350<N**512,'composed clock envelope')
    width,source_width,rounds=17,4,9
    actual=((width+source_width-1)//source_width)*rounds
    need(actual>width//source_width,'rounds cannot be dropped')
    return dict(production_h_min=3000,absorption_n_min=n0,
                register_macro_steps='2^20 (2w+1)^4',adapter_macro_bound='2^32 (N+1)^4',derived_polynomial='< B N^350',complete_bookkeeping_steps='< B N^512 <= W',
                callback_bodies_excluded=True,setup_generation_excluded=True,
                scope='Proved conservative upper bound, not a measured production instruction count.')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path);a=parser.parse_args()
    authenticate()
    result=dict(status='PASS_SEQUENTIAL_DECODER_BOOKKEEPING',opcodes=opcode_checks(),registers=register_checks(),tables=table_checks(),controllers=controller_checks(),complete_run=complete_run_check(),tariff=tariff_checks())
    if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({'status':result['status'],'controller_fixtures':len(result['controllers']),
                      'tape_cell_actions':sum(x['tape_cell_actions'] for x in result['controllers']),
                      'table_operations':result['tables']['operations']},sort_keys=True))

if __name__=='__main__':main()
