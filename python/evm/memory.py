from collections.abc import Sequence
from dataclasses import dataclass
import itertools
from typing import Union

from .types import Hex


@dataclass
class Variable:
    name: str
    addr: Hex
    t_size: int


@dataclass
class Array(Variable):
    shape: Union[Sequence[int], int]
    steps: Union[Sequence[int], None] = None

    def __init__(self, name, addr, t_size, shape, steps=None):
        super().__init__(name, addr, t_size)

        if isinstance(shape, int):
            self.shape = (shape, )
        else:
            self.shape = tuple(shape)
        self.ndims = len(self.shape)

        if steps is None:
            self.steps = [1]
            cumprod = 1
            for s in self.shape[:0:-1]:
                cumprod *= s
                self.steps.append(cumprod)
            self.steps.reverse()
        else:
            self.steps = steps
        if len(self.steps) != self.ndims: 
            raise ValueError(f"Wrong ndims in view's {self.name} steps: "
                             f"passed {len(self.steps)} "
                             f"expected {len(self.ndims)}")

        self.m_size = self.t_size
        for sh in self.shape:
            self.m_size *= sh

    def iter_index(self):
        return itertools.product(*(range(sh) for sh in self.shape))

    def __iter__(self):
        return iter(self[idx] for idx in self.iter_index())

    def _get_view(self, indices):
        offset = 0
        shape = []
        steps = []
        for d, (i, sh, st) in enumerate(zip(indices, self.shape, self.steps)):
            if isinstance(i, int):
                if i >= sh:
                    raise IndexError(f"Index out of bound for dim {d}: "
                                     f"passed {i} for size {sh}")
                offset += i * st
            elif isinstance(i, slice):
                start, stop, by = i.indices(sh)
                offset += start * st
                shape.append((stop - start) // by)
                steps.append(st)
            else:
                raise IndexError(f"Index for dim {d} should be int or slice: "
                                 f"passed {i}")
        return (shape, steps, offset)

    def __getitem__(self, args):
        if isinstance(args, int) or isinstance(args, slice):
            args = [args]
        else:
            args = list(args)
        if len(self.shape) < len(args):
            IndexError(f"Too many indices for Array {self.name}: "
                       f"passed {len(args)} expected at most {len(self.shape)}")
        # Missing indices -> keep the dimension
        for i in range(len(args), len(self.shape)):
            args.append(slice(None, None, None))

        for d, (s, a) in enumerate(zip(self.shape, args)):
            if isinstance(a, int) and (s <= a or -s > a):
                IndexError(f"Index out of bounds for dim {d}: "
                           f"passed {a} for shape {s}")
        sh, st, of = self._get_view(args)
        if sh:
            return Array(
                name=f"__{self.name}[{args}]",
                addr=Hex(self.addr + of * self.t_size),
                t_size=self.t_size,
                shape=sh,
                steps=st
            )
        else:
            return Variable(
                name=f"__{self.name}[{args}]",
                addr=Hex(self.addr + of * self.t_size),
                t_size=self.t_size,
            )

    def check_compatibility(self, value):
        def check_shapes(val, shapes):
            if shapes:
                if len(val != shapes[0]):
                    raise ValueError(f"Wrong shape for Array {self.name}")
                for i in range(shapes[0]):
                    check_shapes(val[i], shapes[1:])

    def zip(self, value):
        def get_multi_idx(li, idx):
            res = li
            for i in idx:
                res = res[i]
            return res

        return (
            (self[idx], get_multi_idx(value, idx))
            for idx in self.iter_index()
        )
        

class MemoryAllocator:
    """Simple One-Time MemoryAllocator"""
    def __init__(self, offset=Hex(0), offset_max=Hex(0), size_max=4):
        self.ap = offset
        self.variables = {}
        self.offset_max = offset_max  # EVM max
        self.size_max = size_max  # EVM max

    def __contains__(self, key: [Variable, str]):
        if isinstance(key, Variable):
            return True  # allocated
        return key in self.variables

    def __getitem__(self, key: str):
        return self.variables[key]

    def alloc(self, name: str, t_size: int=32, shape: int=None):
        if name in self.variables:
            raise MemoryError(f"Variable {name} is already allocated")
        if shape:
            self.variables[name] = Array(name, self.ap, t_size, shape)
            self.ap += self.variables[name].m_size
        else:
            self.variables[name] = Variable(name, self.ap, t_size)
            self.ap += t_size
        return self.variables[name]

    def slot(self, var):  # EVM max
        return Hex((var.addr - self.offset_max) // (8*self.size_max))
