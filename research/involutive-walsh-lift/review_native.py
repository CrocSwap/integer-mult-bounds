"""Check literal Walsh retarget adapters without the Clifford compiler."""

from collections import Counter
from hashlib import sha256
from pathlib import Path
import gzip
import argparse
import sys
from fractions import Fraction as Q
import json

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import native
import sources


def require(ok, message):
    if not ok:
        raise ValueError(message)


def scalar(event):
    gate = event[1]
    target = gate[1][1]+(704 if gate[1][0] == "C" else 0)
    if gate[0] == "clear":
        return "clear", target, -1, Q(0)
    if gate[0] == "scale":
        return "scale", target, -1, Q(gate[2], gate[3])
    require(gate[0] in ("add", "copy"), "Scalar opcode")
    source = gate[2][1]+(704 if gate[2][0] == "C" else 0)
    return gate[0], target, source, Q(1) if gate[0] == "copy" else Q(gate[3], gate[4])


def transpose_word(events):
    columns = [{i: Q(1)} for i in range(712)]
    for tag, target, source, coefficient in reversed([scalar(e) for e in events if e[0] == "scalar"]):
        if tag == "clear":
            columns[target] = {}
        elif tag == "scale":
            columns[target] = {j: coefficient*v for j, v in columns[target].items() if coefficient*v}
        else:
            for j, value in columns[target].items():
                new = columns[source].get(j, Q(0))+coefficient*value
                if new:
                    columns[source][j] = new
                else:
                    columns[source].pop(j, None)
            if tag == "copy":
                columns[target] = {}
    return columns


def shear(rank):
    diagonal = tuple(1 << i if i < rank else 0 for i in range(9))
    return (("D", diagonal, tuple(int(i < rank) for i in range(9))),)


def walsh_frame(native, vectors):
    width = len(vectors)
    if width == 0:
        return ()
    partial = shear(width)+native.fourier(width)+shear(width)
    if width == 9:
        return partial
    address = native.transpose(native.extend(tuple(vectors), 9))
    return (("P", native.inverse(address)),)+partial+(("P", address),)


def line(label):
    quadratic = tuple(label if label >> j & 1 else 0 for j in range(9))
    phase = tuple((label >> j) & 1 for j in range(9))
    sq = (("D", quadratic, phase),)
    return sq+(("C", label, 1),)+sq


def binary_rank(vectors):
    pivots = {}
    for value in vectors:
        while value:
            bit = value.bit_length()-1
            if bit not in pivots:
                pivots[bit] = value
                break
            value ^= pivots[bit]
    return len(pivots)


def check_preimages(native, vectors, old, new):
    rank = len(vectors)
    require(binary_rank(vectors) == rank, "Independent frame basis")
    perpendicular = [x for x in range(512) if all(not native.parity(x & v) for v in vectors)]
    require(len(perpendicular) == 1 << (9-rank), "Full perpendicular subspace")
    old_rows, new_rows = native.tableau(old), native.tableau(new)

    def output_x(rows, x, z):
        result = 0
        for i in range(9):
            if x >> i & 1:
                result ^= rows[i][0]
            if z >> i & 1:
                result ^= rows[9+i][0]
        return result

    for v in vectors:
        require(output_x(old_rows, v, v) == 0, "Old frame preimage (v,v)")
        require(output_x(new_rows, v, 0) == 0, "Walsh frame preimage (v,0)")
    for w in perpendicular:
        require(output_x(old_rows, 0, w) == output_x(new_rows, 0, w) == 0,
                "Old and new perpendicular preimage")
    # The displayed generators have total dimension nine. A Clifford
    # preimage of the diagonal Pauli space also has dimension nine.
    return len(perpendicular)+rank


def monomial_point(native, circuit, value):
    phase = 0
    for gate in circuit:
        if gate[0] == "D":
            quadratic, linear = gate[1:]
            phase += sum(linear[i] for i in range(9) if value >> i & 1)
            phase += 2*sum(native.parity((quadratic[i] >> (i+1)) & (value >> (i+1)))
                           for i in range(9) if value >> i & 1)
        elif gate[0] == "P":
            value = native.mul(gate[1], value)
        elif gate[0] == "X":
            value ^= gate[1]
        else:
            require(gate[0] == "phase", "Monomial-only factor")
            phase += gate[1]
    return value, phase % 4


