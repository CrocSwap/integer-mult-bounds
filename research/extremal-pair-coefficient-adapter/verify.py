#!/usr/bin/env python3
"""Read-only actual encoded adapter replay with an inherited independent oracle.
SPDX-License-Identifier: Apache-2.0
"""
from fractions import Fraction as Q
from hashlib import sha256
from pathlib import Path
import argparse,importlib.util,json,sys

HERE=Path(__file__).resolve().parent

def need(ok,message):
    if not ok:raise ValueError(message)


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(spec);sys.modules[name]=result
    spec.loader.exec_module(result)
    return result


def authenticate(root):
    pins=json.loads((HERE/'RUNTIME-PINS.json').read_text())
    for item in pins['files']:
        path=root/item['path']
        need(path.is_file() and not path.is_symlink(),'regular pinned input '+item['path'])
        data=path.read_bytes()
        need(len(data)==item['bytes'] and sha256(data).hexdigest()==item['sha256'],'exact runtime source '+item['path'])
    for item in json.loads((HERE/'DEPENDENCIES.json').read_text())['files']:
        data=(HERE/item['local']).read_bytes()
        need(len(data)==item['bytes'] and sha256(data).hexdigest()==item['sha256'],'retained proof '+item['local'])
    return len(pins['files'])


def decoded(raw):
    need(raw[0]==2,'Count left marker')
    k=1;value=0
    while k<len(raw) and raw[k] in (0,1):value+=raw[k]<<(k-1);k+=1
    need(k>1 and k<len(raw) and raw[k]==3 and (k==2 or raw[k-1]==1),'canonical Count extent')
    need(all(v==4 for v in raw[k+1:]),'blank Count suffix')
    return value


