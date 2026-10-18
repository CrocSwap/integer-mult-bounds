"""Independent finite GL enumeration, directory order and route endpoints."""
from fractions import Fraction as F
from hashlib import sha256
from itertools import product
import json

from binding import owner_common, selected_episode
from check_support import Origins, audit, bits, inspect_count, no_decode
from counts import Count, high_power
from directory import Context, Odometer, produce
from low_codes import LowCodes
from matrices import Matrices
import oracle
from records import RECORD_END, Tape, append_finite, append_word, read_finite, read_word
from routes import compile_route, high_key, inverse_rational, route_packet
from sources import ROOT, compile_templates, identity
from words import Arena, BLANK, Ring, need


def low_codes():
    counts = {}
    for dimension in (1,2,3):
        codes, ordinal = LowCodes(3,dimension,2), 0
        for values in product(range(3), repeat=dimension*dimension):
            matrix = tuple(tuple(values[i*dimension:(i+1)*dimension]) for i in range(dimension))
            try:
                oracle.inverse(matrix,3)
            except ValueError:
                continue
            need(codes.rank(matrix) == ordinal and codes.unrank(ordinal) == matrix,
                 "independent lexicographic GL census")
            for request, common in ((0,False),(1,True)):
                code = codes.encode(request,common,matrix)
                need(codes.decode(code) == (request,common,matrix), "request/view/low code injection")
            ordinal += 1
        need(ordinal == codes.size, "complete GL cardinality")
        counts[str(dimension)] = ordinal
    large = LowCodes(3,64,28278)
    ordinals = (0,1,large.size//3,large.size//2,large.size-2,large.size-1)
    for ordinal in ordinals:
        low = large.unrank(ordinal)
        need(large.rank(low) == ordinal, "selected GL64 ordinal round trip")
        oracle.inverse(low,3)
    return {"exhaustive_GL_counts":counts, "selected_GL64_samples":len(ordinals),
            "full_request_code_bits":large.bits, "selected_low_count_sha256":sha256(str(large.size).encode()).hexdigest()}


def encoded_old(context, records):
    out = Tape()
    for prefix in records:
        for code, high in prefix:
            append_finite(out,code,context.codes.bits)
            for value in high:
                word = context.arena.input(value)
                append_word(out,word)
                context.arena.free(word)
            out.append(RECORD_END)
    out.rewind()
    return out


def directory_case(dimension=2,width=2,fields=2):
    q, modulus = 3,3**width
    arena, indices = Arena(modulus.bit_length()+1), Arena(8)
    mod, old_fields = arena.input(modulus), indices.input(fields)
    ring, codes = Ring(mod), LowCodes(q,dimension,2)
    context = Context(ring,codes)
    old_count = Count.literal(3)
    old_code, code = codes.encode(0,False,oracle.eye(dimension)), codes.encode(1,True,oracle.eye(dimension))
    high = tuple((i*2+1) % (modulus//q) for i in range(dimension*dimension))
    # Equal frozen tuples at positions0 and2 represent different physical rows.
    records = [tuple((old_code, high if p != 1 else tuple(reversed(high))) for _ in range(fields))
               for p in range(3)]
    old = encoded_old(context,records)
    original = bytes(old.cells)
    with no_decode():
        directory, count = produce(old,old_fields,old_count,code,context)
    h = (modulus//q)**(dimension*dimension)
    need(inspect_count(count) == 3*h, "unbounded emitted directory count")
    for prefix in records:
        for current in product(range(modulus//q),repeat=dimension*dimension):
            for expected_code, expected_high in prefix+((code,current),):
                need(read_finite(directory,codes.bits) == expected_code, "physical field tag order")
                for expected in expected_high:
                    value = read_word(directory,arena)
                    need(value.inspect() == expected, "old multiplicity and canonical high order")
                    arena.free(value)
                need(directory.read() == RECORD_END, "complete output field")
                directory.step(1)
    need(directory.read() == BLANK and old.head == 1 and bytes(old.cells) == original,
         "complete source-preserving directory")
    result = {"dimension":dimension,"width":width,"old_fields":fields,"old_prefixes":3,
              "prefixes":3*h,"bytes":len(directory.cells)-1,"code_bits":codes.bits,
              "sha256":sha256(bytes(directory.cells)).hexdigest()}
    directory.clear(); old.clear(); count.close(); old_count.close(); context.close(); ring.close()
    arena.free(mod); indices.free(old_fields)
    audit(arena); audit(indices)
    return result


def route_case(width=2,older=3):
    q,modulus,dimension,fibre_size = 3,3**width,2,5
    codes = LowCodes(q,dimension,2)
    arena = Arena(modulus.bit_length()+1)
    mod = arena.input(modulus); ring = Ring(mod); context = Context(ring,codes)
    low = ((1,2),(0,1))
    chart = ((F(1,2),F(1)),(F(-1),F(2)))
    route = compile_route(low,chart,codes)
    inverse = compile_route(route.target_low,inverse_rational(chart),codes)
    h = (modulus//q)**4
    count,fibre = Count.literal(older),Count.literal(fibre_size)
    origins = Origins()
    source = origins.source(older*h*fibre_size)
    original = bytes(source.cells)
    with no_decode():
        output = route_packet(source,route,context,count,fibre,origins.factory)
    carry_witnesses = 0
    for old in range(older):
        for ordinal,high in enumerate(product(range(modulus//q),repeat=4)):
            raw = [[low[i][j]+q*high[2*i+j] for j in range(2)] for i in range(2)]
            target = oracle.multiply(raw,oracle.reduce_rational(chart,modulus),modulus)
            high_only = oracle.multiply([high[:2],high[2:]],oracle.reduce_rational(chart,modulus//q),modulus//q) if width>1 else [[0,0],[0,0]]
            key = tuple(value//q for row in target for value in row)
            carry_witnesses += key != tuple(value for row in high_only for value in row)
            destination = 0
            for value in key: destination = destination*(modulus//q)+value
            for suffix in range(fibre_size):
                old_index = (old*h+ordinal)*fibre_size+suffix
                new_index = (old*h+destination)*fibre_size+suffix
                need(output.origins.get(new_index+1) == old_index and
                     output.cells[new_index+1] == original[old_index+1], "exact route bit origins")
    with no_decode():
        restored = route_packet(output,inverse,context,count,fibre,origins.factory)
    need(bits(restored) == bits(source) and all(restored.origins.get(i+1) == i for i in range(older*h*fibre_size)),
         "full owner inverse return")
    need(origins.live == {source,output,restored} and bytes(source.cells) == original and
         source.head == output.head == restored.head == 1, "route scratch and input ownership")
    result = {"width":width,"old_prefixes":older,"highs_per_prefix":h,"bits":older*h*fibre_size,
              "carry_witnesses":carry_witnesses,"erased_tapes":origins.erased,
              "payload_sha256":sha256(bits(output)).hexdigest()}
    for tape in (source,output,restored):tape.clear()
    count.close();fibre.close();context.close();ring.close();arena.free(mod);audit(arena)
    return result


def selected_binding():
    codes = LowCodes(3,64,2)
    move = compile_templates()[1]
    native = tuple(tuple(int(x) for x in row) for row in move.chart)
    owner,common,route = owner_common(move,native,0,codes)
    need(route.target_low == tuple(map(tuple,identity(64))), "actual MOVE common identity header")
    zero = tuple((0,)*64 for _ in range(64))
    correct = oracle.projector(common.template,common.low,zero,2)
    wrong = oracle.projector(move,common.low,zero,2)
    need(correct[0][0] == 1 and correct[8][8] == 0 and wrong[0][0] == 0 and wrong[8][8] == 1,
         "actual double-chart witness E00 versus E88")
    episode = selected_episode()
    u = (0,1,-1,0,-1,0,0,-1)
    for i in range(64):
        for j in range(64):
            expected = F(i == j)-F(u[i]*u[j],4) if i<8 and j<8 else F(0)
            need(episode.template.base[i][j] == expected, "independent COPY511 complement vector")
    # A mixed dyadic data chart comes from the retained stage-one port8 route.
    geometry = json.loads((ROOT / "research/community-hyperplane599-audit/pr589/bit589/v9/nine/GEOMETRY.json").read_text())
    port = geometry["ports"][8]
    axes = port["routes"][1]["axes"]
    chart = identity(64)
    for i,a in enumerate(axes):
        for j,b in enumerate(axes):chart[a][b] = F(port["rho15"][i][j])
    charts = (move.chart,episode.chart,tuple(map(tuple,chart)))
    arena = Arena(5); mod=arena.input(9); ring=Ring(mod); context=Context(ring,codes)
    matrices = Matrices(ring)
    checked = 0
    for chart in charts:
        route = compile_route(oracle.eye(64),chart,codes)
        fixed = matrices.constants(route.chart)
        for seed in (0,1,2):
            high = tuple(tuple((i*7+j*11+seed) % 3 for j in range(64)) for i in range(64))
            encoded = [[arena.input(x) for x in row] for row in high]
            with no_decode():key=high_key(encoded,route,fixed,context)
            raw = [[int(i==j)+3*high[i][j] for j in range(64)] for i in range(64)]
            expected = oracle.multiply(raw,oracle.reduce_rational(chart,9),9)
            need([[x.inspect() for x in row] for row in key] == [[x//3 for x in row] for row in expected],
                 "selected binary high-key/carry preparation")
            matrices.free(encoded);matrices.free(key);checked+=1
        matrices.free(fixed)
    context.close();ring.close();arena.free(mod);audit(arena)
    return {"double_chart_input":0,"correct_output":127,"wrong_output":0,
            "selected_high_matrices":checked,"selected_high_entries":checked*4096,
            "source_code_bits":codes.bits,"episode_sha256":episode.sha256,"targets":len(episode.targets)}
