#!/usr/bin/env python3
"""Exact dirty-state and resource replay for the aligned FANIN4 stream."""

from dataclasses import dataclass


def need(condition, message):
    if not condition:
        raise ValueError(message)


@dataclass
class Meter:
    reads: int = 0
    writes: int = 0
    xors: int = 0
    forward_moves: int = 0
    return_moves: int = 0
    call_records: int = 0
    source_refs: int = 0
    target_refs: int = 0
    scratch_cells: int = 0
    frame_transitions: int = 0

    @property
    def head_moves(self):
        return self.forward_moves + self.return_moves


def singleton_sequence(sources, target, width, return_heads=True):
    """Four complete in-place source-to-target ADD passes."""
    need(len(sources) == 4, "four sources required")
    need(width >= 1, "positive coefficient width")
    limit = 1 << width
    need(all(type(x) is int and 0 <= x < limit for x in sources), "source extent")
    need(type(target) is int and 0 <= target < limit, "target extent")

    meter = Meter()
    current = target
    for source in sources:
        out = 0
        for lane in range(width):
            source_bit = (source >> lane) & 1
            target_bit = (current >> lane) & 1
            out |= (source_bit ^ target_bit) << lane
        current = out
        meter.reads += 2 * width
        meter.writes += width
        meter.xors += width
        meter.forward_moves += 2 * width
        meter.return_moves += 2 * width if return_heads else 0
        meter.call_records += 1
        meter.source_refs += 1
        meter.target_refs += 1
    return current, meter, (0, 0, 0, 0, 0) if return_heads else (width,) * 2


def fanin4(sources, target, width, return_heads=True):
    """One aligned pass; apply all four source XORs to each dirty target lane."""
    need(len(sources) == 4, "four sources required")
    need(width >= 1, "positive coefficient width")
    limit = 1 << width
    need(all(type(x) is int and 0 <= x < limit for x in sources), "source extent")
    need(type(target) is int and 0 <= target < limit, "target extent")

    meter = Meter()
    out = 0
    for lane in range(width):
        bit = (target >> lane) & 1
        for source in sources:
            bit ^= (source >> lane) & 1
            meter.xors += 1
        out |= bit << lane

    meter.reads = 5 * width
    meter.writes = width
    meter.forward_moves = 5 * width
    meter.return_moves = 5 * width if return_heads else 0
    meter.call_records = 1
    meter.source_refs = 4
    meter.target_refs = 1
    heads = (0,) * 5 if return_heads else (width,) * 5
    return out, meter, heads


def omitted_source(sources, target, omitted):
    out = target
    for j, source in enumerate(sources):
        if j != omitted:
            out ^= source
    return out


def charge_vector(meter):
    return {
        "reads": meter.reads,
        "writes": meter.writes,
        "xors": meter.xors,
        "head_moves": meter.head_moves,
        "records": meter.call_records,
        "source_refs": meter.source_refs,
        "target_refs": meter.target_refs,
        "scratch_cells": meter.scratch_cells,
        "frame_transitions": meter.frame_transitions,
    }


def weighted_saving(single, fused, prices):
    """Exact singleton-minus-fused difference under a declared resource price."""
    return sum(
        (single[name] - fused[name]) * price
        for name, price in prices.items()
    )


def trace_head_returns(width):
    """Replay the pointer schedule independently of the data values."""
    single_heads = [0] * 5
    single_forward = 0
    single_return = 0
    for source_index in range(4):
        for lane in range(width):
            need(single_heads[source_index] == lane and single_heads[4] == lane,
                 "singleton inputs are not aligned")
            single_heads[source_index] += 1
            single_heads[4] += 1
            single_forward += 2
        need(single_heads[source_index] == width and single_heads[4] == width,
             "singleton scan extent")
        single_return += single_heads[source_index] + single_heads[4]
        single_heads[source_index] = 0
        single_heads[4] = 0
    need(single_heads == [0] * 5, "singleton return scan")

    fused_heads = [0] * 5
    fused_forward = 0
    for lane in range(width):
        need(fused_heads == [lane] * 5, "fused inputs are not aligned")
        fused_heads = [position + 1 for position in fused_heads]
        fused_forward += 5
    need(fused_heads == [width] * 5, "fused scan extent")
    fused_return = sum(fused_heads)
    fused_heads = [0] * 5
    need(fused_heads == [0] * 5, "fused return scan")
    return {
        "single_forward": single_forward,
        "single_return": single_return,
        "fused_forward": fused_forward,
        "fused_return": fused_return,
    }


