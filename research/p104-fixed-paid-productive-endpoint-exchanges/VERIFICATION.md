# Verification

Run `python3.12 -I -B research/p104-fixed-paid-productive-endpoint-exchanges/replay.py` on POSIX. Only the standard library is required. The package resolves every dependency relative to its own directory. Exact source and provenance identities are in PROVENANCE.json and PINS.json. Source history in SOURCES.json binds the canonical guides and task record. The packaged word, signed application and caller bytes match the exact #7481 package inputs.

Five engines run with separate 30-second caps. The first two enumerate by forward and reverse ADD anchors and compare every ID and coarsened class. Their original full receipts exceed five megabytes each. The package stores each full normalized SHA-256 and every tested matrix rather than duplicating those files. Both original-format receipts can be regenerated directly with the documented runner commands below. Measured timing is ignored when comparing scientific outputs.

```sh
cd research/p104-fixed-paid-productive-endpoint-exchanges
python3.12 -I -B lead/check_exchange.py --inputs inputs
python3.12 -I -B independent/check_endpoint_windows.py --inputs inputs
python3.12 -I -B pivot/check_cycle.py
python3.12 -I -B cycle-prefix-independent/cycle1049_prefix.py --word inputs/7481-WORD.json.gz
python3.12 -I -B cycle-independent/cycle1049_forward.py --word inputs/7481-WORD.json.gz
```

The prefix exact solver and separate forward probes agree. The independent suffix checker reconstructs the determinant and checks a missing carrier control. The wrapper also rejects duplicate pin keys, altered input bytes and a corrupt determinant. Literal swap and incomplete exchange controls and synthetic price/nesting controls are inside the pair runners. The successful runner exits are zero. No new whole supplier or complete κ replay was required.
