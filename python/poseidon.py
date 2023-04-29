import json

from .evm import Program, Hex
from .params import import_parameters


def program(params):
    if params["sbox"] not in [3]:
        raise NotImplementedError(f"Sbox {params['sbox']} is not yet supported.")
    
    lim_full = (params["n_full_rounds"] // 2)
    lim_partial = lim_full + params["n_partial_rounds"]
    n_rounds = params["n_full_rounds"] + params["n_partial_rounds"]
    sbox_n_mods = 2 if params["sbox"] == 3 else 3
    
    pgr = Program()
    mod = pgr.memory.alloc("modulus")
    state = pgr.memory.alloc("state", shape=(params["size"],))
    temp = pgr.memory.alloc("temp", shape=(params["size"],))
    mds = pgr.memory.alloc("mds", shape=(params["size"], params["size"]))
    rk = pgr.memory.alloc("rk", shape=(params["size"],))
    fp = pgr.memory.alloc("fp")  # need only one return point
    
    partial = pgr.segment("permute_partial")
    partial.jumpdest()
    # Top stack = params["modulus"], dup to avoid reloading
    for _ in range(1 + sbox_n_mods):
        partial.dup(1)
    # Ark
    partial.mload(rk[0])
    partial.mload(state[0])
    partial.addmod()
    # Sbox
    partial.swap(1)
    partial.dup(2)
    partial.dup(1)
    partial.mulmod()
    partial.mulmod()
    partial.mstore(temp[0])
    for j in range(1, params["size"]):
        # Top stack = params["modulus"], avoid consuming it
        partial.dup(1)
        # Ark
        partial.mload(rk[j])
        partial.mload(state[j])
        partial.addmod()
        # No Sbox
        partial.mstore(temp[j])
    # Mix
    for j in range(params["size"]):
        # Top stack = params["modulus"], avoid consuming it
        for _ in range(2 * params["size"] - 1):
            partial.dup(1)
        for k in range(params["size"]):
            partial.mload(mds[j][k])
            partial.mload(temp[k])
            partial.mulmod()
            n_sw = 2 * params["size"] - 2 * k - 3
            if n_sw > 0:
                partial.swap(n_sw)
        for _ in range(params["size"] - 1):
            partial.addmod()
        partial.mstore(state[j])
    partial.jump(fp)
    
    full = pgr.segment("permute_full")
    full.jumpdest()
    for j in range(params["size"]):
        # Top stack = params["modulus"], avoid consuming it
        for _ in range(1 + sbox_n_mods):
            full.dup(1)
        # Ark
        full.mload(rk[j])
        full.mload(state[j])
        full.addmod()
        # Sbox
        full.swap(1)
        full.dup(2)
        full.dup(1)
        full.mulmod()
        full.mulmod()
        full.mstore(temp[j])
    # Mix
    for j in range(params["size"]):
        # Top stack = params["modulus"], avoid consuming it
        for _ in range(2 * params["size"] - 1):
            full.dup(1)
        for k in range(params["size"]):
            full.mload(mds[j][k])
            full.mload(temp[k])
            full.mulmod()
            n_sw = 2 * params["size"] - 2 * k - 3
            if n_sw > 0:
                full.swap(n_sw)
        for _ in range(params["size"] - 1):
            full.addmod()
        full.mstore(state[j])
    full.jump(fp)
    
    # Static analysis for jumpdests
    sponge_jumpdest = 2 + len(full) + len(partial)
    sponge_jumpdest_size = Hex(sponge_jumpdest).nbytes()
    sponge_jumpdest = Hex(sponge_jumpdest + sponge_jumpdest_size)
    if sponge_jumpdest.nbytes() > sponge_jumpdest_size:
        sponge_jumpdest = Hex(sponge_jumpdest + 1)
    
    main = pgr.segment("main")
    main.jump(sponge_jumpdest)
    
    jumpdests = {
        "partial": Hex(len(main)),
        "full": Hex(len(main) + len(partial)),
        "sponge": sponge_jumpdest,
    }
    
    sponge = pgr.segment("sponge")

    # We know all code offsets for jumps.
    partial.offset = Hex(len(main))
    full.offset = Hex(len(main) + len(partial))
    sponge.offset = sponge_jumpdest
    
    sponge.jumpdest()
    sponge.mstore(dest=mod, value=params["modulus"])
    sponge.calldatacopy(dest=state[:params["rate"]], offset=0)
    sponge.mstore(dest=mds, value=params["mds"])
    sponge.mload(mod)  # Keep field params["modulus"] on stack, duplicated as needed
    for i in range(lim_full):
        sponge.mstore(rk, params["rks"][i])
        sponge.call(fp, jumpdests["full"])
    for i in range(lim_full, lim_partial):
        sponge.mstore(rk, params["rks"][i])
        sponge.call(fp, jumpdests["partial"])
    for i in range(lim_partial, n_rounds):
        sponge.mstore(rk, params["rks"][i])
        sponge.call(fp, jumpdests["full"])
    
    # sponge.pop()  # Remove modulus from stack
    sponge.return_(state[:params["rate"]])

    pgr.ops.extend(main.ops)
    pgr.ops.extend(partial.ops)
    pgr.ops.extend(full.ops)
    pgr.ops.extend(sponge.ops)
    return pgr