def run(root):
    core=root/'research/physical-gaussian-core';sys.path.insert(0,str(core))
    source=module('gaussian_sources',core/'gaussian_sources.py')
    oracle=module('adapter_oracle',root/'research/encoded-gaussian-directed-coefficient-audit/oracle.py')
    with source.opened():
        from cardinal_counts import Count
        from check_support import no_decode
        from gaussian_exponentials import Exponentials
        from router_metadata import owned
        from scratch_pool import ScratchPool
        from session import OuterScope,sealed_constructors,borrowed_tape,erase_marker
        adapter=module('extremal_adapter',HERE/'adapter.py')
        raw=lambda c:bytes(borrowed_tape(c.tape).cells)
        calls=[];original=Exponentials.grid_interval
        def observe(self,argument,positive_exponent=False,binary_scale=None):
            before=self.taylor_steps
            record={'negative':argument.numerator.negative,'numerator':raw(argument.numerator.magnitude),
                    'denominator':raw(argument.denominator),'growth':positive_exponent,
                    'scale':None if binary_scale is None else raw(binary_scale)}
            result=original(self,argument,positive_exponent,binary_scale)
            record.update({key:raw(getattr(self,key)) for key in ('precision','argument_bound','R','k','terms','J')})
            record.update(lower=raw(result[0]),upper=raw(result[1]),steps=self.taylor_steps-before)
            calls.append(record)
            return result
        Exponentials.grid_interval=observe
        pool=ScratchPool(512);scope=OuterScope(pool);values=(1,2,101,102,103,104)
        try:
            with owned(*(Count.literal(v) for v in values)) as params:
                initial=[raw(c) for c in params]
                with sealed_constructors(),scope.installed():
                    with no_decode():tables=adapter.produce(*params)
                    output=[tables.precision,*tables.entries]
                    need(len(pool.live)==9 and len({id(c.tape) for c in output})==9,'nine distinct live output owners')
                    need(all(c.tape.head==1 for c in output+list(params)),'all output and borrowed heads returned')
                    need([raw(c) for c in params]==initial,'complete borrowed inputs unchanged')
                    payload=[raw(c) for c in output]
                    history=sum(len(t.cells) for t in pool.tapes)
                    tables.close();pool.empty()
                need([raw(c) for c in params]==initial and all(c.tape.head==1 for c in params),'retirement preserves borrowed inputs')
            rejected=[]
            for bad in [(0,2,101,102,103,104),(1,0,101,102,103,104),
                        (1,3,101,102,103,104),(1,2,1,2,103,104),
                        (1,2,101,101,103,104),(1,2,101,202,103,104),
                        (1,2,101,102,103,103)]:
                with owned(*(Count.literal(v) for v in bad)) as params:
                    initial=[raw(c) for c in params]
                    with sealed_constructors(),scope.installed():
                        try:
                            with no_decode():unexpected=adapter.produce(*params)
                        except ValueError:rejected.append(bad)
                        else:
                            unexpected.close();raise ValueError('invalid producer domain accepted')
                        need(not pool.live,'domain rejection retires private owners')
                        pool.empty()
                    need([raw(c) for c in params]==initial and all(c.tape.head==1 for c in params),'rejection preserves inputs and heads')
            need(len(calls)==4,'exactly four calls; invalid domains do not call scalar backend')
        finally:
            Exponentials.grid_interval=original
        for tape in pool.tapes:erase_marker(tape)
        need(not pool.live and all(t.head==1 and all(v==4 for v in t.cells) for t in pool.tapes),'all private history blank and markers retired')
    p,alpha,s1,t1,s2,t2=values;P=p+8;u=alpha*alpha
    expected=[Q(u*(2*(t-s)+1),s) if direction==0 else Q(u*(2*s-1),s)
              for s,t in ((s1,t1),(s2,t2)) for direction in (0,1)]
    rows=[]
    for record,f in zip(calls,expected):
        n,d=decoded(record['numerator']),decoded(record['denominator'])
        need(not record['negative'] and Q(n,d)==f,'exact source directed argument and order')
        need(record['growth'] is False and record['scale'] is None,'decay with zero binary normalization')
        row={key:decoded(record[key]) for key in ('precision','argument_bound','R','k','terms','J','lower','upper')}
        need(row['precision']==P and row['argument_bound']==2*u,'shared source setup parameters')
        X=8*u;k=(8*(X+1)-1).bit_length();H=P+X+k+16;c=(H-1).bit_length();R=P+4*X+4*k+2*c+64
        need((row['R'],row['k'],row['terms'],row['J'])==(R,k,(R+2)//3+8,(R+3)//4+8),'unchanged scalar precision policy')
        lo,hi=oracle.interval(f,P)
        need(Q(row['lower'],1<<P)<=lo<=hi<=Q(row['upper'],1<<P),'entire independent oracle enclosed')
        need(0<=row['upper']-row['lower']<=2,'two-ulp source interval')
        need(hi-Q(row['lower'],1<<P)<Q(1,1<<(p+7)),'strict emitted coefficient error')
        row.update(argument=[f.numerator,f.denominator],raw_numerator=n,raw_denominator=d,
                   steps=record['steps'],oracle=[[x.numerator,x.denominator] for x in (lo,hi)])
        rows.append(row)
    observed=[decoded(x) for x in payload]
    wanted=[P,1<<P,rows[0]['lower'],rows[1]['lower'],1<<P,1<<P,rows[2]['lower'],rows[3]['lower'],1<<P]
    need(observed==wanted,'complete row-major dyadic table output')
    need(rows[0]['lower']!=rows[2]['lower'],'fixture exposes returning axis swap')
    wrong=wanted[:];wrong[2],wrong[6]=wrong[6],wrong[2]
    need(wrong!=observed,'returning wrong-axis table assignment detected')
    need(any(f!=f/alpha for f in expected),'fixture exposes omitted alpha square')
    need(rows[1]['lower']==rows[3]['lower']==0,'small packet is outside A12 margin threshold')
    return {'input':values,'emitted_precision':P,'row_major_numerators':observed[1:],
            'calls':rows,'live_outputs_before_retirement':9,'observed_private_history_cells':history,
            'cleanup':'all private cells blank, markers erased, heads at1; borrowed bytes unchanged',
            'domain_rejections':rejected,'controls':['returning-axis-swap','omitted-alpha-square-argument',
            'exact-F-P-policy','growth-or-normalization-mismatch','small-valid-producer-is-not-A12-rank-admission']}


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-root',type=Path,default=HERE.parents[1]);args=ap.parse_args()
    root=args.source_root.resolve();count=authenticate(root)
    result={'status':'PASS_EXTREMAL_PAIR_COEFFICIENT_ADAPTER','authenticated_runtime_files':count,
            'packet':run(root),'scope':'Unchanged encoded scalar backend with source-bound four-call adapter; finite packet corroborates universal theorem; no full Gaussian producer or native-ROM claim.'}
    print(json.dumps(result,sort_keys=True,indent=2))

if __name__=='__main__':main()