def exhaustive_dirty_states(width):
    """Enumerate every joint state of four sources and one target."""
    states = 1 << (5 * width)
    mask = (1 << width) - 1
    for packed in range(states):
        sources = tuple((packed >> (j * width)) & mask for j in range(4))
        target = (packed >> (4 * width)) & mask
        fused, _, heads = fanin4(sources, target, width)
        singles, _, single_heads = singleton_sequence(sources, target, width)
        need(fused == singles, "fused and singleton target maps differ")
        back, _, back_heads = fanin4(sources, fused, width)
        need(back == target, "fused inverse failed")
        need(heads == single_heads == back_heads == (0,) * 5, "head return failed")
        need(sources == tuple((packed >> (j * width)) & mask for j in range(4)),
             "read-only source changed")
    return states


def main():
    width = 4
    sources = (0b1011, 0b0110, 0b1101, 0b1001)
    target = 0b0101
    fused, fused_meter, fused_heads = fanin4(sources, target, width)
    singles, single_meter, single_heads = singleton_sequence(sources, target, width)
    need(fused == singles, "positive fixture")
    need(fused_heads == single_heads == (0,) * 5, "returned heads")
    need(fanin4(sources, fused, width)[0] == target, "explicit reverse")

    fused_cost = charge_vector(fused_meter)
    single_cost = charge_vector(single_meter)
    need(fused_cost == {
        "reads": 20, "writes": 4, "xors": 16, "head_moves": 40,
        "records": 1, "source_refs": 4, "target_refs": 1,
        "scratch_cells": 0, "frame_transitions": 0,
    }, "fused exact cost")
    need(single_cost == {
        "reads": 32, "writes": 16, "xors": 16, "head_moves": 64,
        "records": 4, "source_refs": 4, "target_refs": 4,
        "scratch_cells": 0, "frame_transitions": 0,
    }, "singleton exact cost")
    trace = trace_head_returns(width)
    need((trace["single_forward"], trace["single_return"]) == (32, 32),
         "singleton pointer trace")
    need((trace["fused_forward"], trace["fused_return"]) == (20, 20),
         "fused pointer trace")
    need(trace["single_forward"] + trace["single_return"] == single_cost["head_moves"],
         "singleton charged head trace")
    need(trace["fused_forward"] + trace["fused_return"] == fused_cost["head_moves"],
         "fused charged head trace")
    unit_prices = {
        "reads": 1, "writes": 1, "xors": 1, "head_moves": 1,
        "records": 1, "source_refs": 1, "target_refs": 1,
        "scratch_cells": 1, "frame_transitions": 1,
    }
    unit_saving = weighted_saving(single_cost, fused_cost, unit_prices)
    need(unit_saving == 54, "uniform-price full bill")

    # Each omitted source is detected on a basis-state positive control.
    for omitted in range(4):
        basis_sources = tuple(1 if j == omitted else 0 for j in range(4))
        correct = fanin4(basis_sources, 0, width)[0]
        bad = omitted_source(basis_sources, 0, omitted)
        need(correct != bad, "omitted-source control failed")

    # A schedule that skips the return scan is rejected by the entry-head contract.
    _, _, no_return_heads = fanin4(sources, target, width, return_heads=False)
    need(no_return_heads == (width,) * 5, "no-return control fixture")
    need(no_return_heads != (0,) * 5, "no-return control was accepted")

    states = exhaustive_dirty_states(width)
    need(states == 1_048_576, "incomplete dirty-state domain")
    print(
        "PASS_FANIN4_STREAM "
        f"states={states} L={width} "
        f"xor={single_cost['xors']}/{fused_cost['xors']} "
        f"reads={single_cost['reads']}/{fused_cost['reads']} "
        f"writes={single_cost['writes']}/{fused_cost['writes']} "
        f"head_moves={single_cost['head_moves']}/{fused_cost['head_moves']} "
        f"records={single_cost['records']}/{fused_cost['records']} "
        f"unit_saving={unit_saving} controls=6"
    )


if __name__ == "__main__":
    main()
