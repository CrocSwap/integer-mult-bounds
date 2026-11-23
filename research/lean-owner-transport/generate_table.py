#!/usr/bin/env python3
"""Generate an untrusted explicit Lean witness; OwnerTable checks its index links.
Source byte projection is reproduced separately. No claimed property is assumed
by the Lean checker on the basis of this generator's output.
"""
from pathlib import Path
from collections import defaultdict
import argparse, gzip, hashlib, json

ROOT = Path(__file__).resolve().parent

def generate():
    pin = json.loads((ROOT/'SOURCE531.json').read_text())
    for name, digest in pin['sha256'].items():
        if hashlib.sha256((ROOT/'source531'/name).read_bytes()).hexdigest() != digest:
            raise ValueError('Changed immutable source: '+name)
    plan = json.loads((ROOT/'source531/PLAN.json').read_text())
    roles = json.loads(gzip.decompress((ROOT/'source531/OWNERS.json.gz').read_bytes()))
    helpers, calls = len(plan['baseline_widths']), len(plan['order'])
    ports = plan['copies']
    children = len(plan['pairs'])
    replicas = max(int(k.split(',')[0]) for k in plan['windows']) + 1
    lanes = max(2*int(v)+plan['sides'][k] for k,v in plan['pairs'].items())+1
    roles = sorted(roles, key=lambda r:(r['time'],r['helper']))
    if len(roles) != helpers*calls:
        raise ValueError('Wrong source row count')
    groups, family = defaultdict(list), defaultdict(list)
    for index, r in enumerate(roles):
        if index != r['time']*helpers+r['helper']:
            raise ValueError('Source has a missing or repeated row coordinate')
        gid = (r['owner_replica']*children+r['child'])*ports+r['port']
        groups[gid].append(index)
        family[r['time']].append(index)
    slots, ranks = {}, {}
    for refs in groups.values():
        refs.sort(key=lambda i:roles[i]['offset'])
        slots.update({i:position for position,i in enumerate(refs)})
    for refs in family.values():
        refs.sort(key=lambda i:roles[i]['family'])
        ranks.update({i:position for position,i in enumerate(refs)})
    def nums(xs): return '['+', '.join(map(str,xs))+']'
    row_literals = []
    for i,r in enumerate(roles):
        fields = [r[k]for k in ['time','helper','stage','replica','owner_replica','child','port','family','offset','width']]+[slots[i],ranks[i]]
        row_literals.append('⟨'+', '.join(map(str,fields))+'⟩')
    def array(name,ty,rows):
        # Bounded literals avoid quadratic parsing of one 36,288-row expression.
        chunk_size = 64
        chunks = [rows[i:i+chunk_size] for i in range(0,len(rows),chunk_size)]
        out = ''
        for i,chunk in enumerate(chunks):
            out += f'def {name}Part{i} : Array ({ty}) := #[\n  '+',\n  '.join(chunk)+']\n\n'
        def dispatch(lo,hi):
            if hi-lo == 1: return f'{name}Part{lo}'
            mid=(lo+hi)//2
            return f'(if block < {mid} then {dispatch(lo,mid)} else {dispatch(mid,hi)})'
        argument = 'block' if len(chunks)>1 else '_block'
        out += f'def {name}Block ({argument} : Nat) : Array ({ty}) := {dispatch(0,len(chunks))}\n\n'
        out += f'def {name} (i : Nat) : {ty} := (({name}Block (i / {chunk_size}))[i % {chunk_size}]?).getD default\n\n'
        return out
    output='''/- Generated literal PR531 witness. All auxiliary indexes are checked in Lean.
Imported source: db0e57bc7f36b5ac0fc844ad7ce1396165ee6647.
Original owner data: icekylinx and credited predecessors; Apache-2.0.
Generator/proofs: Rohan Arun with OpenAI Codex assistance. -/
import OwnerTable
namespace OwnerTransport.PR531Table
open OwnerTable
set_option maxRecDepth 100000
set_option maxHeartbeats 0

'''
    output += array('rows','Role',row_literals)
    output += array('groups','List Nat',[nums(groups[i])for i in range(replicas*children*ports)])
    output += array('families','List Nat',[nums(family[i])for i in range(calls)])
    windows=[]
    for rep in range(replicas):
        for child in range(children):
            cap,times=plan['windows'][f'{rep},{child}']
            windows.append(f'⟨{cap}, {nums(times)}⟩')
    output += array('windows','Window',windows)
    output += array('schedule','Nat × Nat',[f'({s}, {r})'for s,r in plan['order']])
    output += array('widths','Nat',list(map(str,plan['baseline_widths'])))
    output += array('laneIds','Nat',[str(2*plan['pairs'][str(i)]+plan['sides'][str(i)])for i in range(children)])
    output += f'''def witness : Table where
  ports := {ports}
  children := {children}
  replicas := {replicas}
  helpers := {helpers}
  calls := {calls}
  lanes := {lanes}
  row := rows
  group := groups
  byFamily := families
  window := windows
  call := schedule
  width := widths
  lane := laneIds

end OwnerTransport.PR531Table
'''
    return output

