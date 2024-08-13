"""
Scripts related to UCR&UAE datasets http://timeseriesclassification.com/index.php

Most of code comes from library tslearn https://github.com/tslearn-team/tslearn.

For more information please refer to:
https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/ucr_uea_datasets

"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: BSD-3-Clause

import os
import warnings

import numpy as np
from sklearn.utils.estimator_checks import _NotAnArray as NotAnArray


def load_ucr_uea_dataset(local_path, dataset_name):
    try:
        # if both TXT and ARFF files are provided, the TXT versions are
        # used
        # both training and test data must be available in the same format
        if _has_files(local_path, dataset_name, ext="arff"):
            X_train, y_train = _load_arff_uea(
                os.path.join(local_path, dataset_name + "_TRAIN.arff")
            )
            X_test, y_test = _load_arff_uea(
                os.path.join(local_path, dataset_name + "_TEST.arff")
            )
        elif _has_files(local_path, dataset_name, ext="txt"):
            X_train, y_train = _load_txt_uea(
                os.path.join(local_path, dataset_name + "_TRAIN.txt")
            )
            X_test, y_test = _load_txt_uea(
                os.path.join(local_path, dataset_name + "_TEST.txt")
            )
        else:
            warnings.warn(
                'dataset "%s" is not provided in either TXT '
                "or ARFF format and thus could not be loaded" % dataset_name,
                category=RuntimeWarning,
                stacklevel=2,
            )
            return None

        data = {
            "X_train": X_train,
            "y_train": y_train,
            "X_test": X_test,
            "y_test": y_test,
        }

        return data

    except Exception as exception:
        warnings.warn(
            'dataset "%s" could be downloaded but not '
            "parsed: %s" % (dataset_name, str(exception)),
            category=RuntimeWarning,
            stacklevel=2,
        )


def _has_files(data_dir, dataset_name, ext):
    """Determines whether some downloaded and unzipped dataset provides
    both training and test data in the given format.

    Parameters
    ----------
    dataset_name : str
        the name of the dataset
    ext : str or None
        the file extension without a dot, e.g `"txt"` or `"arff"`;
        if set to None (the default), `True` will be returned if either TXT
        or ARFF files are present

    Returns
    -------
    bool
        if there are both training and test files with the specified
        file extension
    """
    basename = os.path.join(data_dir, dataset_name)
    return os.path.exists(basename + "_TRAIN.%s" % ext) and os.path.exists(
        basename + "_TEST.%s" % ext
    )


def ts_size(ts):
    """Returns actual time series size.

    Final timesteps that have `NaN` values for all dimensions will be removed
    from the count. Infinity and negative infinity ar considered valid time
    series values.

    Parameters
    ----------
    ts : array-like
        A time series.

    Returns
    -------
    int
        Actual size of the time series.

    Examples
    --------
    >>> ts_size([1, 2, 3, np.nan])
    3
    >>> ts_size([1, np.nan])
    1
    >>> ts_size([np.nan])
    0
    >>> ts_size([[1, 2],
    ...          [2, 3],
    ...          [3, 4],
    ...          [np.nan, 2],
    ...          [np.nan, np.nan]])
    4
    >>> ts_size([np.nan, 3, np.inf, np.nan])
    3
    """
    ts_ = to_time_series(ts)
    sz = ts_.shape[0]
    while sz > 0 and np.all(np.isnan(ts_[sz - 1])):
        sz -= 1
    return sz


def to_time_series(ts, remove_nans=False):
    """Transforms a time series so that it fits the format used in ``tslearn``
    models.

    Parameters
    ----------
    ts : array-like
        The time series to be transformed.
    remove_nans : bool (default: False)
        Whether trailing NaNs at the end of the time series should be removed
        or not

    Returns
    -------
    np.ndarray of shape (sz, d)
        The transformed time series. This is always guaraneteed to be a new
        time series and never just a view into the old one.

    Examples
    --------
    >>> to_time_series([1, 2])
    array([[1.],
           [2.]])
    >>> to_time_series([1, 2, np.nan])
    array([[ 1.],
           [ 2.],
           [nan]])
    >>> to_time_series([1, 2, np.nan], remove_nans=True)
    array([[1.],
           [2.]])

    See Also
    --------
    to_time_series_dataset : Transforms a dataset of time series
    """
    ts_out = np.array(ts, copy=True)
    if ts_out.ndim <= 1:
        ts_out = ts_out.reshape((-1, 1))
    if ts_out.dtype != float:
        ts_out = ts_out.astype(float)
    if remove_nans:
        ts_out = ts_out[: ts_size(ts_out)]
    return ts_out


def to_time_series_dataset(dataset, dtype=float):
    """Transforms a time series dataset so that it fits the format used in
    ``tslearn`` models.

    Parameters
    ----------
    dataset : array-like
        The dataset of time series to be transformed. A single time series will
        be automatically wrapped into a dataset with a single entry.
    dtype : data type (default: float)
        Data type for the returned dataset.

    Returns
    -------
    np.ndarray of shape (n_ts, sz, d)
        The transformed dataset of time series.

    Examples
    --------
    >>> to_time_series_dataset([[1, 2]])
    array([[[1.],
            [2.]]])
    >>> to_time_series_dataset([1, 2])
    array([[[1.],
            [2.]]])
    >>> to_time_series_dataset([[1, 2], [1, 4, 3]])
    array([[[ 1.],
            [ 2.],
            [nan]],
    <BLANKLINE>
           [[ 1.],
            [ 4.],
            [ 3.]]])
    >>> to_time_series_dataset([]).shape
    (0, 0, 0)

    See Also
    --------
    to_time_series : Transforms a single time series
    """
    try:
        import pandas as pd

        if isinstance(dataset, pd.DataFrame):
            return to_time_series_dataset(np.array(dataset))
    except ImportError:
        pass
    if isinstance(dataset, NotAnArray):  # Patch to pass sklearn tests
        return to_time_series_dataset(np.array(dataset))
    if len(dataset) == 0:
        return np.zeros((0, 0, 0))
    if np.array(dataset[0]).ndim == 0:
        dataset = [dataset]
    n_ts = len(dataset)
    max_sz = max([ts_size(to_time_series(ts, remove_nans=True)) for ts in dataset])
    d = to_time_series(dataset[0]).shape[1]
    dataset_out = np.zeros((n_ts, max_sz, d), dtype=dtype) + np.nan
    for i in range(n_ts):
        ts = to_time_series(dataset[i], remove_nans=True)
        dataset_out[i, : ts.shape[0]] = ts
    return dataset_out.astype(dtype)


def _load_arff_uea(
    full_file_path_and_name,
    replace_missing_vals_with="NaN",
):
    """Load data from a classification/regression WEKA arff file to a 3D np array.

    Parameters
    ----------
    full_file_path_and_name: str
        The full pathname of the .ts file to read.
    replace_missing_vals_with: str
       The value that missing values in the text file should be replaced
       with prior to parsing.

    Returns
    -------
    data: np.ndarray
        time series data, np.ndarray (n_cases, n_channels, n_timepoints)
    y : np.ndarray of string or int
        target variable
    """
    instance_list = []
    class_val_list = []
    data_started = False
    is_multi_variate = False
    is_first_case = True
    n_cases = 0
    n_channels = 1
    with open(full_file_path_and_name, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                if (
                    is_multi_variate is False
                    and "@attribute" in line.lower()
                    and "relational" in line.lower()
                ):
                    is_multi_variate = True

                if "@data" in line.lower():
                    data_started = True
                    continue
                # if the 'data tag has been found, the header information
                # has been cleared and now data can be loaded
                if data_started:
                    line = line.replace("?", replace_missing_vals_with)

                    if is_multi_variate:
                        line, class_val = line.split("',")
                        class_val_list.append(class_val.strip())
                        channels = line.split("\\n")
                        channels[0] = channels[0].replace("'", "")
                        if is_first_case:
                            n_channels = len(channels)
                            n_timepoints = len(channels[0].split(","))
                            is_first_case = False
                        elif len(channels) != n_channels:
                            raise ValueError(
                                f" Number of channels not equal in "
                                f"dataset, first case had {n_channels} channel "
                                f"but case number {n_cases + 1} has "
                                f"{len(channels)}"
                            )
                        inst = np.zeros(shape=(n_channels, n_timepoints))
                        for c in range(len(channels)):
                            split = channels[c].split(",")
                            inst[c] = np.array([float(i) for i in split])
                    else:
                        line_parts = line.split(",")
                        if is_first_case:
                            is_first_case = False
                            n_timepoints = len(line_parts) - 1
                        class_val_list.append(line_parts[-1].strip())
                        split = line_parts[: len(line_parts) - 1]
                        inst = np.zeros(shape=(n_channels, n_timepoints))
                        inst[0] = np.array([float(i) for i in split])
                    instance_list.append(inst)
    return np.asarray(instance_list), np.asarray(class_val_list)


def _load_txt_uea(dataset_path):
    """Load arff file for uni/multi variate dataset

    Parameters
    ----------
    dataset_path: string of dataset_path
        Path to the TXT file to be read

    Returns
    -------
    x: np array of shape (n_timeseries, n_timestamps, n_features)
        Time series dataset
    y: np array of shape (n_timeseries, )
        Vector of targets

    Raises
    ------
    Exception: on any failure, e.g. if the given file does not exist or is
               corrupted
    """
    data = np.loadtxt(dataset_path)
    X = to_time_series_dataset(data[:, 1:])
    y = data[:, 0].astype(int)
    return X, y
