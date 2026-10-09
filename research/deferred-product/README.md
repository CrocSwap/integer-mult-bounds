# Deferred bit word and a new complex producer under stopped-product accounting

**κ = 1044939/10^10 = 1.044939×10^-4**, conditional on PR #104's retained interfaces. This is
**+34.06% over PR #104** (7.79476×10^-5).

- **Bit side.** Swapnil Jain's round-seven deferred word (PR #97's import, h = 23) is charged
  by PR #104's one-child rule. Every residual is a nested projector residual, so each counts
  as one child. The coarse saving is 620523/(5·10^9) = 1.2410×10^-4, and the ordinary saving
  after stopping is 1.2402×10^-4.
- **Complex side.** A new h = 24 producer with all 24 centers disjoint uses 28,705 roles,
  against 44,918 for PR #104's producer. That gives a_c = 26129/(2.5·10^8) = 1.0452×10^-4 in
  PR #104's framework, and this side binds.
- **Assembly.** PR #104's assembly runs at PHASE_STOP = 10^-6. The largest bit child is 528,
  so the bit halving degree is 367 and the row stock p^22000.

```sh
make deferred-product-verify
```

The target does the following:

1. Replays #97's literal ledger (both shears, reflected continuity, event histogram).
2. Runs Swapnil Jain's exact frame check.
3. Rebuilds the complex row from the shipped DAG with PR #104's unchanged matcher.
   It then replays the complete signed two-stage complex word at gate level: nesting, whole
   residuals, reflection, and a paid histogram equal to the row's profile. The 3,308
   alternating rank-2 residuals use PR #104's one-child Gauss normal form.
4. Recomputes the one-child list, both moments and the assembly.

[PROOF.md](PROOF.md) lists the preconditions and the scope.

Credits:

- **Bit network:** Swapnil Jain (round seven).
- **Ledgers and integration:** jacklightChen (PR #97).
- **Stopped-product accounting, framework and assembly:** icekylinx (PR #104), on its retained lineage.
- **Complex producer and this integration:** eumemic, with Anthropic Claude assistance.
