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

def test_circular_buffer():
    capacity = 10
    buffer = CircularBuffer(capacity)

    for i in range(1, 11):  # Add 1 -> 9 into the buffer (filling it)
        buffer.push(i)

    # Assert the buffer status
    assert buffer.length() == capacity
    assert buffer.capacity() == capacity
    assert buffer.head() == 1
    assert buffer.tail() == capacity
    assert buffer.is_full() is True

    for i in range(1, 11): # Assert the values in the buffer
        assert buffer[i - 1] == i

    for i in range(11, 21):  # Add 11 -> 20 into the buffer (filling it again)
        buffer.push(i)

    # Assert the buffer status
    assert buffer.length() == capacity
    assert buffer.capacity() == capacity
    assert buffer.head() == 11
    assert buffer.tail() == 20
    assert buffer.is_full() is True

    for i in range(1, 11): # Assert the values in the buffer
        assert buffer[i - 1] == i + capacity
