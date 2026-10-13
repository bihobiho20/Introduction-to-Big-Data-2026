#!/usr/bin/env python3
"""Task 1: Bloom filter, Flajolet-Martin, and reservoir sampling."""
import argparse, hashlib, math, random, statistics


class BloomFilter:
    def __init__(self, m, k, seed=246):
        if m <= 0 or k <= 0:
            raise ValueError("m and k must be positive")
        self.m = m
        self.k = k
        self.seed = seed
        self.bits = bytearray((m + 7) // 8)

    def _positions(self, item):
        # 이중 해싱으로 k개 위치 생성
        value = str(item).encode("utf-8")
        digest = hashlib.blake2b(value, digest_size=16,
                                 key=str(self.seed).encode()).digest()
        first = int.from_bytes(digest[:8], "big")
        step = int.from_bytes(digest[8:], "big") | 1
        for i in range(self.k):
            yield (first + i * step) % self.m

    def add(self, item):
        for position in self._positions(item):
            self.bits[position // 8] |= 1 << (position % 8)

    def __contains__(self, item):
        return all(self.bits[position // 8] & (1 << (position % 8))
                   for position in self._positions(item))

    def expected_fp_rate(self, n_inserted):
        """삽입 수에 따른 이론 오탐률."""
        return (1 - math.exp(-self.k * n_inserted / self.m)) ** self.k


def flajolet_martin(stream, n_hashes=8, seed=246):
    """한 번 순회해 서로 다른 항목 수를 추정한다."""
    if n_hashes <= 0:
        raise ValueError("n_hashes must be positive")

    # 해시별 최대 후행 0 개수 기록
    maxima = [0] * n_hashes
    saw_item = False
    for item in stream:
        saw_item = True
        value = str(item).encode("utf-8")
        for start in range(0, n_hashes, 8):
            digest = hashlib.blake2b(
                value, digest_size=64,
                key=f"{seed}:{start // 8}".encode()).digest()
            for offset in range(min(8, n_hashes - start)):
                # 해시별 최대 후행 0 갱신
                number = int.from_bytes(digest[offset * 8:offset * 8 + 8], "big")
                trailing = 64 if number == 0 else (number & -number).bit_length() - 1
                index = start + offset
                if trailing > maxima[index]:
                    maxima[index] = trailing

    if not saw_item:
        return 0.0

    # 해시별 추정치의 중앙값으로 극단값 영향을 줄임
    return math.log(2) * statistics.median(2.0 ** r for r in maxima)


def reservoir_sample(stream, k, seed=246):
    """스트림에서 항목 k개를 균등하게 뽑는다."""
    if k < 0:
        raise ValueError("k must be non-negative")
    rng = random.Random(seed)
    reservoir = []
    for seen, item in enumerate(stream):
        if seen < k:
            reservoir.append(item)
        elif k:
            # 지금까지 본 항목 수로 교체 여부 결정
            index = rng.randrange(seen + 1)
            if index < k:
                reservoir[index] = item
    return reservoir


# ------------------------------------------------------------------- harness
def verify():
    fails = 0
    rng = random.Random(246)

    def check(label, ok, detail=""):
        nonlocal fails
        print(f"  {'ok  ' if ok else 'FAIL'}  {label:<46} {detail}")
        fails += not ok

    # --- Bloom: no false negatives, ever
    try:
        bf = BloomFilter(m=8192, k=5)
    except NotImplementedError:
        print("  BloomFilter is still a stub"); return 1
    inserted = [f"item-{i}" for i in range(800)]
    for x in inserted:
        bf.add(x)
    check("no false negatives", all(x in bf for x in inserted))

    absent = [f"other-{i}" for i in range(20_000)]
    fp = sum(1 for x in absent if x in bf) / len(absent)
    predicted = bf.expected_fp_rate(len(inserted))
    close = abs(fp - predicted) < max(0.02, predicted * 0.5)
    check("measured false-positive rate matches theory", close,
          f"measured {fp:.3%}, predicted {predicted:.3%}")

    # --- Flajolet-Martin: a factor of two is what this method gives you
    try:
        distinct = 20_000
        stream = [f"k{rng.randrange(distinct)}" for _ in range(120_000)]
        est = flajolet_martin(stream)
    except NotImplementedError:
        print("  flajolet_martin is still a stub"); return 1
    true_distinct = len(set(stream))
    ratio = est / true_distinct
    check("distinct estimate within a factor of 2", 0.5 <= ratio <= 2.0,
          f"estimated {est:,.0f}, true {true_distinct:,} ({ratio:.2f}x)")

    # --- Reservoir: uniform over many trials
    try:
        counts = [0] * 20
        trials = 4000
        for t in range(trials):
            s = reservoir_sample(range(20), 5, seed=t)
            for i in s:
                counts[i] += 1
    except NotImplementedError:
        print("  reservoir_sample is still a stub"); return 1
    expected = trials * 5 / 20
    spread = (max(counts) - min(counts)) / expected
    check("reservoir is uniform across items", spread < 0.15,
          f"spread {spread:.1%} around {expected:.0f}")

    print(f"\n  {'all ok' if not fails else str(fails) + ' failed'}")
    return 1 if fails else 0


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--verify", action="store_true")
    a = p.parse_args()
    raise SystemExit(verify() if a.verify else p.print_help())
