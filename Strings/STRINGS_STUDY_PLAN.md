# Strings — End-to-End Study Plan

**Target:** solve string mediums solo in 25–30 min and narrate the approach.
**Duration:** 3 weeks (21 days). Weekdays 2 h, weekends 3 h → ~50 h total.
**Language:** Python 3. **Prereq:** [Arrays plan](../Array/ARRAYS_STUDY_PLAN.md) — strings reuse two pointers, sliding window, and prefix-sum style thinking; this plan assumes those are already comfortable.

---

## 1. Concepts (Week 1, Days 1–2)

### 1.1 How Python strings are stored
- A Python `str` is **immutable** — once created, it never changes. Every "modification" (`s + "x"`, `s.replace(...)`, `s[1:]`) builds a brand-new string.
- Internally stored as a contiguous array of characters (fixed-width internally per string, not variable-width like UTF-8 on disk) — indexing `s[i]` is O(1).
- Because it's immutable, strings are hashable → usable as dict keys / set members directly, unlike lists.

### 1.2 Cost table — Python string operations

| Operation | Time | Note |
|---|---|---|
| `s[i]` | O(1) | |
| `len(s)` | O(1) | stored |
| `s[i:j]` | O(j−i) | copies a new string |
| `s + t` | O(len s + len t) | new string allocated |
| `s * k` | O(len s · k) | new string |
| `s in t` | O(len s · len t) worst case | CPython uses an optimized search, ~O(n) typical |
| `s.find(x)` / `s.index(x)` | O(n·m) worst case | |
| `s.replace(a, b)` | O(n) | builds new string |
| `s.split(sep)` | O(n) | returns list |
| `sep.join(list)` | O(total chars) | prefer over repeated `+=` |
| `s.lower()/upper()/strip()` | O(n) | new string |
| `sorted(s)` | O(n log n) | returns a **list** of chars, not a string |
| `s == t` | O(min(n,m)) | short-circuits on first mismatch |
| `s.count(x)` | O(n) | |
| `ord(c)` / `chr(i)` | O(1) | char ↔ code point |

### 1.3 Python-specific gotchas

```python
# 1. String concatenation in a loop is O(n^2) total — each += builds a new string
s = ""
for c in chars: s += c          # BAD: O(n^2)
s = "".join(chars)               # GOOD: O(n)

# 2. Strings are immutable — can't do s[i] = 'x'
s[0] = 'x'                       # TypeError
lst = list(s); lst[0] = 'x'; s = "".join(lst)   # convert, mutate, rejoin

# 3. Slicing always copies
sub = s[1:]                      # O(k) new string, not a view

# 4. Comparing/hashing is case- and whitespace-sensitive
"abc" == "ABC"                   # False
"abc " == "abc"                  # False — trailing space matters

# 5. Unicode vs ASCII — len() counts code points, not bytes or "visual characters"
len("é")                         # 1 if it's one composed code point, 2 if it's e + combining accent
# interview problems are almost always ASCII/lowercase — confirm this with the interviewer

# 6. in / index use linear search — don't assume O(1)
if target in big_string: ...     # O(n*m) worst case, fine for most interview sizes

# 7. Off-by-one with slicing vs indexing
s[i:j]                           # chars from i up to BUT NOT INCLUDING j
s[i] through s[j]  inclusive  == s[i:j+1]

# 8. Mutable default via list(s) aliasing
a = list("abc"); b = a           # b is the SAME list; b[0]='x' changes a too
```

### 1.4 "From scratch" exercise — build your own `StringBuilder`
Strings are immutable, so repeated concatenation is slow. Implement the accumulator pattern yourself to internalize *why* `.join()` exists.

```python
class StringBuilder:
    def __init__(self):
        self._parts = []            # collect pieces here instead of concatenating each time

    def append(self, s):
        # just remember the piece — don't combine it with anything yet
        self._parts.append(s)
        return self                 # returning self lets you chain: sb.append("a").append("b")

    def build(self):
        # do the ONE expensive join at the very end, not on every append
        return "".join(self._parts)
```

