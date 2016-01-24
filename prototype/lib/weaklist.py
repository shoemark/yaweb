# from http://stackoverflow.com/questions/677978/weakref-list-in-python

import weakref


class WeakList(list):
    def __init__(self, seq=()):
        list.__init__(self)
        self._refs  = []
        self._dirty = False
        for item in seq:
            self.append(item)

    def _mark_dirty(self, ref):
        self._dirty = True

    def flush(self):
        self._refs  = [ref for ref in self._refs if ref() is not None]
        self._dirty = False

    def __getitem__(self, index):
        if self._dirty:
            self.flush()
        if isinstance(index, slice):
            return [ref() for ref in self._refs[index]]
        else:
            return self._refs[index]()

    def __setitem__(self, index, item):
        if isinstance(index, slice):
            self._refs[index] = [weakref.ref(item, self._mark_dirty) for i in item]
        else:
            self._refs[index] = weakref.ref(item, self._mark_dirty)

    def __delitem__(self, index):
        del self._refs[index]

    def __getslice__(self, i, j):
        return self.__getitem__(slice(i, j))

    def __setslice__(self, i, j, items):
        return self.__setitem__(slice(i, j, items))

    def __delslice__(self, i, j):
        return self.__delitem__(slice(i, j))

    def __iter__(self):
        for ref in self._refs:
            item = ref()
            if item is not None:
                yield item

    def __repr__(self):
        return "WeakList(%r)" % list(self)

    def __len__(self):
        if self._dirty:
            self.flush()
        return len(self._refs)

    def append(self, item):
        self._refs.append(weakref.ref(item, self._mark_dirty))

    def count(self, item):
        return list(self).count(item)

    def extend(self, items):
        for item in items:
            self.append(item)

    def index(self, item):
        return list(self).index(item)

    def insert(self, index, item):
        self._refs.insert(index, weakref.ref(item, self._mark_dirty))

    def pop(self, index):
        if self._dirty:
            self.flush()
        item = self._refs[index]()
        del self._refs[index]
        return item

    def remove(self, item_to_remove):
        if self._dirty:
            self.flush()
        for index, item in enumerate(self):
            if item == item_to_remove:
                del self[index]

    def reverse(self):
        self._refs.reverse()

    def sort(self, cmp=None, key=None, reverse=False):
        if self._dirty:
            self.flush()
        if key is not None:
            key = lambda ref, key=key: key(ref())
        else:
            key = apply
        self._refs.sort(cmp=cmp, key=key, reverse=reverse)

    def __add__(self, other):
        l = WeakList(self)
        l.extend(other)
        return l

    def __iadd__(self, other):
        self.extend(other)
        return self

    def __contains__(self, item):
        return item in list(self)

    def __mul__(self, n):
        return WeakList(list(self)*n)

    def __imul__(self, n):
        self._refs *= n
        return self
