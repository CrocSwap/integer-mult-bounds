"""Transcribe the frozen native word into ordinary-kernel Lean certificates.

No generated result is trusted: every frame, span witness, inverse, event,
intermediate frame state, and invoice is rechecked by NativeCore.lean.
The Python/hash/JSON-to-Lean transcription boundary is stated in Native-note.md.
"""
from collections import Counter
from fractions import Fraction
import gzip
from hashlib import sha256
import json
from pathlib import Path
import argparse
import subprocess
import sys
import tomllib

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / 'research/kappa-round3-warp-20261022'
EXPECTED = 'cfcd36b40326d7a5815e1db5313444379b3fb756b27d5201c561574c085cc0dd'
CHUNK = 128


def arr(xs):
    return '#[' + ','.join(map(str, xs)) + ']'


def lis(xs):
    return '[' + ','.join(map(str, xs)) + ']'


def tree(xs):
    if not xs:
        return '.empty'
    if len(xs) == 1:
        return '(.leaf (' + str(xs[0]) + '))'
    cut = len(xs)//2
    return f'(.branch {cut} {tree(xs[:cut])} {tree(xs[cut:])})'


def table_declarations(name, typ, values):
    chunks=[]; out=[]
    for i in range(0,len(values),64):
        label=f'{name}Part{i//64:03d}'; part=values[i:i+64]
        out += [f'def {label} : Table {typ} :=\n'+tree(part)+'\n']
        chunks.append((len(part),label))
    def join(parts):
        if len(parts)==1:
            return parts[0]
        cut=len(parts)//2
        n,l=join(parts[:cut]);m,r=join(parts[cut:])
        return n+m,f'(.branch {n} {l} {r})'
    _,root=join(chunks)
    return out+[f'def {name} : Table {typ} :=\n'+root+'\n']


def list_declarations(name, typ, values, batch=64):
    out=[];labels=[]
    for i in range(0,len(values),batch):
        label=f'{name}Part{i//batch:03d}';labels.append(label)
        out += [f'def {label} : List {typ} := [\n',
                ',\n'.join('  '+v for v in values[i:i+batch]),'\n]\n']
    out += [f'def {name} : List {typ} := '+lis(labels)+'.flatten\n',
            '#eval "NativeData: '+name+' checked"\n']
    return out


def sharded_declarations(header, module, name, typ, values, batch, shards=4):
    files=[[header] for _ in range(shards)];labels=[]
    for i in range(0,len(values),batch):
        j=i//batch;label=f'{name}Part{j:03d}';labels.append(label)
        files[j%shards] += [f'def {label} : List {typ} := [\n',
            ',\n'.join('  '+v for v in values[i:i+batch]),'\n]\n']
    for j,body in enumerate(files):
        body += ['#eval "'+module+str(j)+' checked"\nend NativeData\n']
        write(module+str(j)+'.lean',''.join(body))
    return [f'def {name} : List {typ} := '+lis(labels)+'.flatten\n']


def combo(basis, mask):
    v = 0
    for i, b in enumerate(basis):
        if mask >> i & 1:
            v ^= b
    return v


def all_coordinates(basis):
    result = {combo(basis, mask): mask for mask in range(1 << len(basis))}
    assert len(result) == 1 << len(basis)
    return result


def allowance(e):
    kind, _, _, _, _, _, _, num, den = e
    if kind in (6, 7):
        return 2
    q = Fraction(num, den)
    n, d = abs(q.numerator), q.denominator
    assert n and not d & (d - 1)
    if kind == 5:
        assert not n & (n - 1)
        return 2 * (abs(n.bit_length() - d.bit_length()) + (q < 0))
    return 2 * (3 + n.bit_length() - 1 + n.bit_count() + d.bit_length() - 1)


def write(name, content):
    (HERE / name).write_text(content, encoding='utf-8', newline='\n')


