# Vendored files

Byte-for-byte copies; nothing here is modified. The sha256 and git blob ids are
pinned in `../lib.py` (`VENDOR_PINS`) and checked before any use.

- `pr1043/`: Ali Romman (@aliromman), PR1043, head
  `e309e17f83f5759b1ea1fa24a76f24838784cb4d`, from
  `research/bit-boundary-persistence/`. Apache-2.0. Its own `NOTICE.md` is
  copied unchanged; it states substantial OpenAI Codex assistance.
- `pr1345/`: Andrzej Marszałek (@hipotures), PR1345, head
  `b54a856aa79857d91cd5d65f8f7144e26c8c084f`, from
  `research/bit589-transport-atlas/`. Apache-2.0. Its docstring states it was
  prepared with an autonomous opencode research agent (Qwen3.8-Flash). The
  bug fixes live in `../atlas.patch` and are applied at run time; this copy is
  the original file.
