"""Check the source data for the common-product rank bound."""

from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import argparse
import json
import resource


HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent


def require(condition, label):
    if not condition:
        raise ValueError(label)


def span(rows):
    result = {0}
    for row in rows:
        result |= {value ^ row for value in result}
    return result


def main(args):
    spec = spec_from_file_location("review_source", HERE / "check_line_paths.py")
    helper = module_from_spec(spec)
    spec.loader.exec_module(helper)
    word, programs = helper.load_source()
    centres = word["center_frames"]
    require(centres == list(range(415, 423)), "Centre frame IDs")
    intersection = set.intersection(*(span(word["frames"][frame]) for frame in centres))
    basis = [30, 45, 75, 128, 256]
    require(intersection == span(basis) and len(intersection) == 32, "Common five-dimensional space")
    gram = [sum(((u & v).bit_count() % 2) << j for j, v in enumerate(basis)) for u in basis]
    require(gram == [0, 0, 0, 8, 16] and len(helper.binary_basis(gram)) == 2, "Common Gram rank")
    sharp = []
    for frame_id in centres:
        frame = word["frames"][frame_id]
        require(len(helper.binary_basis(frame)) == 8, "Centre dimension")
        perpendicular = helper.binary_basis(value for value in range(1, 512)
                                             if all(not ((value & u).bit_count() % 2) for u in frame))
        label = [u | (u << 9) for u in frame] + [v << 9 for v in perpendicular]
        twisted_zero = [((1 << j) & (128 | 256)) | (1 << (j + 9)) for j in range(9)]
        pairing = [sum(helper.omega(u, v) << j for j, v in enumerate(twisted_zero)) for u in label]
        changed_rank = len(helper.binary_basis(pairing))
        require(changed_rank == 6, "Sharp common-product rank")
        fixed = {u for u in span(frame) if u == (u & (128 | 256))}
        require(fixed == {0, 128, 256, 384}, "Sharp fixed space")
        sharp.append({"frame": frame_id, "old_rank": 8, "new_rank": changed_rank})
    proof = PACKAGE / "proofs/COMMON-PRODUCT-RANK.md"
    result = {
        "status": "ACCEPTED_COMMON_PRODUCT_CENTRE_RANK_BOUND",
        "source_base": helper.BASE,
        "source_pins": helper.PINS,
        "common_basis": basis,
        "common_gram_rows": gram,
        "common_gram_rank": 2,
        "sharp_gauge": "C_128 C_256",
        "sharp_ranks": sharp,
        "proof_review": [
            "Every product and inverse has symplectic action S_B(x,z)=(x+Bz,z), where B is a sum of aa^T with a in A. Thus im(B) is in A and B kills U-perp.",
            "The intersection of L_U and S_B L_0 is parametrized by w in U-perp and u in Fix(B|U), with z=w+u. The parametrization is injective: a fixed vector in U-perp must be zero.",
            "The intersection dimension is n-dim(U)+dim Fix(B|U). Hence the exact native rank is dim(U)-dim Fix(B|U).",
            "Each fixed vector is in A and in the image of B|A. The map B|A factors through the restricted dot product on A, whose rank is s. The fixed space has dimension at most s, so native rank is at least dim(U)-s.",
            "Applying the same symplectic gauge to both labels reduces two arbitrary endpoint products to their relative product. Native rank depends only on these labels, so phases do not change this rank bound."
        ],
        "scope": "A local native-rank bound for products of translation-line gauges from one fixed common subspace A. This does not price the complete scalar graph, all child moments, or a supplier.",
        "not_claimed": ["A bound for lines outside A", "No complete-cost gain", "All Clifford gauges", "A changed native supplier replay or a kappa bound"],
        "source_sha256": {str(path.relative_to(PACKAGE)): sha256(path.read_bytes()).hexdigest()
                          for path in (proof, HERE / "check_line_paths.py", HERE / "check_common_product_rank.py")},
        "maximum_resident_bytes": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(result["status"])
    print("common_dimension=5 gram_rank=2 centre_ranks=6,6,6,6,6,6,6,6")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, required=True)
    main(parser.parse_args())
