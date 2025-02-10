import logging
import pathlib
import time
from chunky_logs.common.chunk import Chunk
from chunky_logs.common.hashing import file_md5sum
from chunky_logs.author.author_metadata import AuthorMetaData

class AuthorChunk(Chunk):
    """
    This class knows how to author data to Chunks, and to update the metadata
    """
    def __init__(self, group_path: pathlib.Path, chunk_name: pathlib.Path):
        """
        This is the constructor for an AuthorChunk
        :param group_path: This is the path to the group under which this chunk lives
        :param chunk_name: This is the name for the chunk this instance represents
        """
        self._logger = logging.getLogger(self.__class__.__name__)
        super().__init__(group_path, chunk_name, AuthorMetaData(group_path, chunk_name))

    def write_line(self, line_data):
        """
        This writes a new line to the Chunk, along with updating the metadata
        :param line_data: This is the new line data to write (it should be able to be represented as a string)
        """
        time_now_ms = int(time.time_ns() / 1000000)
        # The chunk has just been created, set the relevant details
        if self.metadata.chunk_line_count == 0:
            self.metadata.chunk_time_create = time_now_ms

        # Write the data out
        with open(self._chunk_file, 'a') as chunk_data:
            chunk_data.write(f"{time_now_ms},{str(line_data)}\n")

        # Update the metadata and write to disk
        self.metadata.chunk_line_count += 1
        self.metadata.chunk_time_update = time_now_ms
        self.metadata.chunk_checksum_hash = file_md5sum(self._chunk_file)
        self.metadata.write_to_disk()
