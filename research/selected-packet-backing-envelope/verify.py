#!/usr/bin/env python3
"""Finite source instrumentation for the caller backing proof; no heap census."""
from pathlib import Path
import importlib.util
import json
import sys
from types import SimpleNamespace as NS

ROOT = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('envelope_runtime', ROOT/'runtime.py')
runtime = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runtime)
need = runtime.require


def envelope(N, F, K, D, Q, A=None):
    for value in (N,F,K,D,Q):
        need(type(value) is int, 'integer domain, excluding bool')
    need(N>=1 and F>=1 and Q>=2 and K>=N*F+1 and D>=N*(Q-1)+1, 'backing domain')
    prefix = K+(2*N+1)*F+4+D+3*Q
    copy = K+(2*N+2)*F+4+D+2*Q
    result = dict(prefix=prefix, copy=copy, caller=max(prefix,copy))
    if A is not None:
        need(type(A) is int and A>=F+1, 'action includes its returned array')
        result['action'] = K+2*N*F+3+D+2*Q+A
        result['composed'] = max(result['caller'],result['action'])
    return result


def unique_size(values):
    return sum(len(v.cells) for v in {id(x.cells):x for x in values}.values())


def fixture(rt,N,F,Q,padding,passes,scratch=0,native=False):
    """Synthetic records/layout; unchanged engine, reader, copying and clearing."""
    import packet_engine
    Tape=rt.records.Tape
    source,directory,first=Tape(),Tape(),Tape()
    payload=bytes(((7*i+i//3)^(i//2))&1 for i in range(N*F))
    source.cells.extend(payload)
    if padding:
        source.cells.extend(bytes([rt.words.BLANK])+bytes(padding))
    record=bytes([0])*(Q-2)+bytes([rt.records.RECORD_END])
    directory.cells.extend(record*N)
    first.cells.extend(bytes([rt.words.BLANK])*(Q-1))
    K,D=len(source.cells),len(directory.cells)
    count,fields=rt.counts.Count.literal(N),rt.counts.Count.literal(1)
    bill=envelope(N,F,K,D,Q,F+1+scratch)
    seen=dict(caller_peak=0,composed_peak=0,samples=0,prefix_cuts=[],copy_cuts=[],temporary_peak=0)
    original_action,original_copy,original_reader=packet_engine.action,packet_engine.copy_bits,packet_engine.read_prefix
    private=[]

    def find_run(frame):
        while frame is not None:
            if frame.f_code is packet_engine.run.__code__:
                return frame
            frame=frame.f_back
        return None

    def measure(frame,extra=(),action_extra=()):
        run=find_run(frame)
        if run is None:
            return None
        values=run.f_locals
        owners=[source,directory,first]
        owners.extend(values[n] for n in ('current','output','local','changed','fields')
                      if isinstance(values.get(n),Tape))
        cursor=frame
        while cursor is not run:
            if cursor.f_code is rt.packet.read_prefix.__code__ and isinstance(cursor.f_locals.get('out'),Tape):
                owners.append(cursor.f_locals['out'])
            cursor=cursor.f_back
        owners.extend(extra)
        total=unique_size(owners)
        need(total<=bill['caller'],'caller envelope')
        combined=unique_size(owners+private+list(action_extra))
        need(combined<=bill['composed'],'composed action envelope')
        seen['caller_peak']=max(seen['caller_peak'],total)
        seen['composed_peak']=max(seen['composed_peak'],combined)
        seen['samples']+=1
        return total

    def trace(frame,event,arg):
        code=frame.f_code
        if code is packet_engine.run.__code__ or code is rt.packet.read_prefix.__code__:
            if event in ('line','return'):
                measure(frame)
        elif event=='return' and code in (Tape.__init__.__code__,Tape.write.__code__,Tape.clear.__code__):
            extra=()
            if code is Tape.__init__.__code__ and frame.f_back.f_code in (packet_engine.run.__code__,rt.packet.read_prefix.__code__):
                extra=(frame.f_locals['self'],)
            total=measure(frame,extra)
            if extra and frame.f_back.f_code is packet_engine.run.__code__:
                seen['temporary_peak']=max(seen['temporary_peak'],total or 0)
        return trace

    def reader(d,f):
        out=original_reader(d,f)
        seen['prefix_cuts'].append(measure(sys._getframe(),(out,)))
        return out

    def copier(src,dst,length):
        original_copy(src,dst,length)
        run=sys._getframe(1)
        if dst is run.f_locals['output']:
            seen['copy_cuts'].append(measure(run))

    def action(local,event,layout,coefficient,factory):
        nonlocal private
        if native:
            out=original_action(local,event,layout,coefficient,factory)
        else:
            out=Tape()
            private=[out]
            if scratch:
                temp=Tape()
                temp.cells.extend(bytes([0])*(scratch-1))
                private.append(temp)
            for value in local.cells[1:]:
                out.append(value)
                measure(sys._getframe())
            out.rewind()
        measure(sys._getframe(),action_extra=(out,))
        need(out is not local and len(out.cells)==F+1,'fresh complete action result')
        need(len(local.cells)==F+1,'action preserves local backing')
        private=[]
        return out

    ring=arena=modulus=None
    if native:
        need(F%3==0,'native sign fibres')
        arena=rt.words.Arena(3);modulus=arena.input(3);ring=rt.words.Ring(modulus)
    def extent(n):
        x=rt.counts.Count.literal(n)
        out=x.marginal();x.close()
        return out
    layout=NS(fibre=lambda:rt.counts.Count.literal(F),ring=ring,q=3,
              extents=lambda _:[extent(F//3),extent(1)])
    def events():
        for _ in range(passes):
            yield NS(kind='sign',first=None)
    packet_engine.read_prefix,packet_engine.copy_bits,packet_engine.action=reader,copier,action
    try:
        sys.settrace(trace)
        output=packet_engine.run(source,events(),layout,directory,count,fields,lambda _:None)
    finally:
        sys.settrace(None)
        packet_engine.read_prefix,packet_engine.copy_bits,packet_engine.action=original_reader,original_copy,original_action
    need(len(output.cells)==N*F+1 and output is not source,'whole packet result')
    expected=payload
    if native and passes%2:
        expected=bytes(payload[n*F+b*3+(-a)%3] for n in range(N) for b in range(F//3) for a in range(3))
    need(bytes(output.cells[1:])==expected,'independent output oracle')
    need(bytes(source.cells[1:1+N*F])==payload and len(source.cells)==K,'source restoration')
    need(len(seen['prefix_cuts'])==N*passes==len(seen['copy_cuts']),'complete cut coverage')
    need(max(seen['prefix_cuts'])==bill['prefix'],'predecessor prefix maximum')
    need(max(seen['copy_cuts'])==bill['copy'],'copy maximum')
    need(seen['caller_peak']==bill['caller'],'sharp caller maximum')
    if not native:
        need(seen['composed_peak']==bill['composed'],'sharp synthetic scratch composition')
    count.close();fields.close()
    if native:
        ring.close();arena.free(modulus);need(not arena.live,'native arena cleanup')
    return dict(N=N,F=F,Q=Q,K=K,D=D,passes=passes,scratch=scratch,native_sign=native,bill=bill,**seen)


def main():
    rt=runtime.load_runtime();rows=[]
    for N in (1,2,4):
        for F,Q in ((1,2),(2,2),(3,2),(3,7),(9,4)):
            for padding in (0,5):
                for scratch in (0,1,13):
                    rows.append(fixture(rt,N,F,Q,padding,3,scratch))
    for N in (1,2,4):
        for F,Q in ((3,2),(3,7),(9,4)):
            rows.append(fixture(rt,N,F,Q,0,3,native=True))
    result=dict(status='PASS_PACKET_BACKING_ENVELOPE',source_head=runtime.PIN,
                cases=len(rows),samples=sum(x['samples'] for x in rows),
                prefix_cuts=sum(len(x['prefix_cuts']) for x in rows),
                copy_cuts=sum(len(x['copy_cuts']) for x in rows),fixtures=rows,
                native_private_scratch_certified=False,no_new_kappa=True)
    if (ROOT/'RESULT.json').exists():
        runtime.check_receipt(json.loads((ROOT/'RESULT.json').read_text()),result)
    print(json.dumps(result,indent=2,sort_keys=True))


if __name__=='__main__':main()
