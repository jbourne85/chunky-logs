import logging
import os
import pathlib
import time
from chunky_logs.common.chunk import Chunk
from chunky_logs.common.circular_buffer import CircularBuffer

class Group:
    CHUNK_FILE_EXTENSION = 'dat'

    def __init__(self, group_name: str, group_path: pathlib.Path, max_line_count, max_chunk_count):
        """
        This creates a group that stores its data in chunk files in a given group path
        :param group_name: This is groups name
        :param group_path: This is the root path that the groups will be created under
        :param max_line_count: This is the maximum number of lines per chunk
        :param max_chunk_count: This is the maximum number of active chunks per group
        """
        self._logger = logging.getLogger(f"{self.__class__.__name__}")
        self._file_count  = 0
        self._chunks = CircularBuffer(max_chunk_count)

        self.group_name = group_name
        self.group_path = group_path.joinpath(group_name)
        self.max_line_count = max_line_count
        self.max_chunk_count = max_chunk_count

        if not os.path.exists(self.group_path):
            os.makedirs(self.group_path)

    def __iter__(self):
        """
        Allows class to be iterable
        :return:
        """
        for chunk in self._chunks:
            yield chunk

    def __getitem__(self, index: int):
        """
        This will allow clients of this class to iterate over a set of chunks that are currently loaded
        :param index: This is the index of the chunk to get
        :return: The chunk
        """
        return self._chunks[index]

    def _add_existing_chunk(self, data_chunk: Chunk):
        """
        This adds an existing chunk to the group
        :param data_chunk: This is the data chunk to add
        """
        self._chunks.push(data_chunk)
        self._file_count += 1
        self._logger.debug(
            f"Adding existing data file. "
            f" chunk.path={data_chunk.metadata.chunk_file}"
            f" chunk.line_count={data_chunk.metadata.chunk_line_count}"
            f" metadata.path={data_chunk.metadata.file}"
            f" chunks.count={self._file_count}")

    def _generate_unique_chunk_filename(self):
        """
        This generates a unique new chunk filename for the given group
        :return: A unique chunk filename
        """
        time_now_ms = int(time.time_ns() / 1000000)

        def construct_file_path(group_name, group_path, timestamp_ms, count):
            return group_path.joinpath(f"{group_name}.{timestamp_ms}.{count}.{Group.CHUNK_FILE_EXTENSION}")

        # Determine the first filename that doesn't have the same group_name/timestamp and count combination
        # This ensures that high frequency calls to this method results in unique file combinations
        count = 0
        filename = construct_file_path(self._group_name, self._group_path, time_now_ms, count)
        while os.path.exists(filename):
            count += 1
            filename = construct_file_path(self._group_name, self._group_path, time_now_ms, count)

        return filename