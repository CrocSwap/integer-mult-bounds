"""Separate exact chronological and free-word replay, Apache-2.0.

Prepared by 1337isnot1337 with substantial OpenAI Codex assistance. This uses
the retained event meanings but imports none of the retained row primitives.
"""
from collections import Counter
from fractions import Fraction

from frame_dag import image, inverse, need, space, dimension


def replay(canonical, program, backward=False):
    frames = list(map(space, canonical["frames"]))
    maps = {}
    for warp in canonical["warps"]:
        columns = tuple(warp["G_columns"])
        maps[warp["op"]], maps[-warp["op"]] = columns, inverse(columns)
    rows = [{(role, ()): Fraction(1)} for role in range(632)] + [{}]
    current = canonical["start"][:] + [None]
    paid = Counter()

    def register(role):
        need(role[0] in ("L", "C"), "Known register class")
        if role[0] == "C":
            need(role[1] == 0, "Only the retained owned C0")
            return 632
        need(0 <= role[1] < 632, "Live register range")
        return role[1]

    for event in program:
        kind = event[0]
        if kind == "weighted_swap":
            _, left, right, a, b, before, after = event
            need(left != right and [current[left], current[right]] == before, "Swap incoming frames")
            a, b = Fraction(a), Fraction(b)
            need(a and b, "Invertible weighted swap")
            rows[left], rows[right] = ({key: a * value for key, value in rows[right].items()},
                                       {key: b * value for key, value in rows[left].items()})
            current[left], current[right] = current[right], current[left]
            need([current[left], current[right]] == after, "Swap carries frames")
        elif kind == "warp":
            _, role, operator, old, new = event
            target = register(role)
            need(operator in maps and current[target] == old, "Warp incoming frame")
            need(image(maps[operator], frames[old]) == frames[new], "Warp map/frame mismatch")
            symbol = (1 if operator > 0 else -1) * (abs(operator) + (1000000 if backward else 0))
            moved = {}
            for (variable, word), value in rows[target].items():
                word = word[1:] if word and word[0] == -symbol else (symbol,) + word
                key = variable, word
                moved[key] = moved.get(key, Fraction(0)) + value
            rows[target] = {key: value for key, value in moved.items() if value}
            current[target] = new
        elif kind in ("climb", "center"):
            if kind == "climb":
                _, _, target, old, new, rank = event
                need(frames[old] & frames[new] == frames[old] and old != new,
                     "Strict nested climb")
            else:
                _, target, old, new, rank = event
                need(target == 0, "Owned C0 center")
                target = 632
                need(frames[old] & frames[new] in (frames[old], frames[new]), "Nested center")
            need(current[target] == old, "Paid incoming frame")
            need(rank == abs(dimension(frames[new]) - dimension(frames[old])) and rank > 0,
                 "Paid rank mismatch")
            current[target] = new
            paid[rank] += 1
        elif kind == "scalar":
            gate, frame = event[1:]
            target = register(gate[1])
            if gate[0] == "clear":
                need(target == 632, "Owned clear only")
                rows[target], current[target] = {}, frame
                continue
            need(current[target] == frame, "Scalar target frame")
            if gate[0] in ("add", "copy"):
                source = register(gate[2])
                need(current[source] == frame, "Scalar source frame")
                if gate[0] == "copy":
                    need(target == 632, "Owned copy only")
                    rows[target] = dict(rows[source])
                else:
                    need(target != source, "Distinct ADD operands")
                    coefficient = Fraction(gate[3], gate[4])
                    for key, value in tuple(rows[source].items()):
                        value = rows[target].get(key, Fraction(0)) + coefficient * value
                        if value:
                            rows[target][key] = value
                        else:
                            rows[target].pop(key, None)
            else:
                need(gate[0] == "scale", "Known scalar opcode")
                coefficient = Fraction(gate[2], gate[3])
                need(coefficient, "Invertible SCALE")
                rows[target] = {key: coefficient * value for key, value in rows[target].items()}
        else:
            need(kind in ("phase", "adapter", "residual_adapter"), "Known inert marker")
    need(current[:632] == canonical["final"] and not rows[632], "Terminal frames and owned clear")
    for role in range(632):
        expected = {(role, ()): Fraction(1)}
        if backward and role < 112:
            expected[role + 112, ()] = Fraction(-1)
        if not backward and 112 <= role < 224:
            expected[role - 112, ()] = Fraction(1)
        need(rows[role] == expected, "Normalized independent-input endpoint")
    return paid
