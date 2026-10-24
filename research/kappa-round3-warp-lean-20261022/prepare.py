"""Derive fresh Lean certificates for the frozen joint helper/map construction.
Source generators: Cao Yifan's PR4610. Apache-2.0; substantial OpenAI assistance.
"""
from pathlib import Path
from hashlib import sha256
import contextlib,importlib.util,io,json,sys
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[1]
OLD=ROOT/'research/kappa-lean-verification-20261022';SOURCE=ROOT/'research/kappa-round3-warp-20261022'
def write(name,s): (HERE/name).write_text(s,encoding='utf-8',newline='\n')
def sub(s,a,b,n=1):
    assert s.count(a)==n,(a,s.count(a),n)
    return s.replace(a,b)
def load(p,n):
    sp=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(sp);sys.modules[n]=m;sp.loader.exec_module(m);return m
def main():
    freeze=json.loads((SOURCE/'ACTUAL-WORD-FREEZE.json').read_text(encoding='utf-8'))
    arithmetic=json.loads((SOURCE/'ARITHMETIC.json').read_text(encoding='utf-8'))
    write('NativeCore.lean',(OLD/'NativeCore.lean').read_text(encoding='utf-8'))
    s=(OLD/'native_generate.py').read_text(encoding='utf-8')
    s=sub(s,"'research/warp-interface-20261022'","'research/kappa-round3-warp-20261022'")
    s=sub(s,'4409d2d9328fffbd276bb03fb800f59a33ec3b2ab15f79a330a7af66e75110cc',freeze['canonical_payload_sha256'])
    a=s.index('    sys.path.insert(0, str(SOURCE))\n    from verify_candidate import inputs')
    z=s.index('    frames = c[\'frames\']',a)
    s=s[:a]+'''    oldraw = gzip.decompress((ROOT/'research/warp-interface-20261022/ACTUAL-WORD.json.gz').read_bytes())
    assert sha256(oldraw).hexdigest() == '4409d2d9328fffbd276bb03fb800f59a33ec3b2ab15f79a330a7af66e75110cc'
    base = json.loads(oldraw)['canonical']
    programs = payload['programs']
'''+s[z:]
    s=sub(s,'assert len(new_paid) == len(set(new_paid)) == 128','assert len(new_paid) == len(set(new_paid))')
    a=s.index('        body = [header.replace(\'import NativeCore\',\'import NativeData\')]')
    z=s.index("        terminal='backwardFinalFrames'",a)
    s=s[:a]+'''        # Both orientations are sharded; every event still carries a kernel proof.
        shard_count=8
        names=[];parts=[[header.replace('import NativeCore','import NativeData')] for _ in range(shard_count)]
        for shard,part in enumerate(parts):
            begin=shard*len(chunks)//shard_count;end=(shard+1)*len(chunks)//shard_count
            for i in range(begin,end+1):
                snapshot=chunks[i][0] if i<len(chunks) else chunks[-1][1]
                part += [f'def {direction}Shard{shard}State{i:03d} : Table Nat := '+tree(snapshot)+'\\n']
            for i in range(begin,end):
                start,endstate,es,census,cost=chunks[i]
                name=f'{direction}_{i:03d}';names.append(name)
                prefix=f'{direction}Shard{shard}State'
                part += [f'def {name} : CheckedSegment frames paid warps :=\\n',
                    f'  ⟨⟨{prefix}{i:03d}, {prefix}{i+1:03d},\\n    [\\n']
                part += ['      ⟨'+','.join(map(str,e))+'⟩,\\n' for e in es]
                part += ['    ],'+arr(census)+f',{cost}⟩, by decide⟩\\n']
            part += [f'#eval "Native{direction.title()}Proofs{shard} checked"\\nend NativeData\\n']
            write(f'Native{direction.title()}Proofs{shard}.lean',''.join(part))
        body=[header.replace('import NativeCore','\\n'.join(f'import Native{direction.title()}Proofs{j}' for j in range(shard_count)))]
        if direction=='backward':
            body += ['def backwardFinalFrames : Table Nat := '+tree(c['final']+[state[632]])+'\\n',
                'theorem backward_persistent_final_matches : backwardFinalFrames.toList.take 632 = finalFrames.toList.take 632 := by decide\\n']
'''+s[z:]
    s=sub(s,'#[0,2201,412,506,135,36,0,0,8,0]','#[0,2201,412,510,127,40,0,0,8,0]')
    write('native_generate.py',s)
    s=(OLD/'numerical_generate.py').read_text(encoding='utf-8')
    s=sub(s,'Q(302153, 100000000)','Q(302177, 100000000)')
    s=sub(s,"ROOT/'research/kappa-interface-round2-20261022/ARITHMETIC.json'","ROOT/'research/kappa-round3-warp-20261022/ARITHMETIC.json'")
    write('numerical_generate.py',s)
    s=(OLD/'generate_arithmetic.py').read_text(encoding='utf-8')
    s=sub(s,"ROOT/'research/kappa-interface-round2-20261022/ARITHMETIC.json'","ROOT/'research/kappa-round3-warp-20261022/ARITHMETIC.json'")
    s=sub(s,'37769/12500000','9443/3125000')
    s=sub(s,'3020165/1000000000','37769/12500000')
    write('generate_arithmetic.py',s)
    write('CompilerCapacity.lean',(OLD/'CompilerCapacity.lean').read_text(encoding='utf-8').replace('302153 / 100000000','302177 / 100000000'))
    aggregate=(OLD/'KappaWarpVerification.lean').read_text(encoding='utf-8')
    for a,b in [('37769 / 12500000','9443 / 3125000'),('3020165 / 1000000000','37769 / 12500000'),('302153 / 100000000','302177 / 100000000'),('99697847 / 100000000','99697823 / 100000000'),('119697847 / 100000000','119697823 / 100000000'),('#[0,2201,412,506,135,36,0,0,8,0]','#[0,2201,412,510,127,40,0,0,8,0]')]:
        assert a in aggregate,a
        aggregate=aggregate.replace(a,b)
    write('KappaWarpVerification.lean',aggregate)
    load(HERE/'numerical_generate.py','joint3_numerical_generator').main()
    load(HERE/'generate_arithmetic.py','joint3_outer_generator').main()
    if (SOURCE/'PHASE-VALIDATION.json.gz').exists():
        with contextlib.redirect_stdout(io.StringIO()) as out:load(HERE/'native_generate.py','joint3_native_generator').main()
        manifest=json.loads(out.getvalue());write('NATIVE-TRANSCRIPTION.json',json.dumps(manifest,indent=2,sort_keys=True)+'\n')
        s=(OLD/'Native.lean').read_text(encoding='utf-8')
        s=s.replace('paidEntries.length = 2863',f"paidEntries.length = {manifest['paid_classes']}")
        s=s.replace('newPaidIndices.size = 128',f"newPaidIndices.size = {manifest['new_paid_classes']}")
        s=s.replace('exactly_34_operator_changes','exactly_20_operator_changes').replace(') 0 = 34',') 0 = 20')
        s=s.replace('all_128_new_paid_indices','all_new_paid_indices')
        s=s.replace('#[0,2201,412,506,135,36,0,0,8,0]','#[0,2201,412,510,127,40,0,0,8,0]')
        assert manifest['changed_operators']==20
        write('Native.lean',s)
        print('GENERATED_FRESH_NATIVE',manifest)
    else:print('Native generation awaits phase admission')
if __name__=='__main__':main()