def certificate():
    plan = json.loads((ROOT/'source531/PLAN.json').read_text())
    helpers, calls = len(plan['baseline_widths']), len(plan['order'])
    ports, windows = plan['copies'], len(plan['windows'])
    out = """/- Generated kernel-checked finite certificates for the pinned PR531 witness. -/
import PR531TableData
namespace OwnerTransport.PR531Table
open OwnerTable
set_option maxRecDepth 100000
set_option maxHeartbeats 0

def checkGroup (g : Nat) : Bool :=
  checkBlocks witness g (witness.window (g / witness.ports)).capacity 0 (witness.group g)

def checkCall (t : Nat) : Bool :=
  checkFamilies witness t 0 (witness.byFamily t)

"""
    for label,check,size,count in [('row','checkRow witness',helpers,calls),
                                  ('group','checkGroup',ports,windows),
                                  ('call','checkCall',1,calls)]:
        for q in range(count):
            out += f'theorem {label}Chunk{q} : checkRange ({check}) {q*size} {size} = true := by decide\n'
        out += f'\ntheorem {label}Chunks (q : Nat) (h : q < {count}) :\n    checkRange ({check}) (q * {size}) {size} = true := by\n  match q with\n'
        for q in range(count):
            out += f'  | {q} => exact {label}Chunk{q}\n'
        out += f'  | n + {count} => omega\n\n'
    out += f"""/-- Every row and every inverse-index list of the selected witness is checked. -/
theorem accepted : Accepted witness := by
  refine ⟨?_, ?_, ?_⟩
  · intro i hi
    exact chunks_sound (checkRow witness) {helpers} {calls} (by decide) rowChunks i hi
  · intro g hg
    exact chunks_sound checkGroup {ports} {windows} (by decide) groupChunks g hg
  · intro t ht
    exact chunks_sound checkCall 1 {calls} (by decide) callChunks t ht

/-- Each of the actual selected rows meets the semantic row contract. -/
theorem every_row_valid (i : Nat) (hi : i < rowCount witness) : RowValid witness i :=
  accepted_row witness accepted i hi

/-- The exact declared window bounds every occupied coordinate. -/
theorem every_coordinate_fits (i x : Nat) (hi : i < rowCount witness)
    (hx : x < (witness.row i).width) :
    (witness.row i).offset + x <
      (witness.window ((witness.row i).ownerReplica * witness.children + (witness.row i).child)).capacity :=
  accepted_declared_window_capacity witness accepted i x hi hx

/-- Equal physical-family identifiers in the same call identify the same row. -/
theorem owners_injective (i j : Nat) (hi : i < rowCount witness) (hj : j < rowCount witness)
    (ht : (witness.row i).time = (witness.row j).time)
    (hf : (witness.row i).family = (witness.row j).family) : i = j :=
  accepted_owner_injective witness accepted i j hi hj ht hf

/-- The actual per-group occupied addresses are injective. -/
theorem coordinates_injective (i j x y : Nat)
    (hi : i < rowCount witness) (hj : j < rowCount witness)
    (hg : groupId witness (witness.row i) = groupId witness (witness.row j))
    (hx : x < (witness.row i).width) (hy : y < (witness.row j).width)
    (heq : (witness.row i).offset + x = (witness.row j).offset + y) : i = j ∧ x = y :=
  accepted_nonalias witness accepted i j x y hi hj hg hx hy heq

/-- Every call/helper pair is represented by exactly one row. -/
theorem every_helper_present (t helper : Nat) (ht : t < witness.calls) (hh : helper < witness.helpers) :
    ∃ i, i < rowCount witness ∧ (witness.row i).time = t ∧ (witness.row i).helper = helper ∧
      ∀ j, j < rowCount witness → (witness.row j).time = t → (witness.row j).helper = helper → j = i :=
  accepted_census witness accepted t helper ht hh

/-- Concrete helpers in each selected invocation have pairwise distinct owners. -/
theorem helper_owners_injective (t : Nat) (ht : t < witness.calls) :
    ∀ a b : Fin witness.helpers, helperOwner witness t a = helperOwner witness t b → a = b :=
  helper_owner_injective witness accepted t ht

end OwnerTransport.PR531Table
"""
    return out

def main():
    p=argparse.ArgumentParser();p.add_argument('--check',action='store_true');a=p.parse_args()
    outputs={'PR531TableData.lean':generate(),'PR531TableCertificate.lean':certificate()}
    for name,s in outputs.items():
        target=ROOT/name
        if a.check:
            if target.read_text()!=s:raise ValueError('Witness source does not match regeneration: '+name)
        else:target.write_text(s)
    print(json.dumps({'status':'PASS_LITERAL_PROJECTION','bytes':{name:len(s.encode())for name,s in outputs.items()}}))
if __name__=='__main__':main()
