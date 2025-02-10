import pytest
from chunky_logs.common.circular_buffer import CircularBuffer, CircularBufferIndexError

def test_construct():
    capacity = 10
    buffer = CircularBuffer(capacity)
    assert buffer.length() == 0
    assert len(buffer) == 0
    assert buffer.capacity() == capacity
    assert buffer.is_full() is False
    assert buffer.is_empty() is True

    with pytest.raises(CircularBufferIndexError):
        buffer.head()

    with pytest.raises(CircularBufferIndexError):
        buffer.tail()

    with pytest.raises(CircularBufferIndexError):
        buffer[0]

    with pytest.raises(CircularBufferIndexError):
        buffer[0] = 1
