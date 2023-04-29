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
    montR2 = pgr.memory.alloc("montR2")
    state = pgr.memory.alloc("state", shape=(params["size"],))
    temp = pgr.memory.alloc("temp", shape=(params["size"],))
    mds = pgr.memory.alloc("mds", shape=(params["size"], params["size"]))
    rk = pgr.memory.alloc("rk", shape=(params["size"],))
    
    def permute_partial(partial):
        # Ark
        partial.addmodx(state[0], state[0], rk[0]) 
        # Sbox
        # Reuse rk as accumulator
        partial.mulmontx(rk[0], state[0], state[0])
        partial.mulmontx(temp[0], rk[0], state[0])
        for j in range(1, params["size"]):
            # Ark and No Sbox
            partial.addmodx(temp[j], state[j], rk[j])
        # Mix
        for j in range(params["size"]):
            partial.mulmontx(state[j], temp[0], mds[j][0])
            for k in range(1, params["size"]):
                # Reuse rk as accumulator
                partial.mulmontx(rk[k], temp[k], mds[j][k])
                partial.addmodx(state[j], state[j], rk[k])
    
    def permute_full(full):
        for j in range(params["size"]):
            # Ark
            full.addmodx(state[j], state[j], rk[j]) 
            # Sbox
            # Reuse rk as accumulator
            full.mulmontx(rk[j], state[j], state[j])
            full.mulmontx(temp[j], rk[j], state[j])
        # Mix
        for j in range(params["size"]):
            full.mulmontx(state[j], temp[0], mds[j][0])
            for k in range(1, params["size"]):
                # Reuse rk as accumulator
                full.mulmontx(rk[k], temp[k], mds[j][k])
                full.addmodx(state[j], state[j], rk[k])
    
    sponge = pgr.segment("sponge")
    sponge.mstore(dest=mod, value=params["modulus"])
    sponge.mstore(dest=montR2, value=params["montR2"])
    sponge.setmodx(modulus=mod)
    sponge.calldatacopy(dest=state[:params["rate"]], offset=0)
    sponge.mstore(dest=mds, value=params["mds"])
    # Input tomontx
    for j in range(params["rate"]):
        sponge.mulmontx(state[j], state[j], montR2)

    for i in range(lim_full):
        sponge.mstore(rk, params["rks"][i])
        permute_full(sponge)
    for i in range(lim_full, lim_partial):
        sponge.mstore(rk, params["rks"][i])
        permute_partial(sponge)
    for i in range(lim_partial, n_rounds):
        sponge.mstore(rk, params["rks"][i])
        permute_full(sponge)
    
    # Output frommontx
    sponge.mstore(dest=montR2, value=Hex(1))
    for j in range(params["rate"]):
        sponge.mulmontx(state[j], state[j], montR2)
    sponge.return_(state[:params["rate"]])

    pgr.ops.extend(sponge.ops)
    return pgr
