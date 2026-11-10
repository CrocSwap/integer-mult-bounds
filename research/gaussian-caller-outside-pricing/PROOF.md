# Proof: the caller outside the selected pricing assembly does not consume C

## Setting

The selected conditional result is PR6030, κ = 781451/250000000.
`research/p104-helper470-twin-rung-removal/pricing.py` is the pricing
assembly admitted with that result. Inside `run`, after the stock gate

    atom > ordinary > admitted > TESTED,

it builds a parameter dictionary whose `bit_saving` entry is `admitted`
and passes that dictionary to the PR4359 ledger. The recorded PR5679
component

    C = 3507410738409/1000000000000000

is the `admitted` field of `research/g20-helper-split/ORDINARY-RESULT.json`,
with `whole_kappa = null`. The fork note that rejects C as that assembly's
admitted input does not identify a caller outside the assembly. This note
names the caller the selected verifier actually loads.

## The caller and its parameters

`research/p104-helper470-twin-rung-removal/verify.py` loads

    research/p104-productive-controller/caller.py

and then, in this order,

    caller = C.construct()
    physical = C.physical(caller, word)
    price = P.run(local, native, caller, physical)

`construct` takes no arguments. Its return value is the controller object
stored in `CONTROLLER.json`. The verifier's equality message calls that
object the physical caller. That JSON object has no `bit_saving` field and
does not contain the numerator of C.

`physical` is the function that contains the Gaussian checks. Its source
has exactly one copy of each of

    Multiply the Gaussian pair twice with exact real and imaginary parts.
    All idle Gaussian axes

and its only parameters are `word` and `local`, with no defaults. The
selected call passes two positional arguments. The first is the controller
returned by `construct`. The second is the regenerated edited word stored
in the verifier's variable `word`. That second object is the edited PR5907
word, not the replay dictionary the verifier names `local`, and not C.
Neither parameter is named `bit_saving`. The function's only direct return
statement builds a dictionary. Its keys include `whole_idle_jobs` and do
not include `bit_saving`. No function in the module has an argument named
`bit_saving`, and the module text does not contain that identifier.

`pricing.run` is a different function. Its parameters are
`local, native, word, physical`. The `bit_saving` entry is created inside
the body and set to `admitted`. `physical` returns before that assignment.
The caller does not use the pricing assembly.

## What this obstruction says

For this named function, there is no `bit_saving` input that can be set to
C. The recorded controller artifact also has no such field. The caller
therefore does not consume C. No execution receipt for `physical` is
claimed, because an execution cannot place C into a parameter the function
does not have.

## Finite census of `caller.py`

At base commit `7c49fe32c55de02c2c873655c804b16e4c3fef0a`,
`git ls-tree -r --name-only` lists every path in the tree. The paths whose
final component is `caller.py` are exactly 15, and they are the list in
`verify.py`. Each blob was read in full. None contains the byte string
`bit_saving`. Exactly seven of those blobs contain `Gaussian` or
`gaussian`. Five of them are the same blob,
`6ac5e735691555ecafe2afbcff71edd923178113`: the named file and the copies
under the caller-independent audit, the contact-independent audit,
`research/p104-coupled-helper-bases/caller.py`, and
`research/p104-cut-stability/whole-caller/inputs/caller.py`. The other two
are different files. `research/native-involutive-dual/caller.py` contains
the check `Real K commutes full Gaussian` and the field
`gaussian_supplier`. `research/physical-boundary-rhs-caller/caller.py`
imports `gaussian_page`. Neither of those two defines `physical`. None of
the seven contains `bit_saving`. This is an exhaustive finite census of
that filename at that commit. It is not a census of every function in the
repository. In particular,
`research/gaussian-height-contract/check_caller.py` is not named
`caller.py`, and the PR4359 ledger is not in this census.

## What is not claimed

This does not rerun the selected stock gate, change the thinned
controller's cover, or treat the assembly rejection of C as a prohibition
on every possible caller. A function outside these 15 files could still
have a `bit_saving` parameter. The selected κ is unchanged. The five
framework assumptions remain in force. `physical` was not executed.