**Calling it — a worked example:**
```python
sb = StringBuilder()
sb.append("Hello")      # _parts = ["Hello"]
sb.append(", ")          # _parts = ["Hello", ", "]
sb.append("world")       # _parts = ["Hello", ", ", "world"]
sb.append("!")           # _parts = ["Hello", ", ", "world", "!"]

print(sb.build())        # one join at the end -> "Hello, world!"
```
**Why this matters:** `sb.append(x)` is O(1) amortized (just a list append — reuse the Arrays plan's dynamic-array reasoning). `sb.build()` is O(total length), done once. Compare to `s += x` in a loop, which re-copies the whole growing string every single time → O(n²) total.

**Checks:** time `"".join(parts)` vs `s += part` in a loop for n=10,000 — confirm the gap. Then explain why strings being immutable forces this pattern.

---

## 2. Pattern List (learning order)

### P1. Frequency Counting (hash map / fixed array)
**Recognize:** anagram, "contains all characters of", char-count comparisons; alphabet known and small (usually lowercase a–z).
```python
from collections import Counter
c1, c2 = Counter(s), Counter(t)
is_anagram = c1 == c2

# fixed-size array version (faster, avoids hashmap overhead) — only for known alphabet
freq = [0] * 26
for ch in s: freq[ord(ch) - ord('a')] += 1
for ch in t: freq[ord(ch) - ord('a')] -= 1
is_anagram = all(f == 0 for f in freq)
```
**Complexity:** O(n) / O(1) if alphabet fixed, O(k) otherwise.
**Mistakes:** using a hashmap when a 26-length array is faster and simpler; forgetting Unicode/uppercase isn't covered by `ord(ch)-ord('a')`; comparing `Counter` objects when order matters (they don't care about order, by design).

### P2. Two Pointers on Strings
**Recognize:** palindrome check/construction, reverse in place, compare from both ends.
```python
def is_palindrome(s):
    l, r = 0, len(s) - 1
    while l < r:
        if s[l] != s[r]: return False
        l += 1; r -= 1
    return True

# reverse in place (on a list, since str is immutable)
def reverse(chars):
    l, r = 0, len(chars) - 1
    while l < r:
        chars[l], chars[r] = chars[r], chars[l]
        l += 1; r -= 1
```
**Complexity:** O(n) / O(1) (O(n) if you must build a new string).
**Mistakes:** trying to mutate a `str` directly; forgetting to skip non-alphanumeric chars / case-fold for "valid palindrome" variants; off-by-one on `l < r` vs `l <= r`.

### P3. Sliding Window on Strings
**Recognize:** longest/shortest substring with a constraint (no repeats, at most k distinct, contains all chars of another string).
```python
from collections import defaultdict
cnt = defaultdict(int); l = 0; best = 0
for r, ch in enumerate(s):
    cnt[ch] += 1
    while invalid(cnt):              # shrink while window breaks the rule
        cnt[s[l]] -= 1
        if cnt[s[l]] == 0: del cnt[s[l]]
        l += 1
    best = max(best, r - l + 1)

# "minimum window substring" shape — shrink INSIDE a while once window is valid
need = Counter(t); missing = len(t); l = 0; best = (float('inf'), 0, 0)
for r, ch in enumerate(s):
    if need[ch] > 0: missing -= 1
    need[ch] -= 1
    while missing == 0:                       # window currently valid -> try to shrink
        if r - l + 1 < best[0]: best = (r - l + 1, l, r + 1)
        need[s[l]] += 1
        if need[s[l]] > 0: missing += 1
        l += 1
```
**Complexity:** O(n) (each index enters/leaves window once) / O(k) for the counter.
**Mistakes:** forgetting to delete a zeroed key from the frequency map (breaks "no repeats" checks that test `len(cnt)`); confusing "shrink while invalid" (longest) with "shrink while valid" (shortest) — they're opposite loop conditions.

### P4. String Building / Reconstruction
**Recognize:** "reverse words", "remove duplicates", "compress", build output char-by-char under a rule.
```python
# never concatenate in a loop — collect then join
out = []
for ch in s:
    if keep(ch): out.append(ch)
result = "".join(out)

# reverse words in a sentence
result = " ".join(reversed(s.split()))

# run-length encoding
out = []
i = 0
while i < len(s):
    j = i
    while j < len(s) and s[j] == s[i]: j += 1
    out.append(s[i] + str(j - i))
    i = j
compressed = "".join(out)
```
**Complexity:** O(n) / O(n).
**Mistakes:** `s += ch` in a loop (O(n²)); `s.split()` with no args already handles multiple/leading/trailing spaces — don't reinvent that; forgetting the run-length count can be multi-digit.

