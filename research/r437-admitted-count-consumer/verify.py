#!/usr/bin/env python3
"""Admitted original-root binary Count through the actual initial Count consumers."""
import argparse,hashlib,importlib.util,json,shutil,sys,time
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace as NS,MethodType
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def need(ok,message):
    if not ok:raise ValueError(message)
def sha(data):return hashlib.sha256(data).hexdigest()
def integer(x):return dict(bits=x.bit_length(),sha256=sha(x.to_bytes(max(1,(x.bit_length()+7)//8),'big')))
def authenticate():
    m=json.loads((HERE/'SOURCES.json').read_text())
    for row in m['files']:
        if row['usage']=='input':need(sha((ROOT/row['path']).read_bytes())==row['sha256'],'source hash '+row['path'])
    for row in m['retained']:need(sha((HERE/row['path']).read_bytes())==row['sha256'],'retained hash '+row['path'])
    return sum(x['usage']=='input'for x in m['files'])
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path);out=importlib.util.module_from_spec(spec);spec.loader.exec_module(out);return out

def run(diagnostic=False):
    started=time.monotonic();inputs=authenticate()
    def phase(name):
        if diagnostic:print(json.dumps(dict(phase=name,seconds=round(time.monotonic()-started,3))),flush=True)
    sys.path.insert(0,str(ROOT/'research/selected-bit-physical-caller'));import loader
    with TemporaryDirectory(prefix='r437-admitted-count-source-')as temp:
        projection=Path(temp)
        for row in json.loads((loader.CALLER/'SOURCES.json').read_text())['files']:
            if row['usage']!='input':continue
            dest=projection/row['path'];dest.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(HERE/'retained/selected-result.json'if row['path']=='certificates/selected-result.json'else ROOT/row['path'],dest)
        loader.REPOSITORY=projection;loader.compatibility_controls()
        sys.path.insert(0,str(ROOT/'research/r437-carrier-integration'))
        import admission,compiler,numerical
        cat,top=admission.load_certified('D');admission.authenticate_certified(cat)
        ordinal=module('r437_admitted_count_ordinal',ROOT/'research/r437-sharp-stock-entry/retained/ordinal.py');ordinal.install_ordinal_counts(cat.codes)
        import words,records,macro_binding,macro_machine,oracle
        from catalogue import Specifications
        from cardinal_counts import Count
        specs=Specifications(cat);record=compiler.early_source87(cat,top,0,0)
        low=tuple(map(tuple,oracle.eye(64)));handle=compiler.source_handle(cat,record['identifier'],False,low)
        spec=compiler.resolve_handle(cat,specs,handle)
        need(spec.good and spec.template.rank==2,'actual admitted SOURCE87 native specification')
        q=cat.q;rows=numerical.stock_unit(q,2)
        domain=admission.RootDomain(64,64,2,0,(q*q).bit_length()+1,64 .bit_length()+1,cat.codes.bits,rows)
        need((domain.L,domain.I,domain.Q)==(255,8,520213)and top.families==28416,'actual root widths/families')
        batch=module('r437_admitted_count_batch',ROOT/'research/r437-batched-high-quotient/adapter.py')
        quotient,constant=batch.compile_quotient(q,64)
        bridge=module('r437_admitted_count_bridge',HERE/'bridge.py');node_prefix,boundary=bridge.compile_node_prefix(macro_machine,quotient)
        phase('certified source and actual NODE prefix bound')
        calls=[];controls=[]
        def check_entry(d=domain,h=handle,callback=lambda:None):
            return admission.checked_entry(cat,specs,h,d,callback,mode='numerical',expected_key=handle.request_key,expected_common=False)
        for name,d in [('wrong precision',replace(domain,L=domain.L-1)),('reset root index',replace(domain,I=domain.I+1)),('wrong code width',replace(domain,Q=domain.Q-1)),('incompatible rows',replace(domain,rows=rows+1)),('nonroot history',replace(domain,h=1))]:
            before=len(calls)
            try:check_entry(d,callback=lambda:calls.append('forbidden'))
            except ValueError as e:controls.append(dict(name=name,error=str(e),continuation_called=False))
            else:raise ValueError('bad original root accepted '+name)
            need(len(calls)==before,'guard rejects before encoding')
        stale=replace(handle,identity='0'*64)
        try:check_entry(h=stale,callback=lambda:calls.append('forbidden'))
        except ValueError as e:controls.append(dict(name='stale actual source',error=str(e),continuation_called=False))
        else:raise ValueError('stale source accepted')
        tapes=[];old_init=records.Tape.__init__
        def register(t):old_init(t);tapes.append(t)
        records.Tape.__init__=register
        def actions(m):return {k:getattr(m,k)for k in ('reads','writes','moves')}
        def record_actions():return {k:sum(getattr(t.meter,k)for t in tapes)for k in ('reads','writes','moves')}
        def value(count):
            body=count.tape.cells[1:];end=body.index(words.RIGHT)
            need(all(x in(0,1)for x in body[:end]),'binary Count observation')
            return int(''.join(str(x)for x in reversed(body[:end])),2)
        def continuation():
            calls.append('actual encoded continuation')
            ia,ra=words.Arena(domain.I,256),words.Arena(domain.L,32768)
            modulus=ra.literal(q**domain.w);ring=words.Ring(modulus)
            program=records.Program.fixture(ia,ra,domain.n,2,(),cat.codes.bits)
            binding=object.__new__(macro_binding.SelectedBinding);binding.codes=cat.codes;binding.specifications=specs;binding.ambient=handle.code
            roles={name:records.Tape()for name in('unused','leading','fibre','old_directory')}
            root_count=Count.literal(domain.rows);roles['rows']=root_count.tape
            for name in('before','gap','suffix','old_count'):roles[name]=Count.literal(1).tape
            dirty=Count.literal(173);dirty_word=ra.literal(37)
            runtime=NS(indices=ia,arena=ra,context=NS(q=q,dimension=64,codes=cat.codes,ring=ring),
                binding=binding,topology=top,program=program,size=ia.literal(domain.n),depth=ia.literal(domain.h),roles=roles)
            for name in('tape','count','commit','save_count'):setattr(runtime,name,MethodType(getattr(macro_machine.Machine,name),runtime))
            need(runtime.indices.bits==domain.I and runtime.arena.bits==domain.L and runtime.context.codes is cat.codes,'encoded widths/codebook match admitted root')
            borrowed=[(t,bytes(t.cells),t.head)for t in[roles[n]for n in('rows','before','gap','suffix','old_count','old_directory')]+[program.tape,dirty.tape]]
            dirty_saved=(bytes(dirty_word.cells),dirty_word.head);live=(set(ia.live),set(ra.live));existing=set(map(id,tapes))
            phase('actual root Count encoded')
            before=dict(record=record_actions(),index=actions(ia.meter),residue=actions(ra.meter))
            old_inspect=words.Word.inspect;words.Word.inspect=lambda _:(_ for _ in()).throw(ValueError('runtime numerical decoding forbidden'))
            try:local_fibre=node_prefix(runtime)
            finally:words.Word.inspect=old_inspect
            phase('literal ingress quotient stock and leading/fibre product finished')
            observed={name:value(runtime.count(name))for name in('unused','leading')}
            observed['pre_expansion_fibre']=value(local_fibre)
            local_fibre.close()  # Explicit disposal of the adapter-returned original local Count.
            need(observed==dict(unused=9475,leading=9475,pre_expansion_fibre=9475),'independent actual downstream Count values')
            need(live==(set(ia.live),set(ra.live)),'NODE prefix numerical ownership restored')
            need(all((bytes(t.cells),t.head)==(raw,head)for t,raw,head in borrowed),'borrowed root/Count metadata preserved')
            need((bytes(dirty_word.cells),dirty_word.head)==dirty_saved,'unrelated dirty residue word preserved')
            need(all(t.head==1 and all(c==words.BLANK for c in t.cells[1:])for t in tapes if id(t)not in existing),'temporary Count backing erased')
            after=dict(record=record_actions(),index=actions(ia.meter),residue=actions(ra.meter))
            invoice={lane:{k:after[lane][k]-before[lane][k]for k in after[lane]}for lane in after}
            returned={name:integer(v)for name,v in observed.items()}
            for t in roles.values():t.clear()
            dirty.close();program.tape.clear();ia.free_many(runtime.size,runtime.depth);ra.free(dirty_word);ring.close();ra.free(modulus)
            need(not ia.live and not ra.live,'complete terminal numerical cleanup')
            need(all(t.head==1 and all(c==words.BLANK for c in t.cells[1:])for t in tapes),'all record backing blank after owned/fixture disposal')
            return dict(outputs=returned,node_invoice=invoice,full_construct_execute_dispose=dict(record=record_actions(),index=actions(ia.meter),residue=actions(ra.meter)),visited_record_cells=sum(len(t.cells)for t in tapes),borrowed_preserved=True,numerical_restored=True,record_backing_erased=True)
        result,entry=check_entry(callback=continuation);need(calls==['actual encoded continuation'],'one actual admitted continuation')
        records.Tape.__init__=old_init
        phase('complete disposal')
        return dict(status='PASS_R437_ADMITTED_INITIAL_COUNT_CONSUMER',live_inputs=inputs,root_entry=entry,node_boundary=boundary,
            input_rows=integer(rows),batch_constant=integer(constant),construction=quotient.construction,
            encoded_result=result,controls=controls,full_directory_context_constructed=False,production_payload_executed=False,
            remaining_original_expansion=dict(word_divisions=2*domain.n*domain.w,count_multiply_small=2*domain.n*domain.w,final_fibre_bits=(9475*(q**domain.w)**(2*domain.n)).bit_length()),
            scope='Original admitted root to literal NODE ingress/quotient/stock/saved leading/initial fibre product; original fibre expansion, full Context, physical big-int tariff and payload remain open.')

def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--diagnostic',action='store_true');a=p.parse_args();result=run(a.diagnostic)
    if a.write:(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(json.dumps(json.loads((HERE/'RESULT.json').read_text()),sort_keys=True)==json.dumps(result,sort_keys=True),'typed deterministic receipt')
    print(result['status'])
if __name__=='__main__':main()
