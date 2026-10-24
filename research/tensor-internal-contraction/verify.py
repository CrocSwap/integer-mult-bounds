#!/usr/bin/env python3
"""Source-authenticated, bounded actual Tensor expansion-prefix audit."""
import argparse
from collections import Counter
from contextlib import ExitStack
from fractions import Fraction as F
from hashlib import sha256
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from majorant import (Cursor, axis, block, block_page, count_raw, expand, fraction,
                      need, pairs, signed_raw, tile_page, trunc)


def digest(raw):
    return sha256(raw).hexdigest()


def authenticate(path, expected):
    need(path.is_file() and not path.is_symlink() and digest(path.read_bytes()) == expected,
         "exact live source bytes: "+str(path))


def sources():
    manifest = json.loads((HERE/"SOURCES.json").read_text())
    rows = [row for row in manifest["files"] if row["usage"] == "input"]
    for row in rows:
        authenticate(ROOT/row["path"], row["sha256"])
    need(rows, "nonempty authenticated caller closure")
    with TemporaryDirectory() as directory:
        forged = Path(directory)/"changed.py"
        original = (ROOT/rows[0]["path"]).read_bytes()
        forged.write_bytes(original+b"\n# fault\n")
        try:
            authenticate(forged, rows[0]["sha256"])
        except ValueError as error:
            need("exact live source bytes" in str(error), "source-byte mutation rejection")
        else:
            raise ValueError("source-byte mutation accepted")
    return {"live_inputs": len(rows), "source_mutant": "rejected"}


