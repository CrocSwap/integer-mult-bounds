"""Small explicit source guards; not a general compiler or proof checker.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
import ast
from hashlib import sha256
from rounded_sources import HERE,authenticate,need
from rounded_leaf import S,L,A,C,Count,Tape,Provider

def check():
    files=authenticate();data=(HERE/'rounded_leaf.py').read_bytes();tree=ast.parse(data)
    need(Count is L.Count and Tape is L.Tape and Tape is C.S.records.Tape
         and A is L.S.abi and C is L.S.codec and S.cutoff.S.common is S.common,
         'one unchanged Count/Tape/codec/ABI source object closure')
    forbidden={'cells','data','head','origin','high','actions','visited','visited_high','__dict__'}
    need(not any(isinstance(n,ast.Attribute) and n.attr in forbidden for n in ast.walk(tree)
                 if not (isinstance(n,ast.Attribute) and n.attr=='origin' and isinstance(n.value,ast.Name) and n.value.id=='A')),
         'no numerical hardware-address/backing observer in production')
    changes=[n for n in ast.walk(tree) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name)
             and n.func.id=='dict' and any(k.arg=='record_bits' for k in n.keywords)]
    need(len(changes)==1 and [k.arg for k in changes[0].keywords]==['record_bits','row_bits'],
         'widened parent changes exactly two physical extent fields')
    need(all(Provider(r).port_count==521 for r in range(1,9)),
         'same fixed inventory at every actual source rank')
    child=L.Provider.run
    need(child.__code__.co_filename.endswith('/leaf_provider.py'), 'actual retained numeric provider')
    return dict(retained_files=files,production_sha256=sha256(data).hexdigest(),
                unchanged_Count_Tape_codec_ABI_objects=True,widened_fields=['record_bits','row_bits'],
                fixed_ports=521,source_guard_is_general_proof_checker=False)
