#!/usr/bin/env python3
"""Complete high-cube producer/actual leaf/XOR differential and role controls.

JoyboyBrian; substantial OpenAI Codex assistance; Apache-2.0.
"""
import argparse,hashlib,importlib.util,itertools,json,shutil,sys
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace as NS
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[1]
def need(ok,message):
    if not ok:raise ValueError(message)
def sha(b):return hashlib.sha256(b).hexdigest()
def module(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m

def authenticate():
    m=json.loads((HERE/'SOURCES.json').read_text())
    for row in m['files']:
        if row['usage']=='input':need(sha((ROOT/row['path']).read_bytes())==row['sha256'],'source hash '+row['path'])
    for row in m['retained']:need(sha((HERE/row['path']).read_bytes())==row['sha256'],'retained hash '+row['path'])
    return sum(x['usage']=='input'for x in m['files'])
def run():
    inputs=authenticate();sys.path.insert(0,str(ROOT/'research/selected-bit-physical-caller'));import loader
    with TemporaryDirectory(prefix='r437-stream-source-')as t:
        projection=Path(t)
        for row in json.loads((loader.CALLER/'SOURCES.json').read_text())['files']:
            if row['usage']!='input':continue
            f=projection/row['path'];f.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(HERE/'retained/selected-result.json'if row['path']=='certificates/selected-result.json'else ROOT/row['path'],f)
        loader.REPOSITORY=projection;loader.compatibility_controls();loader.activate()
        import words,records,directory,numeric,layout,trace,packet_engine,episode,packet
        from cardinal_counts import Count
        from stream import Counter
        streaming=module('r437_streaming_directory',HERE/'streaming.py')
        tapes=[];old_init=records.Tape.__init__
        def register(tape):old_init(tape);tapes.append(tape)
        records.Tape.__init__=register
        try:
            ia,ra=words.Arena(8,1024),words.Arena(5,1024)
            modulus=ra.literal(9);ring=words.Ring(modulus)
            codes=NS(q=3,dimension=2,limit=16,bits=4);context=directory.Context(ring,codes)
            fields=ia.literal(1);count=Count.literal(3);old=records.Tape()
            histories=[(3,[[0,1],[2,0]]),(4,[[2,0],[0,1]]),(3,[[0,1],[2,0]])]
            def field_bytes(code,matrix):
                out=[(code>>i)&1 for i in range(codes.bits)]+[records.WORD_END]
                for row in matrix:
                    for x in row:out.extend([(x>>i)&1 for i in range(ra.bits)]+[records.WORD_END])
                return bytes(out+[records.RECORD_END])
            for code,H in histories:
                for b in field_bytes(code,H):old.append(b)
            old.rewind();saved=(bytes(old.cells),old.head)
            original,expected=directory.produce(old,fields,count,5,context)
            received=[];prefix_ids=set();allocations=[];prefix_lengths=[]
            live=(set(ia.live),set(ra.live));before=len(tapes)
            def consume(prefix):
                received.append(bytes(prefix.cells[1:]));prefix_ids.add(id(prefix));allocations.append(len(tapes));prefix_lengths.append(len(prefix.cells)-1)
            observed=streaming.visit(old,fields,count,5,context,consume)
            need(all(x==allocations[0]for x in allocations),'no record Tape construction inside any emission iteration')
            need(len(prefix_ids)==1 and len(received)==243,'one reusable current-prefix role and exact C*H')
            oracle=[field_bytes(code,H)+field_bytes(5,[list(v[:2]),list(v[2:])])
                    for code,H in histories for v in itertools.product(range(3),repeat=4)]
            need(received==oracle and bytes(original.cells[1:])==b''.join(oracle),'complete byte/order/multiplicity differential')
            need(received[:81]==received[162:]and received[:81]!=received[81:162],'physical repeated prefixes retained')
            need(observed.equals(expected),'complete encoded prefix product')
            original.clear();expected.close();observed.close()
            need((set(ia.live),set(ra.live))==live and(bytes(old.cells),old.head)==saved,'producer borrowed and numerical restoration')
            need(all(t.head==1 and all(b==words.BLANK for b in t.cells[1:])for t in tapes[before:]),'all producer owned backing erased')
            # Actual source leaf and actual XOR consumer on all 243 complete prefixes.
            program=object();columns,depth,parent=[ia.literal(x)for x in(1,0,1)]
            geometry=numeric.Geometry(NS(dimension=1,rank=1),ia,columns,depth,5,program)
            one=Count.literal(1);shape=layout.Layout(geometry,parent,ring,3,one,one,one)
            left,right,width=[ia.literal(x)for x in(0,1,1)]
            volume=81;size=243*volume
            initial=bytes(((i*17+i//7)^(i//3))&1 for i in range(size));target_bits=bytes(((i*13+i//5)^(i//11))&1 for i in range(size))
            source,target=records.Tape(),records.Tape()
            for b in initial:source.append(b)
            for b in target_bits:target.append(b)
            source.rewind();target.rewind()
            borrowed=[(t,bytes(t.cells),t.head)for t in(source,target,old,count.tape,context.highs.tape)]
            borrowed_words=[(v,bytes(v.cells),v.head)for v in(modulus,ring.one,fields)]
            protected_live=(set(ia.live),set(ra.live));calls=[0]
            def coefficient(prefix,request):
                prefix.rewind();value=ra.zero()
                try:
                    for f in range(2):
                        code=records.read_finite(prefix,codes.bits);need(code<codes.limit,'fixture source code')
                        for i in range(4):
                            digit=records.read_word(prefix,ra)
                            if i==0:
                                following=ring.add(value,digit);ra.free(value);value=following
                            ra.free(digit)
                        need(prefix.read()==records.RECORD_END,'fixture field end');prefix.step(1)
                    need(prefix.read()==words.BLANK,'complete fixture prefix')
                    three=ring.literal(3);multiple=ring.multiply(value,three);ra.free_many(value,three)
                    value=ring.add(multiple,ring.one);ra.free(multiple)
                    if request.negative_inverse:
                        inverse=ring.inverse(value);ra.free(value);need(inverse is not None,'fixture unit coefficient')
                        value=ring.negate(inverse);ra.free(inverse)
                    calls[0]+=1;return value
                finally:prefix.rewind()
            full,full_count=directory.produce(old,fields,count,5,context)
            emitted_fields=ia.literal(2);fibre=Count.literal(volume);baseline=None
            inspect=words.Word.inspect;words.Word.inspect=lambda _:(_ for _ in()).throw(ValueError('runtime decode forbidden'))
            try:
                eager=packet_engine.run(source,trace.leaf(geometry,left,right,width,'good'),shape,full,full_count,emitted_fields,coefficient)
                baseline=episode.xor_packet(eager,target,context,count,fibre);eager.clear()
                eager_calls=calls[0];calls[0]=0
                streamed=streaming.run(source,target,lambda:trace.leaf(geometry,left,right,width,'good'),shape,old,fields,count,5,context,coefficient)
            finally:words.Word.inspect=inspect
            need(calls[0]==eager_calls==1458,'all six callbacks per complete prefix retained')
            need(bytes(streamed.cells)==bytes(baseline.cells),'actual complete producer/leaf/XOR equivalence')
            output_oracle=bytearray();index=0
            for _,oldH in histories:
                for digits in itertools.product(range(3),repeat=4):
                    lam=(1+3*(oldH[0][0]+digits[0]))%9
                    for x in range(9):
                        for y in range(9):
                            j=(lam*y%9)*9+(pow(lam,-1,9)*x%9)
                            output_oracle.append(initial[index*volume+j]^target_bits[index*volume+x*9+y])
                    index+=1
            need(bytes(streamed.cells[1:])==bytes(output_oracle),'independent complete payload permutation/XOR')
            output_sha=sha(bytes(streamed.cells));streamed.clear();baseline.clear();full.clear();full_count.close();fibre.close();ia.free(emitted_fields)
            need(all((bytes(t.cells),t.head)==(raw,head)for t,raw,head in borrowed),'all borrowed packet/directory/Count bytes and heads')
            need(all((bytes(v.cells),v.head)==(raw,head)for v,raw,head in borrowed_words),'borrowed Ring/index words')
            need(protected_live==(set(ia.live),set(ra.live)),'actual consumer numerical restoration')
            # Guard controls cover complete records, not arbitrary malformed Word rollback.
            def reject(code,old_count,message,expected_callbacks):
                pre=len(tapes);live=(set(ia.live),set(ra.live));seen=[0]
                def observed(_):seen[0]+=1
                try:streaming.visit(old,fields,old_count,code,context,observed)
                except ValueError as error:need(str(error)==message,'source guard reason '+str(error))
                else:raise ValueError('invalid streamed directory accepted')
                need(seen[0]==expected_callbacks,'guard callback boundary')
                need((set(ia.live),set(ra.live))==live and old.head==1,'guard borrowed/numerical restoration')
                need(all(t.head==1 and all(b==words.BLANK for b in t.cells[1:])for t in tapes[pre:]),'guard producer backing cleanup')
            reject(codes.limit,count,'new compiled source code',0)
            first_digit=1+codes.bits+1
            original_digit=bytes(old.cells[first_digit:first_digit+ra.bits])
            old.cells[first_digit:first_digit+ra.bits]=bytes([1,1]+[0]*(ra.bits-2))
            try:reject(5,count,'old high digit range',0)
            finally:old.cells[first_digit:first_digit+ra.bits]=original_digit;old.rewind()
            missing=Count.literal(2)
            try:reject(5,missing,'complete streamed raw directory',162)
            finally:missing.close()
            need((bytes(old.cells),old.head)==saved,'guard old bytes restored')
            # A callback failure retires producer-owned stores without claiming child rollback.
            fail=RuntimeError('stop after a complete prefix');pre=len(tapes);protected=(set(ia.live),set(ra.live))
            try:streaming.visit(old,fields,count,5,context,lambda _:(_ for _ in()).throw(fail))
            except RuntimeError as error:need(error is fail,'original callback failure identity')
            else:raise ValueError('callback failure ignored')
            need(protected==(set(ia.live),set(ra.live))and(bytes(old.cells),old.head)==saved,'callback producer restoration')
            need(all(t.head==1 and all(b==words.BLANK for b in t.cells[1:])for t in tapes[pre:]),'callback failure producer backing cleanup')
            shape.close();geometry.close();ia.free_many(columns,depth,parent,left,right,width);one.close()
            source.clear();target.clear();old.clear();count.close();ia.free(fields);context.close();ring.close();ra.free(modulus)
            need(not ia.live and not ra.live,'complete fixture numeric disposal')
            need(all(t.head==1 and all(b==words.BLANK for b in t.cells[1:])for t in tapes),'complete owned record disposal')
            return dict(status='PASS_R437_STREAMING_DIRECTORY',live_inputs=inputs,
                producer=dict(q=3,w=2,dimension=2,old_physical_prefixes=3,highs=81,emitted=243,
                    one_current_prefix_role=True,no_record_constructor_in_emission_loop=True,
                    directory_bytes=243*60,max_current_prefix_bytes=max(prefix_lengths),sha256=sha(b''.join(oracle))),
                complete_consumer=dict(prefixes=243,fibre_bits=81,packet_bits=size,callbacks=eager_calls,
                    actual_leaf_and_xor=True,word_inspect_disabled=True,output_sha256=output_sha),
                controls=['duplicate physical prefixes retained','nonzero high-cube order','independent complete payload oracle',
                    'callback failure clears fixed producer stores','invalid new code rejected before callbacks',
                    'complete out-of-range old high rejected with cleanup','omitted physical prefix rejected after162 callbacks'],
                scope='Complete generic high cube and actual source leaf/XOR consumer; production GL64 and total physical reserve remain unproved.')
        finally:records.Tape.__init__=old_init

def main():
    a=argparse.ArgumentParser();a.add_argument('--write',action='store_true');args=a.parse_args();result=run()
    if args.write:(HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    else:need(json.dumps(json.loads((HERE/'RESULT.json').read_text()),sort_keys=True)==json.dumps(result,sort_keys=True),'typed deterministic receipt')
    print(result['status'])
if __name__=='__main__':main()