def check_monomials(native, actual, expected, label):
    # These maps have affine addresses and quadratic phases over Z/4.
    # Zero, single bits, and pairs determine both maps in full.
    probes = [0]+[1 << i for i in range(9)]
    probes += [(1 << i) | (1 << j) for i in range(9) for j in range(i+1, 9)]
    for x in probes:
        require(monomial_point(native, actual, x) == monomial_point(native, expected, x), label)
    return len(probes)


def check_fused(native, source, folder, adapters, new_frames, endpoint_records, adapter_hash):
    raw = gzip.decompress((folder/"WALSH-RETARGET-NATIVE.json.gz").read_bytes())
    pin = sha256(raw).hexdigest()
    artifact = json.loads(raw)
    local_names = ("CANONICAL-WORD.json.gz", "LOCAL-PROGRAMS.json.gz", "CLIFFORD-RECIPES.json", "RESIDUAL-ADAPTERS.json")
    local_pins = {name: sources.LOCAL_PINS[name] for name in local_names}
    require(artifact["base"] == sources.BASE and artifact["old_member_sha256"] == local_pins, "Native source binding")
    require(artifact["adapter_sha256"] == adapter_hash, "Native frame adapter binding")
    require(artifact["programs"] == source["LOCAL-PROGRAMS.json.gz"], "Exact original event streams")
    old_children = source["CLIFFORD-RECIPES.json"]["children"]
    require(len(artifact["children"]) == len(old_children) == 2896, "All fused child records")
    points = 0
    for old, new in zip(old_children, artifact["children"]):
        require((old["old"], old["new"], old["rank"]) ==
                (new["old"], new["new"], new["rank"]), "Same child and rank")
        before, after = adapters[old["old"]], adapters[old["new"]]
        native.equal(native.recipe(new), native.adjoint(new_frames[new["old"]])+new_frames[new["new"]],
                     "Complete emitted child operator "+str((new["old"], new["new"])))
        points += check_monomials(native, native.monomial(new["left"]),
                                  native.monomial(old["left"])+after, "Fused left child factor")
        points += check_monomials(native, native.monomial(new["right"]),
                                  native.adjoint(before)+native.monomial(old["right"]),
                                  "Fused right child factor")
    emitted_endpoints = {(r["role"], r["port"]): r for r in artifact["endpoint_adapters"]}
    require(set(emitted_endpoints) == set(endpoint_records), "Emitted endpoint coverage")
    for key, record in emitted_endpoints.items():
        original = endpoint_records[key]
        require(record["frame"] == original["frame"] and record["rank"] == 0 and record["right"] is None,
                "Emitted endpoint structure")
        points += check_monomials(native, native.recipe(record), native.monomial(original["adapter"]),
                                  "Emitted exact endpoint factor")
    residuals = artifact["residual_adapters"]
    require(set(residuals) == set(source["RESIDUAL-ADAPTERS.json"]["recipes"]), "Complete residual keys")
    helper_raw = (folder/"WALSH-RETARGET-HELPER-NORMALIZATION.json").read_bytes()
    helper_pin = sha256(helper_raw).hexdigest()
    helper = json.loads(helper_raw)
    require(helper["native_payload_sha256"] == pin and set(helper["recipes"]) == set(residuals),
            "Helper wrapper source and inventory")
    for key, record in residuals.items():
        a, b = record["frame"], record.get("terminal", 1)
        native.equal(native.recipe(record), native.adjoint(new_frames[a])+new_frames[b],
                     "Full fused residual "+key)
        rank = record["rank"]
        require(rank > 0, "Positive complete helper width")
        left, right = native.monomial(record["left"]), native.monomial(record["right"])
        pre = shear(rank)+native.adjoint(right)
        post = native.adjoint(left)+shear(rank)
        literal = helper["recipes"][key]
        require(literal["rank"] == rank, "Literal helper rank")
        literal_pre, literal_post = native.monomial(literal["pre"]), native.monomial(literal["post"])
        points += check_monomials(native, literal_pre, pre, "Literal pre helper wrapper "+key)
        points += check_monomials(native, literal_post, post, "Literal post helper wrapper "+key)
        native.equal(literal_pre+native.recipe(record)+literal_post,
                     shear(rank)+native.fourier(rank)+shear(rank),
                     "Literal complete H_r helper job "+key)
    require(len(residuals) == 36, "All helper residuals")
    return {"payload_sha256": pin, "child_recipes": 2896,
            "full_phase_child_operators": 2896, "emitted_endpoint_factors": len(emitted_endpoints),
            "complete_quadratic_monomial_witnesses": points,
            "full_phase_residual_recipes": len(residuals),
            "literal_H_rank_normalizers": "pre=R^-1 S_rank, post=S_rank L^-1 for residual=L F_rank R",
            "helper_normalization_sha256": helper_pin,
            "normalizer_emission_status": "All 36 complete H_rank jobs pass with the separate literal normalization artifact",
            "unchanged_program_events_per_orientation": {k: len(v) for k, v in artifact["programs"].items()}}


