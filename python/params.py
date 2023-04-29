import json

from .evm.types import Hex


def import_parameters(f):
    params = json.load(f)
    params["modulus"] = Hex(params["modulus"])
    params["montR"] = Hex(params["montR"])
    params["montR2"] = Hex(params["montR2"])
    params["montRinv"] = Hex(params["montRinv"])
    params["mds"] = [[Hex(x) for x in row] for row in params["mds"]]
    params["rks"] = [[Hex(x) for x in row] for row in params["rks"]]
    return params


def import_parameters_as_le(f):
    params = json.load(f)
    params["modulus"] = Hex(params["modulus"]).to_le(zfill=32)
    params["montR"] = Hex(params["montR"]).to_le(zfill=32)
    params["montR2"] = Hex(params["montR2"]).to_le(zfill=32)
    params["montRinv"] = Hex(params["montRinv"]).to_le(zfill=32)
    params["mds"] = [[Hex(x).to_le(zfill=32) for x in row] for row in params["mds"]]
    params["rks"] = [[Hex(x).to_le(zfill=32) for x in row] for row in params["rks"]]
    return params
