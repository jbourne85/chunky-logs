from unittest import mock, TestCase
import pathlib
import pytest
from chunky_logs.common import Chunk, ChunkManagedFileError

class TestChunk(TestCase):
    @mock.patch("chunky_logs.common.chunk.MetaData")
    def setUp(self, mock_metadata):
        group_path = pathlib.PurePosixPath('/tmp/test_group')
        chunk_name = pathlib.PurePosixPath('chunk_1')

        mock_metadata_instance = mock.MagicMock()

        self.metadata_file_patcher = mock.patch.object(mock_metadata_instance, "file", new_callable=mock.PropertyMock)
        self.metadata_file_property = self.metadata_file_patcher.start()
        self.metadata_file_property.return_value = 'chunk_1.metadata'

        self.test_chunk = Chunk(group_path, chunk_name, mock_metadata_instance)

    def tearDown(self):
        self.metadata_file_patcher.stop()

    def test_constructor(self):
        """
        Tests the Chunk constructor, and tests the list of managed files are correct
        """
        assert self.test_chunk._managed_files == [
            pathlib.PurePosixPath('/tmp/test_group/chunk_1.chunk'),
            self.metadata_file_property
        ]

    @mock.patch('os.remove')
    def test_delete_success(self, patch_os_remove):
        """
        Tests the success case for Chunk.delete(), and that all managed files are requested to be removed
        """
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
        """
        Tests the failure case for Chunk.delete(), and that an exception is raised
        """
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
    @mock.patch('os.remove')
    def test_archive_success(self, patch_os_remove, patch_zip_file_write, patch_zip_file_init):
        """
        Tests the success case for Chunk.archive(), and that all managed files are archived and then removed
        """
        self.test_chunk._managed_files = [
            'managed_file_1',
            'managed_file_2',
            'managed_file_3',
        ]

        patch_zip_file_init.return_value = None
        self.test_chunk.archive()

        patch_zip_file_init.assert_called_once_with(pathlib.PurePosixPath('/tmp/test_group/chunk_1.zip'), 'w')

        assert patch_zip_file_write.call_count == 3
        patch_zip_file_write.assert_any_call('managed_file_1')
        patch_zip_file_write.assert_any_call('managed_file_2')
        patch_zip_file_write.assert_any_call('managed_file_3')

        assert patch_os_remove.call_count == 3
        patch_os_remove.assert_any_call('managed_file_1')
        patch_os_remove.assert_any_call('managed_file_2')
        patch_os_remove.assert_any_call('managed_file_3')

    @mock.patch('zipfile.ZipFile.__init__')
    @mock.patch('zipfile.ZipFile.write')
    @mock.patch('os.remove')
    def test_archive_failure(self, patch_os_remove, patch_zip_file_write, patch_zip_file_init):
        """
        Tests the failure case for Chunk.archive(), and that an exception is raised and no files are removed
        """
        self.test_chunk._managed_files = [
            'managed_file_1',
            'managed_file_2',
            'managed_file_3',
        ]

        patch_zip_file_init.return_value = None
        patch_zip_file_write.side_effect=OSError("Unable to create archive")

        with pytest.raises(ChunkManagedFileError):
            self.test_chunk.archive()

        patch_zip_file_init.assert_called_once_with(pathlib.PurePosixPath('/tmp/test_group/chunk_1.zip'), 'w')

        assert patch_zip_file_write.call_count == 1
        assert patch_os_remove.call_count == 0
