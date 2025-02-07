import pathlib
import pytest
from unittest import mock, TestCase
from chunky_logs.parser.parser_chunk import ParserChunk

class TestParserChunk(TestCase):
    @mock.patch("chunky_logs.common.chunk.MetaData")
    def setUp(self, mock_metadata):
        group_path = pathlib.PurePosixPath('/tmp/test_group')
        chunk_name = pathlib.PurePosixPath('chunk_1')

        self.mock_metadata_instance = mock.MagicMock()
        mock_metadata.return_value = self.mock_metadata_instance

        self.metadata_file_patcher = mock.patch.object(self.mock_metadata_instance, "file", new_callable=mock.PropertyMock)
        self.metadata_file_property = self.metadata_file_patcher.start()
        self.metadata_file_property.return_value = 'chunk_1.metadata'

        self.test_parser_chunk = ParserChunk(group_path, chunk_name)

    def tearDown(self):
        self.metadata_file_patcher.stop()

    def test_read_success(self):
        test_data_lines = [
            "line1",
            "line2",
            "line3",
            "line4",
            "line5"
        ]
        test_tells_pos = [
            10,
            20,
            30,
            40,
            50
        ]
        expected_seeks = [
            None,
            10,
            20,
            30,
            40,
        ]

        mock_chunk_file = mock.mock_open()
        with mock.patch('builtins.open', mock_chunk_file):
            for line_data, tell_pos, expected_seek_pos in zip(test_data_lines, test_tells_pos, expected_seeks):
                mock_chunk_file.return_value.readline.return_value = line_data
                mock_chunk_file.return_value.tell.return_value = tell_pos

                # Check that the correct line is read, and that the position in the chunk is updated
                assert line_data == self.test_parser_chunk.read_line()
                assert tell_pos == self.test_parser_chunk._chunk_pos

                # Check that the seek is called starting after the first call
                if expected_seek_pos:
                    mock_chunk_file().seek.assert_called_with(expected_seek_pos)
                else:
                    mock_chunk_file().seek.assert_not_called()

    def test_has_changed(self):
        with mock.patch.object(self.mock_metadata_instance, "checksum", new='9256f72dec56351070913a92666bd6ad'):
            self.test_parser_chunk._current_checksum = '9256f72dec56351070913a92666bd6ad'

            assert False == self.test_parser_chunk.has_changed()
            self.mock_metadata_instance.reload.assert_not_called()

        with mock.patch.object(self.mock_metadata_instance, "checksum", new='4aceec376e84509844ca378775a18ebb'):
            self.test_parser_chunk._current_checksum = '9256f72dec56351070913a92666bd6ad'

            assert True == self.test_parser_chunk.has_changed()
            self.mock_metadata_instance.reload.assert_called_once()
