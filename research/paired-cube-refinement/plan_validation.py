"""Validate frame-plan structure before indexing any operation or factor proof."""


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def validate_plan(plan, operation_count, p=12):
    require(type(operation_count) is int and operation_count>0, "operation count")
    require(type(p) is int and p>0, "parameter")
    require(isinstance(plan,dict) and type(plan.get("p")) is int and plan["p"]==p,
            "plan parameter")
    frames=plan.get("frames")
    require(isinstance(frames,list), "frame entries list")
    previous=-1
    for item in frames:
        require(isinstance(item,list) and len(item)==2, "frame entry shape")
        index,basis=item
        require(type(index) is int and 0<=index<operation_count, "operation index range and type")
        require(index>previous, "unique strictly increasing operation indices")
        previous=index
        require(isinstance(basis,list) and 0<len(basis)<=2*p, "nonempty frame basis")
        require(all(isinstance(row,list) and len(row)==2*p and
                    all(type(x) is int for x in row) for row in basis),
                "exact integer frame coordinates and ambient dimension")
    return dict(p=p,operation_count=operation_count,changed_operation_frames=len(frames))
