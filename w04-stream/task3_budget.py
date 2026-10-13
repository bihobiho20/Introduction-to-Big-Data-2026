#!/usr/bin/env python3
"""Task 3: Bloom filter with a fixed bit budget."""
import hashlib


class NaiveFilter:
    """One hash function, and the bits it was given."""

    def __init__(self, n_bits, seed=246):
        self.n_bits = n_bits
        self.seed = seed
        self.bits = bytearray(n_bits)

    def _index(self, item):
        d = hashlib.blake2b(str(item).encode(), digest_size=8,
                            key=str(self.seed).encode()).digest()
        return int.from_bytes(d, "big") % self.n_bits

    def add(self, item):
        self.bits[self._index(item)] = 1

    def __contains__(self, item):
        return bool(self.bits[self._index(item)])

    def memory_bits(self):
        return self.n_bits


class YourFilter:
    def __init__(self, n_bits, seed=246):
        if n_bits <= 0:
            raise ValueError("n_bits must be positive")
        self.n_bits = n_bits
        self.seed = seed
        # 10비트/항목 기준 최적 해시 수: 반올림(10 ln 2) = 7
        self.k = 7
        self.full_bytes, self.extra_bits = divmod(n_bits, 8)
        self.bits = bytearray(self.full_bytes)
        self.tail = 0

    def _has_bit(self, position):
        if position < self.full_bytes * 8:
            return bool(self.bits[position // 8] & (1 << (position % 8)))
        return bool(self.tail & (1 << (position - self.full_bytes * 8)))

    def _set_bit(self, position):
        if position < self.full_bytes * 8:
            self.bits[position // 8] |= 1 << (position % 8)
        else:
            self.tail |= 1 << (position - self.full_bytes * 8)

    def _positions(self, item):
        # 이중 해싱으로 k개 위치 생성
        digest = hashlib.blake2b(
            str(item).encode(), digest_size=16,
            key=str(self.seed).encode()).digest()
        first = int.from_bytes(digest[:8], "big")
        step = int.from_bytes(digest[8:], "big") | 1
        for i in range(self.k):
            yield (first + i * step) % self.n_bits

    def add(self, item):
        for position in self._positions(item):
            self._set_bit(position)

    def __contains__(self, item):
        return all(self._has_bit(position) for position in self._positions(item))

    def memory_bits(self):
        return self.full_bytes * 8 + self.extra_bits
