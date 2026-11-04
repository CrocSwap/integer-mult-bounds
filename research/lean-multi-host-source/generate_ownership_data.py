#!/usr/bin/env python3
"""Extract constructive owner permutations from the pinned actual stage-2 call.
Offline provenance bridge, not a kernel-verified JSON parser. Apache-2.0.
Prepared with substantial OpenAI Codex assistance.
"""
import argparse, gzip, hashlib, json, re
from pathlib import Path

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def arr(xs): return '#[' + ', '.join(map(str,xs)) + ']'
def tree(xs, default=0):
 n=1
 while n<len(xs):n*=2
 xs=list(xs)+[default]*(n-len(xs))
 def rec(v):
  if all(x==v[0] for x in v):return f'(.leaf {v[0]})'
  return f'(.node {rec(v[::2])} {rec(v[1::2])})'
 return rec(xs)

GENERATED_MODULES = (
 'OwnershipDatumCore', 'OwnershipInverseTable',
 'OwnershipCertificatePermutations', 'OwnershipCertificateMasks',
 'OwnershipCertificateOwner', 'OwnershipCertificateHelpers', 'OwnershipData',
)

def parse_lookup(text):
 """Parse only literal Lookup trees and named subtree references."""
 tokens = re.findall(r'\(|\)|\.leaf|\.node|[0-9]+|[A-Za-z_]\w*', text)
 assert ''.join(tokens) == re.sub(r'\s+', '', text), 'Unparsed Lookup syntax'
 index = 0
 def parse():
  nonlocal index
  token = tokens[index]; index += 1
  if token != '(':
   assert re.fullmatch(r'[A-Za-z_]\w*', token), token
   return token
  kind = tokens[index]; index += 1
  if kind == '.leaf':
   value = int(tokens[index]); index += 1
  else:
   assert kind == '.node', kind
   value = (parse(), parse())
  assert tokens[index] == ')'
  index += 1
  return value
 result = parse()
 assert index == len(tokens), 'Unused Lookup syntax'
 return result

def literal_lookup(value):
 return f'(.leaf {value})' if isinstance(value,int) else f'(.node {literal_lookup(value[0])} {literal_lookup(value[1])})'

def lookup_signature(declaration):
 match = re.match(r'def (\w+) : ([^\n]+?) :=\s*', declaration)
 assert match, 'Expected an explicitly typed Lookup declaration'
 return match[1], match[2], declaration[match.end():]

def check_flattened_lookup(original, generated):
 """Independently expand the emitted definitions and compare the full tree."""
 public_name, type_name, literal = lookup_signature(original)
 expected = parse_lookup(literal)
 rows = re.findall(r'^def ('+re.escape(public_name)+r'(?:_part\d+)?) : '+re.escape(type_name)+r' := (.+)$', generated, re.M)
 assert len(rows) == len(dict(rows)) and rows[-1][0] == public_name
 parsed = {name:parse_lookup(body) for name,body in rows}
 expanded, active, visited = {}, set(), set()
 def expand(value):
  if isinstance(value,int):return value
  if isinstance(value,tuple):return (expand(value[0]),expand(value[1]))
  assert value in parsed and value not in active, 'Missing or cyclic Lookup reference'
  visited.add(value)
  if value not in expanded:
   active.add(value); expanded[value] = expand(parsed[value]); active.remove(value)
  return expanded[value]
 actual = expand(public_name)
 assert visited == set(parsed), 'Unused Lookup subtree'
 assert actual == expected, 'Flattened inverse-owner tree changed'
 return {'original_literal_sha256':hashlib.sha256(literal_lookup(expected).encode()).hexdigest(),
         'expanded_literal_sha256':hashlib.sha256(literal_lookup(actual).encode()).hexdigest(),
         'subtree_definitions':len(rows)-1,
         'max_literal_leaves_per_definition':max(body.count('(.leaf ') for _,body in rows),
         'max_literal_nodes_per_definition':max(body.count('(.node ')+body.count('(.leaf ') for _,body in rows)}

