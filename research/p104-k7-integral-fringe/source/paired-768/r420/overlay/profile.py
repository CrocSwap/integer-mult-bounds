"""Change only the terminal booking in the frozen Round 415 profile."""
from hashlib import sha256
import json
from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory

OLD_RATE = "0.003900857269150"
NEW_RATE = "0.003900857312000"
BEFORE = b'TERMINAL = Profile((31808, 502922, 7951907, 125730703, 134217727), 208653, Q(".003900857269150"), Q(1, 256))'
AFTER = BEFORE.replace(b".003900857269150", b".003900857312000")
PREIMAGE = "1c6978b8c7d136ef87191512d9ab9eb3dda8a818844244b96cb165d46d97b1df"
OLD_PATCH = "2eb7d8a20b5202774aa787a1313f645e20428419ba85fb8490fe4d76df7f3059"
OLD_IMAGE = "37460b2be0a93ecfe110be25de5a4ea787c2d09973f926f680ea148453dc89e2"
OLD_MANIFEST = "c6a31ad88b5f1b60d337b26a02f9e6328129eb7f1ed1b9088bdd0a9295cb866d"


def digest(value):
    return sha256(value).hexdigest()


def authenticate(path, pin):
    value = path.read_bytes()
    if digest(value) != pin:
        raise ValueError(f"Unexpected frozen bytes: {path.name}")
    return value


def installation_image(preimage, patch):
    with TemporaryDirectory(prefix="typed-period-profile-") as temporary:
        target = Path(temporary) / "installations.py"
        target.write_bytes(preimage)
        run(
            ["git", "apply", "--no-index", "--include=installations.py",
             "--whitespace=nowarn", "-"],
            cwd=temporary, input=patch, check=True, timeout=10,
        )
        return target.read_bytes()


def patch_profile(peer: Path) -> dict:
    """Replay the selected source image and update its two manifest pins."""
    patch_file = peer / "runtime.patch"
    manifest_file = peer / "SOURCES.json"
    patch = authenticate(patch_file, OLD_PATCH)
    manifest = json.loads(authenticate(manifest_file, OLD_MANIFEST))
    preimage = authenticate(peer.parent / "tiered-native-multiplier" / "installations.py", PREIMAGE)
    images = manifest["runtime_images"]["installations.py"]
    if images != {"before": PREIMAGE, "after": OLD_IMAGE} or manifest["local_sources"]["runtime.patch"] != OLD_PATCH:
        raise ValueError("Unexpected frozen profile manifest pins")
    baseline = installation_image(preimage, patch)
    if digest(baseline) != OLD_IMAGE or baseline.splitlines().count(BEFORE) != 1:
        raise ValueError("Unexpected installed selector preimage")
    if patch.splitlines().count(b"+" + BEFORE) != 1 or AFTER in patch:
        raise ValueError("Expected one exact terminal selector patch line")

    changed_patch = patch.replace(b"+" + BEFORE, b"+" + AFTER, 1)
    changed = installation_image(preimage, changed_patch)
    if changed != baseline.replace(BEFORE, AFTER, 1):
        raise ValueError("Unexpected additional installed selector edit")
    compile(changed, "installations.py", "exec")
    images["after"] = digest(changed)
    manifest["local_sources"]["runtime.patch"] = digest(changed_patch)
    encoded = (json.dumps(manifest, indent=2) + "\n").encode()
    patch_file.write_bytes(changed_patch)
    manifest_file.write_bytes(encoded)
    return {
        "scope": "Literal installation selector and dependency pins; installed science unrun",
        "installation_preimage_sha256": PREIMAGE,
        "baseline_installation_sha256": OLD_IMAGE,
        "baseline_runtime_patch_sha256": OLD_PATCH,
        "baseline_sources_sha256": OLD_MANIFEST,
        "baseline_terminal_kappa": OLD_RATE,
        "candidate_installation_sha256": images["after"],
        "candidate_runtime_patch_sha256": digest(changed_patch),
        "candidate_sources_sha256": digest(encoded),
        "candidate_terminal_kappa": NEW_RATE,
    }
