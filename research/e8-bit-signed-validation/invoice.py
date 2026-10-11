"""Conservatively charge the signed witness while preserving the parity program.
Prepared with OpenAI Codex assistance. Apache-2.0.
"""
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import struct


def run(priced, original, source_input, raw_path, signed_path, signed, prefix, signed_prefix):
    raw_bytes, signed_bytes = Path(raw_path).read_bytes(), Path(signed_path).read_bytes()
    raw = list(struct.iter_unpack('<6i', raw_bytes))
    witness = list(struct.iter_unpack('<6i', signed_bytes))
    assert sha256(raw_bytes).hexdigest() == signed['exported_F2_record_sha256'] == prefix['record_sha256']
    assert sha256(signed_bytes).hexdigest() == signed['signed_record_sha256']
    assert signed_prefix['record_sha256']==signed['signed_record_sha256']
    parity = [(op,a,b,c%2 if op==1 else c,f,z) for op,a,b,c,f,z in witness if op!=1 or c%2]
    assert parity == raw
    raw_weighted = sum(op==1 for op,*_ in raw)
    raw_unit = sum(abs(c) for op,a,b,c,f,z in raw if op==1)
    weighted = sum(op==1 for op,*_ in witness)
    unit = sum(abs(c) for op,a,b,c,f,z in witness if op==1)
    assert (raw_weighted,raw_unit,weighted,unit) == (14689,14689,14801,14953)
    assert source_input['weighted']==raw_weighted and source_input['unit']==raw_unit
    assert signed['literal_parity_record_equality'] and signed['arbitrary_helper_dirt_restored_exactly']
    assert signed['forward_then_signed_inverse_identity'] and signed['target_decoder_mod2_identity']
    assert signed['forward_and_reflected_ledgers'][0] == signed['forward_and_reflected_ledgers'][1]
    h,v,R,m,T,stock,KP = (source_input[k] for k in ('h','v','R','m','T','stock','Kpairs'))
    assert (h,v,R,m,T,stock,KP)==(8,120,822,56,7,10794,3)
    S=2*KP+1; ncopy=source_input['ncopy']; assert ncopy==9
    H=Counter({int(k):n for k,n in priced['normalized_histogram'].items()})
    E=sum(H.values());mass=sum(r*n for r,n in H.items())
    assert (E,mass)==(original['positive_rank_children'],original['rank_mass'])
    assert m*stock-mass==1512 and priced['halving_degree']==2
    assert original['row_reserve']['internal_coefficient']==2*(m*m+1)==6274
    assert original['row_reserve']['external_complex_coefficient']==20161
    assert max(H)==34 and m*m>2*max(H)**2
    local=Counter()
    for op,a,b,c,f,z in raw:
        if op==0 and f:local[f]+=1
        if op==2:local[z]+=1
    assert dict(sorted(local.items())) == {int(k):n for k,n in signed['forward_and_reflected_ledgers'][0]['histogram'].items()}
    # Full unsplit idle gaps from the freshly checked B3 geometry.
    rebuilt=Counter({r:T*S*n for r,n in local.items()})
    for r in (14,7,28,7,34,20,6):rebuilt[r]+=2*v*T
    assert H==rebuilt
    N=2*m;d=m*m;J=T*(2*S*(2*v+R)+2*KP*v)
    K=2*S*T*((stock-1)+R*m*((m-1)+m))
    assert source_input['K']==K
    good=8*m*m+8;high=16*(d+1)**2
    fixed=J*high+J*(stock+ncopy)+E*good+E*(128*N**3)+16*m**3+S*ncopy*T+E+K+1
    bridge=T*6*(KP-1)*v
    old_coefficient=T*S*raw_unit+bridge+fixed
    coefficient=T*S*unit+bridge+fixed
    assert old_coefficient==original['coefficient']==56223565806031
    assert coefficient==56223565818967 and coefficient-old_coefficient==12936
    assert coefficient.bit_length()==old_coefficient.bit_length()==46 and coefficient<2**80
    assert prefix['formal_columns']==stock and prefix['copies']==S*T*ncopy
    payload=prefix['payload_prefix'];assert payload.bit_length()==71 and payload<2**104
    signed_payload=signed_prefix['payload_prefix']
    assert signed_prefix['formal_columns']==stock and signed_prefix['copies']==S*T*ncopy
    assert signed_payload.bit_length()==71 and signed_payload<2**104
    F=signed['forward']['max_prefix_row_l1'];B=signed['literal_signed_inverse']['max_prefix_row_l1']
    legacy=64*F**3*B**2
    assert (F,B)==(742,7500) and legacy==original['payload_prefix_upper'] and legacy<payload
    result=deepcopy(original)
    result.update(coefficient=coefficient,weighted_additions=T*S*weighted+bridge,
        unit_expanded_additions=T*S*unit+bridge,payload_prefix_upper=payload,payload_prefix_bits=71,
        status='PASS_COMPENSATED_SIGNED_WITNESS_INVOICE_AND_ACTUAL_SEVEN_STAGE_SCALAR_PREFIX',
        original_counted_coefficient=old_coefficient,conservative_extra_coefficient=12936,
        signed_witness_payload_prefix=signed_payload,signed_witness_payload_bits=71,
        local_additions=dict(emitted_weighted=raw_weighted,emitted_unit=raw_unit,
            signed_weighted=weighted,signed_unit=unit,extra_weighted=weighted-raw_weighted,
            extra_unit=unit-raw_unit,invocations=T*S),
        replaced_legacy_payload=dict(value=legacy,bits=legacy.bit_length(),valid_upper_bound=False),
        payload_method='Cancellation-free scan of every actual exported parity ADD, COPY, ERASE, bridge and terminal exchange in all seven stages and seven replicas.',
        scope='The defining signed integer witness is conservatively charged; the actual emitted parity record bytes and recursive profile remain unchanged. The scalar prefix is not a separate proof of all-size chart/compiler, routing or recovery interfaces.')
    return result
