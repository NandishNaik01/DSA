# Arrays — End-to-End Study Plan

**Target:** solve array mediums solo in 25–30 min and narrate the approach.
**Duration:** 4 weeks (28 days). Weekdays 2 h, weekends 3 h → ~68 h total.
**Language:** Python 3.

---

## 1. Concepts (Week 1, Days 1–3)

### 1.1 Memory layout
- A Python `list` is a contiguous block of **pointers** (8 bytes each) to heap objects. Not the values themselves.
- Index access = base + 8·i → O(1).
- Cache-friendly when iterating in order; random access is still O(1) but slower in practice.
- `array.array` / NumPy store raw values contiguously — use when asked about "real" arrays.

### 1.2 Dynamic array internals
- Backing buffer has `capacity ≥ len`. Append writes at `len`, increments `len`.
- When full: allocate a bigger buffer (CPython growth ≈ 1.125×, textbook 2×), copy, free old one.
- Shrinks when `len < capacity/2` (CPython) to avoid thrashing.

### 1.3 Amortized analysis
- Doubling: resizes at sizes 1,2,4,…,n → total copies < 2n → **O(1) amortized** per append.
- Say it this way in interviews: "Any single append can be O(n), but n appends cost O(n) total, so each is O(1) amortized."
- Aggregate method is enough; mention potential method only if asked.

### 1.4 Cost table — Python list

| Operation | Time | Note |
|---|---|---|
| `a[i]`, `a[i] = x` | O(1) | |
| `len(a)` | O(1) | stored |
| `a.append(x)` | O(1) amortized | |
| `a.pop()` | O(1) | |
| `a.pop(0)`, `a.insert(0, x)` | O(n) | shifts everything → use `deque` |
| `a.insert(i, x)`, `a.pop(i)`, `del a[i]` | O(n − i) | |
| `a.remove(x)` | O(n) | search + shift |
| `x in a` | O(n) | use `set` for O(1) |
| `a.index(x)` | O(n) | |
| `a[i:j]` | O(j − i) | **copies** |
| `a + b` | O(len a + len b) | new list |
| `a.extend(b)`, `a += b` | O(len b) | in place |
| `a * k` | O(n·k) | shallow copies |
| `a.sort()`, `sorted(a)` | O(n log n) | Timsort, stable |
| `a.reverse()` | O(n) | in place |
| `reversed(a)` | O(1) | iterator |
| `min/max/sum` | O(n) | |
| `a.count(x)` | O(n) | |
| `a.copy()`, `a[:]`, `list(a)` | O(n) | shallow |
| `enumerate`, `zip` | O(1) setup | lazy |

### 1.5 Python gotchas

```python
# 1. Slicing copies — O(k) time and memory, breaks "in-place" requirements
sub = a[1:]           # new list; recursion with a[1:] is O(n^2) total

# 2. Shared-row 2D bug
grid = [[0] * m] * n          # WRONG: n references to ONE row
grid[0][0] = 1                # every row changes
grid = [[0] * m for _ in range(n)]   # correct

# 3. Aliasing
b = a                 # same object
b.append(1)           # a changed too
b = a[:]              # shallow copy — nested objects still shared
import copy; b = copy.deepcopy(a)

# 4. Deleting while iterating
for x in a:
    if bad(x): a.remove(x)     # skips elements
a = [x for x in a if not bad(x)]         # correct
for i in range(len(a) - 1, -1, -1):      # or iterate backward
    if bad(a[i]): a.pop(i)

# 5. Default mutable args
def f(acc=[]): ...             # shared across calls → use None

# 6. Negative indices & modulo
a[-1]                          # last; a[(i - k) % n] handles negative shifts

# 7. Integer division / floor
mid = (lo + hi) // 2           # no overflow in Python, but say "lo + (hi-lo)//2" for other langs

# 8. sort key stability
a.sort(key=lambda p: p[0])     # stable: equal keys keep input order
```

### 1.6 From-scratch exercise — Dynamic Array
Implement without using `list` methods for storage (use a fixed-size `[None]*cap` as the raw buffer).

