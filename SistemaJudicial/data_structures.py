from typing import Any, Optional


# ─────────────────────────────────────────────
# NODE HELPERS
# ─────────────────────────────────────────────

class SinglyNode:
    """Node for singly-linked list."""
    def __init__(self, data: Any):
        self.data = data
        self.next: Optional["SinglyNode"] = None


class DoublyNode:
    """Node for doubly-linked list."""
    def __init__(self, data: Any):
        self.data = data
        self.prev: Optional["DoublyNode"] = None
        self.next: Optional["DoublyNode"] = None


# ─────────────────────────────────────────────
# QUEUE  (cases waiting to be processed)
# ─────────────────────────────────────────────

class CaseQueue:
    """
    FIFO queue implemented with a singly-linked list.
    Used to hold cases waiting to enter the judicial pipeline.
    """

    def __init__(self):
        self._head: Optional[SinglyNode] = None
        self._tail: Optional[SinglyNode] = None
        self._size: int = 0

    def enqueue(self, case) -> None:
        node = SinglyNode(case)
        if self._tail:
            self._tail.next = node
        self._tail = node
        if self._head is None:
            self._head = node
        self._size += 1

    def dequeue(self):
        if self._head is None:
            raise IndexError("Queue is empty")
        data = self._head.data
        self._head = self._head.next
        if self._head is None:
            self._tail = None
        self._size -= 1
        return data

    def peek(self):
        if self._head is None:
            return None
        return self._head.data

    def is_empty(self) -> bool:
        return self._size == 0

    def __len__(self) -> int:
        return self._size

    def to_list(self) -> list:
        result = []
        cur = self._head
        while cur:
            result.append(cur.data)
            cur = cur.next
        return result


# ─────────────────────────────────────────────
# STACK  (evidence — LIFO)
# ─────────────────────────────────────────────

class EvidenceStack:
    """
    LIFO stack for case evidence.
    Last evidence added is the first to be analyzed.
    """

    def __init__(self):
        self._items: list = []

    def push(self, evidence) -> None:
        self._items.append(evidence)

    def pop(self):
        if self.is_empty():
            raise IndexError("Stack is empty")
        return self._items.pop()

    def peek(self):
        if self.is_empty():
            return None
        return self._items[-1]

    def is_empty(self) -> bool:
        return len(self._items) == 0

    def __len__(self) -> int:
        return len(self._items)

    def to_list(self) -> list:
        return list(reversed(self._items))


# ─────────────────────────────────────────────
# ARRAY  (legal articles / law base)
# ─────────────────────────────────────────────

class LegalArticlesArray:
    """
    Fixed-capacity array that stores legal articles.
    Supports O(1) random access by article index.
    """

    def __init__(self, capacity: int = 200):
        self._capacity = capacity
        self._items: list = [None] * capacity
        self._size: int = 0

    def add(self, article: dict) -> int:
        if self._size >= self._capacity:
            raise OverflowError("Legal articles array is full")
        self._items[self._size] = article
        idx = self._size
        self._size += 1
        return idx

    def get(self, index: int) -> dict:
        if index < 0 or index >= self._size:
            raise IndexError(f"Index {index} out of range")
        return self._items[index]

    def search_by_category(self, category: str) -> list:
        return [
            self._items[i]
            for i in range(self._size)
            if self._items[i] and self._items[i].get("category") == category
        ]

    def __len__(self) -> int:
        return self._size

    def to_list(self) -> list:
        return [self._items[i] for i in range(self._size)]


# ─────────────────────────────────────────────
# SINGLY LINKED LIST  (case history)
# ─────────────────────────────────────────────

class CaseHistoryList:
    """
    Singly-linked list that records all resolved cases.
    New cases are appended; traversal goes oldest → newest.
    """

    def __init__(self):
        self._head: Optional[SinglyNode] = None
        self._size: int = 0

    def append(self, case) -> None:
        node = SinglyNode(case)
        if self._head is None:
            self._head = node
        else:
            cur = self._head
            while cur.next:
                cur = cur.next
            cur.next = node
        self._size += 1

    def find_by_id(self, case_id: str):
        cur = self._head
        while cur:
            if cur.data.case_id == case_id:
                return cur.data
            cur = cur.next
        return None

    def __len__(self) -> int:
        return self._size

    def to_list(self) -> list:
        result = []
        cur = self._head
        while cur:
            result.append(cur.data)
            cur = cur.next
        return result


# ─────────────────────────────────────────────
# DOUBLY LINKED LIST  (case stage pipeline)
# ─────────────────────────────────────────────

class StagePipeline:
    """
    Doubly-linked list representing the ordered judicial stages.
    Allows forward (advance) and backward (revert) navigation.
    Stages: Investigación ↔ Juicio ↔ Sentencia
    """

    def __init__(self):
        self._head: Optional[DoublyNode] = None
        self._tail: Optional[DoublyNode] = None
        self._current: Optional[DoublyNode] = None
        self._size: int = 0

    def add_stage(self, stage_name: str) -> None:
        node = DoublyNode(stage_name)
        if self._tail:
            node.prev = self._tail
            self._tail.next = node
        self._tail = node
        if self._head is None:
            self._head = node
            self._current = node
        self._size += 1

    def advance(self) -> Optional[str]:
        if self._current and self._current.next:
            self._current = self._current.next
            return self._current.data
        return None

    def revert(self) -> Optional[str]:
        if self._current and self._current.prev:
            self._current = self._current.prev
            return self._current.data
        return None

    @property
    def current_stage(self) -> Optional[str]:
        return self._current.data if self._current else None

    @property
    def has_next(self) -> bool:
        return self._current is not None and self._current.next is not None

    @property
    def has_prev(self) -> bool:
        return self._current is not None and self._current.prev is not None

    def reset(self) -> None:
        self._current = self._head

    def to_list(self) -> list:
        result = []
        cur = self._head
        while cur:
            result.append(cur.data)
            cur = cur.next
        return result
