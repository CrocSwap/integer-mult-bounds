"""Exact source-word invoice from rational frame ranks and telescoping.

Prepared for Clear1nsight with substantial OpenAI assistance. Apache-2.0.
No normaliser, exporter, or predecessor/native checker is imported. Actual
frame chronology and COPY legality remain the separate native checker's job.
"""

from collections import Counter
from fractions import Fraction


def require(condition, message):
    if not condition:
        raise ValueError(message)


def rational_rank(rows, width):
    """Forward elimination over Q, independent of exported frame dimensions."""
    matrix = [[Fraction(value) for value in row] for row in rows]
    require(all(len(row) == width for row in matrix), "frame row width")
    pivot_count = 0
    for column in range(width):
        pivot = next((index for index in range(pivot_count, len(matrix))
                      if matrix[index][column]), None)
        if pivot is None:
            continue
        matrix[pivot_count], matrix[pivot] = matrix[pivot], matrix[pivot_count]
        divisor = matrix[pivot_count][column]
        matrix[pivot_count] = [value / divisor for value in matrix[pivot_count]]
        for index in range(pivot_count + 1, len(matrix)):
            multiplier = matrix[index][column]
            if multiplier:
                matrix[index] = [value - multiplier * basis for value, basis
                                 in zip(matrix[index], matrix[pivot_count])]
        pivot_count += 1
    return pivot_count


def audit_word(word):
    """Derive the local rank/addition bill for this fixed normalised boundary.

    MOVE charges telescope from initial to final frame dimensions. Retained
    slots each add their scatter-entrance rank, including aliases and unused
    slots. The independent occurrence counts supply normal-form ADD terms.
    This computation does not itself certify that all MOVEs are legal.
    """
    require((word["h"], word["v"], word["R"]) == (8, 111, 439),
            "fixed selected word dimensions")
    labels = word["lines"]
    ranks = [rational_rank([labels[index] for index in frame], word["h"])
             for frame in word["frames"]]
    initial, final = word["start"], word["final"]
    require(len(initial) == len(final) == 661, "complete frame endpoint inventory")
    initial_sum = sum(ranks[frame] for frame in initial)
    final_sum = sum(ranks[frame] for frame in final)
    current = list(initial)
    for section in ("D", "A"):
        for frame, destination, sources in word[section]:
            for register in [destination, *sources]:
                current[register] = frame
    slots = [{"slot": slot, "helper": helper, "frame": current[helper],
              "rank": ranks[current[helper]]}
             for slot, helper in enumerate(word["ret"])]
    distinct_frames = sorted({entry["frame"] for entry in slots})
    copy_mass = sum(entry["rank"] for entry in slots)
    move_mass = final_sum - initial_sum
    terms = sum(sum(count % 2 for count in Counter(row).values())
                for row in word["scatter"])
    other_adds = sum(len(gate[2]) for section in ("D", "A", "B", "C")
                     for gate in word[section])
    return {
        "status": "COMPUTED_EXACT_WORD_INVOICE",
        "rank_method": "rational forward elimination on integer label rows",
        "frame_count": len(ranks),
        "initial_frame_rank_sum": initial_sum,
        "final_frame_rank_sum": final_sum,
        "move_rank_mass": move_mass,
        "retained_slots": slots,
        "distinct_retained_frames": [{"frame": frame, "rank": ranks[frame]}
                                     for frame in distinct_frames],
        "copies": len(slots),
        "copy_rank_mass": copy_mass,
        "raw_rank_mass": move_mass + copy_mass,
        "input_scatter_occurrences": sum(map(len, word["scatter"])),
        "normalised_scatter_adds": terms,
        "non_scatter_adds": other_adds,
        "total_scalar_adds": other_adds + terms,
        "scope": "Fixed local word invoice; actual geometry and COPY legality checked separately.",
    }
