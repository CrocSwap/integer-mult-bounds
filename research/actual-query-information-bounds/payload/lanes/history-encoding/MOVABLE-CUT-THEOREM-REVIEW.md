# Independent proof review of movable snapshot cuts

The reviewed source is
`../cover-algebra/MOVABLE-SNAPSHOT-CUTS.md`, SHA256
`cc26bd7b4d82bece7bd4b409350313539b953a26e88115d1efecb97bf538ead1`.

The theorem is correct in its stated finite linear observation model.
For a node set Omega, restrict inputs to the kernel of every free
observation inside Omega. Induction in circuit order shows that every
inside value lies in the span of values that entered Omega. A value
that leaves and returns is still charged on re-entry. No upward-closure
assumption is needed. Thus incoming rank bounds the output rank on
this input kernel.

The identity

```text
rank(Q restricted to kernel A) = rank([A;Q]) - rank(A)
```

follows from the quotient of row spaces. Nonnegative cut weights can
then be summed when their entering-edge charge does not exceed the
edge cost. This permits arbitrary shared values, cancellation, and
edge multiplicity. The block statement is valid when each field has
the stated fixed payload dimension and all actual observations are
included. It does not grant a new native-frame map.

The actual source-port test is also valid. On `X=JY` with all helpers
and private inputs zero, the accepted support law makes every inside
observation vanish. Shrinking the node set preserves this property
and its source rank. Enlarging the node set need not preserve the
edge charge, so the distinction from a maximal source cut is real.
The two-cut chain example gives the stated bound of two.

No material proof finding remains. This is a proof review. It does
not replay the original snapshot rows or establish a new numerical
bound. The separate rank-eight cut receipt supplies the numerical
certificate for that application.
