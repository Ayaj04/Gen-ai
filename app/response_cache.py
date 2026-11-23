"""Small TTL/LRU cache for stateless answers; not agent conversations."""

from collections import OrderedDict
from copy import deepcopy
from threading import Lock
from time import monotonic

from app.observability import current_metrics

CACHE_MAX_ENTRIES = 128
CACHE_TTL_SECONDS = 300


class ResponseCache:
    def __init__(self, max_entries=CACHE_MAX_ENTRIES, ttl=CACHE_TTL_SECONDS, clock=monotonic):
        self.max_entries = max_entries
        self.ttl = ttl
        self.clock = clock
        self.entries = OrderedDict()
        self.lock = Lock()

    def clear(self):
        with self.lock:
            self.entries.clear()

    def get_or_compute(self, key, compute):
        metrics = current_metrics.get()
        with self.lock:
            now = self.clock()
            for stale in [k for k, (expires, _) in self.entries.items() if expires <= now]:
                del self.entries[stale]
            if key in self.entries:
                self.entries.move_to_end(key)
                if metrics is not None:
                    metrics.cache = "hit"
                return deepcopy(self.entries[key][1])
        if metrics is not None:
            metrics.cache = "miss"
        # Never cache exceptions. Concurrent misses may compute independently.
        result = compute()
        with self.lock:
            self.entries[key] = (self.clock() + self.ttl, deepcopy(result))
            self.entries.move_to_end(key)
            while len(self.entries) > self.max_entries:
                self.entries.popitem(last=False)
        return result


response_cache = ResponseCache()