```python
class DynamicArray:
    def __init__(self, cap=1):
        self._cap = cap        # how many boxes we start with
        self._n = 0            # how many boxes are actually filled
        self._buf = [None] * cap   # the row of boxes, all empty for now

    def __len__(self):
        return self._n          # lets len(d) report filled boxes, not total boxes

    def __getitem__(self, i):
        # d[i] -> only allowed if i points at a filled box
        if not 0 <= i < self._n: raise IndexError
        return self._buf[i]

    def __setitem__(self, i, v):
        # d[i] = v -> only allowed if i points at a filled box
        if not 0 <= i < self._n: raise IndexError
        self._buf[i] = v

    def _resize(self, cap):
        # make a new row of `cap` boxes, copy every real item over, swap it in
        new = [None] * cap
        for i in range(self._n): new[i] = self._buf[i]
        self._buf, self._cap = new, cap

    def append(self, v):
        # add v as the new last item
        if self._n == self._cap: self._resize(2 * self._cap)  # no empty box left -> double the boxes
        self._buf[self._n] = v     # put v in the next free box
        self._n += 1               # one more box is now filled

    def pop(self):
        # remove and return the last item
        if self._n == 0: raise IndexError
        self._n -= 1                           # one less box filled (now points at the last real item)
        v = self._buf[self._n]; self._buf[self._n] = None   # save it, then empty that box
        if 0 < self._n <= self._cap // 4:      # using 1/4 or less of our boxes
            self._resize(self._cap // 2)       # -> shrink to half as many boxes
        return v

    def insert(self, i, v):
        # put v at position i, pushing later items one box to the right
        if not 0 <= i <= self._n: raise IndexError
        if self._n == self._cap: self._resize(2 * self._cap)   # no room -> double the boxes
        # shift items right, starting from the end, moving backward
        # (backward so we never overwrite an item before copying it)
        for j in range(self._n, i, -1): self._buf[j] = self._buf[j - 1]
        self._buf[i] = v   # drop v into the now-empty gap
        self._n += 1        # one more box filled

    def remove_at(self, i):
        # take out the item at position i, pulling later items one box left
        if not 0 <= i < self._n: raise IndexError
        v = self._buf[i]   # remember what we're removing
        # shift items left, starting from i, moving forward
        # (forward so we never overwrite an item before copying it)
        for j in range(i, self._n - 1): self._buf[j] = self._buf[j + 1]
        self._n -= 1; self._buf[self._n] = None   # one less box filled, clear the leftover box
        return v
```

**Calling it — a worked example:**
```python
d = DynamicArray(cap=4)      # _buf = [_, _, _, _]   (4 empty boxes)

d.append(10)                 # _buf = [10, _, _, _]        _n=1
d.append(20)                 # _buf = [10, 20, _, _]       _n=2
d.append(30)                 # _buf = [10, 20, 30, _]      _n=3
d.append(40)                 # _buf = [10, 20, 30, 40]     _n=4  (now full)

d.append(50)                 # full -> doubles to 8 boxes first
                              # _buf = [10, 20, 30, 40, 50, _, _, _]   _n=5, _cap=8

d.insert(1, 99)               # shift 50,40,30,20 right one box, then place 99 at index 1
                              # _buf = [10, 99, 20, 30, 40, 50, _, _]   _n=6

print(d[1])                   # 99
print(len(d))                 # 6

removed = d.remove_at(2)      # removes the 20, shifts everything after it left
                              # _buf = [10, 99, 30, 40, 50, _, _, _]   _n=5
print(removed)                # 20

last = d.pop()                 # removes and returns the last item, 50
                              # _buf = [10, 99, 30, 40, _, _, _, _]   _n=4
print(last)                   # 50
```

**Checks:** write tests for append 1000 → len, pop to empty, insert at 0/mid/end, resize counts. Then explain amortized cost out loud.

---

## 2. Pattern List (learning order)

### P1. Prefix Sums
**Recognize:** "sum of subarray [i, j]" asked repeatedly; "subarray sum equals k"; range queries with no updates.
```python
pre = [0] * (n + 1)
for i, x in enumerate(nums): pre[i + 1] = pre[i] + x
# sum(nums[i:j+1]) == pre[j+1] - pre[i]

# count subarrays with sum == k  (prefix + hashmap)
from collections import defaultdict
seen = defaultdict(int); seen[0] = 1; cur = cnt = 0
for x in nums:
    cur += x
    cnt += seen[cur - k]
    seen[cur] += 1
```
**Complexity:** O(n) build, O(1) query. Space O(n).
**Mistakes:** off-by-one on `pre[j+1] - pre[i]`; forgetting `seen[0] = 1`; using prefix sums when updates exist (needs Fenwick/segment tree).

### P2. In-place Write Pointer (read/write)
**Recognize:** "remove", "move zeroes", "compact", "do it in place with O(1) extra space", return new length.
```python
w = 0
for r in range(len(nums)):
    if keep(nums[r]):
        nums[w] = nums[r]
        w += 1
return w            # nums[:w] is the answer
```
**Complexity:** O(n) / O(1).
**Mistakes:** swapping when a copy suffices (or vice versa when order of tail matters); forgetting to fill the tail (e.g., zeros).

