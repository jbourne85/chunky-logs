from unittest import mock, TestCase
import pathlib
import pytest
from chunky_logs.common.chunk import Chunk, ChunkManagedFileError

class TestChunk(TestCase):
    @mock.patch("chunky_logs.common.chunk.MetaData")
    def setUp(self, mock_metadata):
        group_path = pathlib.PurePosixPath('/tmp/test_group')
        chunk_name = pathlib.PurePosixPath('chunk_1')

        mock_metadata_instance = mock.MagicMock()
        mock_metadata.return_value = mock_metadata_instance

        self.metadata_file_patcher = mock.patch.object(mock_metadata_instance, "file", new_callable=mock.PropertyMock)
        self.metadata_file_property = self.metadata_file_patcher.start()
        self.metadata_file_property.return_value = 'chunk_1.metadata'

        self.test_chunk = Chunk(group_path, chunk_name)

    def tearDown(self):
        self.metadata_file_patcher.stop()

    def test_constructor(self):
        assert self.test_chunk._managed_files == [
            pathlib.PurePosixPath('/tmp/test_group/chunk_1.chunk'),
            self.metadata_file_property
        ]

    @mock.patch('os.remove')
    def test_delete_success(self, patch_os_remove):
        self.test_chunk._managed_files = [
            'managed_file_1',
            'managed_file_2',
            'managed_file_3',
        ]

        self.test_chunk.delete()

        assert patch_os_remove.call_count == 3
        patch_os_remove.assert_any_call('managed_file_1')
        patch_os_remove.assert_any_call('managed_file_2')
        patch_os_remove.assert_any_call('managed_file_3')

    @mock.patch('os.remove')
    def test_delete_failure(self, patch_os_remove):
        self.test_chunk._managed_files = [
            'managed_file_1',
            'managed_file_2',
            'managed_file_3',
        ]

        patch_os_remove.side_effect=OSError("File not found")

        with pytest.raises(ChunkManagedFileError):
            self.test_chunk.delete()

    @mock.patch('zipfile.ZipFile.__init__')
    @mock.patch('zipfile.ZipFile.write')
    def test_archive_success(self, patch_zip_file_write, patch_zip_file_init):
        self.test_chunk._managed_files = [
            'managed_file_1',
            'managed_file_2',
            'managed_file_3',
        ]

        patch_zip_file_init.return_value = None

        with mock.patch.object(self.test_chunk, 'delete') as mock_chunk_delete:
            self.test_chunk.archive()

            patch_zip_file_init.assert_called_once_with(pathlib.PurePosixPath('/tmp/test_group/chunk_1.zip'), 'w')

            assert patch_zip_file_write.call_count == 3
            patch_zip_file_write.assert_any_call('managed_file_1')
            patch_zip_file_write.assert_any_call('managed_file_2')
            patch_zip_file_write.assert_any_call('managed_file_3')

            mock_chunk_delete.assert_called_once()
