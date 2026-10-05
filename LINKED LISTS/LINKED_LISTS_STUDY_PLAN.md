# Linked Lists — End-to-End Study Plan

**Target:** solve linked-list mediums solo in 25–30 min and narrate the approach.
**Duration:** 3 weeks (21 days). Weekdays 2 h, weekends 3 h → ~50 h total.
**Language:** Python 3. **Prereq:** [Arrays plan](../Array/ARRAYS_STUDY_PLAN.md), [Strings plan](../Strings/STRINGS_STUDY_PLAN.md) — two pointers carries over directly; this is where it gets harder because you're chasing `.next` links instead of indices.

---

## 1. Concepts (Week 1, Days 1–2)

### 1.1 Why linked lists exist (vs arrays)
- An array is one contiguous memory block — O(1) random access, but inserting/deleting in the middle costs O(n) (everything shifts).
- A linked list is a chain of separately-allocated nodes, each holding data + a pointer to the next node. Insert/delete at a known node is O(1) — no shifting — but random access is O(n) (must walk from the head).
- Trade-off: **arrays trade flexible insertion for fast access; linked lists trade fast access for flexible insertion.**

### 1.2 Cost table

| Operation | Array | Singly Linked List | Doubly Linked List |
|---|---|---|---|
| Access by index | O(1) | O(n) | O(n) |
| Insert/delete at front | O(n) | O(1) | O(1) |
| Insert/delete at end (no tail ptr) | O(1) amortized | O(n) | O(1) with tail ptr |
| Insert/delete at known node | O(n) | O(1) (if you have the prev node) | O(1) |
| Search by value | O(n) | O(n) | O(n) |
| Extra memory per element | none | 1 pointer | 2 pointers |

### 1.3 The node, and how `Node`/`self.head` actually work
```python
class Node:
    def __init__(self, data):
        self.data = data   # the value this node holds
        self.next = None   # pointer to the next node; None means "end of list"
```
- `self.head` on the list object is just a reference to the **first** `Node`. The list itself has no other storage — every other node is reached by following `.next` chains starting from `head`.
- An empty list is just `head = None`. There's no "empty node" — absence of a node *is* `None`.
- You already have a working implementation of all the basics in [SIngle_linked_list.py](DS/SIngle_linked_list.py) (insert at beginning/end/position, delete from beginning/end, search, print, reverse). Read it before Day 1 — this plan builds on it rather than re-teaching it.

### 1.4 Python-specific gotchas

```python
# 1. Losing the head reference
current = head
while current:
    current = current.next     # fine, we still have `head` saved separately
# but:
head = head.next                # BAD if you needed the original head later — it's gone, no way back

# 2. Forgetting to save `next` before rewiring (classic reverse-list bug)
current.next = prev        # overwrites current.next BEFORE you've saved it
next_node = current.next   # too late — this is now `prev`, not the real next node
# correct order: save next_node FIRST, then rewire

# 3. Off-by-one in "find the node before position k"
# stepping k times lands you ON the k-th node, not before it — count carefully

# 4. Mutating .next on a None node
current.next.next = x      # crashes with AttributeError if current.next is None — always check first

# 5. Comparing nodes vs comparing data
if node1 == node2: ...         # True only if same object (same memory), NOT same data
if node1.data == node2.data: ...   # compares values

# 6. Dummy/sentinel head node trick
# many problems (remove nth node, merge lists, partition) get much simpler with a
# fake node placed BEFORE the real head, so you never special-case "deleting the head"
dummy = Node(0); dummy.next = head
...
return dummy.next     # the real answer, skipping the dummy

# 7. Fast & slow pointers must start correctly
slow = fast = head         # NOT slow=head, fast=head.next, unless the problem specifically needs that offset
while fast and fast.next:
    slow = slow.next
    fast = fast.next.next
```

### 1.5 "From scratch" exercise — build a Doubly Linked List
You already have a singly linked list. Build the doubly-linked version yourself to feel the extra bookkeeping a `prev` pointer requires.

