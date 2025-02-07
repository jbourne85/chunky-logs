import pathlib
import pytest
import shutil
import tempfile
from unittest import mock, TestCase
from chunky_logs.parser.parser_chunk import ParserChunk

class TestParserChunk(TestCase):
    @mock.patch("chunky_logs.common.chunk.MetaData")
    def setUp(self, mock_metadata):
        self.test_data_directory = tempfile.mkdtemp()
        group_path = pathlib.PurePosixPath(self.test_data_directory)
        chunk_name = pathlib.PurePosixPath('chunk_1')

        self.mock_metadata_instance = mock.MagicMock()
        mock_metadata.return_value = self.mock_metadata_instance

        self.metadata_file_patcher = mock.patch.object(self.mock_metadata_instance, "file", new='chunk_1.metadata')
        self.metadata_file_property = self.metadata_file_patcher.start()

        self.test_parser_chunk = ParserChunk(group_path, chunk_name)

    def set_test_chunk_file_contents(self, file_contents):
        with open(self.test_parser_chunk._chunk_file, 'w') as test_chunk_file:
            test_chunk_file.writelines("\n".join(file_contents))

    def tearDown(self):
        self.metadata_file_patcher.stop()
        shutil.rmtree(self.test_data_directory)

    def test_read_success(self):
        test_data_lines = [
            "line1",
            "line2",
            "line3",
            "line4",
            "line5"
        ]
        self.set_test_chunk_file_contents(test_data_lines)

        for line_data in test_data_lines:
            # Check that the correct line is read, and that the position in the chunk is updated
            assert line_data == self.test_parser_chunk.read_line()

    def test_has_changed(self):
        with mock.patch.object(self.mock_metadata_instance, "checksum", new='9256f72dec56351070913a92666bd6ad'):
            self.test_parser_chunk._current_checksum = '9256f72dec56351070913a92666bd6ad'

            assert False == self.test_parser_chunk.has_changed()
            self.mock_metadata_instance.reload.assert_not_called()

        with mock.patch.object(self.mock_metadata_instance, "checksum", new='4aceec376e84509844ca378775a18ebb'):
            self.test_parser_chunk._current_checksum = '9256f72dec56351070913a92666bd6ad'

            assert True == self.test_parser_chunk.has_changed()
            self.mock_metadata_instance.reload.assert_called_once()

    def test_head(self):
        test_data_lines = [
            "line1",
            "line2",
            "line3",
            "line4",
            "line5",
            ""
        ]
        self.set_test_chunk_file_contents(test_data_lines)

        with mock.patch.object(self.mock_metadata_instance, "chunk_line_count", new=5):
            self.assertEqual('line1', self.test_parser_chunk.head())
            self.assertListEqual(test_data_lines[0:3], self.test_parser_chunk.head(3))
            self.assertListEqual(test_data_lines[0:-1], self.test_parser_chunk.head(100))

    def test_tail(self):
        test_data_lines = [
            "line1",
            "line2",
            "line3",
            "line4",
            "line5",
            ""
        ]
        self.set_test_chunk_file_contents(test_data_lines)
        with mock.patch.object(self.mock_metadata_instance, "chunk_line_count", new=5):
            self.assertEqual('line5', self.test_parser_chunk.tail())
            self.assertListEqual(test_data_lines[2:-1], self.test_parser_chunk.tail(3))
            self.assertListEqual(test_data_lines[0:-1], self.test_parser_chunk.tail(100))
