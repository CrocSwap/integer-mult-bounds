"""Restricted encoded-space existence, with explicit nontrivial spectator action."""
import json
from pathlib import Path
O=Path(__file__).resolve().parent
q=3;m=2;N=q**(2*m)
def perm(x,axes):
 d=[]
 for _ in range(2*m):d.append(x%q);x//=q
 for a in axes:d[a],d[m+a]=d[m+a],d[a]
 return sum(t*q**i for i,t in enumerate(d))
old=[perm(x,range(2)) for x in range(N)]
new=[perm(x,[0]) for x in range(N)]+[N+perm(x,[0]) for x in range(N)]
def cycles(p):
 seen=set();fixed=[];pairs=[]
 for i,j in enumerate(p):
  if i in seen:continue
  seen.update([i,j])
  (fixed if i==j else pairs).append(i if i==j else (i,j))
 return fixed,pairs
of,op=cycles(old);nf,np=cycles(new)
embed={a:b for a,b in zip(of,nf)}
for (a,b),(c,d) in zip(op,np):embed[a]=c;embed[b]=d
assert len(embed)==N and len(set(embed.values()))==N
assert all(new[embed[a]]==embed[old[a]] for a in range(N))
remaining=sorted(set(range(2*N))-set(embed.values()))
assert all(new[a] in remaining for a in remaining)
spectator_moved=sum(new[a]!=a for a in remaining)
assert spectator_moved==36
r={'status':'EXACT_RESTRICTED_ENCODING_MODEL_NOT_SUPPLIER_ADMISSION','q':q,'m':m,'logical_columns':N,'physical_columns':2*N,'embedding':[embed[i] for i in range(N)],'all_integer_logical_columns_intertwine':True,'encoding_is_coordinate_value_subset':'Not an orthogonal ADDRESS-axis isometry; custom selector of VALUE addresses.','arbitrary_spectator_columns':len(remaining),'spectator_nonfixed_columns':spectator_moved,'spectator_transpositions':spectator_moved//2,'required_restoration':'18 additional value-address transpositions in this toy, or a new charged local endpoint accommodating them. No cheap legal ADDRESS-selector decomposition supplied.','source_read_write':'Local scalar ADD between identically embedded logical streams can preserve the encoded subspace; fresh COPY and arbitrary full physical dirt need explicit embedding-compatible lowering plus spectator restoration. No source-control or cover compiler proof asserted.','restriction':'Zero spectators or restricted correlated/coherent states give an encoding, but exclude the inherited arbitrary correlated full physical-stream dirt contract. Noninvertible encodings do not contradict the trace obstruction.'}
mask_counts=[sum(b//N==fam for b in embed.values()) for fam in range(2)]
assert all(0<c<N for c in mask_counts)
r['constant_stream_compiler_obstruction']={'encoded_logical_constant_support_per_family':mask_counts,'family_columns':N,'encoding_produces_nonconstant_physical_families':True,'grammar_scope':'Pointwise scalar ADD/COPY and scalar multiplication, plus bijective address permutations, preserve the subspace of arrays constant on every physical family. Zero ancillas remain in that subspace. Hence this custom subset embedding of a logical constant cannot be synthesized by that grammar, including arbitrary finite compositions and paid repeated adds.','escape':'Nonconstant ancilla templates, value-address masks, new read/write primitives or a different encoding require an explicit additional interface and invoice. This claim assumes address operations are bijections and streamwise scalar maps, as inherited; no unprovided masked read/write assumed.'}
r['actual_width8_split7_1_odd_q3_counts']={'m':8,'logical_columns':3**16,'spectator_transpositions':(3**16-3**9-3**15+3**8)//2,'scope':'Exact complement negative eigenspace count, not primitive cost. Actual m78 same formula with N=3^156.'}
(O/'ENCODED.json').write_text(json.dumps(r,indent=2)+'\n');print({k:r[k] for k in ['status','spectator_nonfixed_columns','spectator_transpositions']})