def algebra_controls():
    # These discriminate premises, not a finite surrogate for the proof.
    need(trunc(-7, 2) == -1 and (-7//4) == -2, "signed inward differs from floor")
    need(trunc(3, 2)+trunc(3, 2) != trunc(6, 2), "inward map is nonlinear")
    need(trunc(-1, 2) == 0 and abs(-1//4) > F(1, 4), "floor violates absolute domination")
    need((1, -1)[1] == -1 and abs(1*1+(-1)*(-1)) > (1-1)*1,
         "signed row-sum cannot replace positive absolute mass")
    # Duplication and zero extension commute with a deterministic zero-preserving
    # nonlinear map on another axis; addition does not enter this identity.
    f = lambda row: tuple(trunc(3*x, 2) for x in row)
    rows = [(3, -7), (1, -1)]
    select = [1, 0, 1, None]
    duplicate = lambda data: [data[i] if i is not None else (0, 0) for i in select]
    need([f(row) for row in duplicate(rows)] == duplicate([f(row) for row in rows]),
         "nonlinear duplication and zero extension commute")
    need(f((0, 0)) == (0, 0), "zero preservation")
    return ["negative floor rounding", "nonlinearity", "negative coefficient cancellation",
            "duplicate/zero extension on another axis"]


def physical():
    sys.path.insert(0, str(ROOT/"research/physical-gaussian-tensor"))
    from tensor_sources import opened
    with opened():
        from cardinal_counts import Count
        from check_composed import encode
        from check_support import no_decode
        import expansion_block
        import gaussian_convolution
        from expansion_check_block import packet_bytes
        from ring_check_words import tape
        from session import erase_marker
        from tensor_engine import Tensor
        from tensor_fixture import finite_chirp, literal_native, prepared_catalogue
        from tensor_model import catalogue
        from tensor_records import bounded_record_io
        from tensor_router import FullRouter
        from words import BLANK

        def capture(port):
            head = port.head
            raw = packet_bytes(port)
            while port.head < head:
                port.step(1)
            while port.head > head:
                port.step(-1)
            return raw

        def signed(value):
            return capture(value.magnitude.tape), value.negative

        B = 1 << 48
        # Both components have both signs; no random or floating point input.
        values = [(((17*i+5) % 97-48)*(B//256), ((29*i+11) % 89-44)*(B//256))
                  for i in range(49)]
        need(all(4*(a*a+b*b) <= B*B for a, b in values), "actual half-disk fixture")
        raw_input, raw_catalogue = encode(values, 50), prepared_catalogue()
        header, profiles = catalogue(raw_catalogue)
        need(header["p"] == 48 and header["P"] == 80 and header["sources"] == [7, 7],
             "declared archived two-axis fixture")
        machine = Tensor(finite_chirp(), FullRouter(literal_native()))
        tile_owner, block_owner = machine.lines.expansion, machine.lines.expansion.block
        payload, prepared, rows = tape(raw_input), tape(raw_catalogue), Count.literal(1)
        row_before = capture(rows.tape), rows.tape.head
        blocks, tiles, axes, active = [], [], [], []
        original_call, original_axis = machine.call, machine.apply_lines
        original_block, original_tile = block_owner.run, tile_owner.run
        original_bt, original_ct = expansion_block.truncate, gaussian_convolution.truncate
        snapshot = []
        class PrefixStop(Exception):
            pass

        def observed_truncate(original, label):
            def run(value, amount):
                before, negative = signed(value)
                amount_raw = capture(amount.tape)
                result = original(value, amount)
                after, after_negative = signed(result)
                need(active, "truncation occurs inside actual block")
                active[-1].append((label, before, negative, amount_raw, after, after_negative))
                return result
            return run

        def observed_block(page, source):
            record = dict(page=capture(page), source=capture(source), trace=[])
            active.append(record["trace"])
            try:
                output = original_block(page, source)
                record["output"] = capture(output)
                need(capture(page) == record["page"] and capture(source) == record["source"]
                     and block_owner.closed and not block_owner.pool.live,
                     "actual block borrowed ports and owned scratch")
                blocks.append(record)
                return output
            finally:
                active.pop()

        def observed_tile(page, source):
            page_raw, source_raw = capture(page), capture(source)
            output = original_tile(page, source)
            need(capture(page) == page_raw and capture(source) == source_raw
                 and tile_owner.closed and not tile_owner.pool.live,
                 "actual tile borrowed ports and owned scratch")
            tiles.append(dict(page=page_raw, source=source_raw, output=capture(output),
                              counts=dict(tile_owner.last_counts)))
            return output

        def observed_axis(*parameters, **options):
            original_axis(*parameters, **options)
            axes.append(capture(machine.current))

        def stop_before_chirp(owner, *parameters, **options):
            if owner is machine.chirp:
                snapshot.append(capture(machine.current))
                raise PrefixStop()
            return original_call(owner, *parameters, **options)

        try:
            with ExitStack() as stack:
                stack.enter_context(patch.object(machine, "call", stop_before_chirp))
                stack.enter_context(patch.object(machine, "apply_lines", observed_axis))
                stack.enter_context(patch.object(block_owner, "run", observed_block))
                stack.enter_context(patch.object(tile_owner, "run", observed_tile))
                stack.enter_context(patch.object(expansion_block, "truncate", observed_truncate(original_bt, "block")))
                stack.enter_context(patch.object(gaussian_convolution, "truncate", observed_truncate(original_ct, "convolution")))
                try:
                    with no_decode():
                        machine.run(payload, prepared, rows)
                except PrefixStop:
                    pass
                else:
                    raise ValueError("expansion-prefix stop was not reached")
            expected_counts = dict(natural_padding=2, gathers=2, halos=2, expansion_axes=2,
                                   compression_axes=0, assembled_axes=0, chirps=0)
            need(len(snapshot) == 1 and len(axes) == 2 and machine.last_counts == expected_counts,
                 "actual complete two-axis expansion prefix")
            need(capture(payload) == raw_input and capture(prepared) == raw_catalogue
                 and (capture(rows.tape), rows.tape.head) == row_before,
                 "prefix preserves borrowed payload/catalogue/encoded rows")
            machine.idle()
            need(machine.closed and not machine.pool.live and machine.current is machine.following is None
                 and machine.output.read() == BLANK
                 and all(t.head == 1 and all(v == BLANK for v in t.cells) for t in machine.pool.tapes),
                 "intentional prefix stop releases parent/child ownership")

            rounding, truncations, masses = Counter(), 0, []
            for record in blocks:
                page = block_page(record["page"])
                data = pairs(record["source"], page["p"]+2)
                expected, trace, remainders, row_masses = block(data, page)
                actual_trace = [(label, signed_raw(before, negative), count_raw(amount),
                                 signed_raw(after, after_negative))
                                for label, before, negative, amount, after, after_negative in record["trace"]]
                need(actual_trace == trace, "every actual internal truncation equals the signed staged reference")
                need(pairs(record["output"], page["p"]+2) == expected, "actual block signed complex result")
                b = F(1, 2)+F(1, 20**(page["alpha"]**2)-1)
                need(all(mass <= b for mass in row_masses), "finite source-page majorant row mass")
                masses.extend(row_masses)
                rounding.update(remainders)
                truncations += len(trace)
            need(all(rounding[stage] > 0 for stage in ("weighted", "convolution", "post", "fine", "extract")),
                 "nonzero rounding at all five actual stages")
            need(any(a < 0 for a, b in values) and any(a > 0 for a, b in values)
                 and any(b < 0 for a, b in values) and any(b > 0 for a, b in values),
                 "both signed complex components exercised")
            for record in tiles:
                tile, pages = tile_page(record["page"])
                source = pairs(record["source"], tile["p"]+2)
                need(all(pair == (0, 0) for pair in source[tile["source_count"]:]), "actual tile zero padding")
                expected = []
                next_target = tile["target_start"]
                for page in pages:
                    need(page["target_start"] == next_target, "actual tile original target ownership")
                    offset = page["source_start"]-tile["source_start"]
                    need(0 <= offset and offset+page["n"] <= tile["source_count"], "actual source halo window extent")
                    result, _, _, _ = block(source[offset:offset+page["n"]], page)
                    expected.extend(result)
                    next_target += page["m"]
                need(len(expected) == tile["target_length"]
                     and pairs(record["output"], tile["p"]+2) == expected, "actual complete streamed tile")
            need(any(record["counts"]["overlap_records"] > 0 for record in tiles), "actual retained tile overlaps")
            data, shape, axis_norms = values, (7, 7), []
            initial_norm2 = max(a*a+b*b for a, b in values)
            cumulative = F(1)
            for index, profile in enumerate(profiles):
                data, shape = axis(data, shape, index, profile)
                page = profile["expansion_pages"][0][1][0]
                cumulative *= F(1, 2)+F(1, 20**(page["alpha"]**2)-1)
                physical_values = pairs(axes[index], 50)
                norm2 = max(a*a+b*b for a, b in physical_values)
                need(norm2 == max(a*a+b*b for a, b in data)
                     and norm2 <= initial_norm2*cumulative*cumulative,
                     "actual full-axis nonlinear contraction recurrence")
                axis_norms.append(norm2)
            need(shape == (8, 8) and snapshot[0] == encode(data, 50),
                 "actual halo/layout prefix equals independent natural-coordinate expansion")
            # A wrong natural layout must be observable in these signed fixtures.
            transposed = [data[j*8+i] for i in range(8) for j in range(8)]
            need(encode(transposed, 50) != snapshot[0], "transposed-layout mutant distinguished")

            first = blocks[0]
            page = block_page(first["page"])
            controls = []
            def rejected(raw_page, raw_source, message):
                changed_page, changed_source = tape(raw_page), tape(raw_source)
                try:
                    try:
                        with bounded_record_io(), no_decode():
                            returned = original_block(changed_page, changed_source)
                    except ValueError as error:
                        need(message in str(error), "actual runtime rejection reason: "+str(error))
                    else:
                        returned.clear(); erase_marker(returned)
                        raise ValueError("actual malformed block accepted")
                    need(capture(changed_page) == raw_page and capture(changed_source) == raw_source
                         and block_owner.closed and not block_owner.pool.live and block_owner.output.read() == BLANK,
                         "actual rejection restores block ownership")
                finally:
                    changed_page.clear(); changed_source.clear()
                    erase_marker(changed_page); erase_marker(changed_source)
            negative = bytearray(first["page"])
            negative[page["factor_offset"]+page["width"]-1] = 1
            rejected(bytes(negative), first["source"], "nonnegative normalized expansion coefficient")
            controls.append("actual negative coefficient rejected; borrowed pages preserved")
            # Move the first original target from zero to one, with the same
            # canonical encoded length; actual Tile must reject the gap.
            first_tile = tiles[0]
            cursor = Cursor(first_tile["page"])
            cursor.header("version p P sigma s t alpha radius source_count input_capacity target_length blocks")
            cursor.integer(); cursor.integer()
            cursor.count()
            block_offset = cursor.pos
            tile_block = block_page(cursor.raw[block_offset:block_offset+len(first["page"])])
            need(tile_block["target_start"] == 0, "target-order control begins at original zero")
            wrong_tile = bytearray(first_tile["page"])
            wrong_tile[block_offset+tile_block["target_offset"]+1] = 1
            tile_port, tile_source = tape(wrong_tile), tape(first_tile["source"])
            try:
                try:
                    with bounded_record_io(), no_decode():
                        output = original_tile(tile_port, tile_source)
                except ValueError as error:
                    need("ordered expansion target blocks" in str(error), "actual target-order rejection")
                else:
                    output.clear(); erase_marker(output)
                    raise ValueError("actual target gap accepted")
                need(tile_owner.closed and not tile_owner.pool.live and tile_owner.output.read() == BLANK
                     and capture(tile_port) == bytes(wrong_tile) and capture(tile_source) == first_tile["source"],
                     "actual target-order failure restores tile ownership")
                controls.append("actual original-target gap rejected before block execution")
            finally:
                tile_port.clear(); tile_source.clear()
                erase_marker(tile_port); erase_marker(tile_source)

            tile_description, _ = tile_page(first_tile["page"])
            need(tile_description["source_count"] < tile_description["input_capacity"],
                 "padding control has an actual unused source record")
            nonzero_padding = bytearray(first_tile["source"])
            nonzero_padding[2*50*tile_description["source_count"]] = 1
            tile_port, tile_source = tape(first_tile["page"]), tape(nonzero_padding)
            try:
                try:
                    with bounded_record_io(), no_decode():
                        output = original_tile(tile_port, tile_source)
                except ValueError as error:
                    need("zero expansion source padding" in str(error), "actual nonzero-padding rejection")
                else:
                    output.clear(); erase_marker(output)
                    raise ValueError("actual nonzero source padding accepted")
                need(tile_owner.closed and not tile_owner.pool.live and tile_owner.output.read() == BLANK
                     and capture(tile_port) == first_tile["page"] and capture(tile_source) == bytes(nonzero_padding),
                     "actual padding failure restores tile ownership")
                controls.append("actual nonzero source padding rejected")
            finally:
                tile_port.clear(); tile_source.clear()
                erase_marker(tile_port); erase_marker(tile_source)

            # Actual selected profile must bind its original source axis.
            cursor = Cursor(raw_catalogue)
            cursor.header("version mode p ell axes alpha inner_bits P sigma radius expansion_capacity halo w")
            cursor.take(header["axes"]+(header["axes"]+1)*header["ell"])
            cursor.count()
            changed_axis = bytearray(raw_catalogue)
            need(changed_axis[cursor.pos:cursor.pos+3] == bytes((1, 1, 1)),
                 "original seven-point source axis locator")
            changed_axis[cursor.pos+1] = 0
            wrong_catalogue, index = tape(changed_axis), Count.literal(0)
            try:
                try:
                    with no_decode():
                        output = machine.lines.run(payload, wrong_catalogue, index, rows, rows)
                except ValueError as error:
                    need("tensor profile binds its original global axis" in str(error),
                         "actual original-axis profile rejection")
                else:
                    output.clear(); erase_marker(output)
                    raise ValueError("actual wrong original-axis profile accepted")
                need(machine.lines.closed and not machine.lines.pool.live and machine.lines.output.read() == BLANK
                     and capture(wrong_catalogue) == bytes(changed_axis) and capture(payload) == raw_input,
                     "actual wrong-axis failure restores line ownership")
                controls.append("actual wrong original-axis profile rejected")
            finally:
                index.close(); wrong_catalogue.clear(); erase_marker(wrong_catalogue)

            # Execute one physical block with a deliberately outward work-grid rounding.
            # The precise trace checker must reject even if final low bits later vanish.
            mutant_trace, fired = [], []
            def outward(value, amount):
                before, negative = signed(value)
                amount_raw = capture(amount.tape)
                result = original_bt(value, amount)
                integer, bits = signed_raw(before, negative), count_raw(amount_raw)
                if not fired and abs(integer) % (1 << bits):
                    result.magnitude.increment()
                    result.negative = bool(negative)
                    fired.append(True)
                after, after_negative = signed(result)
                mutant_trace.append(("block", integer, bits, signed_raw(after, after_negative)))
                return result
            mutant_page, mutant_source = tape(first["page"]), tape(first["source"])
            try:
                with patch.object(expansion_block, "truncate", outward), bounded_record_io(), no_decode():
                    output = original_block(mutant_page, mutant_source)
                output.clear(); erase_marker(output)
                correct_trace = [item for item in block(pairs(first["source"], 50), page)[1] if item[0] == "block"]
                need(fired and mutant_trace != correct_trace, "actual outward rounding mutant must fail exact stage checks")
                controls.append("actual outward work-grid rounding executed and distinguished")
            finally:
                mutant_page.clear(); mutant_source.clear()
                erase_marker(mutant_page); erase_marker(mutant_source)
            # A clean reuse after the injected arithmetic and the protected return protocol.
            clean_page, clean_source = tape(first["page"]), tape(first["source"])
            try:
                with bounded_record_io(), no_decode():
                    output = original_block(clean_page, clean_source)
                need(capture(output) == first["output"], "actual positive reuse after fault")
                try:
                    with bounded_record_io(), no_decode():
                        original_block(clean_page, clean_source)
                except ValueError as error:
                    need("consume prior expansion block output" in str(error), "actual protected output guard")
                else:
                    raise ValueError("actual protected output overwritten")
                need(capture(output) == first["output"], "protected actual block return unchanged")
                output.clear(); erase_marker(output)
                controls.append("actual clean reuse and protected return")
            finally:
                clean_page.clear(); clean_source.clear()
                erase_marker(clean_page); erase_marker(clean_source)

            return {"input_records": 49, "expanded_records": 64, "actual_blocks": len(blocks),
                    "actual_tiles": len(tiles), "actual_truncations": truncations,
                    "nonzero_roundings": dict(rounding), "axis_norm2_pgrid": axis_norms,
                    "initial_norm2_pgrid": initial_norm2, "max_page_row_mass": fraction(max(masses)),
                    "counts": machine.last_counts, "parent_pool_peak": machine.pool.peak,
                    "tile_overlap_records": sum(t["counts"]["overlap_records"] for t in tiles),
                    "catalogue_sha256": digest(raw_catalogue), "expanded_sha256": digest(snapshot[0]),
                    "controls": controls+["wrong transposed natural layout distinguished"],
                    "scope": "intentional complete two-axis expansion prefix; no chirp/compression/production tail replay"}
        finally:
            rows.close()
            payload.clear(); prepared.clear()
            erase_marker(payload); erase_marker(prepared)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    arguments = parser.parse_args()
    evidence = {"schema_version": 1, "status": "PASS", "sources": sources(),
                "algebra_controls": algebra_controls(), "physical": physical()}
    frozen = json.loads((HERE/"RESULT.json").read_text())
    need(evidence == frozen, "exact frozen actual-prefix evidence")
    raw = json.dumps(evidence, indent=2, sort_keys=True)+"\n"
    if arguments.output:
        arguments.output.write_text(raw)
    print(raw, end="")


if __name__ == "__main__":
    main()