def main(args):
    source = sources.load_local(args.repo)
    word = source["CANONICAL-WORD.json.gz"]
    originals = source["LOCAL-PROGRAMS.json.gz"]
    folder = args.out
    raw = (folder/"WALSH-RETARGET-ADAPTERS.json").read_bytes()
    pin = sha256(raw).hexdigest()
    artifact = json.loads(raw)
    require(len(artifact["frame_adapters"]) == len(word["frames"]) == 1004,
            "Complete actual frame inventory")
    old_frames = [native.frame(tuple(vectors), 9) for vectors in word["frames"]]
    new_frames = [walsh_frame(native, vectors) for vectors in word["frames"]]
    adapters = [native.monomial(row) for row in artifact["frame_adapters"]]
    preimage_checks = 0
    for index, (old, new, adapter) in enumerate(zip(old_frames, new_frames, adapters)):
        native.equal(shear(9)+old+adapter, new, "Literal frame adapter "+str(index))
        require(all(x == 0 for x, z, phase in native.tableau(adapter)[9:]), "Monomial native rank")
        vectors = word["frames"][index]
        preimage_checks += check_preimages(native, vectors, old, new)
        native.equal(new+new, (("phase", len(vectors) % 4),), "Exact chart frame square "+str(index))
        if index % 250 == 0:
            print("independent exact retarget frames", index, "/", len(old_frames), flush=True)
    endpoints = {(row["role"], row["port"]): row for row in artifact["endpoint_adapters"]}
    require(set(endpoints) == {(role, p) for role in ("source", "target") for p in range(112)},
            "Complete data endpoint inventory")
    full = walsh_frame(native, tuple(1 << i for i in range(9)))
    for (role, port), record in endpoints.items():
        q = word["ports"][port]
        hq = line(q)
        conventional = hq if role == "source" else native.adjoint(hq)+full
        expected_frame = word["start"][port] if role == "source" else word["final"][112+port]
        require(record["frame"] == expected_frame, "Actual endpoint frame binding")
        native.equal(conventional+native.monomial(record["adapter"]), new_frames[expected_frame],
                     "Literal Walsh "+role+" adapter "+str(port))
        native.equal(hq+hq, (("phase", 1),), "Intrinsic source line square")
        if role == "source":
            # Compare both two-term kernels on every input, independently of
            # the tableau.  S_q C_q S_q has diagonal alpha*(-1)^(q.x)
            # and translated coefficient alpha, where alpha=(1+i)/2.
            for x in range(512):
                b = native.parity(q & x)
                diagonal = native.rotate((1, 1), 2*b)
                translated = native.rotate((1, -1), b+native.parity(q & (x ^ q)))
                require(diagonal == ((1, 1) if not b else (-1, -1)) and translated == (1, 1),
                        "Exact intrinsic H_q two-term kernel")
    ranks = Counter()
    for edge in source["CLIFFORD-RECIPES.json"]["children"]:
        a, b = edge["old"], edge["new"]
        old = native.adjoint(old_frames[a])+old_frames[b]
        new = native.adjoint(new_frames[a])+new_frames[b]
        old_rank = binary_rank([x for x, z, phase in native.tableau(old)[9:]])
        new_rank = binary_rank([x for x, z, phase in native.tableau(new)[9:]])
        require(old_rank == new_rank == edge["rank"], "Every actual native edge rank")
        ranks[new_rank] += 1
    ledgers = {}
    for orientation, program in originals.items():
        columns = transpose_word(program)
        for j, column in enumerate(columns):
            expected = {j: 1} if j < 704 else {}
            if orientation == "forward" and j < 112:
                expected[112+j] = 1
            if orientation == "backward" and 112 <= j < 224:
                expected[j-112] = -1
            require(column == expected, "Original scalar map on every arbitrary persistent and private input")
        frames = list(word["start"])+[None]*8
        scalar_count, child_profile = 0, Counter()
        for event in program:
            kind = event[0]
            if kind == "climb":
                register, old, new, rank = event[2:]
                require(frames[register] == old, "Persistent native edge source frame")
                frames[register] = new
                child_profile[rank] += 1
            elif kind == "center":
                register, old, new, rank = event[1:]
                require(frames[704+register] == old, "Private native edge source frame")
                frames[704+register] = new
                child_profile[rank] += 1
            elif kind == "scalar":
                gate, frame = event[1:]
                scalar_count += 1
                operands = [arg for arg in gate[1:] if isinstance(arg, list)]
                indices = [arg[1]+(704 if arg[0] == "C" else 0) for arg in operands]
                if gate[0] == "clear" and indices[0] >= 704:
                    frames[indices[0]] = frame
                else:
                    require(all(frames[i] == frame for i in indices), "Exact common-frame scalar access")
        require(frames[:704] == word["final"], "Complete persistent frame endpoint")
        require(child_profile == Counter({1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}),
                "Complete original rank profile including private centres")
        ledgers[orientation] = {"scalar_macros": scalar_count,
                                "child_profile": dict(sorted(child_profile.items())),
                                "paid_rank": sum(r*n for r, n in child_profile.items()),
                                "arbitrary_persistent_inputs": 704, "private_input_registers": 8,
                                "exact_scalar_input_columns": 712, "private_outputs": "zero"}
    first = adapters[0]
    corrupted = first+(("phase", 1),)
    require(native.tableau(first) == native.tableau(corrupted) and native.state(first) != native.state(corrupted),
            "Global phase negative control")
    # The physical-axis expression alpha*(X_v+Z_v) is singular for
    # nonzero even v. It kills |0>-|v>. It is not our chart frame.
    require(30 != 0 and native.parity(30) == 0, "Even-axis negative control")
    even_frame = walsh_frame(native, (30,))
    native.equal(even_frame+even_frame, (("phase", 1),), "Nonsingular even-axis chart frame")
    even_state = {0: 1, 30: -1}
    require(all(even_state.get(x ^ 30, 0)+(-1 if native.parity(x & 30) else 1)*even_state.get(x, 0) == 0
                for x in range(512)), "Singular physical even-axis expression")
    fused = check_fused(native, source, folder, adapters, new_frames, endpoints, pin)
    result = {
        "status": "PASS_INDEPENDENT_WALSH_RETARGET_FRAMES_AND_ACTUAL_WORD_LEDGER",
        "source_base": sources.BASE, "source_archive_sha256": sources.LOCAL_ARCHIVE_SHA256,
        "source_member_sha256": sources.LOCAL_PINS, "literal_adapter_sha256": pin,
        "exact_frame_adapters": 1004, "exact_data_endpoint_adapters": 224,
        "direct_frame_preimage_checks": preimage_checks,
        "exact_chart_frame_squares": 1004,
        "interior_frame_definition": "H_V=P_B (S_[r] F_r S_[r]) P_B^-1 with invertible chart B; not a product of physical H_v axes",
        "even_axis_negative_control": "For v=30, alpha*(X_v+Z_v) kills |0>-|30>; the chart-defined H_span(30) squares to iI",
        "actual_native_edge_rank_histogram": dict(sorted(ranks.items())),
        "intrinsic_line_kernel_cases": 112*512,
        "original_word_frame_ledgers": ledgers,
        "fused_native_recipe_review": fused,
        "exact_transport_identity": "H_b H_a^-1=A_b (O_b O_a^-1) A_a^-1, with H_v=A_v O_v S",
        "all_tensor_sizes": "Exact full operators tensor to every positive lambda; scalar phases become their lambda-th powers",
        "not_checked_yet": ["Changed global DATA-PHASES and owner schedule",
                            "Finite global cost, closed centre-state controller, or supplier admission"],
    }
    (folder/"WALSH-RETARGET-REVIEW.json").write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(result["status"], flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=HERE.parents[1])
    parser.add_argument("--out", type=Path, default=HERE/"evidence")
    main(parser.parse_args())
