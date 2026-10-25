#!/usr/bin/env python3
"""Week 6 · Task 3 — Make pass two fit.

Textbook §6.3 (PCY), §6.3.2 - §6.3.4.

`PlainApriori` does what Task 1 asked: use pass one to drop infrequent items,
then count every pair of surviving items. That is already much better than
counting all pairs. It is still not enough, because the surviving items are the
common ones, and the common ones appear together constantly.

The harness measures **the peak number of pair counters you held**, because
that is the thing that decides whether the algorithm runs at all. §6.3 is about
spending pass one's spare memory to shrink it.

    python3 bench.py
    python3 bench.py --yours

Correctness first: you must find exactly the same frequent pairs. Finding fewer
is not an optimisation.
"""
from collections import Counter
from array import array
from itertools import combinations


class PlainApriori:
    """Pass one drops infrequent items. Pass two counts every surviving pair."""

    def __init__(self, support):
        self.support = support
        self.peak_counters = 0

    def run(self, baskets):
        counts = Counter()
        for basket in baskets:
            counts.update(basket)
        frequent = {i for i, c in counts.items() if c >= self.support}

        pair_counts = Counter()
        for basket in baskets:
            items = sorted(basket & frequent)
            for pair in combinations(items, 2):
                pair_counts[pair] += 1
            self.peak_counters = max(self.peak_counters, len(pair_counts))

        return {frozenset(p): c for p, c in pair_counts.items()
                if c >= self.support}


class YourAlgorithm:
    """Your frequent-pair finder.

        __init__(support)
        run(baskets) -> {frozenset({a, b}): count}
        .peak_counters -> the most pair counters you ever held at once

    Same pairs as the baseline. Fewer counters.

    Pass one only needs one integer per item, and there are not many items. The
    rest of your memory is sitting idle while you do it. §6.3 spends it: hash
    every pair you see in pass one into a fixed array of buckets, and count the
    buckets rather than the pairs.

    A bucket whose total is below the support threshold cannot contain a
    frequent pair. In pass two you skip every pair landing in such a bucket -
    and the bucket array collapses to a bitmap, one bit each, before you need
    the memory for counters.

    Two things to be careful of:

      * a bucket being frequent does not make its pairs frequent. It is a
        filter, not an answer
      * `peak_counters` is on your honour. Count the pair counters you hold at
        the same time. The bitmap is not a pair counter, but if you keep the
        full bucket counts alive into pass two, that is not free either -
        observation.md asks about it
    """

    def __init__(self, support, n_buckets=1 << 21):
        if not isinstance(support, int) or not 1 <= support <= 0xffffffff:
            raise ValueError("support must be a positive 32-bit integer")
        if not isinstance(n_buckets, int) or n_buckets < 1:
            raise ValueError("n_buckets must be a positive integer")
        self.support = support
        self.n_buckets = n_buckets
        self.peak_counters = 0
        self.bucket_bytes = 0
        self.bitmap_bytes = 0
        self.frequent_buckets = 0

    def run(self, baskets):
        self.peak_counters = 0
        counts = Counter()
        item_ids = {}
        buckets = array("I", [0]) * self.n_buckets
        self.bucket_bytes = len(buckets) * buckets.itemsize

        # Dense integer IDs give each unordered pair the same hash in both
        # passes, including for items whose types cannot be sorted together.
        for basket in baskets:
            items = set(basket)
            counts.update(items)
            for item in items:
                if item not in item_ids:
                    item_ids[item] = len(item_ids)
            ids = sorted(item_ids[item] for item in items)
            for pair in combinations(ids, 2):
                bucket = hash(pair) % self.n_buckets
                # Only the comparison with support matters; saturation avoids
                # overflow without changing which buckets become frequent.
                if buckets[bucket] < self.support:
                    buckets[bucket] += 1

        bitmap = bytearray((self.n_buckets + 7) // 8)
        self.frequent_buckets = 0
        for bucket, count in enumerate(buckets):
            if count >= self.support:
                bitmap[bucket >> 3] |= 1 << (bucket & 7)
                self.frequent_buckets += 1
        self.bitmap_bytes = len(bitmap)
        # The transition briefly holds both arrays; account for it in the
        # report, then release the integer counters before pass two.
        del buckets
        frequent = {item_ids[item] for item, count in counts.items()
                    if count >= self.support}
        del counts

        pair_counts = Counter()
        for basket in baskets:
            ids = sorted(item_ids[item] for item in set(basket)
                         if item_ids[item] in frequent)
            for pair in combinations(ids, 2):
                bucket = hash(pair) % self.n_buckets
                if bitmap[bucket >> 3] & (1 << (bucket & 7)):
                    pair_counts[pair] += 1
        # Pair counters only grow, so their final size is their peak.
        self.peak_counters = len(pair_counts)
        del bitmap
        items = list(item_ids)
        return {frozenset((items[a], items[b])): count
                for (a, b), count in pair_counts.items()
                if count >= self.support}