### P5. Hashing / Rolling Hash (string matching)
**Recognize:** find all occurrences of a pattern, "repeated substring", compare many substrings fast (anagram-in-window, string matching at scale).
```python
# naive substring search (fine for interview-sized inputs)
def contains(s, pat):
    n, m = len(s), len(pat)
    for i in range(n - m + 1):
        if s[i:i+m] == pat: return i
    return -1

# rolling hash (Rabin-Karp) — O(n+m) average, avoids re-slicing every window
BASE, MOD = 256, 10**9 + 7
def rabin_karp(s, pat):
    n, m = len(s), len(pat)
    if m > n: return -1
    h = pow(BASE, m - 1, MOD)
    p_hash = s_hash = 0
    for i in range(m):
        p_hash = (p_hash * BASE + ord(pat[i])) % MOD
        s_hash = (s_hash * BASE + ord(s[i])) % MOD
    for i in range(n - m + 1):
        if s_hash == p_hash and s[i:i+m] == pat:   # verify on hash hit (hash collisions exist)
            return i
        if i < n - m:
            s_hash = ((s_hash - ord(s[i]) * h) * BASE + ord(s[i + m])) % MOD
    return -1
```
**Complexity:** O(n+m) average / O(1) extra beyond input.
**Mistakes:** forgetting to verify an actual match on hash collision (hashes can collide — always double check); off-by-one in the rolling update; using Python's `in` operator is usually fine in interviews unless asked specifically to implement matching yourself.

### P6. Palindrome Patterns (expand-from-center, DP)
**Recognize:** "longest palindromic substring", "count palindromic substrings", "can be rearranged into a palindrome".
```python
# expand around center — handles both odd and even length palindromes
def longest_palindrome(s):
    best = ""
    def expand(l, r):
        while l >= 0 and r < len(s) and s[l] == s[r]:
            l -= 1; r += 1
        return s[l+1:r]          # last valid window before the mismatch
    for i in range(len(s)):
        odd = expand(i, i)         # center is one character
        even = expand(i, i + 1)    # center is between two characters
        best = max(best, odd, even, key=len)
    return best
```
**Complexity:** O(n²) time (n centers × O(n) expansion) / O(1) extra.
**Mistakes:** only checking odd-length centers (misses even-length palindromes like `"abba"`); off-by-one in the final slice (`s[l+1:r]`, not `s[l:r]`, since the loop over-expands by one past the real boundary).

