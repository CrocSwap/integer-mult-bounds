"""Exact semantic checks and generated source-bound receipt. Apache-2.0."""

import argparse
import hashlib
import json
from pathlib import Path
from random import Random

from fusion import Layout, commit_code, execute, prepare, read_code, register, require


def scalar_identity() -> int:
    cases = 0
    for width in range(1, 11):
        for bits in (1, 2, 4, 8):
            for offset in range(0, width - bits + 1, bits):
                mask = (1 << bits) - 1
                for word in range(1 << width):
                    old = (word >> offset) & mask
                    for new in range(1 << bits):
                        actual = word ^ ((old ^ new) << offset)
                        expected = (word & ~(mask << offset)) | (new << offset)
                        require(actual == expected, "field identity failed")
                        cases += 1
    return cases


def transition(layout: Layout, heads: list[int], words: list[int], new: list[int]) -> int:
    memory = prepare(layout, heads, words)
    # Fill every register with arbitrary dirt, leaving the ABI parameters intact.
    for address in range(2, layout.base):
        memory.setdefault(address, (address * 37 + 11) & layout.word_mask)
    spectator = layout.word_mask
    require(spectator not in memory, "fixture spectator aliases data")
    memory[spectator] = layout.word_mask // 3
    initial = dict(memory)
    reads = [op for tape in range(layout.tapes) for op in read_code(layout, tape)]
    require(execute(reads, memory, layout.width) == 13 * layout.tapes, "read bill")
    for tape, head in enumerate(heads):
        index = head if head >= 0 else -head - 1
        offset = layout.field_bits * (index % layout.block_size)
        old = (words[tape] >> offset) & ((1 << layout.field_bits) - 1)
        require(memory[register(tape) + 13] == old, "simultaneous observation")
        require(0 <= new[tape] < 1 << layout.field_bits, "new field overflow")
        memory[register(tape) + 2] = new[tape]
    commits = [op for tape in range(layout.tapes) for op in commit_code(layout, tape)]
    require(execute(commits, memory, layout.width) == 4 * layout.tapes, "commit bill")
    expected = {a: v for a, v in initial.items() if a >= layout.base}
    for tape, head in enumerate(heads):
        index = head if head >= 0 else -head - 1
        block, field = divmod(index, layout.block_size)
        address = layout.base + layout.stride * block + 2 * tape + (head < 0)
        offset = layout.field_bits * field
        mask = ((1 << layout.field_bits) - 1) << offset
        expected[address] = (words[tape] & ~mask) | (new[tape] << offset)
    require({a: v for a, v in memory.items() if a >= layout.base} == expected,
            "write, spectator, padding or bank preservation")
    return 17 * layout.tapes


def program_cases() -> dict:
    rng = Random(20261022)
    cases, instructions = 0, 0
    for tapes in (1, 2, 3, 8, 16, 64):
        for width in (16, 32, 64, 128, 256):
            for field_log in range(5):
                for block_log in range(9):
                    if (1 << (field_log + block_log)) > width:
                        continue
                    layout = Layout(tapes, field_log, block_log, width)
                    for trial in range(8):
                        heads = [rng.randrange(-3 * layout.block_size,
                                               3 * layout.block_size) for _ in range(tapes)]
                        if trial < 4:
                            heads = [(0, -1, layout.block_size - 1,
                                      -layout.block_size - 1)[trial]] * tapes
                        words = [rng.getrandbits(width) for _ in range(tapes)]
                        new = [rng.getrandbits(layout.field_bits) for _ in range(tapes)]
                        instructions += transition(layout, heads, words, new)
                        cases += 1
    return {"transition_cases": cases, "executed_access_instructions": instructions}


def dispatcher_fixture() -> int:
    layout = Layout(2, 1, 2, 16)
    memory = prepare(layout, [0, 0], [0xABCD, 0x5678])
    reads = read_code(layout, 0) + read_code(layout, 1)
    r0, r1 = register(0), register(1)
    # Register 2 is initially zero. These are two actual successful instructions.
    dispatch = [("xor", r0 + 2, r1 + 13, 2), ("xor", r1 + 2, r0 + 13, 2)]
    code = reads + dispatch + commit_code(layout, 0) + commit_code(layout, 1)
    count = execute(code, memory, layout.width)
    require(count == 36, "dispatcher-inclusive instruction bill")
    require(memory[layout.base] == 0xABCC and memory[layout.base + 2] == 0x5679,
            "literal simultaneous swap dispatcher")
    return count


def controls() -> dict:
    invalid_layouts = [(True, 0, 0, 16), (0, 0, 0, 16), (65, 0, 0, 32),
                       (1, 5, 0, 64), (1, 0, 9, 256), (1, 0, 0, 9),
                       (1, 4, 1, 16), (64, 0, 0, 10)]
    rejected = 0
    for parameters in invalid_layouts:
        try:
            Layout(*parameters)
        except ValueError:
            rejected += 1
    invalid_words = [(Layout(1, 0, 0, 10), [1000], [0]),
                     (Layout(1, 0, 0, 10), [0], [1024]),
                     (Layout(1, 0, 6, 64), [1 << 64], [0])]
    for parameters in invalid_words:
        try:
            prepare(*parameters)
        except ValueError:
            rejected += 1
    try:
        execute([("bad", 0, 0, 0)], {}, 16)
    except ValueError:
        rejected += 1
    require(rejected == 12, "invalid boundary accepted")
    layout = Layout(1, 1, 1, 16)
    mutations = 0
    for mutation in ("omit_delta", "shift_wrong", "clobber_cache", "stale_word"):
        memory = prepare(layout, [1], [0xFFFF])
        execute(read_code(layout, 0), memory, 16)
        r = register(0)
        memory[r + 2] = 0
        code = commit_code(layout, 0)
        if mutation == "omit_delta":
            code = code[1:]
        elif mutation == "shift_wrong":
            code[1] = ("shiftl", r + 14, r + 14, 0)
        elif mutation == "clobber_cache":
            memory[r + 13] = 0
        else:
            memory[layout.base] ^= 1
        before = memory[layout.base]
        execute(code, memory, 16)
        expected = before & ~(3 << 2)
        require(memory[layout.base] != expected, "mutation escaped observation")
        mutations += 1
    return {"invalid_inputs_rejected": rejected, "semantic_controls_rejected": mutations}


def receipt() -> dict:
    package = Path(__file__).resolve().parent
    hashes = {name: hashlib.sha256((package / name).read_bytes()).hexdigest()
              for name in ("fusion.py", "verify.py", "README.md", "TASK.json",
                           "SOURCES.json", "VERIFY.json")}
    return {"status": "PASS_PACKED_TAPE_FUSION", "source_sha256": hashes,
            "scalar_identity_cases": scalar_identity(), **program_cases(),
            "dispatcher_fixture_instructions": dispatcher_fixture(), **controls(),
            "read_instructions_per_tape": 13, "commit_instructions_per_tape": 4,
            "access_instructions_per_tape": 17,
            "predecessor_separate_access_instructions_per_tape": 30,
            "claim_type": "scoped construction proof with finite corroboration"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="regenerate source-bound receipt")
    args = parser.parse_args()
    result = receipt()
    target = Path(__file__).resolve().with_name("RESULT.json")
    if args.write:
        target.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    require(json.loads(target.read_text()) == result, "receipt differs from computed result")
    print(json.dumps(result, sort_keys=True))


if __name__ == "__main__":
    main()
