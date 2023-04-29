# Poseidon for EVMMAX
Implementation of Poseidon for EVMMAX.

Poseidon is a family of ZK-friendly hash functions used in rollups such as Starknet.
A precompile for the Ethereum Virtual Machine has been proposed in [EIP-5988](https://ethereum-magicians.org/t/eip-5988-add-poseidon-hash-function-precompile/11772).

EVMMAX is an extension of the EVM with optimised modular arithmetics.
It has been proposed in [EIP-5843](https://ethereum-magicians.org/t/eip-5843-evm-modular-arithmetic-extensions/12425) and [EIP-6601](https://ethereum-magicians.org/t/eip-6601-evm-modular-arithmetic-extensions-evmmax/13168).

We compare in this repository different possible solutions for implementing poseidon for the EVM or EVMMAX.


## Description of Poseidon
Poseidon inputs and outputs are elements of a given finite field.
Our implementations use a prime field; in that case, elements are integers modulo a (large) prime number.

We will use fixed-width hash functions.
They receive _rate_ field elements as input and produce _rate_ field elements as output.
Internally, it pads the input to a state vector _S_ of length _size_ (_rate_ < _size_), permutes it using a permutation _P_ and outputs _rate_ elements of the permuted input vector _P(S)_.

Poseidon's permutation is constructed by applying many rounds of a simpler permutation.
This simpler permutation in turn is the composition of 3 basic operations:

  1. Ark: round constants are added to _S_ (different for each round)
  1. S-Box: elements of _S_ are taken to a power _a_
  1. Mix: the state _S_ is multiplied by a fixed MDS-matrix _M_

For efficiency purposes, most rounds are actually partial.
Partial rounds differ in that the S-Box is applied to a single element only instead of all state elements.

### Parameters
We use the following parameters, the whole set being avaible in [params]().
The 256bits modulus is always: 2^251 + 2^196 + 2^192 + 1

| Variant   | Rate | Size | S-Box | N-full | N-partial |
|:---------:|:----:|:----:|:-----:|:------:|:---------:|
| Poseidon2 |   2  |   3  |   3   |    8   |    83     |


### Number of Modular Operations
Permutations use additions and multiplications:

  - Ark: _size_ additions
  - S-Box: 2 multiplications per element for power = 3
  - Mix: _size_^2 multiplications + (_size_ - 1) * _size_ additions
    
| Variant   | Round  | Add | Mult |
|:---------:|:------:|:---:|:----:|
| Poseidon2 |  Full  |  9  |  15  |
| Poseidon2 | Partial|  9  |  11  |
| Poseidon2 | Total  | 819 | 1'049|

Note that with EVMMAX, we need to use 2 * _rate_ multiplications to convert inputs and outputs from and to Montgomery's form.

### Implementation variants
Deploiement costs can be taken as negligible given that we target many millions of calls to the hash function.
Hence we aim at exploring different implementation with the goal of reducing the most the gas cost of a call, but we are also interested in execution time.

The following variants qualifiers describe implementation choices:

  - std : uses standard modular arithmetic op codes.
  - max : uses EVMMAX modular arithmetic op codes.
  - rs : uses poseidon-rs precompile.
  - cst : modulus, round constants and mds-matrix are included directly in code and pushed to the stack as needed.
  - mem : modulus and mds-matrix are kept in memory and loaded on the stack as neeeded.
  - unwind : rounds are concatenated one after the other in the code.
  - func : rounds are function call-like to reduce code size, but imply 2 jumps per round.

Note that for EVMMAX, operations happen directly in memory, so we are obliged to load constants in memory.

## Results
Here are some stats of executing poseidon hash

| Variant   | Implementation | CodeSize (B) | Timing (ms) | GasCost | N-ops |
|:----------|:---------------|:------------:|:-----------:|:-------:|:-----:|
| Poseidon2 | std-cst-unwind |              |             |         |       |
| Poseidon2 | std-mem-unwind |     21'914   |    1.446    | 38'687  | 9'793 |
| Poseidon2 | std-mem-func   |              |             |         |       |
| Poseidon2 | max-unwind     |     17'950   |    0.540    |  5'549  | 2'721 |
| Poseidon2 | max-func       |              |             |         |       |
| Poseidon2 | rs             |              |             |         |       |

## Observations
EVMMAX brings gas savings of the order of 80% compared to a standard implementation.
However, we note that the majority of these savings come from EVMMAX operation model and not from the modular arithmetic costs themselves.
Indeed, we save on the numerous operations (PUSH, MLOAD, MSTORE) aiming at bringing constants to the stack for modular arithmetics.
This is due to the fact that in EVMMAX, modular arithmetics happen directly in memory, and the arguments are given as immediate indices in the code.

This can be seen in the following profiling of Op Codes

| Variant   | Implementation | MSTORE | MLOAD | PUSH |  DUP | SWAP | GasCost |
|:----------|:---------------|:------:|:-----:|:----:|:----:|:----:|:-------:|
| Poseidon2 | std-cst-unwind |        |       |      |      |      |         |
| Poseidon2 | std-mem-unwind |   555  | 1'911 | 2'754| 2'066|  653 | 23'817  |
| Poseidon2 | std-mem-func   |        |       |      |      |      |         |
| Poseidon2 | max-unwind     |   285  |   0   |  577 |   0  |   0  |  2'586  |
| Poseidon2 | max-func       |        |       |      |      |      |         |
| Poseidon2 | rs             |        |       |      |      |      |         |

Note that modular arithmetics gas costs are incompressible, and are given by

| Variant   | Implem   | cost add | cost mul | cost set | TotalGas |
|:----------|:---------|----------|----------|----------|----------|
| Poseidon2 | standard | 8 x 819  | 8 x 1'049|    --    |  14'816  | 
| Poseidon2 | EVMMAX   | 1 x 819  | 2 x 1'053|  1 x  90 |   2'925  |

Thus we have the following gas savings distribution for EVMMAX

| Variant   | Implem | Stack Savings | Arith Savings | Total Savings |
|:----------|:------:|:-------------:|:-------------:|:-------------:|
| Poseidon2 | unwind |  21'231 (64%) |  11'891 (36%) |    33'138     |