def flatten_lookup_declaration(original, leaf_budget=64):
 """Keep every branch and leaf, bounding each emitted declaration's literal."""
 assert leaf_budget > 0
 public_name, type_name, literal = lookup_signature(original)
 value = parse_lookup(literal)
 def leaves(node):return 1 if isinstance(node,int) else leaves(node[0])+leaves(node[1])
 lines = []
 def emit(node, root=False):
  if leaves(node) <= leaf_budget:
   body = literal_lookup(node)
  else:
   left, right = emit(node[0]), emit(node[1])
   body = f'(.node {left} {right})'
  name = public_name if root else f'{public_name}_part{len(lines)}'
  lines.append(f'def {name} : {type_name} := {body}\n\n')
  return name
 emit(value, root=True)
 result = ''.join(lines)
 check_flattened_lookup(original,result)
 return result

def split_rendered(monolith):
 """Partition declarations; flatten the inverse table without changing its value.

 The large inverse-owner table is needed only by owner_inverse. Keeping it
 in a separate branch lets the other certificates compile independently.
 """
 start = monolith.index('inductive Lookup where\n')
 end = monolith.index('end SourceOwnership\n')
 text = monolith[start:end]
 matches = list(re.finditer(r'^(inductive|def|abbrev|theorem) (\w+)\b', text, re.M))
 declarations = {
  match[2]: text[match.start():matches[i+1].start() if i+1 < len(matches) else len(text)]
  for i,match in enumerate(matches)
 }
 assert len(matches) == len(declarations) and ''.join(declarations.values()) == text
 groups = {
  'OwnershipCertificatePermutations': ['perm_inverse', 'inverse_perm'],
  'OwnershipCertificateMasks': ['perm_support', 'fingerprint_injective'],
  'OwnershipCertificateOwner': ['owner_inverse'],
  'OwnershipCertificateHelpers': ['family_data', 'helper_range', 'helper_frame', 'helper_child'],
 }
 theorems = {match[2] for match in matches if match[1] == 'theorem'}
 assert theorems == {name for names in groups.values() for name in names} | {'family_tag_injective'}

 def module(imports, names):
  return ('\n'.join('import '+name for name in imports)+'\n\n'
   '/-! Literal PR442 ownership certificate partition. Apache-2.0.\n'
   'Prepared with substantial OpenAI Codex assistance.\n'
   'Generated by generate_ownership_data.py; declarations are unchanged. -/\n'
   'set_option maxRecDepth 1000000\nset_option maxHeartbeats 0\n'
   'namespace SourceOwnership\n\n'
   + ''.join(declarations[name] for name in names) + 'end SourceOwnership\n')

 core = [name for name in declarations if name not in theorems and name != 'inverseOwnerTable']
 files = {'OwnershipDatumCore.lean': monolith[:start]
          + ''.join(declarations[name] for name in core) + 'end SourceOwnership\n'}
 original_inverse = declarations['inverseOwnerTable']
 declarations['inverseOwnerTable'] = flatten_lookup_declaration(original_inverse)
 files['OwnershipInverseTable.lean'] = module(['OwnershipDatumCore'], ['inverseOwnerTable']).replace(
  'declarations are unchanged.', 'the inverse-table literal is split into named subtrees.')
 for name,names in groups.items():
  dependency = 'OwnershipInverseTable' if name == 'OwnershipCertificateOwner' else 'OwnershipDatumCore'
  files[name+'.lean'] = module([dependency], names)
 files['OwnershipData.lean'] = (module(list(groups), ['family_tag_injective'])
   + monolith[end+len('end SourceOwnership\n'):])
 assert set(files) == {name+'.lean' for name in GENERATED_MODULES}
 return files

def render_files(monolith):
 """Return all filename-to-source entries for an emitted ownership certificate."""
 return split_rendered(monolith)