def main():
    raw = gzip.decompress((SOURCE / 'ACTUAL-WORD.json.gz').read_bytes())
    assert sha256(raw).hexdigest() == EXPECTED
    payload = json.loads(raw)
    c = payload['canonical']
    # Reuse the exact authenticated inherited constructor solely to transcribe
    # old G columns for the finite changed-operator comparison.
    oldraw = gzip.decompress((ROOT/'research/warp-interface-20261022/ACTUAL-WORD.json.gz').read_bytes())
    assert sha256(oldraw).hexdigest() == '4409d2d9328fffbd276bb03fb800f59a33ec3b2ab15f79a330a7af66e75110cc'
    base = json.loads(oldraw)['canonical']
    programs = payload['programs']
    frames = c['frames']
    coordinates = list(map(all_coordinates, frames))
    old_g = {w['op']: w['G_columns'] for w in base['warps']}
    operators = []
    for w in sorted(c['warps'], key=lambda w: w['op']):
        direct = w['G_columns']
        invmap = all_coordinates(direct)
        inverse = [invmap[1 << i] for i in range(9)]
        assert all(combo(inverse, combo(direct, x)) == x for x in range(512))
        operators.append((direct, inverse, old_g[w['op']]))
    assert len(operators) == 72
    paid_keys = sorted({(e[3] if e[0] == 'climb' else e[2],
                         e[4] if e[0] == 'climb' else e[3],
                         e[5] if e[0] == 'climb' else e[4], e[0] == 'climb')
                        for p in programs.values() for e in p
                        if e[0] in ('climb', 'center')})
    paid_index = {key: i for i, key in enumerate(paid_keys)}
    paid = []
    for a, b, r, ascending in paid_keys:
        if ascending:
            src, dst = a, b
        else:
            # Centers may go up or down; the ascending flag describes the
            # actual inclusion, not which allocation owns the field.
            ascending = len(frames[a]) < len(frames[b])
            src, dst = (a, b) if ascending else (b, a)
        assert len(frames[src]) + r == len(frames[dst])
        paid.append((a, b, r, ascending, [coordinates[dst][v] for v in frames[src]]))
    warp_keys = sorted({(e[2], e[3], e[4]) for p in programs.values()
                        for e in p if e[0] == 'warp'})
    warp_index = {key: i for i, key in enumerate(warp_keys)}
    warps = []
    for op, a, b in warp_keys:
        direct, inverse, _ = operators[abs(op) - 1]
        if op < 0:
            direct, inverse = inverse, direct
        assert len(frames[a]) == len(frames[b])
        warps.append((op, a, b,
            [coordinates[b][combo(direct, v)] for v in frames[a]],
            [coordinates[a][combo(inverse, v)] for v in frames[b]]))
    phase = json.loads(gzip.decompress((SOURCE / 'PHASE-VALIDATION.json.gz').read_bytes()))
    assert len(warps) == len(phase['actual_warp_classes']) == 180
    assert warp_keys == [(w['operator'], w['input'], w['output']) for w in phase['actual_warp_classes']]
    new_paid = []
    for e in phase['new_paid_pairs']:
        key = (e['input'], e['output'], e['rank'], True)
        new_paid.append(paid_index[key])
    assert len(new_paid) == len(set(new_paid))
    helpers = []
    for role in range(224,632):
        a,b = c['start'][role],c['final'][role]
        rank = len(frames[b])-len(frames[a])
        assert rank > 0
        helpers.append((a,b,rank,[coordinates[b][v] for v in frames[a]]))
    header = ('-- Generated by native_generate.py from canonical payload SHA256\n'
              '-- ' + EXPECTED + '\nimport NativeCore\n'
              'set_option maxRecDepth 100000\nset_option maxHeartbeats 0\n'
              'namespace NativeData\nopen NativeCertificate\n')
    rawdata = [header]
    rawdata += table_declarations('frames','Basis',[arr(b) for b in frames])
    rawdata += ['#eval "NativeRaw: frame table elaborated"\n']
    rawdata += table_declarations('operators','Operator',['⟨'+','.join(arr(x) for x in g)+'⟩' for g in operators])
    rawdata += ['#eval "NativeRaw: operator table elaborated"\n']
    rawdata += table_declarations('paid','Paid',['⟨'+f'{a},{b},{r},{str(up).lower()},{arr(cs)}'+'⟩' for a,b,r,up,cs in paid])
    rawdata += ['#eval "NativeRaw: paid table elaborated"\n']
    rawdata += table_declarations('warps','Warp',['⟨'+f'{op},{a},{b},{arr(cs)},{arr(ds)}'+'⟩' for op,a,b,cs,ds in warps])
    rawdata += ['#eval "NativeRaw: warp table elaborated"\n',
       'theorem raw_tables_well_formed : frames.wellFormed && operators.wellFormed && paid.wellFormed && warps.wellFormed = true := by decide\n',
       'end NativeData\n']
    write('NativeRaw.lean',''.join(rawdata))
    # Each declaration carries an ordinary `decide` proof; proof construction
    # is segmented so a failed finite item has a local diagnostic.
    shardheader=header.replace('import NativeCore','import NativeRaw')
    imports='\n'.join(f'import NativeFrames{j}\nimport NativeOperators{j}' for j in range(4))
    out = [header.replace('import NativeCore',imports)]
    out += ['deriving instance DecidableEq for Operator\n',
            'deriving instance DecidableEq for Paid\n',
            'deriving instance DecidableEq for Warp\n']
    out += sharded_declarations(shardheader,'NativeFrames','frameEntries','CheckedBasis',
        ['⟨'+arr(b)+', by decide⟩' for b in frames],64)
    out += ['theorem frame_transcription_exact : frameEntries.map (·.data) = frames.toList := by decide\n']
    out += sharded_declarations(shardheader,'NativeOperators','operatorEntries','CheckedOperator',
        ['⟨⟨'+','.join(arr(x) for x in g)+'⟩, by decide⟩' for g in operators],2)
    out += ['theorem operator_transcription_exact : operatorEntries.map (·.data) = operators.toList := by decide\n']
    out += list_declarations('paidEntries','(CheckedPaid frames)',[
        '⟨⟨'+f'{a},{b},{r},{str(up).lower()},{arr(cs)}'+'⟩, by decide⟩' for a,b,r,up,cs in paid])
    out += ['theorem paid_transcription_exact : paidEntries.map (·.data) = paid.toList := by decide\n']
    out += list_declarations('warpEntries','(CheckedWarp frames operators)',[
        '⟨⟨'+f'{op},{a},{b},{arr(cs)},{arr(ds)}'+'⟩, by decide⟩' for op,a,b,cs,ds in warps],32)
    out += ['theorem warp_transcription_exact : warpEntries.map (·.data) = warps.toList := by decide\n']
    out += list_declarations('helperEntries','(CheckedPaid frames)',[
        '⟨⟨'+f'{a},{b},{r},true,{arr(cs)}'+'⟩, by decide⟩' for a,b,r,cs in helpers])
    out += [
            'def newPaidIndices : Array Nat := ' + arr(new_paid) + '\n',
            'def initialFrames : Table Nat := ' + tree(c['start'] + [len(frames)]) + '\n',
            'def finalFrames : Table Nat := ' + tree(c['final'] + [next(e[2] for e in reversed(programs['forward']) if e[0] == 'scalar' and e[1][0] == 'clear')]) + '\n',
            'end NativeData\n']
    write('NativeData.lean', ''.join(out))
    phase_labels = {x: i for i, x in enumerate(sorted({e[1] for p in programs.values()
                                                    for e in p if e[0] == 'phase'}))}
    adapter_labels = {x: i for i, x in enumerate(sorted({e[1] for p in programs.values()
                                                      for e in p if e[0] == 'adapter'}))}
    def role(r):
        assert r[0] == 'L' or r == ['C', 0]
        return r[1] if r[0] == 'L' else 632
    def encode(e):
        k = e[0]
        if k == 'phase': return [0,0,0,0,0,0,phase_labels[e[1]],0,1]
        if k == 'adapter': return [8,e[2],0,e[3],0,0,adapter_labels[e[1]],0,1]
        if k in ('climb', 'center'):
            a,b,r = e[3:6] if k == 'climb' else e[2:5]
            return [1 if k == 'climb' else 2,e[2] if k == 'climb' else 632,0,a,b,
                    paid_index[a,b,r,k == 'climb'],0,0,1]
        if k == 'warp':
            _,r,op,a,b = e
            return [3,role(r),0,a,b,warp_index[op,a,b],op,0,1]
        assert k == 'scalar'
        g,f = e[1:]
        kind = {'add':4,'scale':5,'clear':6,'copy':7}[g[0]]
        target = role(g[1]); source = role(g[2]) if kind in (4,7) else 0
        num,den = (g[3:5] if kind == 4 else g[2:4]) if kind in (4,5) else (0,1)
        return [kind,target,source,f,0,0,0,num,den]
    summaries = {}
    for direction, program in programs.items():
        events = list(map(encode, program))
        state = c['start'] + [len(frames)]
        chunks = []
        for i in range(0, len(events), CHUNK):
            es = events[i:i+CHUNK]
            start = state.copy(); census = [0]*10; cost = 0
            for e in es:
                kind,r,s,a,b,ref,op,num,den = e
                if kind in (0,8): continue
                if kind == 6: state[r] = a
                else:
                    assert state[r] == a, (direction,i,e,state[r])
                    if kind in (4,7): assert state[s] == a
                    if kind in (1,2,3): state[r] = b
                if kind in (1,2): census[paid[ref][2]] += 1
                if kind in (4,5,6,7): cost += allowance(e)
            chunks.append((start,state.copy(),es,census,cost))
        assert state[:632] == c['final']
        # Both orientations are sharded; every event still carries a kernel proof.
        shard_count=8
        names=[];parts=[[header.replace('import NativeCore','import NativeData')] for _ in range(shard_count)]
        for shard,part in enumerate(parts):
            begin=shard*len(chunks)//shard_count;end=(shard+1)*len(chunks)//shard_count
            for i in range(begin,end+1):
                snapshot=chunks[i][0] if i<len(chunks) else chunks[-1][1]
                part += [f'def {direction}Shard{shard}State{i:03d} : Table Nat := '+tree(snapshot)+'\n']
            for i in range(begin,end):
                start,endstate,es,census,cost=chunks[i]
                name=f'{direction}_{i:03d}';names.append(name)
                prefix=f'{direction}Shard{shard}State'
                part += [f'def {name} : CheckedSegment frames paid warps :=\n',
                    f'  ⟨⟨{prefix}{i:03d}, {prefix}{i+1:03d},\n    [\n']
                part += ['      ⟨'+','.join(map(str,e))+'⟩,\n' for e in es]
                part += ['    ],'+arr(census)+f',{cost}⟩, by decide⟩\n']
            part += [f'#eval "Native{direction.title()}Proofs{shard} checked"\nend NativeData\n']
            write(f'Native{direction.title()}Proofs{shard}.lean',''.join(part))
        body=[header.replace('import NativeCore','\n'.join(f'import Native{direction.title()}Proofs{j}' for j in range(shard_count)))]
        if direction=='backward':
            body += ['def backwardFinalFrames : Table Nat := '+tree(c['final']+[state[632]])+'\n',
                'theorem backward_persistent_final_matches : backwardFinalFrames.toList.take 632 = finalFrames.toList.take 632 := by decide\n']
        terminal='backwardFinalFrames' if direction=='backward' else 'finalFrames'
        body += [f'def {direction}Segments : List (CheckedSegment frames paid warps) :=\n  '+lis(names)+'\n',
                 f'def {direction}Data : List Segment := {direction}Segments.map (·.data)\n',
                 f'theorem {direction}_linked : linked initialFrames {terminal} {direction}Data = true := by decide\n',
                 f'theorem {direction}_paid : totalPaid {direction}Data = #[0,2201,412,510,127,40,0,0,8,0] := by decide\n',
                 f'theorem {direction}_scalar_cost : totalScalarCost {direction}Data = {sum(x[4] for x in chunks)} := by decide\n',
                 f'theorem {direction}_event_count : totalEvents {direction}Data = 21449 := by decide\n',
                 'end NativeData\n']
        write('Native' + direction.title() + '.lean', ''.join(body))
        summaries[direction] = {'events':len(events),'segments':len(chunks),
            'paid':[sum(x[3][r] for x in chunks) for r in range(10)],
            'scalar_cost':sum(x[4] for x in chunks)}
    manifest = {'canonical_payload_sha256':EXPECTED,'frames':len(frames),
        'operators':len(operators),'changed_operators':sum(g[0]!=g[2] for g in operators),
        'paid_classes':len(paid),'warp_classes':len(warps),'new_paid_classes':len(new_paid),
        'orientations':summaries,'source_phase_labels':phase_labels,'source_adapter_labels':adapter_labels}
    print(json.dumps(manifest,sort_keys=True))


