import pathlib
import pytest
import shutil
import tempfile
from unittest import mock, TestCase
from chunky_logs.author import AuthorChunk

class TestParserChunk(TestCase):
    @mock.patch("chunky_logs.author.author_chunk.AuthorMetaData")
    def setUp(self, mock_metadata):
        self.test_data_directory = tempfile.mkdtemp()
        group_path = pathlib.PurePosixPath(self.test_data_directory)
        chunk_name = pathlib.PurePosixPath('chunk_1')

        self.mock_metadata_instance = mock.MagicMock()
        mock_metadata.return_value = self.mock_metadata_instance

        self.test_author_chunk = AuthorChunk(group_path, chunk_name)

    @mock.patch("time.time_ns")
    @mock.patch("chunky_logs.author.author_chunk.file_md5sum")
    def test_write_line(self, patch_file_md5sum, patche_time_ns):
        patche_time_ns.return_value = 1739201327644200000
        patch_file_md5sum.return_value = 'xliyudtn3e'

        self.mock_metadata_instance.chunk_line_count = 0

        with mock.patch("builtins.open", mock.mock_open()) as mock_file:
            self.test_author_chunk.write_line('test_data_1')

            assert self.mock_metadata_instance.chunk_line_count == 1
            assert self.mock_metadata_instance.chunk_time_create == 1739201327644
            assert self.mock_metadata_instance.chunk_time_update == 1739201327644
            assert self.mock_metadata_instance.chunk_checksum_hash == 'xliyudtn3e'
            assert self.mock_metadata_instance.write_to_disk.call_count == 1
            mock_file.assert_called_once_with(self.test_author_chunk._chunk_file, 'a')
            file_handle = mock_file()
            file_handle.write.assert_called_once_with("1739201327644,test_data_1\n")

        with mock.patch("builtins.open", mock.mock_open()) as mock_file:
            patche_time_ns.return_value = 1739201725461603000
            patch_file_md5sum.return_value = 'eo2tzhwvd3'

            self.test_author_chunk.write_line('test_data_2')

            assert self.mock_metadata_instance.chunk_line_count == 2
            assert self.mock_metadata_instance.chunk_time_create == 1739201327644
            assert self.mock_metadata_instance.chunk_time_update == 1739201725461
            assert self.mock_metadata_instance.chunk_checksum_hash == 'eo2tzhwvd3'
            assert self.mock_metadata_instance.write_to_disk.call_count == 2
            mock_file.assert_called_once_with(self.test_author_chunk._chunk_file, 'a')
            file_handle = mock_file()
            file_handle.write.assert_called_once_with("1739201725461,test_data_2\n")
