"""Behavioral corruption/relocation checks, confined to temporary copies.

Prepared for commdata2338 with substantial OpenAI Codex assistance.
Apache-2.0.
"""

from pathlib import Path
import json
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    # Honour the caller's ordinary temporary-directory policy.
    with tempfile.TemporaryDirectory(prefix="mixed-descriptor-") as temp:
        root = Path(temp)/"relocated"
        package = root/"research"/HERE.name
        shutil.copytree(HERE,package,ignore=shutil.ignore_patterns("__pycache__"))
        pins = json.loads((package/"SOURCES.json").read_text())
        for pin in pins["files"]:
            if pin["usage"] == "input":
                target = root/pin["path"]
                target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(ROOT/pin["path"],target)

        def run(ok, expected, *args):
            result = subprocess.run([sys.executable,"-I","-O","-B",str(package/"verify.py"),*args],
                                    cwd=root,capture_output=True,text=True,timeout=180)
            output = result.stdout+result.stderr
            require((result.returncode == 0) == ok and expected in output,
                    "unexpected subprocess behavior: " + output[-3000:])

        # Relocation must succeed with no predecessor checkout or executable.
        run(True,"PASS_SELECTED_BIT_MIXED_DESCRIPTOR")
        receipt = package/"RESULT.json"
        original = receipt.read_bytes()
        value = json.loads(original)
        value["fallback_child_allowance"] = float(value["fallback_child_allowance"])
        receipt.write_text(json.dumps(value))
        run(False,"committed result mismatch")
        receipt.write_bytes(original)
        receipt.unlink()
        run(False,"FileNotFoundError")
        receipt.write_bytes(original)
        receipt.write_bytes(b'{"scope":"duplicate",'+original[1:])
        run(False,"duplicate receipt key")
        receipt.write_bytes(original)
        source = root/"research/e8-bit-p111-tuned/tune/EXPECTED.json"
        source_bytes = source.read_bytes()
        source.write_bytes(source_bytes+b" ")
        run(False,"source pin:")
        source.write_bytes(source_bytes)
        output = root/"already-exists.json"
        output.write_text("retain this exact file\n")
        run(False,"FileExistsError","--write-result",str(output))
        require(output.read_text()=="retain this exact file\n","candidate output overwritten")
    print("PASS_MIXED_DESCRIPTOR_BEHAVIOR groups=6 optimized=True")


if __name__ == "__main__":
    main()
