import collections

class CircularBufferIndexError(IndexError):
    pass

class CircularBuffer:
    """
    This class represents a basic circular buffer. Newer items are added onto the tail of the buffer, once the buffer is
    full the oldest item (at the head) will be removed. The means the head is always the oldest data, and the tail is
    always the newest
    """
    def __init__(self, capacity):
        """
        Creates a new empty circular buffer
        :param capacity: This is the max size that the buffer can grow to
        """
        self._data = collections.deque(maxlen=capacity)
        self._N = capacity
        self._n = 0

    def push(self, new_data):
        """
        This pushes new data onto the circular buffer's tail
        :param new_data: This is the new data to push to the buffer
        :return:
        """
        if self.is_full():
            del self._data[0]
        self._data.append(new_data)
        self._n = min(self._n + 1, self._N)

    def is_full(self):
        """
        This returns a boolean value which indicates if the buffer has reached
        capacity. This is when the length == capacity
        :return: True if the buffer has reached capacity, False if not
        """
        return self._n == self._N

    def is_empty(self):
        """
        This returns a boolean value which indicates if the buffer is empty or not.
        Emptiness is indicated by when length is 0
        :return: True if the buffer is empty, False if not
        """
        return self._n == 0

    def _unknown_index_exception(self):
        """
        Class decorator for when accessing an unknown index
        """
        def decorator(*args):
            try:
                return self(*args)
            except IndexError as e:
                raise CircularBufferIndexError(f"Trying to access unknown index: {e}") from None
        return decorator

    @_unknown_index_exception
    def tail(self):
        """
        This gets the value at the tail of the buffer.
        :return: The value at the buffer's tail on success, raises CircularBufferIndexError on empty buffer
        """
        return self._data[self._n - 1]

    @_unknown_index_exception
    def head(self):
        """
        This gets the value at the head of the buffer.
        :return: The value at the buffer's head on success, raises CircularBufferIndexError on empty buffer
        """
        return self._data[0]

    def capacity(self):
        """
        Returns the total capacity of the buffer
        :return: capacity of the buffer
        """
        return self._N

    def length(self):
        """
        Returns the current length of the buffer
        :return: current length of the buffer
        """
        return self._n

    def __len__(self):
        """
        Returns the current length of the buffer (via the len command)
        :return: current length of the buffer
        """
        return self._n

    @_unknown_index_exception
    def __getitem__(self, index):
        """
        Implement the __getitem__ magic method so the class can be treated like an array
        """
        return self._data[index]

    @_unknown_index_exception
    def __setitem__(self, index, value):
        """
        Implement the __setitem__ magic method so the class can be treated like an array
        """
        self._data[index] = value
