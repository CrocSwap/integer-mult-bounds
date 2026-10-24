#!/usr/bin/env python3
"""Actual eager versus prefix-fused R437 leaf/consumer comparison.

JoyboyBrian, substantial OpenAI Codex assistance. Apache-2.0.
Based on Chris R/Clear1nsight's PR4176 produced-child physical bridge.
"""
import argparse,ast,hashlib,importlib.util,json,shutil,sys
from dataclasses import replace
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace as NS
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]

def need(ok,message):
    if not ok:raise ValueError(message)
def sha(data):return hashlib.sha256(data).hexdigest()
def integer(x):return dict(bits=x.bit_length(),sha256=sha(x.to_bytes(max(1,(x.bit_length()+7)//8),'big')))
def authenticate():
    manifest=json.loads((HERE/'SOURCES.json').read_text())
    for row in manifest['files']:
        if row['usage']=='input':need(sha((ROOT/row['path']).read_bytes())==row['sha256'],'source hash '+row['path'])
    for row in manifest['retained']:need(sha((HERE/row['path']).read_bytes())==row['sha256'],'retained hash '+row['path'])
    return sum(r['usage']=='input' for r in manifest['files'])

def run(probe=False):
    inputs=authenticate();sys.path.insert(0,str(HERE));sys.path.insert(0,str(ROOT/'research/selected-bit-physical-caller'));import loader
    with TemporaryDirectory(prefix='r437-high-source-') as temp:
        projection=Path(temp)
        for row in json.loads((loader.CALLER/'SOURCES.json').read_text())['files']:
            if row['usage']!='input':continue
            target=projection/row['path'];target.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(HERE/'retained/selected-result.json' if row['path']=='certificates/selected-result.json' else ROOT/row['path'],target)
        loader.REPOSITORY=projection;loader.compatibility_controls()
        sys.path.insert(0,str(ROOT/'research/r437-carrier-integration'));import physical
        s=physical.source('D')
        import words,records,directory,macro_binding,numeric,layout,trace,packet_engine,packet,episode,oracle
        from cardinal_counts import Count
        from plan import Request
        # Oracle chart construction, outside encoded execution; no runtime field decoded.
        P=oracle.reduce_rational(s.spec.template.preparation,9);Pinv=oracle.inverse(P,9)
        def header(pivots):
            matrix=oracle.eye(64)
            for i,pivot in enumerate(pivots):
                j=i+2;matrix[i][i]=1;matrix[i][j]=1;matrix[j][i]=pivot-1;matrix[j][j]=pivot
            return matrix
        chart0=oracle.multiply(header([2,2]),Pinv,9)
        low=tuple(tuple(x%3 for x in row) for row in chart0)
        s.low=low;s.handle=physical.compiler.source_handle(s.cat,s.record['identifier'],True,low)
        s.spec=physical.compiler.resolve_handle(s.cat,s.specs,s.handle);s.plan=s.specs.plan(s.handle.code)
        need(s.spec.good and s.spec.template.rank==2,'actual alternate GOOD common low chart')
        def high(pivots):
            target=header(pivots);chart=oracle.multiply(target,Pinv,9)
            need(all(chart[i][j]%3==s.low[i][j] for i in range(64) for j in range(64)),'same actual compiled low class')
            H=[[(chart[i][j]-s.low[i][j])//3 for j in range(64)] for i in range(64)]
            need(any(x for row in H for x in row) and all(0<=x<3 for row in H for x in row),'canonical nonzero high chart')
            need(oracle.multiply(chart,P,9)==target,'independent prepared chart')
            inverse=oracle.inverse(target,9)
            projector=oracle.multiply([row[:2] for row in target],inverse[:2],9)
            need(oracle.good_pivots(projector,2,9)==pivots,'independent projector pivots')
            return H
        old_high=high([2,5]);current_highs=[high([2,5]),high([8,2])]
        weights=[[8,2],[5,8]]
        # directory.Odometer advances the last entry first: row-major big-endian base3.
        def ordinal(matrix):
            value=0
            for row in matrix:
                for digit in row:value=value*3+digit
            return value
        ordinals=[ordinal(H) for H in current_highs];need(ordinals[0]!=ordinals[1] and all(0<=i<3**4096 for i in ordinals),'two distinct full-cube indices')
        for index,H in zip(ordinals,current_highs):
            recovered=[]
            for _ in range(4096):index,digit=divmod(index,3);recovered.append(digit)
            need(index==0 and list(reversed(recovered))==sum(H,[]),'full index decoding')
        tapes=[];old_init=records.Tape.__init__
        def register(t):old_init(t);tapes.append(t)
        records.Tape.__init__=register
        ia=words.Arena(13,1024);ra=words.Arena(5,131072);modulus=ra.literal(9);ring=words.Ring(modulus)
        parent=records.Program.fixture(ia,ra,2048,2,((0,s.handle.code,2,0,0,0),),s.cat.codes.bits)
        fields=[]
        for H in current_highs:fields.extend([(s.handle.code,old_high),(s.handle.code,H)])
        all_fields=records.Fields.fixture(ia,ra,fields,s.cat.codes.bits)
        prefix_count=Count.literal(2);field_count=ia.literal(2)
        parent_runtime=NS(indices=ia,arena=ra,context=NS(ring=ring,q=3),program=parent,size=ia.literal(64),depth=ia.literal(1),binding=NS(codes=s.cat.codes))
        binding=object.__new__(macro_binding.SelectedBinding);binding.specifications=s.specs;binding.codes=s.cat.codes;binding.ambient=s.handle.code
        definition=NS(code=s.handle.code,plan=s.plan)
        before,gap,suffix=[Count.literal(1) for _ in range(3)]
        volume=9**4;initial=bytes(((i*17+i//3+7)^(i//5))&1 for i in range(2*volume));target_bits=bytes(((i*13+i//7+3)^(i//2))&1 for i in range(2*volume))
        source,target=records.Tape(),records.Tape()
        for bit in initial:source.append(bit)
        for bit in target_bits:target.append(bit)
        source.rewind();target.rewind()
        protected=[(t,bytes(t.cells),t.head) for t in [source,target,parent.tape,all_fields.tape,prefix_count.tape,before.tape,gap.tape,suffix.tape]]
        old_live=(set(ia.live),set(ra.live));old_tapes=set(map(id,tapes))
        def actions(m):return {k:getattr(m,k) for k in ('reads','writes','moves')}
        def record_actions():return {k:sum(getattr(t.meter,k) for t in tapes) for k in ('reads','writes','moves')}
        start=dict(record=record_actions(),index=actions(ia.meter),residue=actions(ra.meter))
        first=packet.read_prefix(all_fields.tape,field_count);all_fields.tape.rewind()
        try:produced=binding.child_program(parent_runtime,definition,NS(child_kind='good',field=0,reverse=False,half=False),first)
        finally:first.clear()
        # Same source/tag/rank makes the produced Program independent of the selected high fiber.
        copied=records.Tape();directory.append_tape(produced,copied);copied.rewind();need(bytes(copied.cells)==bytes(produced.cells),'actual produced Program handoff')
        child=NS(indices=ia,arena=ra,context=NS(ring=ring,q=3),binding=NS(codes=s.cat.codes),size=ia.literal(2),depth=ia.literal(2))
        child.program=macro_binding.view(records.Program,child,copied);incoming=binding.incoming(child)
        calls=[];runtime_controls=[]
        old_inspect=words.Word.inspect
        def coefficient(prefix,request):
            need(request.kind=='child' and request.child_kind=='good' and request.field==0 and not request.half and not request.reverse and request.reference is None and not request.reverse_adapter,'fixed GOOD bridge contract')
            coord=old_inspect(request.coordinate)
            raw=bytes(prefix.cells);which=None
            for i in range(2):
                if raw==prefix_bytes[i]:which=i
            need(which is not None,'actual selected complete prefix')
            value=incoming.coefficient(prefix,replace(request,kind='incoming'))
            expected=(-pow(weights[which][coord],-1,9))%9 if request.negative_inverse else weights[which][coord]
            need(old_inspect(value)==expected,'actual nonzero-high coordinate weight '+str((which,coord,old_inspect(value),expected)))
            calls.append(dict(prefix=which,coordinate=coord,negative_inverse=request.negative_inverse,value=expected))
            return value
        prefix_bytes=[]
        for _ in range(2):
            one=packet.read_prefix(all_fields.tape,field_count);prefix_bytes.append(bytes(one.cells));one.clear()
        all_fields.tape.rewind()
        if not probe:
            # Both represented complete prefixes use the actual child producer.
            second=records.Tape()
            for v in prefix_bytes[1][1:]:second.append(v)
            second.rewind()
            try:
                other=binding.child_program(parent_runtime,definition,NS(child_kind='good',field=0,reverse=False,half=False),second)
                need(bytes(other.cells)==bytes(produced.cells),'same produced metadata for distinct high prefix');other.clear()
            finally:second.clear()
            def reject_prefix(prefix,expected):
                coord=ia.literal(0);live=(set(ia.live),set(ra.live));saved=[(t,bytes(t.cells),t.head) for t in (prefix,copied,parent.tape)]
                try:
                    value=incoming.coefficient(prefix,Request('incoming',coord));ra.free(value)
                except ValueError as e:need(str(e)==expected,'actual rejection reason '+str(e))
                else:raise ValueError('invalid actual callback accepted')
                need(live==(set(ia.live),set(ra.live)),'rejecting callback numerical restoration')
                need(all((bytes(t.cells),t.head)==(raw,head) for t,raw,head in saved),'rejecting callback borrowed restoration')
                ia.free(coord);runtime_controls.append(expected)
            bad_high=[row[:] for row in old_high];bad_high[0][0]=3
            bad=records.Fields.fixture(ia,ra,[(s.handle.code,bad_high),(s.handle.code,current_highs[0])],s.cat.codes.bits)
            reject_prefix(bad.tape,'canonical high digit');bad.tape.clear()
            steps=[i for i,v in enumerate(copied.cells) if v==records.STEP]
            rank_bit=steps[-1]+1+(records.FINITE_BITS+1)+(s.cat.codes.bits+1)
            need(copied.cells[rank_bit]==0,'produced rank2 bit');copied.cells[rank_bit]=1
            valid=records.Tape()
            for v in prefix_bytes[0][1:]:valid.append(v)
            valid.rewind()
            try:reject_prefix(valid,'actual selected rank')
            finally:copied.cells[rank_bit]=0;valid.clear()
        if probe:
            one=packet.read_prefix(all_fields.tape,field_count);all_fields.tape.rewind();coord=ia.literal(0)
            try:
                value=coefficient(one,Request('child',coord,child_kind='good'));ra.free(value)
            finally:one.clear();ia.free(coord)
            return dict(status='PROBE_NONZERO_HIGH',first=calls)
        cols=ia.literal(1);geometry=numeric.Geometry(NS(dimension=2,rank=2),ia,cols,child.depth,s.handle.code,child.program)
        shape=layout.Layout(geometry,child.size,ring,3,before,gap,suffix)
        left,right,span=[ia.literal(x) for x in (0,2,2)];lifetime=[]
        words.Word.inspect=lambda _:(_ for _ in ()).throw(ValueError('runtime numerical decoding forbidden'))
        try:returned=packet_engine.run(source,trace.leaf(geometry,left,right,span,'good'),shape,all_fields.tape,prefix_count,field_count,coefficient,observe=lifetime.append)
        finally:words.Word.inspect=old_inspect
        need(returned is not source and lifetime==['enter','return'],'actual owned child return')
        need(len(calls)==24,'twelve actual callbacks per represented prefix')
        for i in range(2):
            one=[c for c in calls if c['prefix']==i];need([c['coordinate'] for c in one]==[0]*6+[1]*6,'per-prefix coordinate chronology')
        # Matrix product of the eight literal primitives gives x_i <- lambda_i*y_(1-i), y_(1-i) <- lambda_i^-1*x_i.
        def permutation(lambdas):
            out=[]
            for x0 in range(9):
             for x1 in range(9):
              for y0 in range(9):
               for y1 in range(9):
                a=lambdas[0]*y1%9;b=lambdas[1]*y0%9;c=pow(lambdas[1],-1,9)*x1%9;d=pow(lambdas[0],-1,9)*x0%9
                out.append(((a*9+b)*9+c)*9+d)
            need(sorted(out)==list(range(volume)),'complete finite permutation')
            return out
        maps=[permutation(row) for row in weights]
        # Explicit embedding/projection commutation on every represented coordinate.
        offsets=[n*volume for n in ordinals]
        for i,mapping in enumerate(maps):
            need(all((offsets[i]+j)//volume==ordinals[i] and (offsets[i]+j)%volume==j and
                     (offsets[i]+mapping[j])//volume==ordinals[i] for j in range(volume)),
                 'global selected-fiber offset and permutation intertwiner')
        expected=bytes(initial[i*volume+j] for i,m in enumerate(maps) for j in m)
        need(bytes(returned.cells[1:])==expected,'independent full two-fiber payload oracle')
        call=s.top.call(s.record['key'][1],s.record['key'][2]);position=s.record['position']+1;event=call.events[position]
        need(event[0]==1 and event[2]==87,'literal next SOURCE87 consumer')
        # Explicit selected-fiber restriction: actual full context has 3^4096 highs.
        consumer_highs=Count.literal(2);consumer_old=Count.literal(1);fibre=Count.literal(volume)
        consumer=episode.xor_packet(returned,target,NS(highs=consumer_highs),consumer_old,fibre)
        need(bytes(consumer.cells[1:])==bytes(a^b for a,b in zip(expected,target_bits)),'real XOR consumer uses computed return')
        controls=list(runtime_controls)
        module_spec=importlib.util.spec_from_file_location("r437_prefix_consumer_fusion_adapter",HERE/"adapter.py")
        adapter=importlib.util.module_from_spec(module_spec);module_spec.loader.exec_module(adapter)
        need(Path(adapter.__file__).resolve()==HERE/"adapter.py" and callable(adapter.run),"exact package-local fusion module")
        eager_calls=list(calls);calls.clear();returned_lengths=[]
        fuse_start=dict(record=record_actions(),index=actions(ia.meter),residue=actions(ra.meter))
        words.Word.inspect=lambda _:(_ for _ in ()).throw(ValueError('runtime numerical decoding forbidden'))
        try:
            fused=adapter.run(source,target,lambda:trace.leaf(geometry,left,right,span,'good'),
                shape,all_fields.tape,prefix_count,field_count,coefficient,
                NS(highs=consumer_highs),consumer_old,
                observe=lambda tape:returned_lengths.append(len(tape.cells)-1))
        finally:words.Word.inspect=old_inspect
        need(bytes(fused.cells)==bytes(consumer.cells),'actual fused/eager complete consumer bytes')
        need(returned_lengths==[volume,volume],'one complete local return at each consumer boundary')
        need(len(calls)==24 and calls!=eager_calls,'changed cross-prefix schedule with all callbacks retained')
        for i in range(2):
            need([c for c in calls if c['prefix']==i]==[c for c in eager_calls if c['prefix']==i],
                 'unchanged callback order within prefix')
        fused_sha=sha(bytes(fused.cells));fused.clear()
        fuse_end=dict(record=record_actions(),index=actions(ia.meter),residue=actions(ra.meter))
        fusion_invoice={lane:{k:fuse_end[lane][k]-fuse_start[lane][k] for k in fuse_end[lane]} for lane in fuse_end}
        # Front-end rejection is before expensive callback execution.
        bad_count=Count.literal(1)
        try:
            try:adapter.run(source,target,lambda:trace.leaf(geometry,left,right,span,'good'),
                    shape,all_fields.tape,bad_count,field_count,coefficient,NS(highs=consumer_highs),consumer_old)
            except ValueError as e:need(str(e)=='complete fused prefix product','count-product control reason')
            else:raise ValueError('missing prefix accepted')
        finally:bad_count.close()
        controls.append('encoded prefix product rejects omitted prefix before payload')
        try:adapter.run(source,source,lambda:trace.leaf(geometry,left,right,span,'good'),
                shape,all_fields.tape,prefix_count,field_count,coefficient,NS(highs=consumer_highs),consumer_old)
        except ValueError as e:need(str(e)=='distinct fused borrowed roles','borrowed alias control reason')
        else:raise ValueError('aliased dirty target accepted')
        controls.append('aliased source/dirty target rejected before payload')
        tiny_source,tiny_target,tiny_dir=records.Tape(),records.Tape(),records.Tape()
        for t in (tiny_source,tiny_target,tiny_dir):t.append(1);t.rewind()
        unit=Count.literal(1);one_field=ia.literal(1);tiny_saved=[(t,bytes(t.cells),t.head) for t in (tiny_source,tiny_target,tiny_dir)]
        try:
            try:adapter.run(tiny_source,tiny_target,lambda:iter(()),NS(fibre=lambda:Count.literal(1)),
                    tiny_dir,unit,one_field,lambda *_:None,NS(highs=unit),unit)
            except ValueError as e:need(str(e)=='complete fused raw prefix','truncated-prefix control reason')
            else:raise ValueError('truncated raw prefix accepted')
            need(all((bytes(t.cells),t.head)==(raw,head)for t,raw,head in tiny_saved),'truncated-prefix borrowed restoration')
        finally:
            unit.close();ia.free(one_field)
            for t in (tiny_source,tiny_target,tiny_dir):t.clear()
        controls.append('truncated raw-prefix reader clears owned counter/output and restores borrowed heads')
        dirty=records.Tape()
        for bit in returned.cells[1:]:dirty.append(bit)
        dirty.cells[1]^=1;dirty.rewind()
        corrupted=episode.xor_packet(dirty,target,NS(highs=consumer_highs),consumer_old,fibre)
        need(bytes(corrupted.cells)!=bytes(consumer.cells),'dirty child return reaches actual consumer')
        dirty.clear();corrupted.clear();controls.append('one-bit wrong return changes actual SOURCE87 consumer')
        stale=bytes(initial[i*volume+j] for i in range(2) for j in maps[0])
        need(stale!=expected,'stale first-prefix coefficients discriminated');controls.append('stale prefix0 coefficient vector changes second fiber')
        wrong_inverse_maps=[permutation([pow(v,-1,9) for v in row]) for row in weights]
        wrong=bytes(initial[i*volume+j] for i,m in enumerate(wrong_inverse_maps) for j in m)
        need(wrong!=expected,'wrong weight orientation discriminated');controls.append('inverse-weight substitution changes actual output')
        result=dict(status='PASS_R437_PREFIX_CONSUMER_FUSION',live_inputs=inputs,q=3,w=2,modulus=9,source_request=s.record['identifier'],source_identity=s.cat.source_identity,root_width=2048,child_width=2,selected_prefix_count=2,full_high_cube_count=integer(3**4096),global_high_indices=[integer(x) for x in ordinals],global_fiber_offsets=[integer(x) for x in offsets],weights=weights,eager_callback_calls=eager_calls,fused_callback_calls=calls,fused_consumer_sha256=fused_sha,local_child_return_lengths=returned_lengths,fusion_invoice=fusion_invoice,complete_fiber_bits=volume,total_executed_bits=2*volume,produced_program_sha256=sha(bytes(copied.cells)),return_sha256=sha(bytes(returned.cells)),consumer_sha256=sha(bytes(consumer.cells)),literal_consumer_event=event,literal_consumer_position=position,controls=controls,scope='Uniform source-bound prefix-major leaf/XOR composition, corroborated by actual two-prefix R437 payload; full high cube/root reachability and fixed-tape tariff unexecuted.')
        consumer.clear();consumer_highs.close();consumer_old.close();fibre.close();returned.clear();shape.close();geometry.close();ia.free_many(cols,left,right,span,child.size,child.depth);produced.clear();copied.clear()
        need(old_live==(set(ia.live),set(ra.live)),'complete child/consumer numerical ownership restored')
        need(all((bytes(t.cells),t.head)==(raw,head) for t,raw,head in protected),'all borrowed payload/metadata bytes and heads restored')
        need(all(t.head==1 and all(v==words.BLANK for v in t.cells[1:]) for t in tapes if id(t) not in old_tapes),'all owned record backing erased')
        finish=dict(record=record_actions(),index=actions(ia.meter),residue=actions(ra.meter));result['invoice']={lane:{k:finish[lane][k]-start[lane][k] for k in finish[lane]} for lane in finish}
        result.update(borrowed_preserved=True,owned_erased=True,full_high_cube_executed=False,numerical_admitted=False)
        records.Tape.__init__=old_init
        return result

def main():
    p=argparse.ArgumentParser();p.add_argument('--write',action='store_true');p.add_argument('--probe',action='store_true');args=p.parse_args();result=run(args.probe)
    if args.probe:print(json.dumps(result));return
    if args.write:(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(json.dumps(json.loads((HERE/'RESULT.json').read_text()),sort_keys=True)==json.dumps(result,sort_keys=True),'typed deterministic receipt')
    print(result['status'])
if __name__=='__main__':main()
