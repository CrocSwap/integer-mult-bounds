"""Reconstruct both #8088 words and census target compiler input sizes."""
from collections import Counter
from hashlib import sha256
import gzip,json,sys
from pathlib import Path

root=Path(sys.argv[1]).resolve()
runtime=root/'runtime'; peer=root/'research/frequency-weighted-native-multiplier'
pins={'installations.py':'5df81fddba26013b142195f5c3119491fa2f07b1e72c3616ae76e7d7ffbb0fd1',
      'raw_binary_stage.py':'e24bd735598d278dbd46cada584a63da01796d77ad557a45b80a4dfc7bbbd0b0',
      'grades.py':'6124744b40f806c80b6f10010a72e755bc11d64a8cc9a04f5e8316799eb6f05d',
      'transport.py':'9eb8f0d77a4c53fc4fddffdfe198cab930b6d1f49e2b6d43c970397051bb7818',
      'retimed_supplier.py':'2a87c2781ca93fa854aee098dcb7c50a65f2a46267ba926e3997b442e5a25f2c',
      'strong_complex.py':'8f3fb92523df006e2e94505127088aaf2e64fadd20b3cab2344f62d7690e875d',
      'w5669_shortcut5.json.gz':'6ef741c346ea075c4f2ed11f9d42d7076103e72d4a9e5059d495f1cb990fd149'}
for name,want in pins.items(): assert sha256((runtime/name).read_bytes()).hexdigest()==want, name
sys.path[:0]=[str(runtime),str(peer/'portable'),str(peer.parent/'tiered-native-multiplier'/'source'),str(peer.parent/'tiered-native-multiplier')]
from upstream import HERE, install
install()
import installations
from strong_complex import load_changed,digest,required_pairs
from band_product import production_supplier
from grades import numerical_recipe
from activation import resource_receipt
from compiler_state import construct
from record_census import inspect
from tape_directory import dump

new,layout=load_changed(HERE/'inputs')
from verify_split_helpers import read,reconstruct
from sparse_helpers import rebuild
parent,old_layout=rebuild(); old,_=reconstruct(parent,read('BANK-FACTORS.json.gz'))
assert layout==old_layout
assert digest(old)=='38d2b3a2311a9ba5fee091cc7aa204c7ed95651aec95d75184b2391df090cbfb'
assert digest(new)=='ed3bea7186f962f3a8a8ae389cecce3d1ef48a7a832cf9af6c9048a6b5919b35'
assert all(new[k]==old[k] for k in ('initial','final','frames','first_output'))
assert (len(old['moves']),len(new['moves']))==(5674,5669)

def shape(root):
 todo=[(root,0)]; out={'nodes':0,'max_depth':0,'max_list_entries':0,'max_map_entries':0,'max_string_utf8_bytes':0,'max_integer_bits':0}
 while todo:
  item,depth=todo.pop();out['nodes']+=1;out['max_depth']=max(depth,out['max_depth'])
  if isinstance(item,dict):
   out['max_map_entries']=max(len(item),out['max_map_entries'])
   for k,v in item.items(): todo.extend(((k,depth+1),(v,depth+1)))
  elif isinstance(item,(list,tuple)):
   out['max_list_entries']=max(len(item),out['max_list_entries']);todo.extend((v,depth+1) for v in item)
  elif isinstance(item,str):out['max_string_utf8_bytes']=max(len(item.encode()),out['max_string_utf8_bytes'])
  elif type(item) is int:out['max_integer_bits']=max(abs(item).bit_length(),out['max_integer_bits'])
  elif item is not None and type(item) is not bool:raise TypeError(type(item))
 return out

pack=runtime/'w5669_shortcut5.json.gz'; raw=gzip.decompress(pack.read_bytes())
canonical=json.dumps(new,separators=(',',':'),sort_keys=True).encode()
assert sha256(canonical).hexdigest()==digest(new)
new_pairs=required_pairs(new,layout);old_pairs=required_pairs(old,layout)
new_mov=Counter(tuple(x) for x in new['moves']); old_mov=Counter(tuple(x) for x in old['moves'])
newshape=shape(new);oldshape=shape(old)
producer=production_supplier(85406,10**18); recipe=producer.recipe; types=recipe.types()
role_counts=[{'targets':len(w.targets),'paid':len(w.paid),'total':len(w.targets)+len(w.paid)} for w in types]
grade_count=len(recipe.paid.histogram)+len(recipe.targets.histogram)
cell_bits=max(max(x.numerator.bit_length(),x.denominator.bit_length()) for x in recipe.cells.values())
assert all(x['total']<2**20 for x in role_counts) and sum(x['total'] for x in role_counts)<2**20
assert grade_count<2**8 and cell_bits<512
assert len(recipe.cells)==51 and len(recipe.typed_cells())==88
assert len(raw)<2**23 and len(pack.read_bytes())+len(raw)<2**23
assert newshape['max_depth']<32 and newshape['max_map_entries']<256 and newshape['max_string_utf8_bytes']<256
assert newshape['max_integer_bits']<512 and newshape['nodes']<2**23
assert len(new_pairs)<2**20 and len(old_pairs)<2**20
assert (len(old_pairs),len(new_pairs),len(new_pairs-old_pairs),len(old_pairs-new_pairs))==(2971,2964,1,8)
heights=(*installations.ENTRY.rank_logs,installations.ENTRY.complex_log,*installations.TERMINAL.rank_logs,installations.TERMINAL.complex_log)
assert heights==(3000,3080,1024,8192,106000,1681001,85406)
result={'source_head':'06691302af526a488f3dee0298035f86b6e69c51','runtime_sha256':{name:sha256((runtime/name).read_bytes()).hexdigest() for name in ('installations.py','grades.py','transport.py','retimed_supplier.py','strong_complex.py','w5669_shortcut5.json.gz','raw_binary_stage.py')},
 'old_word_sha':digest(old),'new_word_sha':digest(new),'compressed_bytes':pack.stat().st_size,'json_bytes':len(raw),'canonical_bytes':len(canonical),
 'unchanged_graph_sections':[k for k in old if old[k]==new[k]],'top_lengths':{k:{'old':len(old[k]),'new':len(new[k])} for k in old if isinstance(old[k],(list,dict))},
 'old_shape':oldshape,'new_shape':newshape,'old_pairs':len(old_pairs),'new_pairs':len(new_pairs),'new_only_pairs':len(new_pairs-old_pairs),'removed_pairs':len(old_pairs-new_pairs),
 'removed_move_tuples':sum((old_mov-new_mov).values()),'added_move_tuples':sum((new_mov-old_mov).values()),
 'role_counts':role_counts,'grade_count_sum':grade_count,'cells':len(recipe.cells),'typed_cells':len(recipe.typed_cells()),'max_cell_fraction_bits':cell_bits,
 'atlas_counts':{'factors':len(producer.physical.factors),'forms':len(producer.physical.forms),'words':len(producer.physical.words),'roots':len(producer.physical.roots),'moves':len(producer.physical.moves)},
 'heights':heights,'source_stock':resource_receipt(installations.TERMINAL),
 'interpretation':'Observed finite counts verify cardinality/width hypotheses; do not alone prove an all-input action bound, paid-source admission, or terminal-scale multiplication.'}
print(json.dumps(result,indent=2,sort_keys=True))
