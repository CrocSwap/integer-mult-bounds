"""Source-specific cutoff data-flow checks supporting the written audit.

This is not a general static analysis or proof kernel. Prepared for
@CubeJerry with substantial OpenAI assistance. Apache-2.0.
"""
import ast
from hashlib import sha256
from cutoff_sources import HERE,authenticate,need

BASE="vendor/leaf/vendor/atomic/"
FILES={
    "leaf":BASE+"vendor/leaf/leaf_provider.py",
    "coefficient":BASE+"vendor/leaf/vendor/leaf/coefficient_engine.py",
    "axis":BASE+"vendor/leaf/vendor/leaf/axis_stream.py",
    "header": "vendor/leaf/vendor/header/header_view.py",
    "monomial":BASE+"vendor/monomial/phase_adapter.py",
    "compact":BASE+"vendor/monomial/vendor/binding/provider.py",
    "rows":BASE+"vendor/monomial/vendor/binding/vendor/dispatch/row_programs.py",
    "services":"vendor/row-provenance/services.py",
    "compiler_routes":"vendor/row-provenance/compiler_routes.py",
    "padding":"vendor/row-provenance/pattern_padding.py",
}


def cutoff_literals(tree):
    return sum(isinstance(n,ast.Constant) and n.value=="cutoff" for n in ast.walk(tree))


def leaf_flow(raw):
    tree=ast.parse(raw)
    provider=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=="Provider")
    functions={n.name:n for n in provider.body if isinstance(n,ast.FunctionDef)}
    prepare=functions["prepare"]; run=functions["run"]
    need(cutoff_literals(tree)==cutoff_literals(prepare)==2,"only positivity and comparison use leaf cutoff")
    accesses=[n for n in ast.walk(prepare) if isinstance(n,ast.Subscript)
              and isinstance(n.value,ast.Name) and n.value.id=="header"
              and isinstance(n.slice,ast.Constant) and n.slice.value=="cutoff"]
    need(len(accesses)==1,"one literal leaf cutoff comparison input")
    calls=[n for n in ast.walk(run) if isinstance(n,ast.Call)
           and isinstance(n.func,ast.Attribute) and n.func.attr=="run_leaf"]
    need(len(calls)==1,"one unchanged positive numerical consumer")
    args=[ast.unparse(x) for x in calls[0].args]
    need(args==["self.bridge","widths","header['f']","header['K']","rho","h","coefficients","rows","self.inverse"],
         "leaf receives actual width and geometry, never cutoff")
    need(not cutoff_literals(functions["__init__"]),"fixed inventory constructor cannot depend on cutoff")
    return dict(cutoff_literals=2,comparison_accesses=1,engine_arguments=args,
                cutoff_changes_inventory=False,cutoff_reaches_numeric_engine=False)


def check():
    count=authenticate(); records={}
    for label,path in FILES.items():
        raw=(HERE/path).read_bytes();tree=ast.parse(raw)
        records[label]=dict(path=path,sha256=sha256(raw).hexdigest(),cutoff_field_literals=cutoff_literals(tree))
    need(all(records[k]["cutoff_field_literals"]==0 for k in
             ("coefficient","axis","header","monomial","services","compiler_routes","padding")),
         "no hidden cutoff-field consumer in unchanged numerical/metadata bodies")
    need(records["compact"]["cutoff_field_literals"]==1,"Compact only names cutoff in generic schema")
    flow=leaf_flow((HERE/FILES["leaf"]).read_bytes())
    rows=ast.parse((HERE/FILES["rows"]).read_bytes())
    uses={}
    for node in ast.walk(rows):
        if isinstance(node,ast.FunctionDef):
            n=cutoff_literals(node)
            if n:uses[node.name]=n
    need(uses=={"cutoff_guard":1,"compile_prepare":1,"compile_leaf":1},"exact row-decision consumer inventory")
    corrupted=(HERE/FILES["leaf"]).read_text().replace(
        'header["f"], header["K"]','header["cutoff"], header["K"]')
    need(corrupted!=(HERE/FILES["leaf"]).read_text(),"numerical loop-leak control applied")
    try:leaf_flow(corrupted)
    except ValueError:pass
    else:raise ValueError("cutoff used as numerical width escaped source audit")
    return dict(retained_files=count,files=records,positive_leaf=flow,
                row_functions=uses,numeric_cutoff_leak_mutant_rejected=True,
                scope="Exact-source structural checks support PROOF; not a general taint analyzer or kernel.")