### P7. Anagram / Permutation-in-Window
**Recognize:** "does s contain a permutation of p", "find all anagram start indices" — fixed-size window + frequency match.
```python
from collections import Counter
def find_anagrams(s, p):
    need = Counter(p); window = Counter()
    res = []
    for i, ch in enumerate(s):
        window[ch] += 1
        if i >= len(p):
            left = s[i - len(p)]
            window[left] -= 1
            if window[left] == 0: del window[left]
        if window == need: res.append(i - len(p) + 1)
    return res
```
**Complexity:** O(n) / O(k) alphabet size.
**Mistakes:** rebuilding the `Counter` from scratch every window (O(n·k) instead of O(n)); comparing lists instead of `Counter`s (order shouldn't matter).

### P8. String-to-Number / Parsing
**Recognize:** "implement atoi", "roman to integer", "compare version numbers" — manual parsing with edge-case rules.
```python
def my_atoi(s):
    s = s.strip()
    if not s: return 0
    i, sign = 0, 1
    if s[0] in "+-":
        sign = -1 if s[0] == "-" else 1
        i = 1
    num = 0
    while i < len(s) and s[i].isdigit():
        num = num * 10 + int(s[i])
        i += 1
    num *= sign
    INT_MAX, INT_MIN = 2**31 - 1, -2**31
    return max(INT_MIN, min(INT_MAX, num))     # clamp to 32-bit range
```
**Complexity:** O(n) / O(1).
**Mistakes:** forgetting leading whitespace, sign, or to stop at the first non-digit; forgetting the overflow clamp (common interview requirement even though Python has no int overflow natively).

---

## 3. Problem Set (36 problems)

Legend: **E/M/H** difficulty · ★ = must-redo · 🎭 = pattern disguise.

| # | LC | Problem | Diff | Pattern | Why this problem |
|---|---|---|---|---|---|
| 1 | 242 | Valid Anagram | E | Frequency count | Canonical counting template. |
| 2 | 49 | Group Anagrams ★ | M | Frequency count (key) | Sorted-tuple / count-tuple as a hashable key. |
| 3 | 383 | Ransom Note | E | Frequency count | Array-based counting, subset check. |
| 4 | 125 | Valid Palindrome | E | Two pointers | Filtering non-alphanumeric + case-fold. |
| 5 | 680 | Valid Palindrome II ★ | M | Two pointers | "Skip one char" branch on mismatch. |
| 6 | 344 | Reverse String | E | Two pointers | In-place reversal on a list of chars. |
| 7 | 5 | Longest Palindromic Substring ★ | M | Expand-from-center | The pattern itself; even/odd centers. |
| 8 | 647 | Palindromic Substrings | M | Expand-from-center | Counting variant of #7. |
| 9 | 3 | Longest Substring Without Repeating Characters ★ | M | Sliding window | Core variable-window template. |
| 10 | 567 | Permutation in String ★ | M | Window + frequency | Fixed-size window, `Counter` equality. |
| 11 | 438 | Find All Anagrams in a String | M | Window + frequency | Same as #10, collect all starts. |
| 12 | 76 | Minimum Window Substring ★ | H | Sliding window (shortest) | The hardest, most-asked window problem. |
| 13 | 340 | Longest Substring with At Most K Distinct Characters | M | Sliding window | "At most k distinct" shrink condition. |
| 14 | 424 | Longest Repeating Character Replacement | M | Sliding window 🎭 | Disguised: track max-freq char, window invalid when `len-maxFreq > k`. |
| 15 | 151 | Reverse Words in a String | M | String building | `split()`/`join()` edge cases (extra spaces). |
| 16 | 443 | String Compression | M | String building | In-place two-pointer + multi-digit counts. |
| 17 | 14 | Longest Common Prefix | E | String building | Vertical scan vs sort-based approach. |
| 18 | 28 | Find the Index of the First Occurrence (strStr) | E | Hashing / matching | Naive search; mention KMP/Rabin-Karp exists. |
| 19 | 459 | Repeated Substring Pattern 🎭 | E | Hashing / matching | Disguised: check `(s+s)[1:-1]` contains `s`. |
| 20 | 686 | Repeated String Match | M | Matching | Figure out minimum repeat count, then search. |
| 21 | 20 | Valid Parentheses ★ | E | Stack (string) | Not a listed pattern above — flags the stack-on-string family. |
| 22 | 71 | Simplify Path 🎭 | M | Stack (string) | Disguised stack problem via `split('/')`. |
| 23 | 394 | Decode String | M | Stack (string) | Nested bracket parsing with counts. |
| 24 | 8 | String to Integer (atoi) ★ | M | Parsing | The parsing-edge-cases pattern itself. |
| 25 | 13 | Roman to Integer | E | Parsing | Lookup table + "subtract if smaller before larger." |
| 26 | 12 | Integer to Roman | M | Parsing | Greedy symbol table construction. |
| 27 | 165 | Compare Version Numbers | M | Parsing | Split on `.`, compare ints not strings. |
| 28 | 58 | Length of Last Word | E | String building | Trailing-space edge case. |
| 29 | 6 | Zigzag Conversion | M | String building (simulation) | Row-tracking simulation, not a "named" pattern — good disguise practice. |
| 30 | 1047 | Remove All Adjacent Duplicates In String | E | Stack (string) | Stack-based adjacent-removal template. |
| 31 | 316 | Remove Duplicate Letters | H | Stack + greedy 🎭 | Disguised: monotonic stack with "last occurrence" lookahead. |
| 32 | 1312 | Minimum Insertion Steps to Make a String Palindrome | H | Palindrome + DP | Bridge into DP; longest-common-subsequence framing. |
| 33 | 791 | Custom Sort String | M | Frequency count | Counting + direct placement, not actual sorting. |
| 34 | 1903 | Largest Odd Number in String | E | String building | Scan from the right for the first digit matching a condition. |
| 35 | 541 | Reverse String II | E | Two pointers | Reverse every other k-block — index-math variant of #6. |
| 36 | 168 | Excel Sheet Column Title | E | Parsing (base conversion) | Off-by-one base-26 conversion; common "easy that trips people up." |

**Mix:** 9 Easy (25%) · 23 Medium (64%) · 4 Hard (11%).
**Must-redo (10):** 49, 680, 5, 3, 567, 76, 20, 8, 424, 394.
**Disguises (4):** 424, 459, 71, 316.

---

## 4. Day-by-Day Schedule (3 weeks)

Blocks: **L** = learn, **P** = problems, **R** = review. Minutes in parentheses.

### Week 1 — Foundations + frequency counting + two pointers + sliding window intro

| Day | Type | Learn | Problems | Review |
|---|---|---|---|---|
| 1 Mon | 2h | §1.1–1.3 storage, cost table, gotchas (50) | Build `StringBuilder` + time it vs `+=` (60) | Log setup (10) |
| 2 Tue | 2h | P1 Frequency counting (25) | 242, 383, 49 (85) | Log (10) |
| 3 Wed | 2h | P2 Two pointers (25) | 125, 344, 680 (85) | Log (10) |
| 4 Thu | 2h | P3 Sliding window intro (30) | 3 (45) | Redo 49 blind (15); log (30) |
| 5 Fri | 2h | — | 567, 438 (80) | Redo 3 blind (20); log (20) |
| 6 Sat | 3h | P6 Palindrome (expand-center) (30) | 5, 647 (80) | **Mock #1** (2 problems, 50 min, narrated) + debrief (50); log (20) |
| 7 Sun | 3h | — | 13, 14 (easy warm-up for parsing feel) (40) | Redo 125, 680, 567 (60); pattern notebook pages for P1–P3 (60); checkpoint (20) |

### Week 2 — Harder windows + string building + stack-on-string

| Day | Type | Learn | Problems | Review |
|---|---|---|---|---|
| 8 Mon | 2h | Window "shrink while valid" vs "invalid" contrast (20) | 340, 424 (90) | Log (10) |
| 9 Tue | 2h | P4 String building (25) | 151, 443, 14 (75) | Redo 5 blind (20) |
| 10 Wed | 2h | Stack-on-string intro (25) | 20, 1047 (65) | Redo 76 attempt #1 (30) |
| 11 Thu | 2h | — | 394, 71 (85) | Log (15) |
| 12 Fri | 2h | P5 Hashing/matching (naive + Rabin-Karp) (35) | 28, 459 (60) | Redo 424, 340 (25) |
| 13 Sat | 3h | — | **Mock #2** (3 problems, 75 min, include 1 disguise) (75) + debrief (45) | Redo 20, 49 (60) |
| 14 Sun | 3h | P7 Anagram window consolidation (20) | 686 (30) | Pattern notebook for P4–P6 (70); redo 567, 438 (60); checkpoint (20) |

### Week 3 — Parsing, hard problems, disguises, consolidation

| Day | Type | Learn | Problems | Review |
|---|---|---|---|---|
| 15 Mon | 2h | P8 Parsing (atoi, roman) (30) | 8, 13, 12 (90) | Log (15) |
| 16 Tue | 2h | — | 165, 58, 6 (85) | Redo 394 blind (15); log (10) |
| 17 Wed | 2h | Attempt 76 solo (hard window) (45) | 76 (45) | Redo attempt debrief + 1 similar window problem (30) |
| 18 Thu | 2h | Monotonic-stack-on-string (25) | 316 (55) | Redo 71, 1047 (40) |
| 19 Fri | 2h | — | 791, 1312 (first DP-adjacent palindrome problem) (75) | Redo 76 second attempt (45) |
| 20 Sat | 3h | — | Redo all 4 disguises blind: 424, 459, 71, 316 (90) | **Mock #3** (2 mediums + 1 hard, 75 min, narrated) (75); debrief (15) |
| 21 Sun | 3h | Cheat sheet from memory, diff vs §9 (40) | Capstone: 4 problems (1E, 2M, 1H, include ≥1 disguise), 100 min (100) | Debrief against rubric (40); final checkpoint + next topic (20) |

**Total:** 21 days / 3 weeks. If a day slips, drop the "learn" block first, never the redo block — same rule as the Arrays plan.

---

## 5. Solving Routine (per problem, 30-min budget)

Identical structure to the Arrays plan, with string-specific prompts in step 3:

| Step | Time | What to do / say |
|---|---|---|
| 1. Restate | 2 min | Confirm: case-sensitive? alphabet (lowercase only, ASCII, Unicode)? empty string allowed? return type (index, bool, new string)? |
| 2. Brute force | 3 min | State the O(n²) or O(n·m) version aloud (e.g. slicing every substring) before optimizing. |
| 3. Pattern match | 3 min | Ask: contiguous substring + constraint? → sliding window. Need char counts? → frequency map/array. Sorted or compare ends? → two pointers. Palindrome? → expand-from-center. Nested structure (brackets)? → stack. Parsing with rules? → manual scan. |
| 4. Optimize | 5 min | State target complexity and the invariant (e.g. "window always has ≤ k distinct chars"). |
| 5. Code | 10 min | Build from `str` input but accumulate output in a list, `.join()` at the end — never `+=` in a loop. |
| 6. Dry run | 5 min | Trace with an empty string, a single char, and a string with repeats. |
| 7. Complexity | 2 min | State time/space; call out whether `.join()`/slicing costs are included. |

**Stuck rule:** identical to Arrays plan — 10 min → pattern hint, 20 min → partial editorial, 30 min → full solution + mandatory re-implementation within 24h, logged and auto-queued for spaced repetition.

---

## 6. Notes System

Reuse the **same problem log and spaced-repetition schedule** as the Arrays plan (1 → 3 → 7 → 14 → 30 days, reset to 1 on any hint/solution). Add one column specific to strings:

### 6.1 Problem log (add this column to the Arrays log)

| Date | LC# | Name | Pattern | Diff | Time | Result | Bug type | **Alphabet assumption checked? (Y/N)** | Key insight | Next review |
|---|---|---|---|---|---|---|---|---|---|---|

(The new column catches a string-specific bug class: assuming lowercase-only when the problem allows uppercase/Unicode/digits.)

### 6.2 Pattern notebook page template
Same template as Arrays (trigger words / invariant / template / complexity / variants / my mistakes / problems / disguises seen) — one new page per pattern in §2 above.

### 6.3 Spaced repetition
Same intervals and rules as the Arrays plan. Since several string patterns (sliding window, two pointers) are shared with arrays, cross-reference: a miss on a string sliding-window problem should also trigger a quick redo of the matching array sliding-window must-redo problem, and vice versa.

---

## 7. Progress Checkpoints

| Checkpoint | When | Pass criteria |
|---|---|---|
| C1 | End Week 1 (Day 7) | ≥ 70% of attempted problems `solo`/`hint-pattern`; can state the cost of `s += x` in a loop vs `.join()` without looking it up; all easies ≤ 15 min. |
| C2 | End Week 2 (Day 14) | Mock #2: 2 of 3 solved solo in time, including the disguise; can distinguish "shrink while valid" vs "shrink while invalid" window code from memory. |
| Capstone | Day 21 | ≥ 3 of 4 solved within 100 min, hard problem included; narration covers alphabet assumptions and immutability trade-offs on every problem. |

**If you miss a target:** same escalation ladder as the Arrays plan — extend by 2 sessions for a small miss; for a bigger miss, isolate the 2 weakest patterns from the log and spend 3 days on nothing else before re-running the mock.

---

## 8. Interview Layer

### 8.1 Five follow-ups interviewers ask on string problems
1. **"What if the string is case-insensitive / has Unicode characters?"** → `.lower()` first if safe to do so; for Unicode, a 26-length array breaks — fall back to a hashmap/`Counter`.
2. **"Can you do it without extra space?"** → reuse two pointers in place (on a `list(s)`, since `str` is immutable); mention you cannot truly mutate a `str` in Python, only simulate "in place" via a char list.
3. **"What if the pattern/needle is much longer than typical, and you can't use `in`?"** → Rabin-Karp or KMP for true O(n+m); explain the rolling hash idea even if you don't code KMP from scratch.
4. **"What's the actual complexity, counting string operations?"** → call out that slicing (`s[i:j]`) and concatenation are **not** O(1); a solution that looks O(n) but slices inside a loop is often O(n²).
5. **"How would this change for a stream of characters instead of a full string?"** → shift to maintaining running state (counts, window pointers) without ever holding the whole input, same idea as Kadane's/running-window from the Arrays plan.

### 8.2 Talking through complexity
- Explicitly separate the cost of the **algorithm's loop structure** from the cost of **string operations inside it** — e.g. "O(n) iterations, but each does an O(k) slice, so it's actually O(n·k)."
- Call out `.join()` vs `+=` by name when building output — it signals you know the immutability cost model.
- State whether you're counting the **output string's** space in your space complexity, and why (usually excluded, same convention as Arrays).

### 8.3 Edge-case checklist for strings
- [ ] Empty string `""`
- [ ] Single character
- [ ] All identical characters
- [ ] Mixed case (does the problem say case-sensitive?)
- [ ] Leading/trailing whitespace
- [ ] Non-alphanumeric characters (punctuation, symbols)
- [ ] Digits mixed into letters
- [ ] Pattern longer than the text (substring search)
- [ ] Multiple valid answers (which one to return — first? any?)
- [ ] Unicode / multi-byte characters (confirm ASCII-only assumption with interviewer)
- [ ] Palindrome edge cases: even vs odd length, single char counts as a palindrome

---

## 9. One-Page Cheat Sheet

**Pattern triggers**
| See… | Think… |
|---|---|
| anagram / same characters, any order | frequency count (`Counter` or 26-array) |
| sorted ends / palindrome check | two pointers |
| longest/shortest substring + constraint | sliding window — "shrink while invalid" (longest) vs "shrink while valid" (shortest) |
| longest palindromic substring/count | expand around center (odd + even) |
| find all occurrences of a pattern | naive `in`/slicing first; Rabin-Karp if asked to implement matching |
| nested brackets / "undo last" structure | stack |
| build output char-by-char | collect in a list, `"".join()` at the end — never `+=` in a loop |
| parse with rules (atoi, roman, version) | manual scan with explicit state machine / lookup table |
| fixed-size window matches another string exactly | frequency map equality, update incrementally (don't rebuild each window) |

**Templates (minimal)**
```python
freq=[0]*26; for ch in s: freq[ord(ch)-97]+=1
l,r=0,len(s)-1; while l<r: if s[l]!=s[r]: return False; l+=1; r-=1
for r,ch in enumerate(s): cnt[ch]+=1; while invalid: cnt[s[l]]-=1; l+=1; best=max(best,r-l+1)
out=[]; for ch in s: if keep(ch): out.append(ch); "".join(out)
def expand(l,r): while l>=0 and r<len(s) and s[l]==s[r]: l-=1; r+=1; return s[l+1:r]
window=Counter(); for i,ch in enumerate(s): window[ch]+=1; if i>=len(p): drop leftmost; if window==need: record
```

**Complexity one-liners**
- `s[i:j]` and `s + t` are O(k), **not** O(1) — never assume string ops are free inside a loop.
- `s += x` in a loop is O(n²) total; `"".join(list)` is O(n).
- Sliding window / two pointers on strings: O(n), same reasoning as arrays — each index enters/leaves once.
- Rabin-Karp: O(n+m) average, O(n·m) worst case (hash collisions) — always verify on a hash match.

**Always say:** restate (case/alphabet/empty) → brute force → pattern → invariant → code (accumulate + join) → dry-run (empty, single char, repeats) → complexity (call out slicing/concat costs explicitly).

### The 5 most common mistakes
1. **String concatenation in a loop** (`s += ch`) — silently O(n²); always collect in a list and `.join()`.
2. **Forgetting strings are immutable** — trying `s[i] = x` directly; convert to `list(s)` first when in-place mutation is needed.
3. **Window shrink direction confusion** — mixing up "shrink while invalid" (longest-valid) with "shrink while valid" (shortest-valid); these are opposite `while` conditions.
4. **Hard-coding a 26-letter alphabet** when the problem allows uppercase, digits, or Unicode — breaks silently on hidden test cases.
5. **Treating slicing as O(1)** — `s[i:j]` inside a loop quietly turns an O(n) solution into O(n²); always account for slice cost.
