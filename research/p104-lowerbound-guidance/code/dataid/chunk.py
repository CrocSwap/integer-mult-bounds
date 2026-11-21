def chunked(name, rowfn_def, rowfn, n=8, sz=13):
    """emit: rowfn def, chunk theorems, forall theorem"""
    out=[rowfn_def]
    for c in range(n):
        out.append(f"theorem {name}_c{c} : (List.range {sz}).all (fun i => {rowfn} ({sz}*{c}+i)) = true := by decide +kernel")
    out.append(f"""theorem {name} : ∀ t, t < {sz*n} → {rowfn} t = true := by
  intro t ht
  refine forall_of_chunks {rowfn} (n := {n}) ?_ t (by omega)
  intro c hc
  interval_cases c""" + ''.join(f"\n  · exact {name}_c{c}" for c in range(n)))
    return '\n'.join(out)+'\n'
