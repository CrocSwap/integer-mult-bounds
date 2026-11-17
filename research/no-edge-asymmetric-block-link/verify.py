"""Verify one complete nonsymmetric block-link pool over F2 at width eight."""

WIDTH = 8
CARRIER_SIZE = 1 << WIDTH
Projector = tuple[int, int]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SystemExit(message)


def pairing(image: int, covector: int) -> int:
    return (image & covector).bit_count() % 2


def off_diagonal(image: int, covector: int) -> int:
    pattern = 0
    for row in range(WIDTH):
        if image & (1 << row):
            pattern |= (covector & ~(1 << row)) << (WIDTH * row)
    return pattern


def span(vectors: tuple[int, ...]) -> set[int]:
    sums = {0}
    for vector in vectors:
        sums |= {value ^ vector for value in sums}
    return sums


def complete_pool(patterns: set[int]) -> tuple[int, set[Projector]]:
    count = 0
    pool = set()
    for image in range(1, CARRIER_SIZE):
        for covector in range(1, CARRIER_SIZE):
            if pairing(image, covector) == 1:
                count += 1
                if off_diagonal(image, covector) in patterns:
                    pool.add((image, covector))
    return count, pool


def orbit_span(vector: int, pool: tuple[Projector, ...]) -> set[int]:
    # A nonzero word value after the first application is one of the
    # pool images. At most len(pool) rounds discover all reachable images.
    orbit = {vector}
    for _ in pool:
        reached = {
            image
            for image, covector in pool
            if any(pairing(value, covector) for value in orbit)
        }
        if reached <= orbit:
            break
        orbit.update(reached)
    return span(tuple(orbit))


def main() -> None:
    left = ((0b110, 0b101), (0b101, 0b110), (0b111, 0b111))
    right = tuple((image << 3, covector << 3) for image, covector in left)
    link = (0b01100100, 0b11100100)
    generators = left + right + (link,)

    require(link[0] != link[1], "link must be nonsymmetric")
    require(all(pairing(*factors) == 1 for factors in generators),
            "each displayed projector must be idempotent")
    patterns = span(tuple(off_diagonal(*factors) for factors in generators)) - {0}
    require(len(patterns) == 31, "pattern dimension differs from five")
    require(all(value.bit_count() > 1 for value in patterns),
            "pattern space contains a matrix unit")
    enumerated, actual = complete_pool(patterns)
    require(enumerated == 32_640, "wrong rank-one idempotent census size")
    require(actual == set(generators), "complete pool differs from the displayed seven")

    joint_image = span(tuple(image for image, _ in generators))
    require(joint_image == set(range(128)), "joint image differs from span(e0,...,e6)")
    for vector in sorted(joint_image - {0}):
        require(orbit_span(vector, generators) == joint_image,
                f"orbit of vector {vector} spans a proper subspace")

    block_line = {0, left[0][0]}
    require(orbit_span(left[0][0], left + right) == block_line,
            "deleting the link should leave a proper invariant line")
    require(pairing(link[0], link[1] ^ (1 << 6)) == 0,
            "deleting the matched fresh covector bit should break idempotence")
    print(
        "PASS_NO_EDGE_ASYMMETRIC_BLOCK_LINK width=8 patterns=31 "
        f"idempotents={enumerated} pool={len(actual)} "
        f"image_dimension=7 spanning_orbits={len(joint_image) - 1} controls=2"
    )


if __name__ == "__main__":
    main()
