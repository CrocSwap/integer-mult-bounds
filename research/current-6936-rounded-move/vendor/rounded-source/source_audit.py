"""Small explicit source-join guards, not a general compiler/proof checker.

Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
import ast
from hashlib import sha256
from rounded_move_sources import HERE,authenticate,need
from rounded_move import RoundedMove,ExactMoveChild,P,S

def check():
    retained=authenticate();data=(HERE/'rounded_move.py').read_bytes();tree=ast.parse(data)
    forbidden={'cells','data','head','origin','high','actions','visited','visited_high','__dict__'}
    need(not any(isinstance(n,ast.Attribute) and n.attr in forbidden for n in ast.walk(tree)),
         'no production numerical hardware observer')
    inherited=('prepare','lift','drop','write_header','read_header','component_width')
    need(all(getattr(RoundedMove,name) is getattr(P.Provider,name) for name in inherited),
         'literal inherited outer width/lift/drop/header methods')
    need(S.serial.S.adapter is S.common.monomial and S.serial.S.codec is P.C
         and S.serial.S.abi is P.A and S.common.monomial.Count is P.Count
         and S.common.monomial.Tape is P.Tape and S.direct.S.abi is P.A,
         'same actual physical Count/Tape/codec/ABI object vocabulary')
    need(S.direct.S.child is S.prior.cutoff.PositiveChild,
         'explicit private-cutoff child substitution')
    need(S.direct.DirectMove.run.__code__.co_filename.endswith('/vendor/direct/direct_move.py')
         and P.Provider.run.__code__.co_filename.endswith('/vendor/rounded/rounded_leaf.py'),
         'both exact protected coordinator and outer runtime retain literal sources')
    return dict(retained_files=retained,shared_identities=109,
                production_sha256=sha256(data).hexdigest(),
                loader_sha256=sha256((HERE/'rounded_move_sources.py').read_bytes()).hexdigest(),
                inherited_outer_methods=list(inherited),
                changed_child_is_explicit=True,source_guard_is_general_proof_checker=False)
