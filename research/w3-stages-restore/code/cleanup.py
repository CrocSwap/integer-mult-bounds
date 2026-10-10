#!/usr/bin/env python3
"""Early restoration of 438 cleanup helpers on the w3 word after the target squares (PR280's rule and checks)."""
import argparse,hashlib,subprocess,sys
from pathlib import Path
if not __debug__:raise SystemExit("Assertions required; refusing -O")
sys.dont_write_bytecode=True
SOURCE_SHA256='7a4f847b197694466cbe92f4b98c9758ceab0715d9440ffe09ba6ceeb4733b65'
OUTPUT_SHA256='a972abfe4fcd7f8b245b06a3af7a2131a1f1635ea6076ecdcce870cce19d2526'
def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--source-dir',type=Path,required=True);ap.add_argument('--export-dir',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);a=ap.parse_args()
    assert digest(a.source_dir/'COHORT249-RECORDS.bin')==SOURCE_SHA256
    code=Path(__file__).resolve().parent;screen=a.output/'cleanup-selection';common=['--source-dir',str(a.source_dir),'--export-dir',str(a.export_dir)]
    subprocess.run([sys.executable,'-B',str(code/'cleanup_screen.py'),*common,'--output-dir',str(screen)],check=True)
    subprocess.run([sys.executable,'-B',str(code/'cleanup_emit.py'),*common,'--screen',str(screen/'screen.json'),'--output',str(a.output)],check=True)
    assert digest(a.output/'COHORT249-RECORDS.bin')==OUTPUT_SHA256
    print('PASS fixed438 cleanup word:',OUTPUT_SHA256,flush=True)
if __name__=='__main__':main()
