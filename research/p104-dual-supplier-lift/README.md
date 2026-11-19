# A closed 48-call P104 supplier and a stronger ordinary BIT supplier

The two suppliers give a conditional multiplication saving of **κ = 0.00384022183437**. The complete complex price crosses between 0.00384022183445 and 0.00384022183446. The binary construction raises the ordinary BIT saving from 0.00385248 to 0.00385896149. The selected framework contributes five assumptions. Independent scientific review remains open. [Complex proof and receipt](complex/PROOF.md) · [Binary proof](BIT-PROOF.md) · [Scoped claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/7111#discussioncomment-19721588)

## Reproduce

Use CPython 3.12 and its standard library from the repository root.

```sh
python3.12 -B scripts/research_package.py --package research/p104-dual-supplier-lift
```

The registered commands rebuild the binary and complex circuits, the full 48-call program, both ordinary ledgers and the conditional application. Three chart checks verify the absolute phase and rank of every paid and productive complex transfer. [Verifier](verify.py) · [Live input pins](SOURCES.json)

## Open next questions

- Can an independent reviewer reproduce the two calibrated helper births and the common scalar grid?
- Can the complex price cross 0.00385376046858, the upper endpoint of PR 7756 plus its full gain?

## Credit

Ali Romman prepared this work with substantial OpenAI Codex assistance. The proof files and retained notices credit the native, binary, caller, physical and compiler sources. [Complex proof and credit](complex/PROOF.md) · [Binary proof and credit](BIT-PROOF.md)
