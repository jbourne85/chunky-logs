import tempfile
from chunky_logs.common.hashing import file_md5sum

def test_get_file_md5sum():
    temp_filename = tempfile.NamedTemporaryFile().name

    data = [
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore\n",
        "magna aliqua.Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo\n",
        "consequat.Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla\n",
        "pariatur.Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est\n",
        "laborum."
    ]

    with open(temp_filename, 'w') as test_file:
        test_file.writelines(data)

    assert file_md5sum(temp_filename) == '2e1c81e7816b8e75c617c80525344a3f'

    with open(temp_filename, 'w') as test_file:
        test_file.write('\n')

    assert file_md5sum(temp_filename) != '2e1c81e7816b8e75c617c80525344a3f'

def test_get_large_file_md5sum():
    temp_filename = tempfile.NamedTemporaryFile().name

    #Create a file larger than the block size (4k)
    data = [
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore\n",
        "magna aliqua.Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo\n",
        "consequat.Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla\n",
        "pariatur.Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est\n",
        "laborum."
    ]

    # Create an approx 100MB file
    with open(temp_filename, 'w') as test_file:
        for i in range(250000):
            test_file.writelines(data)

    assert file_md5sum(temp_filename) == '94a3d4bf17e438258768d3b708e606f1'

    with open(temp_filename, 'w') as test_file:
        test_file.write('\n')

    assert file_md5sum(temp_filename) != '94a3d4bf17e438258768d3b708e606f1'
