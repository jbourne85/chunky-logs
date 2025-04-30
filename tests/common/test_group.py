from unittest import mock, TestCase
import pathlib
import pytest
from chunky_logs.common import Group, Chunk


class TestGroup(TestCase):
    @mock.patch('os.path.exists')
    @mock.patch('os.makedirs')
    def setUp(self, os_make_dirs, os_path_exists):
        group_name = 'test_group'
        group_path = pathlib.Path('/tmp/test_group')
        max_line_count = 1440
        max_chunk_count = 20

        os_path_exists.return_value = False

        self.test_group = Group(group_name, group_path, max_line_count, max_chunk_count)

        self._os_make_dirs_patch = os_make_dirs
        self._os_path_exists_patch = os_path_exists

    def tearDown(self):
        pass

    def test_constructor(self):
        """
        Tests the Group constructor, and tests the initial state is setup
        """
        assert self.test_group.group_name == 'test_group'
        assert self.test_group.group_path == pathlib.PurePosixPath('/tmp/test_group').joinpath('test_group')
        assert self.test_group.max_line_count == 1440
        assert self.test_group.max_chunk_count == 20
        assert len(list(self.test_group)) == 0

        # Check that as the path does not exist and the directory is checked and then created
        assert self._os_path_exists_patch.call_count == 1
        assert self._os_make_dirs_patch.call_count == 1


    def test_add_existing_chunks(self):
        """
        Tests adding existing chunks to the internal buffer works
        """
        mock_metadata_instance = mock.MagicMock()

        # Populate the chunk list
        self.test_group._add_existing_chunk(
            Chunk(self.test_group.group_path, pathlib.Path('test_chunk_1'), mock_metadata_instance)
        )
        self.test_group._add_existing_chunk(
            Chunk(self.test_group.group_path, pathlib.Path('test_chunk_2'), mock_metadata_instance)
        )
        self.test_group._add_existing_chunk(
            Chunk(self.test_group.group_path, pathlib.Path('test_chunk_3'), mock_metadata_instance)
        )
        self.test_group._add_existing_chunk(
            Chunk(self.test_group.group_path, pathlib.Path('test_chunk_4'), mock_metadata_instance)
        )

        # Check the chunks exist
        assert len(list(self.test_group)) == 4
        assert self.test_group[0]._chunk_name == pathlib.Path('test_chunk_1')
        assert self.test_group[1]._chunk_name == pathlib.Path('test_chunk_2')
        assert self.test_group[2]._chunk_name == pathlib.Path('test_chunk_3')
        assert self.test_group[3]._chunk_name == pathlib.Path('test_chunk_4')