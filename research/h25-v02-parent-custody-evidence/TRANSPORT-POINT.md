# Observed transport points and remaining origin gap

This is a sanitized summary of earlier point observations. It contains no host identity, operational paths, process IDs, accounting records or transcript. The underlying private records were preserved, not exported. This publication did not repeat their commands.

| Prior observation | Result and precise scope |
| --- | --- |
| Actual Tool `tty:false, login:false` | fd0 was a character device, returned immediate zero-byte EOF and offered no writable retained session. This route cannot feed the candidate's FIFO-only ingress. |
| Actual Tool raw PTY | 63-byte and 32,768-byte samples arrived correctly, but fd0 remained a character device and fails the current FIFO condition. Successful byte transport alone does not qualify the channel. |
| Fresh anonymous pipe | Capacity was 8,192 bytes; `PIPE_BUF` was 4,096. A private request to increase capacity to 32,768 failed with EPERM. This is a point observation, not a universal Linux configuration claim. |
| Benign preloaded FIFO | With a narrower prospective frame bound, one nonblocking preload succeeded and the sole writer closed before benign child birth. GNU Time passed the same FIFO, exact bytes and EOF to that child. No original parent, protected-origin assignment, genuine decisions or full cost accounting ran. |

The narrower prospective frame domain allows three unescaped printable-ASCII paths of at most 512 characters, three printable identifiers of at most 96 characters, and uint64 metadata. A deliberately overbounding combination produced 3,613 canonical bytes including LF, fitting the observed capacity and atomic-write bound. This restricted domain is a proposed transport assumption, not a source change, current complete source census, or accepted policy for every valid original input. The shipped general encoder and ingress still retain their own wider bounds. The preload design has not been joined to the original caller.

Private observation record digests for audit continuity:

- `TOOL-STDIN-CAPABILITY-POINT-v1.json`: `fdc1e8e33125cecb91325288138f9cc82daac79092445e9b42bfca816672f1c4`.
- `NATIVE-TIME-FD0-POINT-v1.json`: `633a3af60755b22a62bc018c7aef947e07dcc0062b4a4a193cb37661ee3d18ef`.
- `PARENT-PRELOADED-FIFO-FEASIBILITY-v1.json`: `80b14118c4c1b7352305d3e3fcb73aea81deda79e9d600d614a3f12f45701c22`.

These digests identify omitted observations; readers cannot independently reconstruct their private contents from this summary. They confer no operational permission or authenticity. FIFO shape, endpoint identity, expected hashes and an ACK never establish protected origin. A real join must establish independently authenticated original writer/session authority, sole-reader custody, descriptor stability throughout the frame interval, preparation/P continuity, and every failure's cleanup/first-error ownership.
