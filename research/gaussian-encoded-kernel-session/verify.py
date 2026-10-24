"""Actual source page/Core reuse, owner guards, eviction and corruption."""
import hashlib,importlib.util,json,sys
from pathlib import Path
from types import SimpleNamespace
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
SOURCE=ROOT/'research/physical-gaussian-core'

def need(ok,msg):
    if not ok:raise ValueError(msg)

def pins():
    manifest=json.loads((HERE/'SOURCES.json').read_text())
    for row in manifest['files']:
        if row['usage']=='input':need(hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()==row['sha256'],'source pin '+row['path'])

def science():
    sys.path.insert(0,str(SOURCE))
    import gaussian_sources
    with gaussian_sources.opened():
        spec=importlib.util.spec_from_file_location('kernel_session_science',HERE/'kernel_session.py')
        service=importlib.util.module_from_spec(spec);spec.loader.exec_module(service)
        from cardinal_counts import Count
        from gaussian_core import Core
        from gaussian_rationals import Rational
        from ring_words import Signed,write_signed
        from ring_check_words import body
        from router_metadata import owned
        from session import borrowed_tape,erase_marker,sealed_constructors
        from check_support import no_decode
        from records import Tape
        from words import BLANK
        core=Core();session=None;receipts=[];controls=[]
        def meter():
            tapes=(*session.pool.tapes,session.output)
            return {name:sum(getattr(t.meter,name) for t in tapes) for name in ('reads','writes','moves')}
        def carrier(x):
            return borrowed_tape((x.magnitude if hasattr(x,'magnitude') else x).tape)
        def state():
            return [(bytes(t.cells),t.head,t.meter.reads,t.meter.writes,t.meter.moves) for t in (*session.pool.tapes,session.output)]
        with owned(*(Count.literal(v) for v in (13,14,1,1,24))) as parameters:
            try:
                with no_decode():session=service.KernelSession(*parameters)
                axis_meter=meter()
                for index,window_args in enumerate(((1,5,2,3),(1,5,2,3),(1,6,2,3))):
                    start,length,offset,size=window_args
                    with owned(Signed(Count.literal(start)),Count.literal(length),Signed(Count.literal(offset)),Count.literal(size),Count.literal(16)) as args:
                        if index==0:
                            resident=borrowed_tape(session.axis.s.tape)
                            resident.step(1)
                            before=state()
                            try:session.run(SimpleNamespace(magnitude=session.axis.s,negative=True),args[1],args[2],args[3],args[4])
                            except ValueError as e:need(str(e)=='external session window parameters','alias pre-read rejection')
                            else:raise ValueError('resident alias accepted')
                            need(state()==before,'negative resident alias no traffic')
                            resident.rewind();controls.append('negative resident alias before Signed normalization')
                        saved=[(bytes(carrier(x).cells),carrier(x).head) for x in args]
                        with no_decode():page=session.run(*args)
                        page_hash=hashlib.sha256(body(page)).hexdigest()
                        need(saved==[(bytes(carrier(x).cells),carrier(x).head) for x in args],'borrowed parameter frames')
                        before=state()
                        try:session.run(*args)
                        except ValueError as e:need(str(e)=='consume prior protected session page','pending page guard')
                        else:raise ValueError('unconsumed page accepted')
                        need(state()==before,'pending page guard no traffic')
                        output_hash=None;word_calls=None
                        if index<2:
                            halo=Tape();returned=None
                            try:
                                with owned(Count.literal(18)) as (width,):
                                    for _ in range(length):
                                        for value in (8192,-4096):
                                            with owned(Signed(Count.literal(abs(value)),value<0)) as (word,):write_signed(word,halo,width)
                                halo.rewind();borrowed=[(bytes(t.cells),t.head) for t in (page,halo)]
                                old=dict(core.word.calls)
                                with no_decode():returned=core.run(page,halo)
                                raw=body(returned)
                                need(len(raw)==108 and any(v==1 for i,v in enumerate(raw) if i%18),'nonzero real Core output')
                                need(borrowed==[(bytes(t.cells),t.head) for t in (page,halo)],'Core borrowed page/halo frames')
                                output_hash=hashlib.sha256(raw).hexdigest()
                                word_calls={key:core.word.calls[key]-old[key] for key in old}
                            finally:
                                if returned is not None:returned.clear();erase_marker(returned)
                                halo.clear();erase_marker(halo)
                        session.consume()
                        receipts.append({'window':list(window_args),'page_sha256':page_hash,'Core_sha256':output_hash,'Core_word_calls':word_calls,'misses':session.misses,'hits':session.hits,'evictions':session.evictions,'owner_meter':meter()})
                        if index==2:
                            with sealed_constructors(),session.scope.installed():
                                with owned(Count.literal(0),Rational.literal(0)) as (zero,value):session.cache.set(zero,zero,value)
                            try:
                                with no_decode():mutated=session.run(*args)
                            except ValueError:controls.append('actual resident numerical corruption rejected')
                            else:
                                need(hashlib.sha256(body(mutated)).hexdigest()!=page_hash,'resident numerical corruption changes page')
                                controls.append('actual resident numerical corruption changes page')
                                session.consume()
                need(receipts[0]['page_sha256']==receipts[1]['page_sha256']=='49d45e0f26788cf2d2b299749cd110b66dfcdb700a89d6c90bf8034174b96f05','exact source first-page binding')
                need(receipts[0]['Core_sha256']==receipts[1]['Core_sha256']=='56b9ca77fd76a10ddba4a0ac3793ad6a4543108870f580f1e1c468a5c778a354','exact real Core hit endpoint')
                need(receipts[1]['hits']>=1 and receipts[2]['evictions']>=1,'real hit and changed-length eviction')
                peak=session.pool.peak
            finally:
                if session is not None:session.close()
            need(not session.pool.live and all(t.head==1 and all(v==BLANK for v in t.cells) for t in (*session.pool.tapes,session.output)),'full session markers and body disposal')
            backing=sum(len(t.cells) for t in (*session.pool.tapes,session.output))
            controls.extend(['pending page blocks reuse','complete owned disposal'])
            return {'schema_version':1,'axis':[13,14,1,1,24],'target_precision':16,'axis_owner_meter':axis_meter,'windows':receipts,'owner_final_meter':meter(),'owner_retained_backing':backing,'pool_peak':peak,'controls':controls,'scope':'actual encoded fixed-bank session; inherited source arithmetic/production premises; third window page only'}

def main():
    pins();writing=sys.argv[1:]==['--write-result'];need(writing or not sys.argv[1:],'arguments')
    expected=None if writing else json.loads((HERE/'RESULT.json').read_text())
    if expected is not None:
        need(type(expected.get('schema_version')) is int and expected['schema_version']==1,'typed receipt schema')
        need(type(expected.get('pool_peak')) is int and type(expected.get('owner_retained_backing')) is int,'typed receipt counters')
    result=science()
    if writing:(HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
    else:need(json.dumps(expected,sort_keys=True,separators=(',',':'))==json.dumps(result,sort_keys=True,separators=(',',':')),'typed complete frozen receipt')
    print('PASS actual Gaussian session: miss, hit, eviction, Core endpoint and disposal')
if __name__=='__main__':main()
