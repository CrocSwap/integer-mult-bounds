# Adversarial review of the asynchronous construction

Reviewed the actual emitted template, emit_async.py, the complete source execution schedule, the sufficient composition proof, and the independent complex lane audit_async.py / ASYNC-AUDIT.json. The latter passes all40,320 physical owner intervals/charts,72 complete invocations,9,615 remainders, and18 mutation controls. Reviewed template SHA-256:276b69e3fc79a211daaf39776d91b3a6f9c262c415cbd199ab02d5e0ccb9bf4b.

## Event scope

The source has30 replica-local events and two whole-stock events. Projection of the emitted schedule onto EACH of the eight replicas is exactly source events0..29, in order. Replica-local events are local cover calls, pending idle completions, bridges, terminal Y translations, and the terminal signed exchange. The new event's replica / replicas=[replica] explicitly restrict every such event to that replica's data families; it must not be interpreted by an old decoder that silently ignores these fields. The independent checker compares every full event dictionary against this restriction of its source event. There are72 local sweeps,72 one-replica bridge sweeps, eight terminal-translation events and eight terminal signed exchanges.

The empty bank-padding operation and the full-stock correction remain exactly once after all replicas finish. The correction still covers all7,680 live families. It is not duplicated per replica. Private centers/tableau/coefficient streams can be shared because each complete local program restores them before another invocation begins.

## Actual intervals, including bridges

The independent checker derives each owner window from the last preceding touch of its (replica,pair), counting both local calls and every individual bridge, then uses the literal idle-completion event as its deadline. It does not trust the optimizer's stage-window metadata. Every use lies strictly between those physical event positions. In particular, the narrow rank8 windows open after a forward bridge and close before its inverse bridge; final long windows open after the last earlier inverse bridge and close before the final bridge cascade. Initial windows have no preceding touch. The emitter's stage blocks place all source nonlocal events after their local call and before any subsequent call, so its coarser block-time convention agrees with these exact touch intervals.

A foreign replica may use the same pair number while the owner's pair is idle; pair numbers are not physical owners. All800 physical families per complete call are distinct, so this freedom cannot alias an active source/target. No pending block is reused; disjoint blocks plus the explicit remainder exactly cover each original idle child.

## Full-cover composition

The proof uses the admitted endpoint of a COMPLETE normalized invocation, including its whole cover sweep. It never cancels or commutes gates through an unfinished scalar program. Each actual73-column chart is orthogonal; right multiplication by its inverse permutes the cover group, so a unique physical family has one corresponding stream per cover vertex. Thus the retained800-column arbitrary-dirt theorem applies without assuming fresh helper values. Borrowed spectators are restored. The only persistent helper action is the checked residual on its assigned pending coordinates.

After replacing complete invocations by their admitted endpoints, each data replica retains its original data/bridge/terminal order. The only reordered factors between consecutive touches of a family are residuals on disjoint coordinate blocks. These commute and multiply with the remainder to the original pending child. This gives the original endpoint exactly. It relies on the same explicit normalized-invocation, all-size compiler and analytic contracts as PR496; it does not establish those inherited contracts anew.

## Invoice caveat and conclusion

The former192-bit prefix charge cannot simply be inherited: the nine synchronized bridge rounds became72 ordered one-replica sweeps. A sufficient bound is20+37+72+72+4=205 bits, using the retained local transient envelope and a factor2 per complete invocation/bridge. The parent is charging512. Total scalar bridge additions do not increase; only their order changes. Maximum child48 still satisfies73^2>2*48^2.

No additional mathematical admission gap was found in the reviewed finite scheduling change. Final success still requires the parent's independently regenerated coefficient invoice and exact outer assembly. The positive statement is the sufficient endpoint-preserving asynchronous construction, not a claim that a packing relaxation alone proves an improved kappa.