def main():
 p=argparse.ArgumentParser();p.add_argument('--template',type=Path,required=True);p.add_argument('--states',type=Path,required=True);p.add_argument('--frames',type=Path,required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--receipt',type=Path);p.add_argument('--check',action='store_true');a=p.parse_args()
 raw=gzip.decompress(a.template.read_bytes());t=json.loads(raw);s=json.loads(a.states.read_bytes());fs=json.loads(a.frames.read_bytes())['frames']
 c=next(c for c in t['calls'] if c['stage']==2 and c['replica']==0)
 assert c['orientation']=='forward' and c['pair']==0 and len(c['owners'])==987
 assert [z[0] for z in c['owners'][:240]]==list(range(240))
 keys=sorted({tuple(o[1][1:])+(s['initial'][str(i)],) for i,o in enumerate(c['owners']) if i>=240})
 assert len(keys)==16
 ps=[];ins=[];srcbits=[];tarbits=[];details=[]
 for child,off,w,fr in keys:
  f=fs[str(fr)];src=[row.index(1) for row in f['A']]
  assert all(row==[int(j==src[i]) for j in range(8)] for i,row in enumerate(f['A']))
  occupied=sorted(set(range(8))-set(src));assert len(occupied)==f['dim']==8-w
  assert sorted(f['B'])==sorted([[2*int(j==i) for j in range(8)] for i in occupied])
  assert child in (1,2)
  dst=list(range((15 if child==1 else 1)+off,(15 if child==1 else 1)+off+w))
  assert len(src)==len(dst)==w
  perm=dict(zip(src,dst));perm.update(zip([i for i in range(64) if i not in src],[i for i in range(64) if i not in dst]));perm=[perm[i] for i in range(64)]
  assert sorted(perm)==list(range(64));inv=[perm.index(i) for i in range(64)]
  ps.append(perm);ins.append(inv);srcbits.append(sum(1<<i for i in src));tarbits.append(sum(1<<i for i in dst));details.append(dict(child=child,offset=off,width=w,initial_frame=fr,source_axes=src,target_axes=dst,permutation=perm,inverse=inv))
 assert len({tuple(p) for p in ps})==16
 fams=[z[0] for z in c['owners']];tags=[0]*240+[keys.index(tuple(z[1][1:])+(s['initial'][str(i)],)) for i,z in enumerate(c['owners']) if i>=240]
 codes=[16*f+tag for f,tag in zip(fams,tags)];assert len(set(codes))==987
 inverse=[987]*(720*16)
 for i,code in enumerate(codes):inverse[code]=i
 assert all(240<=f<720 for f in fams[240:]);assert all((tag>=7)==(f>=480) for f,tag in zip(fams[240:],tags[240:]))
 # A tiny faithful permutation fingerprint; digits are base64 images of axes0..7.
 fingerprints=[sum(p[i]*64**i for i in range(8)) for p in ps]
 assert len(set(fingerprints))==16
 out='''import Std\n\n/-! Literal ownership certificate for PR442 stage2/replica0, all987roles.\nGenerated by generate_ownership_data.py. The extractor is not kernel verified.\nApache-2.0. Prepared with substantial OpenAI Codex assistance. -/\nset_option maxRecDepth 1000000\nset_option maxHeartbeats 0\nnamespace SourceOwnership\n\ninductive Lookup where\n  | leaf : Nat → Lookup\n  | node : Lookup → Lookup → Lookup\n\ndef lookup : Lookup → Nat → Nat\n  | .leaf n, _ => n\n  | .node l r, i => if i % 2 == 0 then lookup l (i / 2) else lookup r (i / 2)\n\n'''
 for name,vals in [('familyTable',fams),('tagTable',tags),('initialFrameTable',[s['initial'][str(i)] for i in range(987)]),('inverseOwnerTable',inverse),('sourceBits',srcbits),('targetBits',tarbits),('tagInitialFrame',[k[3] for k in keys]),('tagChild',[k[0] for k in keys]),('tagOffset',[k[1] for k in keys]),('tagWidth',[k[2] for k in keys])]:out+=f'def {name} : Lookup := {tree(vals)}\n\n'
 for name,vals in [('permTable',ps),('invPermTable',ins)]:out+=f'def {name} : Lookup := '+tree([x for v in vals for x in v])+'\n\n'
 out+='''abbrev Role := Fin 987
abbrev Tag := Fin 16
abbrev Axis := Fin 64

def family (r : Role) : Nat := lookup familyTable r.val
def tag (r : Role) : Tag := ⟨lookup tagTable r.val % 16, Nat.mod_lt _ (by decide)⟩
def perm (t : Tag) (i : Axis) : Axis :=
  ⟨lookup permTable (64 * t.val + i.val) % 64, Nat.mod_lt _ (by decide)⟩
def invPerm (t : Tag) (i : Axis) : Axis :=
  ⟨lookup invPermTable (64 * t.val + i.val) % 64, Nat.mod_lt _ (by decide)⟩
def sourceMask (t : Tag) (i : Axis) : Bool := (lookup sourceBits t.val).testBit i.val
def targetMask (t : Tag) (i : Axis) : Bool := (lookup targetBits t.val).testBit i.val

theorem perm_inverse : ∀ (t : Tag) (i : Axis), invPerm t (perm t i) = i := by decide +kernel
theorem inverse_perm : ∀ (t : Tag) (i : Axis), perm t (invPerm t i) = i := by decide +kernel
theorem perm_support : ∀ (t : Tag) (i : Axis), targetMask t (perm t i) = sourceMask t i := by decide +kernel

def fingerprint (t : Tag) : Nat :=
  (List.range 8).foldl (fun n i => n + (perm t ⟨i % 64, Nat.mod_lt _ (by decide)⟩).val * 64^i) 0

theorem fingerprint_injective : ∀ (a b : Tag), fingerprint a = fingerprint b → a = b := by decide +kernel

theorem owner_inverse : ∀ r : Role, lookup inverseOwnerTable (16 * family r + (tag r).val) = r.val := by decide +kernel

theorem family_tag_injective {r s : Role} (hf : family r = family s) (ht : tag r = tag s) : r = s := by
  apply Fin.ext
  rw [← owner_inverse r, ← owner_inverse s, hf, ht]

theorem family_data : ∀ r : Fin 240, family ⟨r.val, Nat.lt_trans r.isLt (by decide)⟩ = r.val := by decide +kernel

theorem helper_range : ∀ r : Role, 240 ≤ r.val → 240 ≤ family r ∧ family r < 720 := by decide +kernel

theorem helper_frame : ∀ r : Role, 240 ≤ r.val → lookup initialFrameTable r.val = lookup tagInitialFrame (tag r).val := by decide +kernel

theorem helper_child : ∀ r : Role, 240 ≤ r.val → ((tag r).val ≥ 7 ↔ family r ≥ 480) := by decide +kernel

end SourceOwnership
#print axioms SourceOwnership.perm_inverse
#print axioms SourceOwnership.perm_support
#print axioms SourceOwnership.fingerprint_injective
#print axioms SourceOwnership.family_tag_injective
#print axioms SourceOwnership.helper_frame
'''
 assert a.out.name == 'OwnershipData.lean', '--out must name the OwnershipData.lean facade'
 generated = render_files(out)
 existing = {path.name for pattern in ('OwnershipData.lean', 'OwnershipDatumCore.lean',
  'OwnershipInverseTable.lean', 'OwnershipCertificate*.lean') for path in a.out.parent.glob(pattern)}
 if a.check:
  assert existing == set(generated), 'Ownership certificate module inventory differs'
  for name,text in generated.items():
   assert (a.out.parent/name).read_text() == text, name+' differs from the supplied source'
 else:
  assert not existing-set(generated), 'Remove obsolete ownership certificate modules before regeneration'
  a.out.parent.mkdir(parents=True,exist_ok=True)
  for name,text in generated.items():(a.out.parent/name).write_text(text)
 receipt=dict(source_commit='4e16d001d505d4f21dd2bcfc44591f9be4c279bd',template_sha256=sha(a.template),template_raw_sha256=hashlib.sha256(raw).hexdigest(),states_sha256=sha(a.states),frames_sha256=sha(a.frames),call={k:c[k] for k in ('stage','replica','pair','orientation','local_hash')},roles=[dict(role=i,family=fams[i],tag=tags[i],initial_frame=s['initial'][str(i)],source_route=c['owners'][i][1]) for i in range(987)],charts=details,construction='Map sorted local residual coordinate axes onto sorted actual pending axes; complete by order-preserving bijection of complements. For child2 postcompose by actual B_port⊕I56; child1 has identity postcomposition.',output_sha256=sha(a.out))
 receipt['literal_monolith_sha256']=hashlib.sha256(out.encode()).hexdigest()
 receipt['generated_module_sha256']={name:hashlib.sha256(text.encode()).hexdigest() for name,text in generated.items()}
 if a.receipt:a.receipt.write_text(json.dumps(receipt,indent=2)+'\n')
 print('PASS: 987 roles, 747 helpers, 317 helper families, 16 constructive chart permutations')
if __name__=='__main__':main()
