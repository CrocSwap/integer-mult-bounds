# Exhaustive independent nonlinear transcript-cut audit

This audit supplies a separately implemented finite check of Jose Manuel / @jmbarrancoml's PR1757 outgoing-transcript lemma. It enumerates actual nonlinear reversible gate words and all binary vertex partitions; it does not linearize their endpoints. The general cut/common-flag theorem remains credited to PR1757 and Navinor / PR825.

## Complete declared domain

There are three arbitrary input bits, six directed CNOT gates and three Toffoli gates (one choice of target, the other two roles as controls). Enumerate every word of lengths 1..5 over these nine gates. Retain words containing a Toffoli whose complete eight-input truth table is a permutation of the three input roles. The verifier constructs every physical wire segment, including controls and untouched terminal wires. Every gate is one vertex, as required by the common-frame contract.

For each retained graph enumerate all binary vertex labels, modulo global complement. Both classes are checked, so complement normalization loses no class obligation. For a class, let D be the source roles in the class whose required sink lies outside. Record every outgoing wire symbol in fixed edge order. Fix the other input bits. The checker verifies that no two different D assignments have the same outgoing transcript, and checks outgoing-edge count at least |D|. This covers cuts that are not chronological slices and permits re-entry. The receipt records 66,429 enumerated words,282 admitted nonlinear permutation words (120 nonidentity),272,172 demanded-class cuts and 2,177,376 complete assignment transcripts. The enumeration includes nonidentity role permutations once depth 5 is reached.

This is a genuinely nonlinear test: truth vectors encode all eight inputs, not just zero and one-hot columns. A Toffoli falsely declared to have identity endpoint passes all those basis inputs but fails the full table. A second control removes an actual terminal wire from the sharp identity topology, creating a transcript collision. All729 pairs of upper-triangular2x2 matrices with entries in {-1,0,1} separately check rank(difference)>=number of changed diagonal labels, the local common-flag charging step.

## Why the finite audit is relevant

For a general fixed acyclic deterministic circuit, the outside subgraph can be simulated from the fixed non-D input symbols and outgoing transcript. Complete permutation endpoints then force that transcript to distinguish all independent D inputs. This is the predecessor's universal counting proof. Our finite result tests its implementation consequences over an explicit complete nonlinear word domain; it neither proves all circuits by enumeration nor claims a new universal theorem. Binary partitions alone do not exhaust arbitrary multi-label partitions or geometry.

## Reproduce and scope

    python3.12 scripts/research_package.py --package research/nonlinear-cut-exhaustive-audit

Read-only Python standard library; all checks survive -O. EXTERNAL-SOURCES.json pins the exact predecessor statement and Git blob, no predecessor implementation is imported. Full input independence, fixed topology, complete permutation endpoints and all physical wire charging remain required. No supplier, non-common-flag impossibility, all-size/compiler result, cold replay, Lean proof or new kappa is claimed.

## Open next questions

Can a useful nonlinear circuit admit non-common-flag rational geometry below the rank-mass floor? First provide its complete truth table and charged physical graph, then solve its frame problem. The present census only audits a cut implication; it does not search for or exclude such geometry.

## Credit

Jose Manuel / @jmbarrancoml, PR1757, supplies the nonlinear common-flag extension; Navinor /PR825 the prior linear/common-flag result; retained OpenAI sources supply the shear contract. New independent exhaustive audit prepared for woklerx with substantial OpenAI Codex assistance, Apache-2.0. No independent human review.