def record(module, exit_code):
    """Record a completed actual Lean run; the log comes from the run's tee."""
    expected=['NativeCore','NativeRaw']+[f'NativeFrames{i}' for i in range(4)]+[
        f'NativeOperators{i}' for i in range(4)]+['NativeData','NativeForward']+[
        f'NativeBackwardProofs{i}' for i in range(4)]+['NativeBackward','Native']
    assert module in expected
    lean=(HERE/'.toolchain/lean-4.21.0-windows/bin/lean.exe').resolve()
    path=HERE/'NATIVE-LEAN-VERIFICATION.json'
    receipt=json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}
    rows={r['module']:r for r in receipt.get('modules',[])}
    files={k:HERE/(module+ext) for k,ext in [('source','.lean'),('olean','.olean'),('log','.log')]}
    # An empty compiler stream has an empty genuine log; Tee-Object can omit
    # creating its file when no object was written to the pipeline.
    if not files['log'].exists():
        files['log'].write_bytes(b'')
    row={'module':module,'exit_code':exit_code,
         'argv':[str(lean),'-s','65536','-o',module+'.olean',module+'.lean'],
         'working_directory':str(HERE)}
    for key,p in files.items():
        assert p.exists() or (key=='olean' and exit_code!=0)
        row[key]=p.name
        row[key+'_sha256']=sha256(p.read_bytes()).hexdigest() if p.exists() else None
    rows[module]=row
    revision=next(r['rev'] for r in tomllib.loads((HERE/'lakefile.toml').read_text(encoding='utf-8'))['require'] if r['name']=='mathlib')
    receipt={'status':'PASS' if set(rows)==set(expected) and all(r['exit_code']==0 for r in rows.values()) else 'INCOMPLETE',
        'lean_version':subprocess.check_output([str(lean),'--version'],text=True,encoding='utf-8').strip(),
        'mathlib_revision':revision,'canonical_payload_sha256':EXPECTED,
        'generation_source_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
        'expected_modules':expected,'modules':[rows[k] for k in expected if k in rows],
        'scope':'Ordinary-kernel finite binary frame, G-inverse, full native frame-trace, helper and invoice checks; excludes quantum absolute phases and symbolic endpoint equality.'}
    if 'Native' in rows:
        receipt['axiom_output']=(HERE/'Native.log').read_text(encoding='utf-8')
    path.write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
    print('RECORDED',module,exit_code,receipt['status'])


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--record')
    parser.add_argument('--exit-code',type=int,default=0)
    args=parser.parse_args()
    record(args.record,args.exit_code) if args.record else main()
