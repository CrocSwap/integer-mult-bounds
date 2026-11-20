"""Exercise the zero-saving ordinary service on complete fixed-radix streams."""

from itertools import product


def swap_digit(values, q, prefix, gap, suffix):
    buckets = [[[] for _ in range(q)] for _ in range(q)]
    source = iter(values)
    for _ in range(prefix):
        for x in range(q):
            for _ in range(gap):
                for y in range(q):
                    buckets[x][y].extend(next(source) for _ in range(suffix))
    end = object()
    if next(source, end) is not end:
        raise ValueError("unread source payload")
    streams = [[iter(bucket) for bucket in row] for row in buckets]
    result = []
    for _ in range(prefix):
        for y in range(q):
            for _ in range(gap):
                for x in range(q):
                    result.extend(next(streams[x][y]) for _ in range(suffix))
    if any(next(stream, end) is not end for row in streams for stream in row):
        raise ValueError("unread pair bucket")
    return result


def main():
    cases = cells = 0
    for q, width, pre, gap, tail in product((2, 3, 5), (1, 2, 3), (1, 2), (1, 3), (1, 2)):
        chunk = q**width
        source = list(range(pre * chunk * gap * chunk * tail))
        value = source
        shapes = [(pre*q**j, gap*q**(width-1), tail*q**(width-1-j)) for j in range(width)]
        for shape in shapes:
            value = swap_digit(value, q, *shape)
        expected = [((((p*chunk+x)*gap+g)*chunk+y)*tail+s)
                    for p, y, g, x, s in product(range(pre), range(chunk), range(gap),
                                                  range(chunk), range(tail))]
        if value != expected:
            raise ValueError("ordinary endpoint")
        for shape in reversed(shapes):
            value = swap_digit(value, q, *shape)
        if value != source:
            raise ValueError("complete restoration")
        cases += 1
        cells += len(source)
    print(f"PASS_ELEMENTARY_ORDINARY cases={cases} independent_cells={cells}")


if __name__ == "__main__":
    main()
