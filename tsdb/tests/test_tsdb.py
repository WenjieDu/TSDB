"""
TSDB test cases
"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: GLP-v3

import unittest

import tsdb


class TestTSDB(unittest.TestCase):
    def test_available_datasets(self):
        available_datasets = tsdb.list_available_datasets()
        assert len(available_datasets) > 0

    def test_dataset_loading(self):
        data = tsdb.load_specific_dataset('UCR_UEA_Wine')
        assert isinstance(data, dict)

    def test_dataset_purging(self):
        cached_datasets = tsdb.list_cached_data()
        assert isinstance(cached_datasets, list)
        returned_value = tsdb.delete_cached_data('UCR_UEA_Wine')  # delete single
        assert returned_value
        returned_value = tsdb.delete_cached_data()  # delete all
        assert returned_value


if __name__ == '__main__':
    unittest.main()
