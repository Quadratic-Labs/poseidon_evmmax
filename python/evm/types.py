from typing import Union


class Hex():
    def __init__(self, value: Union[int, str]):
        if isinstance(value, Hex):
            self._value = value._value
        elif isinstance(value, str):
            self._value = int(value, base=16)
        else:
            self._value = value

    def __repr__(self):
        if self._value < 0:
            return ""
        t = hex(self._value)[2:]
        return "0" + t if len(t) % 2 else t

    def __add__(self, other):
        x = self._value
        if isinstance(other, Hex):
            x += other._value
        else:
            x += other
        return self.__class__(x)

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        x = self._value
        if isinstance(other, Hex):
            x -= other._value
        else:
            x -= other
        return self.__class__(x)

    def __rsub__(self, other):
        return self - other

    def __mul__(self, other):
        x = self._value
        if isinstance(other, Hex):
            x *= other._value
        else:
            x *= other
        return self.__class__(x)

    def __rmul__(self, other):
        return self + other

    def __floordiv__(self, other):
        x = self._value
        if isinstance(other, Hex):
            x = x // other._value
        else:
            x = x // other
        return self.__class__(x)

    def __rfloordiv__(self, other):
        return self // other

    def __lt__(self, other):
        return (
            self._value < other._value if isinstance(other, Hex) else
            self._value < other
        )

    def __le__(self, other):
        return (
            self._value <= other._value if isinstance(other, Hex) else
            self._value <=other
        )

    def __gt__(self, other):
        return (
            self._value > other._value if isinstance(other, Hex) else
            self._value > other
        )

    def __ge__(self, other):
        return (
            self._value >= other._value if isinstance(other, Hex) else
            self._value >= other
        )

    def __eq__(self, other):
        return (
            self._value == other._value if isinstance(other, Hex) else
            self._value == other
        )

    def __neq__(self, other):
        return (
            self._value != other._value if isinstance(other, Hex) else
            self._value != other
        )

    def to_hex(self, zfill=1):
        return str(self).zfill(zfill * 2)

    def to_le(self, zfill=1):
        res = []
        hs = self.to_hex(zfill=zfill)
        for a, b in zip(hs[::2], hs[1::2]):
            res.insert(0, a+b)
        return self.__class__("".join(res))

    def nbytes(self) -> int:
        return len(str(self)) // 2