```python
class DNode:
    def __init__(self, data):
        self.data = data      # the value this node holds
        self.next = None      # pointer forward
        self.prev = None      # pointer backward — the new part vs singly linked

class DoublyLinkedList:
    def __init__(self):
        self.head = None      # first node
        self.tail = None      # last node — kept updated so append is O(1)

    def append(self, data):
        # add a new node at the end
        node = DNode(data)
        if self.head is None:          # list was empty -> new node is both head and tail
            self.head = self.tail = node
            return
        node.prev = self.tail          # new node looks back at the old last node
        self.tail.next = node          # old last node looks forward at the new node
        self.tail = node               # new node is now the official last node

    def prepend(self, data):
        # add a new node at the front
        node = DNode(data)
        if self.head is None:
            self.head = self.tail = node
            return
        node.next = self.head          # new node looks forward at the old first node
        self.head.prev = node          # old first node looks back at the new node
        self.head = node               # new node is now the official first node

    def remove(self, node):
        # unlink one specific node, patching its neighbors around the gap
        if node.prev: node.prev.next = node.next      # left neighbor skips over `node`
        else: self.head = node.next                     # `node` was the head -> next becomes head
        if node.next: node.next.prev = node.prev      # right neighbor skips over `node`
        else: self.tail = node.prev                      # `node` was the tail -> prev becomes tail

    def to_list(self):
        # walk forward and collect values, just to see the result
        out, cur = [], self.head
        while cur:
            out.append(cur.data)
            cur = cur.next
        return out
```

**Calling it — a worked example:**
```python
d = DoublyLinkedList()
d.append(10)          # head=10, tail=10            list: 10
d.append(20)          # head=10, tail=20             list: 10 <-> 20
d.append(30)          # head=10, tail=30             list: 10 <-> 20 <-> 30
d.prepend(5)           # head=5,  tail=30            list: 5 <-> 10 <-> 20 <-> 30

print(d.to_list())     # [5, 10, 20, 30]

middle_node = d.head.next.next     # the node holding 20
d.remove(middle_node)              # unlink 20, patch 10 and 30 to point at each other

print(d.to_list())     # [5, 10, 30]
```
**Why this matters:** every `remove` must fix **both** directions (`prev` and `next` of the neighbors) — forgetting one side leaves a dangling pointer. This is exactly the bookkeeping that makes doubly linked list problems (LRU cache, browser history) trickier than singly linked ones.

**Checks:** append 5 items, remove the head, remove the tail, remove a middle node, then `to_list()` after each to confirm the chain stays correct both forward and backward (`d.tail.prev.data` etc.).

---

## 2. Pattern List (learning order)

### P1. Traversal & Dummy Node
**Recognize:** any problem that needs to "process the whole list" or specifically "might remove/change the head itself."
```python
cur = head
while cur:
    # do something with cur.data
    cur = cur.next

# dummy node trick — avoids special-casing "head might be removed/replaced"
dummy = Node(0); dummy.next = head
cur = dummy
...
return dummy.next
```
**Complexity:** O(n) / O(1).
**Mistakes:** forgetting the dummy trick and writing separate "if head is the target" logic that duplicates the main loop; returning `head` instead of `dummy.next` after the head itself may have changed.

### P2. Fast & Slow Pointers (Floyd's)
**Recognize:** find the middle, detect a cycle, find cycle start, "nth from the end" variants, find if palindrome.
```python
# find middle
slow = fast = head
while fast and fast.next:
    slow = slow.next
    fast = fast.next.next
# slow is now the middle (second middle if even length)

# cycle detection
slow = fast = head
has_cycle = False
while fast and fast.next:
    slow = slow.next
    fast = fast.next.next
    if slow == fast:
        has_cycle = True
        break

# find cycle START (after detecting one) — reset one pointer to head
if has_cycle:
    slow = head
    while slow != fast:
        slow = slow.next
        fast = fast.next
    cycle_start = slow
```
**Complexity:** O(n) / O(1).
**Mistakes:** checking `fast` before `fast.next` in the wrong order (crashes on `None.next`); comparing node data instead of node identity for cycle checks; forgetting slow must reset to `head` (not continue from its cycle position) to find the cycle's start node.

### P3. Reversal (full and partial)
**Recognize:** "reverse the list", "reverse between positions m and n", "reverse in groups of k".
```python
def reverse(head):
    prev = None
    cur = head
    while cur:
        nxt = cur.next      # save BEFORE overwriting — see gotcha #2 above
        cur.next = prev
        prev = cur
        cur = nxt
    return prev             # prev is the new head

# reverse a sublist between two nodes, given the node right before the sublist
def reverse_sublist(before, count):
    prev = None
    cur = before.next
    for _ in range(count):
        nxt = cur.next
        cur.next = prev
        prev = cur
        cur = nxt
    before.next.next = cur   # old first node of sublist now links past the reversed part
    before.next = prev        # `before` now points to the new first node (old last)
```
**Complexity:** O(n) / O(1).
**Mistakes:** not saving `nxt` first (breaks the chain); losing track of which node becomes the new head vs tail of the reversed section; off-by-one on how many nodes to reverse.