### P3. Two Pointers
**Recognize:** sorted input; pair/triplet with target; "palindrome"; squares of sorted array; container with most water (monotone decision).
```python
# opposite ends
l, r = 0, len(a) - 1
while l < r:
    s = a[l] + a[r]
    if s == target: return [l, r]
    if s < target: l += 1
    else: r -= 1

# 3Sum skeleton
a.sort()
for i in range(n - 2):
    if i and a[i] == a[i - 1]: continue
    l, r = i + 1, n - 1
    while l < r:
        s = a[i] + a[l] + a[r]
        if s < 0: l += 1
        elif s > 0: r -= 1
        else:
            out.append([a[i], a[l], a[r]])
            l += 1; r -= 1
            while l < r and a[l] == a[l - 1]: l += 1
```
**Complexity:** O(n) (O(n²) for 3Sum) / O(1).
**Mistakes:** applying to unsorted data; `while l <= r` vs `< r`; not skipping duplicates; moving the wrong pointer (must justify why the discarded option can't be better).

### P4. Sliding Window
**Recognize:** contiguous subarray/substring; "longest/shortest/max sum with constraint"; fixed size k.
```python
# fixed k
win = sum(a[:k]); best = win
for r in range(k, n):
    win += a[r] - a[r - k]; best = max(best, win)

# variable (longest valid)
from collections import defaultdict
cnt = defaultdict(int); l = 0; best = 0
for r, x in enumerate(a):
    cnt[x] += 1
    while invalid(cnt):          # shrink
        cnt[a[l]] -= 1; l += 1
    best = max(best, r - l + 1)

# variable (shortest valid)  → update best INSIDE the while
```
**Complexity:** O(n) / O(k) or O(alphabet).
**Mistakes:** using it with negative numbers for sum constraints (monotonicity breaks → use prefix+hash or deque); updating `best` at the wrong place; forgetting to remove `a[l]` from state before `l += 1`.

### P5. Kadane's (max subarray)
**Recognize:** max/min sum contiguous subarray; "best time to buy/sell" (diff array + Kadane); circular variant.
```python
cur = best = a[0]
for x in a[1:]:
    cur = max(x, cur + x)
    best = max(best, cur)
# circular: max(best, total - min_subarray) unless all negative
```
**Complexity:** O(n) / O(1).
**Mistakes:** initializing with 0 (fails all-negative); forgetting the all-negative case in circular; not tracking indices when asked for the subarray.

### P6. Sorting-based
**Recognize:** answer depends on relative order (intervals, meeting rooms, k-th largest, dedupe, "minimum difference"); you can afford O(n log n).
```python
a.sort()                        # or sorted(a, key=..., reverse=True)
for i in range(1, n):
    best = min(best, a[i] - a[i - 1])

import heapq
heapq.nlargest(k, a)            # O(n log k)
```
**Complexity:** O(n log n) / O(1)–O(n).
**Mistakes:** sorting when a hash or counting sort (bounded values) gives O(n); losing original indices (sort `(val, idx)` pairs); mutating input when forbidden.

### P7. Hashing on Arrays
**Recognize:** "exists / count / first duplicate / two-sum unsorted / longest consecutive"; need O(1) lookups.
```python
seen = {}
for i, x in enumerate(a):
    if target - x in seen: return [seen[target - x], i]
    seen[x] = i

# longest consecutive sequence
s = set(a); best = 0
for x in s:
    if x - 1 not in s:          # only start from sequence heads
        y = x
        while y + 1 in s: y += 1
        best = max(best, y - x + 1)
```
**Complexity:** O(n) / O(n).
**Mistakes:** inserting before checking (self-match in two-sum); forgetting the "start of run" check → O(n²); hashing unhashable lists (use tuples).

### P8. Difference Array
**Recognize:** many range **updates** (+v on [l, r]) then read final array; "booking", "car pooling", "flight bookings".
```python
diff = [0] * (n + 1)
for l, r, v in updates:
    diff[l] += v
    diff[r + 1] -= v
res = []; cur = 0
for i in range(n):
    cur += diff[i]; res.append(cur)
```
**Complexity:** O(n + q) / O(n).
**Mistakes:** forgetting `r + 1` slot (size n+1); mixing inclusive/exclusive bounds; using it when interleaved queries exist (needs BIT).

### P9. Matrix / 2D Traversal
**Recognize:** grid input; spiral, diagonal, set-zeroes, search in sorted matrix, rotate.
```python
rows, cols = len(g), len(g[0])
DIRS = [(1,0),(-1,0),(0,1),(0,-1)]
for dr, dc in DIRS:
    nr, nc = r + dr, c + dc
    if 0 <= nr < rows and 0 <= nc < cols: ...

# spiral
top, bot, left, right = 0, rows - 1, 0, cols - 1
while top <= bot and left <= right:
    for c in range(left, right + 1): out.append(g[top][c])
    top += 1
    for r in range(top, bot + 1): out.append(g[r][right])
    right -= 1
    if top <= bot:
        for c in range(right, left - 1, -1): out.append(g[bot][c])
        bot -= 1
    if left <= right:
        for r in range(bot, top - 1, -1): out.append(g[r][left])
        left += 1

# staircase search in row- & column-sorted matrix: start top-right
r, c = 0, cols - 1
while r < rows and c >= 0:
    if g[r][c] == t: return True
    if g[r][c] > t: c -= 1
    else: r += 1

# 2D prefix
P[i+1][j+1] = g[i][j] + P[i][j+1] + P[i+1][j] - P[i][j]
```
**Complexity:** O(rows·cols) / O(1)–O(rows·cols).
**Mistakes:** shared-row bug; missing the `if top <= bot` guards in spiral (duplicates on 1-row/1-col leftovers); confusing `g[r][c]` with `g[c][r]`.

### P10. Rotation / Reversal Tricks
**Recognize:** "rotate by k", "rotate matrix 90°", "reverse words", in-place with O(1) space.
```python
def rev(a, i, j):
    while i < j: a[i], a[j] = a[j], a[i]; i += 1; j -= 1

k %= n
rev(a, 0, n - 1); rev(a, 0, k - 1); rev(a, k, n - 1)   # rotate right by k

# rotate matrix 90° clockwise in place: transpose, then reverse each row
for i in range(n):
    for j in range(i + 1, n): m[i][j], m[j][i] = m[j][i], m[i][j]
for row in m: row.reverse()
```
**Complexity:** O(n) / O(1).
**Mistakes:** forgetting `k %= n`; transposing the full square (swaps back); left vs right rotation direction.

### P11. Cyclic Sort
**Recognize:** values in range `1..n` (or `0..n-1`), "find missing / duplicate / first missing positive" with O(1) space.
```python
i = 0
while i < n:
    j = a[i] - 1                       # correct index for value a[i]
    if 0 <= j < n and a[i] != a[j]:
        a[i], a[j] = a[j], a[i]
    else:
        i += 1
for i in range(n):
    if a[i] != i + 1: return i + 1     # first missing positive
return n + 1
```
**Complexity:** O(n) / O(1) (each swap places one element permanently).
**Mistakes:** infinite loop on duplicates (must compare `a[i] != a[j]`, not `a[i] != i+1`); off-by-one for 0-based vs 1-based values; incrementing `i` after a swap.

### P12. Merge Intervals
**Recognize:** list of `[start, end]`; overlap, merge, insert, min rooms, free time.
```python
iv.sort(key=lambda x: x[0])
out = [iv[0]]
for s, e in iv[1:]:
    if s <= out[-1][1]: out[-1][1] = max(out[-1][1], e)
    else: out.append([s, e])

# min meeting rooms: sweep line
import heapq
ends = []
for s, e in sorted(iv):
    if ends and ends[0] <= s: heapq.heapreplace(ends, e)
    else: heapq.heappush(ends, e)
return len(ends)
```
**Complexity:** O(n log n) / O(n).
**Mistakes:** forgetting to sort; `<` vs `<=` for touching intervals (read the problem); mutating input tuples.

### P13. Dutch National Flag (3-way partition)
**Recognize:** sort array of 3 distinct values in one pass; partition around pivot; "sort colors".
```python
lo, mid, hi = 0, 0, n - 1
while mid <= hi:
    if a[mid] == 0: a[lo], a[mid] = a[mid], a[lo]; lo += 1; mid += 1
    elif a[mid] == 1: mid += 1
    else: a[mid], a[hi] = a[hi], a[mid]; hi -= 1   # do NOT advance mid
```
**Complexity:** O(n) / O(1).
**Mistakes:** advancing `mid` after swapping with `hi` (the swapped-in value is unexamined); `while mid < hi` (misses last element).

### P14. Left/Right Product Passes
**Recognize:** "answer at i depends on everything to the left AND right" — product except self, trapping rain water, candy, max left/right.
```python
res = [1] * n
run = 1
for i in range(n): res[i] = run; run *= a[i]           # prefix products
run = 1
for i in range(n - 1, -1, -1): res[i] *= run; run *= a[i]   # suffix in place

# trapping rain water (two-pointer variant of the same idea)
l, r, lm, rm, water = 0, n - 1, 0, 0, 0
while l < r:
    if a[l] < a[r]:
        lm = max(lm, a[l]); water += lm - a[l]; l += 1
    else:
        rm = max(rm, a[r]); water += rm - a[r]; r -= 1
```
**Complexity:** O(n) / O(1) extra (output excluded).
**Mistakes:** using division (fails on zeros, usually forbidden); allocating two extra arrays when one pass can be folded into the output.

### Bonus: Monotonic Stack (frequently appears "as an array problem")
**Recognize:** next greater/smaller element, daily temperatures, largest rectangle in histogram.
```python
st = []; res = [-1] * n
for i, x in enumerate(a):
    while st and a[st[-1]] < x:
        res[st.pop()] = x
    st.append(i)
```

---

## 3. Problem Set (46 problems)

Legend: **E/M/H** difficulty · ★ = must-redo (spaced repetition) · 🎭 = pattern disguise.

| # | LC | Problem | Diff | Pattern | Why this problem |
|---|---|---|---|---|---|
| 1 | 303 | Range Sum Query – Immutable | E | Prefix | Canonical prefix build + query. |
| 2 | 724 | Find Pivot Index | E | Prefix | Left vs right sum via total − prefix. |
| 3 | 560 | Subarray Sum Equals K ★ | M | Prefix + hash | Core prefix-hash counting; negatives allowed. |
| 4 | 523 | Continuous Subarray Sum | M | Prefix + hash | Prefix mod k; store first index. |
| 5 | 974 | Subarray Sums Divisible by K | M | Prefix + hash | Negative modulo handling in Python. |
| 6 | 27 | Remove Element | E | Write ptr | Simplest read/write pointer. |
| 7 | 283 | Move Zeroes | E | Write ptr | Write pointer + fill tail. |
| 8 | 80 | Remove Duplicates from Sorted Array II ★ | M | Write ptr | Generalizes to "keep at most k". |
| 9 | 167 | Two Sum II | E | Two ptr | Why pointer movement is safe on sorted input. |
| 10 | 977 | Squares of a Sorted Array | E | Two ptr | Fill from the back. |
| 11 | 15 | 3Sum ★ | M | Two ptr | Dedup logic; most-asked two-pointer medium. |
| 12 | 11 | Container With Most Water ★ | M | Two ptr | Greedy pointer discard argument. |
| 13 | 16 | 3Sum Closest | M | Two ptr | Track best delta instead of equality. |
| 14 | 643 | Max Average Subarray I | E | Window (fixed) | Fixed-k template. |
| 15 | 209 | Minimum Size Subarray Sum ★ | M | Window (var) | Shortest-valid variant; positives only. |
| 16 | 904 | Fruit Into Baskets | M | Window (var) | Longest with ≤2 distinct. |
| 17 | 1004 | Max Consecutive Ones III | M | Window (var) | Budget-based shrink condition. |
| 18 | 1658 | Min Operations to Reduce X to Zero 🎭 | M | Window | Disguised: find longest middle window with sum = total − x. |
| 19 | 53 | Maximum Subarray ★ | M | Kadane | The pattern itself. |
| 20 | 121 | Best Time to Buy and Sell Stock 🎭 | E | Kadane / running min | Disguised Kadane on day-to-day diffs. |
| 21 | 918 | Maximum Sum Circular Subarray | M | Kadane | min-subarray trick + all-negative edge. |
| 22 | 152 | Maximum Product Subarray | M | Kadane variant | Track min and max; sign flips. |
| 23 | 88 | Merge Sorted Array | E | Sorting / two ptr | Fill from the back in place. |
| 24 | 179 | Largest Number | M | Sorting (custom key) | Comparator via `cmp_to_key`; "0" edge case. |
| 25 | 215 | Kth Largest Element | M | Sorting / heap / quickselect | Discuss O(n log n) vs O(n log k) vs O(n) avg. |
| 26 | 1 | Two Sum | E | Hash | Check-before-insert. |
| 27 | 217 | Contains Duplicate | E | Hash | Set vs sort trade-off. |
| 28 | 128 | Longest Consecutive Sequence ★ | M | Hash | "Start of run" O(n) argument. |
| 29 | 49 | Group Anagrams | M | Hash | Canonical key (sorted tuple / count tuple). |
| 30 | 1094 | Car Pooling | M | Difference array | Bounded coordinate range; sweep. |
| 31 | 1109 | Corporate Flight Bookings | M | Difference array | Direct template application. |
| 32 | 54 | Spiral Matrix | M | Matrix | Boundary guards. |
| 33 | 73 | Set Matrix Zeroes ★ | M | Matrix | O(1) space using first row/col as markers. |
| 34 | 240 | Search a 2D Matrix II | M | Matrix | Staircase from top-right. |
| 35 | 304 | Range Sum Query 2D | M | Matrix + prefix | Inclusion–exclusion. |
| 36 | 189 | Rotate Array | M | Reversal | Triple reverse; `k %= n`. |
| 37 | 48 | Rotate Image ★ | M | Reversal | Transpose + reverse rows. |
| 38 | 268 | Missing Number | E | Cyclic sort / XOR / sum | Three solutions; compare. |
| 39 | 287 | Find the Duplicate Number 🎭 | M | Cyclic sort / Floyd | Disguised linked-list cycle on index graph. |
| 40 | 41 | First Missing Positive ★ | H | Cyclic sort | The cyclic-sort hard; O(1) space. |
| 41 | 56 | Merge Intervals | M | Intervals | Sort + merge template. |
| 42 | 57 | Insert Interval | M | Intervals | Three-phase scan without sorting. |
| 43 | 253 | Meeting Rooms II | M | Intervals + heap | Sweep line; min-heap of end times. |
| 44 | 75 | Sort Colors ★ | M | Dutch flag | The pattern itself; `mid` pointer rule. |
| 45 | 238 | Product of Array Except Self | M | L/R passes | Fold suffix pass into output. |
| 46 | 42 | Trapping Rain Water 🎭 | H | L/R passes / two ptr | Disguised L/R max; two-pointer refinement. |
| 47 | 84 | Largest Rectangle in Histogram | H | Monotonic stack | Hard stack-on-array; sentinel trick. |
| 48 | 4 | Median of Two Sorted Arrays | H | Binary search on partition | Classic hard; practice explaining invariants. |

**Mix:** 12 Easy (25%) · 31 Medium (65%) · 5 Hard (10%).
**Must-redo (10):** 560, 80, 15, 11, 209, 53, 128, 73, 48, 41 (+ 75 as 11th if time).
**Disguises (4):** 1658, 121, 287, 42.

---

## 4. Day-by-Day Schedule (4 weeks)

Blocks: **L** = learn, **P** = problems, **R** = review (problem log + flashcards + redo). Minutes in parentheses.

### Week 1 — Foundations + Prefix / Write-pointer / Two-pointer

| Day | Type | Learn | Problems | Review |
|---|---|---|---|---|
| 1 Mon | 2h | §1.1–1.3 memory, dynamic array, amortized (60) | — | Write amortized explanation aloud, 3×; set up notes system (60) |
| 2 Tue | 2h | §1.4 cost table, §1.5 gotchas (40) | Build `DynamicArray` + tests (70) | Log (10) |
| 3 Wed | 2h | P1 Prefix sums (30) | 303, 724, 560 (75) | Log + flashcards (15) |
| 4 Thu | 2h | P2 Write pointer (20) | 523, 27, 283, 80 (85) | Log (15) |
| 5 Fri | 2h | P3 Two pointers (30) | 167, 977, 15 (75) | Redo 560 blind (15) |
| 6 Sat | 3h | — | 974, 11, 16 (90) | **Mock #1** (2 mediums, 60 min, timed, narrated) + debrief (30); log (30) |
| 7 Sun | 3h | P4 Sliding window (40) | 643, 209, 904 (90) | Redo 15, 80 blind (40); weekly checkpoint (10) |

### Week 2 — Window / Kadane / Sorting / Hashing

| Day | Type | Learn | Problems | Review |
|---|---|---|---|---|
| 8 Mon | 2h | Window edge cases, negatives (20) | 1004, 1658 (80) | Log (20) |
| 9 Tue | 2h | P5 Kadane + circular + product (30) | 53, 121, 918 (75) | Log (15) |
| 10 Wed | 2h | P6 Sorting-based, `cmp_to_key`, heap (30) | 152, 88, 179 (75) | Redo 209 (15) |
| 11 Thu | 2h | Quickselect walkthrough (25) | 215, 1, 217 (65) | Redo 11, 53 (30) |
| 12 Fri | 2h | P7 Hashing (25) | 128, 49 (65) | Log + flashcards (30) |
| 13 Sat | 3h | — | **Mock #2** (3 problems E/M/M, 75 min) + debrief (45) | Redo 560, 15, 128 (60) |
| 14 Sun | 3h | P8 Difference array (30) | 1094, 1109 (60) | Pattern notebook consolidation Weeks 1–2 (60); checkpoint (30) |

### Week 3 — Matrix / Rotation / Cyclic sort / Intervals

| Day | Type | Learn | Problems | Review |
|---|---|---|---|---|
| 15 Mon | 2h | P9 Matrix traversal (30) | 54, 73 (75) | Log (15) |
| 16 Tue | 2h | 2D prefix, staircase (20) | 240, 304 (70) | Redo 80, 73 (30) |
| 17 Wed | 2h | P10 Rotation/reversal (25) | 189, 48 (65) | Redo 53, 128 (30) |
| 18 Thu | 2h | P11 Cyclic sort (30) | 268, 287 (70) | Log (20) |
| 19 Fri | 2h | — | 41 (45) | Redo 48, 209 blind (45); flashcards (30) |
| 20 Sat | 3h | P12 Intervals (30) | 56, 57, 253 (90) | **Mock #3** (2 mediums + explain, 60 min) (60) |
| 21 Sun | 3h | P13 Dutch flag, P14 L/R passes (40) | 75, 238 (60) | Redo 41, 15, 560 (60); checkpoint (20) |

### Week 4 — Hards, disguises, consolidation, capstone

| Day | Type | Learn | Problems | Review |
|---|---|---|---|---|
| 22 Mon | 2h | Monotonic stack (30) | 42, 84 (75) | Log (15) |
| 23 Tue | 2h | Binary search on partition (30) | 4 (45) | Redo 11, 73, 48 (45) |
| 24 Wed | 2h | — | Random-pick 3 unseen array mediums from LC (90) | Log (30) |
| 25 Thu | 2h | — | Redo all 4 disguises blind: 1658, 121, 287, 42 (90) | Log (30) |
| 26 Fri | 2h | Cheat sheet from memory, then diff vs §9 (40) | Redo 209, 128, 41 (60) | Flashcards (20) |
| 27 Sat | 3h | — | **Capstone test**: 4 problems (1E, 2M, 1H), 100 min, out-loud narration recorded (100) | Debrief against rubric (50); log (30) |
| 28 Sun | 3h | — | Fix every capstone miss: resolve + 1 similar problem each (120) | Final checkpoint + plan next topic (60) |

**Total:** 28 days / 4 weeks. If a day slips, drop the "learn" block first, never the redo block.

---

## 5. Solving Routine (per problem, 30-min budget)

| Step | Time | What to do / say |
|---|---|---|
| 1. Restate | 2 min | Restate problem in one sentence. Confirm input ranges, duplicates, sorted?, in-place?, return type. Write 1 normal + 2 edge examples. |
| 2. Brute force | 3 min | State the obvious O(n²)/O(n³) and its complexity aloud. Never skip — it anchors the optimization. |
| 3. Pattern match | 3 min | Ask: contiguous? → window/prefix/Kadane. Sorted or sortable? → two-ptr/binary search. Values in 1..n? → cyclic sort. Range updates? → diff array. Depends on both sides? → L/R passes. Intervals? → sort+merge. |
| 4. Optimize | 5 min | Pick pattern, state target complexity, name the invariant (e.g., "window always valid", "a[:w] is the answer so far"). |
| 5. Code | 10 min | Write template first, then fill. Name variables `l, r, w, pre, cur, best`. |
| 6. Dry run | 5 min | Trace the 2 edge examples by hand, line by line. Check loop bounds and off-by-one. |
| 7. Complexity | 2 min | State time + space, and why. |

**Stuck rule:**
- 10 min with no viable approach → read **only the pattern tag** (not the solution). Log as "hint-pattern".
- 20 min with approach but broken code → read **first 1/3 of the editorial**. Log as "hint-code".
- 30 min → read the full solution, close it, re-implement from scratch within 24 h. Log as "solved-with-solution"; auto-adds to redo queue.
- Never spend >45 min on one problem in a session.

---

## 6. Notes System

### 6.1 Problem log (one row per attempt; CSV or sheet)

| Date | LC# | Name | Pattern | Diff | Time (min) | Result (`solo` / `hint-pattern` / `hint-code` / `solution`) | Bug type (off-by-one, wrong ptr, edge, TLE, misread) | Key insight (1 line) | Next review date |
|---|---|---|---|---|---|---|---|---|---|

### 6.2 Pattern notebook page template (one page per pattern)

```
# <Pattern name>
Trigger words:        "..." "..." "..."
Invariant:            <one sentence>
Template:             <10–15 lines of Python>
Complexity:           T: O(..)  S: O(..)
Variants:             fixed/variable, longest/shortest, ...
My mistakes:          - ...   (append after every miss)
Problems:             LC#, LC#, LC#  (✔ when solved solo twice)
Disguises seen:       LC# — how it was hidden
```

### 6.3 Spaced repetition
- Intervals after a **solo** solve: **1 → 3 → 7 → 14 → 30 days**.
- After any hint/solution: reset to **1 day**, then continue the ladder.
- A problem "graduates" after 2 consecutive solo solves ≥ 7 days apart.
- Each review slot in the schedule is 15–60 min; pull the oldest-due items first. Cap redo at 3 problems per session.
- Flashcards (physical or Anki): front = trigger words / problem name; back = pattern + invariant + first 3 lines of template.

---

## 7. Progress Checkpoints

| Checkpoint | When | Pass criteria |
|---|---|---|
| C1 | End Week 1 (Day 7) | ≥ 70% of attempted problems `solo` or `hint-pattern`; dynamic array explained aloud without notes; all easies ≤ 15 min. |
| C2 | End Week 2 (Day 14) | Mock #2: 2 of 3 solved solo in time; mediums avg ≤ 35 min; cost table recited from memory. |
| C3 | End Week 3 (Day 21) | ≥ 75% of mediums solo ≤ 30 min; all 10 must-redo problems solved solo at least once; can name the pattern within 3 min on 8/10 unseen titles. |
| Capstone | Day 27 | ≥ 3 of 4 solved (both mediums required) within 100 min; narration covers brute force → optimization → complexity → edge cases on every problem. |

**If you miss a target:**
- Miss by a little (<10 pts): extend that week by 2 weekday sessions of pure redo; shift schedule.
- Miss by a lot: identify the top 2 weakest patterns from the log's `Pattern` × `Result` pivot; spend 3 days doing **only** those patterns (3 problems/day: E, M, M), then re-run the mock.
- Repeated **bug type** (e.g., off-by-one 4+ times): add a 5-minute "bug-specific dry run" step to your routine for the next 10 problems.
- Timing issue but correct logic: practice typing the 14 templates from memory daily, 10 min, until each is < 90 s.

---

## 8. Interview Layer

### 8.1 Five follow-ups interviewers ask on array problems
1. **"Can you do it in O(1) extra space?"** → write pointer, cyclic sort, reversal tricks, reuse output array, first row/col as markers.
2. **"What if the array doesn't fit in memory / is a stream?"** → single pass with O(1) or O(k) state (Kadane, running min, reservoir sampling, heap of k).
3. **"What if there are updates between queries?"** → prefix sums break; Fenwick tree / segment tree O(log n).
4. **"What if values can be negative?"** → sliding-window monotonicity breaks; switch to prefix + hashmap or monotonic deque.
5. **"Can you avoid sorting / is O(n) possible?"** → hashing, counting sort for bounded range, cyclic sort for 1..n, quickselect for k-th.

### 8.2 Talking through complexity
- Say the **loop structure**, not just the Big-O: "one pass, each element enters and leaves the window once → O(n)."
- Separate **input, auxiliary, and output** space: "O(1) extra, excluding the O(n) output."
- Name the **bottleneck**: "sort dominates at O(n log n); the merge pass is linear."
- Mention **amortized** where it applies (append, two-pointer window, stack pops).
- Give **worst vs average** when they differ (quickselect, hashing).

### 8.3 Talking through edge cases
Before coding say: "Let me list the edge cases I'll test at the end," then list them. After coding, dry-run at least two.

**Edge-case checklist for arrays**
- [ ] Empty array `[]`
- [ ] Single element `[x]`
- [ ] Two elements (smallest case where pointers can cross)
- [ ] All elements equal / heavy duplicates
- [ ] Already sorted ascending / descending
- [ ] All negative (Kadane init, circular subarray)
- [ ] Zeros present (product problems, division)
- [ ] Very large / very small values (say "no overflow in Python; in Java I'd use `long`")
- [ ] `k = 0`, `k > n`, `k = n` (rotation, window size)
- [ ] Target not present / multiple valid answers (which to return?)
- [ ] Matrix: 1×n, n×1, 1×1, non-square
- [ ] Intervals: touching endpoints, fully nested, identical
- [ ] Values outside expected range (cyclic sort: ≤ 0 or > n)
- [ ] Input mutation allowed? Stable order required?

---

## 9. One-Page Cheat Sheet

**Pattern triggers**
| See… | Think… |
|---|---|
| subarray sum / range sum, no updates | prefix sum (+ hashmap if "count" or "equals k") |
| range updates, read at end | difference array |
| remove / compact / in place | read-write pointer |
| sorted + pair/triplet | two pointers (sort first if allowed) |
| contiguous + longest/shortest/max with constraint, non-negatives | sliding window |
| max/min sum subarray | Kadane (init with `a[0]`) |
| depends on left AND right of i | two passes (prefix/suffix) or two pointers |
| values 1..n, missing/duplicate, O(1) space | cyclic sort |
| 3 distinct values | Dutch flag |
| intervals | sort by start, merge; heap of ends for rooms |
| rotate by k | triple reversal; matrix = transpose + reverse rows |
| next greater/smaller | monotonic stack |
| exists / count / lookup | hash set/map |
| grid | bounds check helper, direction array, boundary pointers |

**Templates (minimal)**
```python
pre[i+1] = pre[i] + a[i];  rng = pre[j+1] - pre[i]
w=0; for r in ..: if keep: a[w]=a[r]; w+=1
l,r=0,n-1; while l<r: ... l+=1 or r-=1
for r: add a[r]; while bad: remove a[l]; l+=1; best=max(best, r-l+1)
cur=max(x, cur+x); best=max(best,cur)
diff[l]+=v; diff[r+1]-=v; running sum
j=a[i]-1; swap if 0<=j<n and a[i]!=a[j] else i+=1
lo=mid=0; hi=n-1; while mid<=hi: 0→swap lo, 1→mid+=1, 2→swap hi (no mid+=1)
rev(0,n-1); rev(0,k-1); rev(k,n-1)
```

**Complexity one-liners**
- list append O(1) amortized · insert/pop front O(n) · slice O(k) copy · `in` O(n) · sort O(n log n) stable
- Two-pointer / window: each index enters & leaves once → O(n)
- Cyclic sort: each swap fixes one element forever → O(n)

**Always say:** restate → brute force → pattern → invariant → code → dry-run 2 edges → complexity (time, extra space, output).

### The 5 most common mistakes
1. **Off-by-one on bounds** — `pre[j+1]-pre[i]`, `while l < r` vs `<=`, `diff` sized `n+1`, spiral guards.
2. **Wrong initialization** — Kadane with `0` instead of `a[0]`; `seen[0] = 1` missing in prefix-hash.
3. **Advancing the wrong pointer** — Dutch flag `mid` after swapping with `hi`; cyclic sort `i` after a swap; two-pointer without justifying the discard.
4. **Sliding window with negatives** — assuming shrink is monotone when it isn't; use prefix + hash or deque instead.
5. **Python aliasing / copy traps** — `[[0]*m]*n`, slicing inside recursion, mutating while iterating, forgetting `k %= n`.
