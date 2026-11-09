"""Source-bound setup and full physical union replay, with external observers.
Prepared for @CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
from hashlib import sha256
from itertools import product
import json
import sys
import time
from fixture_tools import need, body, snapshot, frame, emit, integer, digest


def meter(tapes):
    return tuple(sum(getattr(t.meter, key) for t in tapes) for key in ('reads', 'writes', 'moves'))


def delta(tapes, before):
    return tuple(a-b for a,b in zip(meter(tapes), before))


def context(window, axes, reference, spectator=0):
    key = dict(schema='physical-union-context-v1', spectator=spectator,
               canonical_commit='7c49fe32c55de02c2c873655c804b16e4c3fef0a',
               numerical_commit='9c6078ff36ae2110e6cc30ff69a9addbf5a47bf2',
               reference_parameters=list(reference.spec.__dict__.values()),
               axis_keys=[dict(origin=window.origin, length=window.length,
                               interior_blocks=window.interior_blocks,
                               block=window.block, P=window.P, w=window.w)
                          for _ in range(axes)])
    raw = json.dumps(key, separators=(',', ':'), sort_keys=True).encode()
    return bytes((v >> i) & 1 for v in raw for i in reversed(range(8))), key


def prepare_bank(window, axes, key, all_tapes, oracle):
    from records import Tape
    from cardinal_counts import Count
    from scratch_pool import ScratchPool
    from session import OuterScope, sealed_constructors, erase_marker, initialize_marker
    from router_metadata import owned
    from check_support import no_decode
    from source_window import physical_factors
    from boundary_pages import prepare_pages
    from union_bits import PART_END, BLOCK_START, BLOCK_END, put_count, put_big, copy_until
    pool = ScratchPool(192); scope = OuterScope(pool)
    for tape in pool.tapes:
        erase_marker(tape); initialize_marker(tape)
    bank = Tape()
    descriptors = tuple(Count.literal(x) for x in
                        (len(window.E),len(window.J),window.block,window.w,window.P))
    a,n,b,w,p = descriptors
    before = meter(all_tapes); started=time.monotonic()
    matrices=[]; pages=[]; page_hashes=[]; page_bits=[]; receipt=None
    try:
        with sealed_constructors(), scope.installed():
            matrices=physical_factors(window,pool)
            print('SOURCE_FACTORS_SERIALIZED',file=sys.stderr,flush=True)
            for pair in (matrices[:2],matrices[2:]):
                with no_decode():
                    pages.append(prepare_pages(*pair,b,w,p,pool))
                print('SOURCE_PAGE_PAIR_PREPARED',file=sys.stderr,flush=True)
            for matrix in matrices:
                matrix.close()
            matrices=[]
            for bank_pages,pair in zip(pages,((window.shear_lower,window.shear_upper),
                                              (window.f_lower,window.f_upper))):
                expected=oracle.page_words(*pair,window.block,window.P)
                for tape,values in zip(bank_pages,expected):
                    raw=body(tape)
                    need([integer(raw[i:i+window.w]) for i in range(0,len(raw),window.w)]==list(values),
                         'original-matrix observer agrees with actual prepared pages')
                    page_hashes.append(sha256(raw).hexdigest());page_bits.append(len(raw))
            prepared_actions=delta(all_tapes,before)
            serialization_before=meter(all_tapes)
            for digit in key:
                bank.append(digit)
            bank.append(PART_END)
            h=(window.length-1).bit_length()
            with owned(Count.literal(h)) as (hb,):
                for _ in range(axes):
                    bank.append(BLOCK_START)
                    for value in (a,n,b):
                        put_count(value,bank)
                    for value in window.E:
                        with owned(Count.literal(value)) as (coordinate,):
                            put_big(coordinate,bank,hb)
                    bank.append(PART_END)
                    for digit in window.j_mask:
                        bank.append(digit)
                    bank.append(PART_END)
                    for bank_pages in pages:
                        for tape in bank_pages:
                            tape.rewind();copy_until(tape,bank);tape.rewind()
                            bank.append(PART_END)
                    bank.append(BLOCK_END)
            bank.rewind()
            serialization_actions=delta(all_tapes,serialization_before)
            for bank_pages in pages:
                for tape in bank_pages:
                    tape.clear()
            pages=[]
        pool.empty()
        receipt=dict(prepared_actions=prepared_actions,serialization_actions=serialization_actions,
                     all_setup_actions=delta(all_tapes,before),page_sha256=page_hashes,
                     page_bits=page_bits,catalogue_bits=len(body(bank)),
                     setup_pool_retained_cells=sum(len(t.cells) for t in pool.tapes),
                     seconds=time.monotonic()-started)
        return bank,receipt
    finally:
        for matrix in matrices:
            matrix.close()
        for bank_pages in pages:
            for tape in bank_pages:
                tape.clear()
        for value in descriptors:
            value.close()
        pool.empty()
        for tape in pool.tapes:
            erase_marker(tape)
        if receipt is not None:
            receipt['all_setup_actions']=delta(all_tapes,before)
            receipt['seconds']=time.monotonic()-started


def run(raw, window, reference, all_tapes, axes=2):
    from records import Tape
    from cardinal_counts import Count
    from words import BLANK
    from check_support import no_decode
    from physical_router import UnionRouter
    import independent_oracle as oracle
    from reference_source import source_receipt
    g=axes;L=window.length;key,key_description=context(window,g,reference)
    source_review=oracle.check_source(reference,window)
    catalogue,preparation=prepare_bank(window,g,key,all_tapes,oracle)
    print('SOURCE_BANK_PREPARED',file=sys.stderr,flush=True)
    owner=UnionRouter();source=Tape()
    points=list(product(range(L),repeat=g))
    initial={x:(((37*i+11)%41-20)*(1<<(window.P-8)),
                ((53*i+7)%47-23)*(1<<(window.P-8))) for i,x in enumerate(points)}
    expected,grid_review=oracle.full_grid(L,(window,)*g,initial)
    emit(source,frame(key,[initial[x] for x in points],window.w))
    metadata=tuple(Count.literal(x) for x in
                   (g,L,(L-1).bit_length(),g.bit_length(),window.w,window.P))
    ports=(source,catalogue,*(x.tape for x in metadata))
    saved=snapshot(ports);before=meter(all_tapes);started=time.monotonic()
    leaves=owner.child.child.kernel.leaves
    try:
        with no_decode():
            returned=owner.run(source,catalogue,*metadata)
        run_actions=delta(all_tapes,before)
        raw_return=body(returned);off=len(key)+1
        need(raw_return[:off]==key+bytes((5,)),'protected complete original context return')
        actual=[(integer(raw_return[i:i+window.w]),integer(raw_return[i+window.w:i+2*window.w]))
                for i in range(off,len(raw_return),2*window.w)]
        need(actual==[expected[x] for x in points],'physical whole union equals independent full-grid reference')
        need(snapshot(ports)==saved,'restored source, complete bank and descriptors')
        protected_cells=sum(len(t.cells) for t in owner.forbidden())
        output_bits=len(raw_return)
        consume_before=meter(all_tapes)
        with no_decode():
            owner.consume()
        consume_actions=delta(all_tapes,consume_before)
        need(all(t.head==1 and all(v==BLANK for v in t.cells) for t in owner.forbidden()),
             'all owned descendants and historical backing erased')
        return dict(marker='PASS_SOURCE_BOUND_WHOLE_PHYSICAL_UNION',
                    source=window.receipt(),source_reference=source_receipt(reference),
                    source_review=source_review,grid_review=grid_review,context=key_description,
                    context_bits=len(key),preparation=preparation,
                    transport=dict(actions=run_actions,consume_actions=consume_actions,
                                   rounds=owner.rounds,visits=owner.visits,substreams=owner.substreams,
                                   dense_records=owner.dense_records,owned_roles=len(owner.forbidden()),
                                   retained_cells=protected_cells,output_bits=output_bits,
                                   pool_peak=owner.pool.peak,
                                   scalar_products=owner.child.child.kernel.leaves-leaves,
                                   output_sha256=digest(actual),seconds=time.monotonic()-started),
                    no_new_kappa=True)
    finally:
        if owner.pending:
            owner.consume()
        for value in metadata:
            value.close()
        source.clear();catalogue.clear()
