"""
TSDB test cases
"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: GLP-v3
import os
import unittest

import tsdb

DATASETS_TO_TEST = [
    'physionet_2012',
    'physionet_2019',
    'electricity_load_diagrams',
    'beijing_multisite_air_quality',
    'UCR_UEA_Wine',
]


class TestTSDB(unittest.TestCase):
    def test_available_datasets(self):
        available_datasets = tsdb.list_available_datasets()
        assert len(available_datasets) > 0

    def test_dataset_loading(self):
        for d_ in DATASETS_TO_TEST:
            data = tsdb.load_dataset(d_)
            assert isinstance(data, dict)

    def test_downloading_only(self):
        tsdb.download_and_extract('UCR_UEA_Wine', './save_it_here')
        file_list = os.listdir()
        assert len(file_list) > 0

    def test_dataset_purging(self):
        cached_datasets = tsdb.list_cached_data()
        assert isinstance(cached_datasets, list)
        tsdb.delete_cached_data('physionet_2012')  # delete single
        tsdb.delete_cached_data()  # delete all


if __name__ == '__main__':
    unittest.main()