### P4. Merge / Split
**Recognize:** "merge two sorted lists", "merge k lists", "split list into parts", "partition around a value".
```python
def merge_two_sorted(l1, l2):
    dummy = Node(0); tail = dummy
    while l1 and l2:
        if l1.data <= l2.data:
            tail.next = l1; l1 = l1.next
        else:
            tail.next = l2; l2 = l2.next
        tail = tail.next
    tail.next = l1 if l1 else l2     # attach whichever list has leftovers
    return dummy.next

# merge k lists — use a min-heap of (value, index, node) to always grab the smallest head
import heapq
def merge_k(lists):
    heap = []
    for i, node in enumerate(lists):
        if node: heapq.heappush(heap, (node.data, i, node))
    dummy = Node(0); tail = dummy
    while heap:
        val, i, node = heapq.heappop(heap)
        tail.next = node; tail = tail.next
        if node.next: heapq.heappush(heap, (node.next.data, i, node.next))
    return dummy.next
```
**Complexity:** merge-two O(n+m) / O(1). merge-k O(N log k) where N = total nodes / O(k) heap.
**Mistakes:** forgetting to attach the leftover tail after one list runs out; in merge-k, forgetting the tie-breaker index in the heap tuple (comparing `Node` objects directly crashes if values tie, since nodes aren't orderable).

### P5. Nth-from-end / Two-Pointer Gap
**Recognize:** "remove nth node from end", "find kth node from end" — without knowing the length upfront.
```python
def remove_nth_from_end(head, n):
    dummy = Node(0); dummy.next = head
    fast = slow = dummy
    for _ in range(n):          # advance fast n steps first
        fast = fast.next
    while fast.next:            # then move both until fast hits the end
        fast = fast.next
        slow = slow.next
    slow.next = slow.next.next  # slow is now right before the node to remove
    return dummy.next
```
**Complexity:** O(n) single pass / O(1).
**Mistakes:** using the dummy node but forgetting it means `slow` starts one before the real head (needed so you can remove the head itself without a special case); off-by-one on how many steps to advance `fast` first.

### P6. In-place Rewiring (no extra list/array)
**Recognize:** "do it in O(1) extra space", "swap nodes in pairs", "rotate the list", "reorder list" (interleave front/back halves).
```python
# swap every pair of adjacent nodes
def swap_pairs(head):
    dummy = Node(0); dummy.next = head
    prev = dummy
    while prev.next and prev.next.next:
        first = prev.next
        second = first.next
        first.next = second.next
        second.next = first
        prev.next = second
        prev = first
    return dummy.next
```
**Complexity:** O(n) / O(1).
**Mistakes:** rewiring in the wrong order and losing a reference to part of the list mid-swap (always save every pointer you'll need before changing any of them); forgetting `prev` must advance to `first` (the now-second node), not `second`.

### P7. Intersection / Equality Checks
**Recognize:** "do two lists intersect", "is this list a palindrome", "are two lists identical".
```python
# intersection of two lists (no cycle) — switch heads once each pointer reaches the end
def get_intersection(a, b):
    p1, p2 = a, b
    while p1 != p2:
        p1 = p1.next if p1 else b
        p2 = p2.next if p2 else a
    return p1     # either the intersection node, or None (both hit None together)

# palindrome check — find middle, reverse second half, compare, (optionally restore)
def is_palindrome(head):
    slow = fast = head
    while fast and fast.next:
        slow = slow.next; fast = fast.next.next
    second_half = reverse(slow)
    p1, p2 = head, second_half
    result = True
    while p2:
        if p1.data != p2.data: result = False; break
        p1 = p1.next; p2 = p2.next
    return result
```
**Complexity:** O(n+m) intersection / O(1). Palindrome O(n) / O(1).
**Mistakes:** comparing values instead of node identity for intersection (two different nodes can coincidentally hold equal data); forgetting the switch-heads trick balances the total distance traveled so both pointers meet exactly at the intersection (or both hit `None` together if there is none).

---

## 3. Problem Set (32 problems)

Legend: **E/M/H** difficulty · ★ = must-redo · 🎭 = pattern disguise.

| # | LC | Problem | Diff | Pattern | Why this problem |
|---|---|---|---|---|---|
| 1 | 206 | Reverse Linked List ★ | E | Reversal | The pattern itself — must be instant recall. |
| 2 | 876 | Middle of the Linked List | E | Fast/slow | Fast/slow template, simplest form. |
| 3 | 141 | Linked List Cycle ★ | E | Fast/slow | Floyd's cycle detection core. |
| 4 | 142 | Linked List Cycle II ★ | M | Fast/slow | Find the cycle's start node — the tricky follow-up. |
| 5 | 83 | Remove Duplicates from Sorted List | E | Traversal | Simplest "skip a node" rewiring. |
| 6 | 82 | Remove Duplicates from Sorted List II | M | Traversal + dummy | Needs dummy node since head itself may be removed. |
| 7 | 203 | Remove Linked List Elements | E | Traversal + dummy | Same dummy trick, value-based removal. |
| 8 | 19 | Remove Nth Node From End ★ | M | Two-pointer gap | The pattern itself; one-pass without knowing length. |
| 9 | 21 | Merge Two Sorted Lists ★ | E | Merge | Canonical dummy-node merge template. |
| 10 | 23 | Merge k Sorted Lists ★ | H | Merge + heap | Scaling #9 up with a min-heap. |
| 11 | 143 | Reorder List ★ | M | In-place rewiring 🎭 | Disguised: find middle + reverse half + merge-interleave, three patterns combined. |
| 12 | 24 | Swap Nodes in Pairs ★ | M | In-place rewiring | The pattern itself; careful pointer order. |
| 13 | 25 | Reverse Nodes in k-Group | H | Reversal (partial) | Generalizes #1 and #12 into chunks of k. |
| 14 | 92 | Reverse Linked List II | M | Reversal (partial) | Reverse only a sublist between positions m,n. |
| 15 | 234 | Palindrome Linked List ★ | M | Fast/slow + reversal | Combines two patterns; very common interview ask. |
| 16 | 160 | Intersection of Two Linked Lists ★ | E | Intersection | The two-pointer switch-heads trick. |
| 17 | 2 | Add Two Numbers | M | Traversal + dummy | Digit-by-digit arithmetic with carry, dummy node output. |
| 18 | 445 | Add Two Numbers II | M | Traversal + stack 🎭 | Disguised: numbers are forward-ordered, needs a stack (or reverse) first. |
| 19 | 328 | Odd Even Linked List | M | In-place rewiring | Two-pointer interleave without extra space. |
| 20 | 86 | Partition List | M | In-place rewiring + dummy | Two dummy "bucket" lists merged at the end. |
| 21 | 138 | Copy List with Random Pointer | M | Hashmap / interleaving 🎭 | Disguised: needs a node→clone map (or interweaving trick) for the random pointer. |
| 22 | 61 | Rotate List | M | Fast/slow + math | Find length, connect tail to head, break at the right offset. |
| 23 | 1669 | Merge In Between Linked Lists | M | Merge + traversal | Splice one list into a specific range of another. |
| 24 | 237 | Delete Node in a Linked List | E | Traversal 🎭 | Disguised: no access to head/prev — copy next node's data forward instead. |
| 25 | 148 | Sort List | M | Merge sort on linked list | O(n log n) sort with O(1) extra space; combines middle-finding + merge. |
| 26 | 2130 | Maximum Twin Sum of a Linked List | M | Fast/slow + reversal | Reuse of palindrome-style half-reversal in a new shape. |
| 27 | 1721 | Swapping Nodes in a Linked List | M | Two-pointer gap | Variant of #8's gap technique, swap instead of remove. |
| 28 | 109 | Convert Sorted List to BST | M | Fast/slow (bridge) | Bridges into trees — middle-finding recursion. |
| 29 | 430 | Flatten a Multilevel Doubly Linked List | M | DLL traversal + stack | Exercises the doubly-linked-list bookkeeping from §1.5. |
| 30 | 707 | Design Linked List | M | Implementation | Build get/add/delete at index from scratch — tests full understanding, not just a pattern. |
| 31 | 146 | LRU Cache ★ | M | DLL + hashmap | The classic DLL application; combines §1.5 directly with a hashmap. |
| 32 | 114 | Flatten Binary Tree to Linked List (optional bridge into trees) | M | Traversal (bridge) | Optional — only if moving to Trees next; otherwise skip. |

**Mix:** 7 Easy (22%) · 22 Medium (69%) · 3 Hard (9%), plus 1 optional bridge problem.
**Must-redo (10) — LC#:** 206 (reverse list), 141 (cycle), 142 (cycle II), 19 (remove nth from end), 21 (merge two sorted), 24 (swap pairs), 234 (palindrome), 160 (intersection), 146 (LRU cache), 143 (reorder list).
**Disguises (4) — LC#:** 143 (reorder list), 445 (add two numbers II), 138 (copy random pointer), 237 (delete node).

---

## 4. Day-by-Day Schedule (3 weeks)

Blocks: **L** = learn, **P** = problems, **R** = review. Minutes in parentheses.

### Week 1 — Foundations + traversal + fast/slow + full reversal

| Day | Type | Learn | Problems | Review |
|---|---|---|---|---|
| 1 Mon | 2h | §1.1–1.3 node/list mechanics; read existing `SIngle_linked_list.py` closely (50) | Extend it: add a `length()` method and a `find_middle()` method yourself (60) | Log setup (10) |
| 2 Tue | 2h | §1.5 Doubly Linked List exercise (40) | Implement `DoublyLinkedList` + test append/prepend/remove (70) | Log (10) |
| 3 Wed | 2h | P1 Traversal & dummy node (25) | 83, 203 (65) | Log (30) |
| 4 Thu | 2h | P2 Fast & slow pointers (30) | 876, 141 (60) | Redo dummy-node problems blind (30) |
| 5 Fri | 2h | — | 142 (45) | Redo 876, 141 (30); log (15) |
| 6 Sat | 3h | P3 Reversal (full) (30) | 206, 92 (75) | **Mock #1** (2 problems, 50 min, narrated) + debrief (50); log (25) |
| 7 Sun | 3h | — | 82 (40) | Redo 206, 142 blind (40); pattern notebook for P1–P3 (60); checkpoint (40) |

### Week 2 — Merge, nth-from-end, in-place rewiring, intersections

| Day | Type | Learn | Problems | Review |
|---|---|---|---|---|
| 8 Mon | 2h | P4 Merge/split (30) | 21 (45) | Redo 92 (20); log (25) |
| 9 Tue | 2h | — | 23 (60) | Redo 21 blind (30) |
| 10 Wed | 2h | P5 Nth-from-end / two-pointer gap (25) | 19 (45) | Redo 19 blind same day (30); log (20) |
| 11 Thu | 2h | P6 In-place rewiring (30) | 24, 328 (60) | Log (30) |
| 12 Fri | 2h | — | 86, 61 (85) | Redo 24 blind (15); log (20) |
| 13 Sat | 3h | P7 Intersection/equality (30) | 160, 234 (85) | **Mock #2** (3 problems, 75 min, include 1 disguise) (75) + debrief (45) |
| 14 Sun | 3h | — | 2, 237 | Redo 234, 160 (60); pattern notebook for P4–P7 (60); checkpoint (20) |

### Week 3 — Disguises, hard problems, DLL applications, consolidation

| Day | Type | Learn | Problems | Review |
|---|---|---|---|---|
| 15 Mon | 2h | — | 143 (Reorder List), 445 (90) | Log (30) |
| 16 Tue | 2h | — | 138 (60) | Redo 19, 24, 143 blind (60) |
| 17 Wed | 2h | Attempt 25 (reverse k-group) solo first (45) | 25 (45) | Redo attempt debrief + compare to 206/92 (30) |
| 18 Thu | 2h | Merge sort on linked list (25) | 148 (65) | Redo 23, 21 blind (30) |
| 19 Fri | 2h | §1.5 revisit — LRU design walkthrough (30) | 146 ★ (65) | Redo 142, 234 (25) |
| 20 Sat | 3h | — | Redo all 4 disguises blind: 143, 445, 138, 237 (90) | **Mock #3** (2 mediums + 1 hard, 75 min, narrated) (75); debrief (15) |
| 21 Sun | 3h | Cheat sheet from memory, diff vs §9 (40) | Capstone: 4 problems (1E, 2M, 1H, include ≥1 disguise + LRU-style), 100 min (100) | Debrief against rubric (40); final checkpoint + next topic (20) |

**Total:** 21 days / 3 weeks. If a day slips, drop the "learn" block first, never the redo block — same rule as the Arrays and Strings plans.

---

## 5. Solving Routine (per problem, 30-min budget)

Same structure as the Arrays/Strings plans, with linked-list-specific prompts in step 3 and a mandatory step added just for this topic:

| Step | Time | What to do / say |
|---|---|---|
| 1. Restate | 2 min | Confirm: singly or doubly linked? can it have a cycle? can it be empty/single-node? is it sorted? |
| 2. Draw it | 2 min | **Always** sketch 4–5 boxes with arrows on paper/whiteboard before coding — linked-list bugs are almost always pointer-order mistakes, and drawing catches them before they're bugs. |
| 3. Brute force | 2 min | State the "dump into an array/list, solve there, rebuild" approach aloud — valid baseline, but costs O(n) space; name that trade-off. |
| 4. Pattern match | 3 min | Ask: need the middle/detect a loop? → fast/slow. Reversing all or part? → reversal. Combining two lists? → merge. "Nth from end" without a length pass? → two-pointer gap. Can head itself change? → dummy node. No access to prev node? → check for the "copy next node forward" disguise. |
| 5. Optimize | 3 min | State target complexity and name the invariant (e.g. "fast always travels 2x slow's distance"). |
| 6. Code | 11 min | Before writing any `.next =` line, say out loud which pointer you're about to lose if you don't save it first. |
| 7. Dry run | 5 min | Trace on: empty list, single node, two nodes, and (if relevant) a list with a cycle. |
| 8. Complexity | 2 min | State time/space, and confirm O(1) extra space if the problem asked for it. |

**Stuck rule:** identical to Arrays/Strings — 10 min → pattern hint, 20 min → partial editorial, 30 min → full solution + mandatory re-implementation within 24h, logged and auto-queued for spaced repetition.

---

## 6. Notes System

Reuse the **same problem log and spaced-repetition schedule** as the Arrays/Strings plans (1 → 3 → 7 → 14 → 30 days, reset to 1 on any hint/solution). Add one column specific to linked lists:

### 6.1 Problem log (add this column)

| Date | LC# | Name | Pattern | Diff | Time | Result | Bug type | **Drew the pointers first? (Y/N)** | Key insight | Next review |
|---|---|---|---|---|---|---|---|---|---|---|

(This column exists because skipping the sketch step is the single biggest predictor of a pointer-order bug — track it honestly.)

### 6.2 Pattern notebook page template
Same template as Arrays/Strings (trigger words / invariant / template / complexity / variants / my mistakes / problems / disguises seen) — one new page per pattern in §2 above.

### 6.3 Spaced repetition
Same intervals and rules as the other two plans. Cross-reference: a miss on fast/slow-pointer problems here should also trigger a quick redo of the Arrays plan's two-pointer must-redo problems, since the underlying discipline (justify each pointer move) is identical.

---

## 7. Progress Checkpoints

| Checkpoint | When | Pass criteria |
|---|---|---|
| C1 | End Week 1 (Day 7) | ≥ 70% of attempted problems `solo`/`hint-pattern`; can reverse a linked list from memory, no notes, in under 90 seconds; all easies ≤ 15 min. |
| C2 | End Week 2 (Day 14) | Mock #2: 2 of 3 solved solo in time, including the disguise; can explain the dummy-node trick's purpose without hesitation. |
| Capstone | Day 21 | ≥ 3 of 4 solved within 100 min, hard problem included; narration covers which pointer you save/lose at every rewiring step. |

**If you miss a target:** same escalation ladder as the other plans — extend by 2 sessions for a small miss; for a bigger miss, isolate the 2 weakest patterns from the log and spend 3 days on nothing else before re-running the mock.

---

## 8. Interview Layer

### 8.1 Five follow-ups interviewers ask on linked-list problems
1. **"Can you do it with O(1) extra space?"** → in-place rewiring instead of dumping into an array; mention the trade-off you gave up in your brute force.
2. **"What if the list could be circular / has a cycle?"** → Floyd's fast/slow detection first, then handle accordingly — never assume `while cur:` terminates.
3. **"What if you don't have access to the head, only the node to delete?"** → the "copy next node's data forward, then skip it" trick (LC 237) — explain why it fails for the actual last node.
4. **"Can you avoid recursion / explain the stack depth risk?"** → recursive solutions (sort, reverse) are elegant but risk stack overflow on very long lists; know the iterative version too.
5. **"How would this differ for a doubly linked list?"** → O(1) backward traversal and O(1) deletion given just the node (no need to find `prev` by scanning) — but double the pointer bookkeeping on every insert/delete.

### 8.2 Talking through complexity
- Name whether you need a **second pass** (e.g. finding length first) vs a true **single pass** (two-pointer gap) — single-pass is usually the better answer when both work.
- For merge-k-lists, state the three options and their costs: sequential merge O(kN), divide-and-conquer merge O(N log k), min-heap O(N log k) — and why you picked one.
- Call out recursive space cost explicitly: "O(n) call stack," not just "O(1) extra" — a common slip when a recursive solution feels "clean."

### 8.3 Edge-case checklist for linked lists
- [ ] Empty list (`head is None`)
- [ ] Single node
- [ ] Two nodes
- [ ] List with a cycle (where relevant)
- [ ] Removing/modifying the head itself
- [ ] Removing/modifying the tail itself
- [ ] All nodes have the same value
- [ ] Already sorted / reverse sorted (merge, sort problems)
- [ ] Odd vs even total length (middle-finding, pair-swapping, k-group reversal)
- [ ] `k` larger than the list length (rotate, k-group reversal, nth-from-end)
- [ ] Operating on a sublist defined by `(m, n)` where `m == n`, or `m == 1`, or `n == length`

---

## 9. One-Page Cheat Sheet

**Pattern triggers**
| See… | Think… |
|---|---|
| find the middle / detect a cycle / cycle start | fast & slow pointers |
| reverse all or part of the list | reversal — save `next` before overwriting, always |
| merge two or more sorted lists | dummy node + tail pointer (heap if more than 2 lists) |
| "nth from the end," no length given upfront | two-pointer gap — advance one pointer n steps first |
| head itself might be removed/changed | dummy node placed before the real head |
| swap/reorder adjacent or chunked nodes | in-place rewiring — draw it first, save every pointer before touching any |
| compare two lists / check palindrome | intersection: switch-heads trick · palindrome: fast/slow + reverse second half |
| need O(1) access to both neighbors | doubly linked list (LRU cache, browser history, flatten multilevel) |

**Templates (minimal)**
```python
dummy = Node(0); dummy.next = head; ...; return dummy.next
slow=fast=head; while fast and fast.next: slow=slow.next; fast=fast.next.next
prev=None; cur=head
while cur: nxt=cur.next; cur.next=prev; prev=cur; cur=nxt
return prev
tail.next = l1 if l1 else l2    # merge leftover attach
for _ in range(n): fast=fast.next     # then race slow and fast together
p1,p2=a,b; while p1!=p2: p1=p1.next if p1 else b; p2=p2.next if p2 else a
```

**Complexity one-liners**
- Access by index: O(n), always — there's no shortcut, unlike arrays.
- Fast/slow, reversal, two-pointer gap, merge: all O(n) time, O(1) extra space.
- Merge k lists with a heap: O(N log k), where N is total nodes and k is list count.
- Recursive reverse/sort: O(n) extra space from the call stack — say this explicitly, don't call it O(1).

**Always say:** restate (singly/doubly, cyclic?, empty/single-node) → **draw it** → brute force (array dump, name the O(n) space cost) → pattern → invariant → code (save pointers before overwriting) → dry-run (empty, 1 node, 2 nodes) → complexity (time, space, call out recursion stack cost).

### The 5 most common mistakes
1. **Overwriting `.next` before saving it** — the #1 linked-list bug; always `nxt = cur.next` before `cur.next = prev`.
2. **Forgetting the dummy node** when the head itself might be removed or replaced — leads to ugly special-case branches or a wrong final head.
3. **Comparing node identity vs data** — using `==` on nodes when you meant `.data ==`, or vice versa (intersection/cycle problems need identity, equality problems need data).
4. **Null-pointer crash from skipping a check** — writing `cur.next.next` without first confirming `cur.next is not None`.
5. **Not drawing it out** — attempting a multi-pointer rewiring (swap pairs, reorder list, k-group reversal) directly in code without sketching boxes and arrows first; this is where almost every "it's close but one link is wrong" bug comes from.
