import io
import linecache
import logging
import pathlib
from chunky_logs.common.chunk import Chunk, ChunkManagedFileError

class ParserChunkManagedFileError(ChunkManagedFileError):
    pass

class ParserChunkReadError(ChunkManagedFileError):
    pass

class ParserChunk(Chunk):
    def __init__(self, group_path: pathlib.Path, chunk_name: pathlib.Path):
        super().__init__(group_path, chunk_name)
        self._logger = logging.getLogger(self.__class__.__name__)
        self._chunk_pos = None
        self._current_checksum = self.metadata.checksum

    def read_line(self):
        """
        This will read a chunk file one line at a time. Repeated calls will continue to read from the last line read,
        this should allow clients to ingest the whole file one line at a time
        :return: The line read on success, once the end of the file is reached it will return None
        """
        try:
            with open(self._chunk_file, 'r') as chunk_data:
                if self._chunk_pos:
                    chunk_data.seek(self._chunk_pos)

                line = chunk_data.readline()

                if line:
                    self._chunk_pos = chunk_data.tell()
                return line.strip()
        except FileNotFoundError as e:
            raise ParserChunkManagedFileError(f"Chunk file not found: {e}") from None
        except Exception as e:
            raise ParserChunkReadError(f"Error while reading chunk: {e}") from None

    def head(self, line_count = 1):
        """
        This will get the first lines in a chunk
        :param line_count: The number of lines to fetch, it defaults to 1
        :return: Either the line, or a list of lines if a line_count > 1 is used (this list will be capped to at the
        number of lines in the file)
        """
        line_count = min(line_count, self.metadata.chunk_line_count)
        lines = []
        try:
            read_line = 1
            while len(lines) < line_count:
                lines.append(linecache.getline(str(self._chunk_file), read_line).strip())
                read_line += 1
        except FileNotFoundError as e:
            raise ParserChunkManagedFileError(f"Chunk file not found: {e}") from None
        except Exception as e:
            raise ParserChunkReadError(f"Error while reading chunk: {e}") from None

        if 1 == line_count:
            return lines[0]
        return lines

    def tail(self, line_count = 1):
        """
        This will display the last lines in a chunk
        :param line_count: The number of lines to fetch, it defaults to 1
        :return: Either the line, or a list of lines if a line_count > 1 is used (this list will be capped to at the
        number of lines in the file)
        """
        line_count = min(line_count, self.metadata.chunk_line_count)
        lines = []
        try:
            read_line = self.metadata.chunk_line_count
            while len(lines) < line_count:
                lines.insert(0, linecache.getline(str(self._chunk_file), read_line).strip())
                read_line -= 1
        except FileNotFoundError as e:
            raise ParserChunkManagedFileError(f"Chunk file not found: {e}") from None
        except Exception as e:
            raise ParserChunkReadError(f"Error while reading chunk: {e}") from None

        if 1 == line_count:
            return lines[0]
        return lines

    def has_changed(self):
            """
            This will use the checksum of the metadata file to decide if the chunk has been updated, this is lighter weight
            than relying on the checksum of the chunk file as it will most likely be magnitudes smaller
            :return: True if the metadata changes (indicating there is new data to parse in the chunk), False if not
            """
            current_checksum = self.metadata.checksum
            if current_checksum != self._current_checksum:
                self._logger.debug(f"Metadata file has been updated, reloading.")
                self.metadata.reload()
                self._current_checksum = current_checksum
                return True
            return False