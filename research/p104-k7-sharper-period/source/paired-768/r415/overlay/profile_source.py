"""Bind the fixed-height tariff candidate to the literal signed profile."""

from hashlib import sha256
import json
from pathlib import Path
from subprocess import run
from tempfile import TemporaryDirectory


BEFORE = b'TERMINAL = Profile((31808, 502922, 7951907, 125730703, 134217727), 208653, Q(".003900857267786"), Q(1, 256))'
AFTER = BEFORE.replace(b".003900857267786", b".003900857269150")
PREIMAGE = "1c6978b8c7d136ef87191512d9ab9eb3dda8a818844244b96cb165d46d97b1df"
OLD_PATCH = "73947f929c432137295b586f6b9b56106b5076942817ae6712541e9e726c75c0"
OLD_IMAGE = "5b31cca69a8f10c78152ae030ae7c7ab156d22feec83347b887aa3fe78098ee7"


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate source manifest key: {key}")
        result[key] = value
    return result


def installation_image(preimage: bytes, patch: bytes) -> bytes:
    """Apply just the one path selected by the existing weighted bootstrap."""
    with TemporaryDirectory(prefix="ordinary-profile-source-") as temporary:
        target = Path(temporary) / "installations.py"
        target.write_bytes(preimage)
        run(
            ["git", "apply", "--no-index", "--include=installations.py",
             "--whitespace=nowarn", "-"],
            cwd=temporary,
            input=patch,
            check=True,
        )
        return target.read_bytes()


def patch_profile(peer: Path) -> dict:
    """Check both exact source images, then change the profile patch and pins."""
    manifest_file = peer / "SOURCES.json"
    manifest = json.loads(manifest_file.read_bytes(), object_pairs_hook=unique_object)
    patch_file = peer / "runtime.patch"
    patch = patch_file.read_bytes()
    patch_digest = digest(patch)
    images = manifest["runtime_images"]["installations.py"]
    if (images != {"before": PREIMAGE, "after": OLD_IMAGE}
            or patch_digest != OLD_PATCH
            or manifest["local_sources"]["runtime.patch"] != OLD_PATCH):
        raise ValueError("The prepared #8094 runtime patch or installation pins differ")

    preimage_path = peer.parent / "tiered-native-multiplier" / "installations.py"
    preimage = preimage_path.read_bytes()
    if digest(preimage) != PREIMAGE:
        raise ValueError("The literal tiered installation preimage differs")
    installed = installation_image(preimage, patch)
    if digest(installed) != OLD_IMAGE or installed.count(BEFORE) != 1:
        raise ValueError("The replayed #8094 installation image differs")

    if patch.splitlines().count(b"+" + BEFORE) != 1 or AFTER in patch:
        raise ValueError("Expected exactly one authenticated terminal profile patch line")
    candidate_patch = patch.replace(b"+" + BEFORE, b"+" + AFTER, 1)
    candidate = installation_image(preimage, candidate_patch)
    if candidate != installed.replace(BEFORE, AFTER, 1):
        raise ValueError("The candidate changed another installed profile byte")
    compile(candidate, "installations.py", "exec")

    candidate_hash = digest(candidate)
    new_patch_hash = digest(candidate_patch)
    receipt = {
        "installation_preimage_sha256": PREIMAGE,
        "baseline_installation_sha256": OLD_IMAGE,
        "candidate_installation_sha256": candidate_hash,
        "baseline_runtime_patch_sha256": patch_digest,
        "candidate_runtime_patch_sha256": new_patch_hash,
        "baseline_terminal_kappa": "0.003900857267786",
        "candidate_terminal_kappa": "0.003900857269150",
        "scope": "Signed installation selector source only. No native or setup replay.",
    }
    images["after"] = candidate_hash
    manifest["local_sources"]["runtime.patch"] = new_patch_hash
    encoded_manifest = json.dumps(manifest, indent=2) + "\n"
    patch_file.write_bytes(candidate_patch)
    manifest_file.write_text(encoded_manifest, encoding="utf-8")
    return receipt
