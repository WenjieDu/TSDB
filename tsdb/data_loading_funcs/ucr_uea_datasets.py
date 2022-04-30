"""
Scripts related to UCR&UAE datasets http://timeseriesclassification.com/index.php

Most of code comes from library tslearn https://github.com/tslearn-team/tslearn.

"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: GLP-v3

import os
import warnings

import numpy
from sklearn.utils.estimator_checks import _NotAnArray as NotAnArray

try:
    from scipy.io import arff

    HAS_ARFF = True

except:
    HAS_ARFF = False


def load_ucr_uea_dataset(local_path, dataset_name):
    try:
        # if both TXT and ARFF files are provided, the TXT versions are
        # used
        # both training and test data must be available in the same format
        if _has_files(local_path, dataset_name, ext="txt"):
            X_train, y_train = _load_txt_uea(
                os.path.join(local_path, dataset_name + "_TRAIN.txt")
            )
            X_test, y_test = _load_txt_uea(
                os.path.join(local_path, dataset_name + "_TEST.txt")
            )
        elif _has_files(local_path, dataset_name, ext="arff"):
            X_train, y_train = _load_arff_uea(
                os.path.join(local_path, dataset_name + "_TRAIN.arff")
            )
            X_test, y_test = _load_arff_uea(
                os.path.join(local_path, dataset_name + "_TEST.arff")
            )
        else:
            warnings.warn("dataset \"%s\" is not provided in either TXT "
                          "or ARFF format and thus could not be loaded"
                          % dataset_name,
                          category=RuntimeWarning, stacklevel=2)
            return None

        data = {
            'X_train': X_train,
            'y_train': y_train,
            'X_test': X_test,
            'y_test': y_test
        }

        return data

    except Exception as exception:
        warnings.warn("dataset \"%s\" could be downloaded but not "
                      "parsed: %s" % (dataset_name, str(exception)),
                      category=RuntimeWarning, stacklevel=2)


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
    return (os.path.exists(basename + "_TRAIN.%s" % ext) and
            os.path.exists(basename + "_TEST.%s" % ext))


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
    >>> ts_size([1, 2, 3, numpy.nan])
    3
    >>> ts_size([1, numpy.nan])
    1
    >>> ts_size([numpy.nan])
    0
    >>> ts_size([[1, 2],
    ...          [2, 3],
    ...          [3, 4],
    ...          [numpy.nan, 2],
    ...          [numpy.nan, numpy.nan]])
    4
    >>> ts_size([numpy.nan, 3, numpy.inf, numpy.nan])
    3
    """
    ts_ = to_time_series(ts)
    sz = ts_.shape[0]
    while sz > 0 and numpy.all(numpy.isnan(ts_[sz - 1])):
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
    numpy.ndarray of shape (sz, d)
        The transformed time series. This is always guaraneteed to be a new
        time series and never just a view into the old one.

    Examples
    --------
    >>> to_time_series([1, 2])
    array([[1.],
           [2.]])
    >>> to_time_series([1, 2, numpy.nan])
    array([[ 1.],
           [ 2.],
           [nan]])
    >>> to_time_series([1, 2, numpy.nan], remove_nans=True)
    array([[1.],
           [2.]])

    See Also
    --------
    to_time_series_dataset : Transforms a dataset of time series
    """
    ts_out = numpy.array(ts, copy=True)
    if ts_out.ndim <= 1:
        ts_out = ts_out.reshape((-1, 1))
    if ts_out.dtype != float:
        ts_out = ts_out.astype(float)
    if remove_nans:
        ts_out = ts_out[:ts_size(ts_out)]
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
    numpy.ndarray of shape (n_ts, sz, d)
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
            return to_time_series_dataset(numpy.array(dataset))
    except ImportError:
        pass
    if isinstance(dataset, NotAnArray):  # Patch to pass sklearn tests
        return to_time_series_dataset(numpy.array(dataset))
    if len(dataset) == 0:
        return numpy.zeros((0, 0, 0))
    if numpy.array(dataset[0]).ndim == 0:
        dataset = [dataset]
    n_ts = len(dataset)
    max_sz = max([ts_size(to_time_series(ts, remove_nans=True))
                  for ts in dataset])
    d = to_time_series(dataset[0]).shape[1]
    dataset_out = numpy.zeros((n_ts, max_sz, d), dtype=dtype) + numpy.nan
    for i in range(n_ts):
        ts = to_time_series(dataset[i], remove_nans=True)
        dataset_out[i, :ts.shape[0]] = ts
    return dataset_out.astype(dtype)


def _load_arff_uea(dataset_path):
    """Load arff file for uni/multi variate dataset

    Parameters
    ----------
    dataset_path: string of dataset_path
        Path to the ARFF file to be read

    Returns
    -------
    x: numpy array of shape (n_timeseries, n_timestamps, n_features)
        Time series dataset
    y: numpy array of shape (n_timeseries, )
        Vector of targets

    Raises
    ------
    ImportError: if the version of *Scipy* is too old (pre 1.3.0)
    Exception: on any failure, e.g. if the given file does not exist or is
               corrupted
    """
    if not HAS_ARFF:
        raise ImportError("scipy 1.3.0 or newer is required to load "
                          "time series datasets from arff format.")
    data, meta = arff.loadarff(dataset_path)
    names = meta.names()  # ["input", "class"] for multi-variate

    # firstly get y_train
    y_ = data[names[-1]]  # data["class"]
    y = numpy.array(y_).astype("str")

    # get x_train
    if len(names) == 2:  # len=2 => multi-variate
        x_ = data[names[0]]
        x_ = numpy.asarray(x_.tolist())

        nb_example = x_.shape[0]
        nb_channel = x_.shape[1]
        length_one_channel = len(x_.dtype.descr)
        x = numpy.empty([nb_example, length_one_channel, nb_channel])

        for i in range(length_one_channel):
            # x_.dtype.descr: [('t1', '<f8'), ('t2', '<f8'), ('t3', '<f8')]
            time_stamp = x_.dtype.descr[i][0]  # ["t1", "t2", "t3"]
            x[:, i, :] = x_[time_stamp]

    else:  # uni-variate situation
        x_ = data[names[:-1]]
        x = numpy.asarray(x_.tolist(), dtype=numpy.float32)
        x = x.reshape(len(x), -1, 1)

    return x, y


def _load_txt_uea(dataset_path):
    """Load arff file for uni/multi variate dataset

    Parameters
    ----------
    dataset_path: string of dataset_path
        Path to the TXT file to be read

    Returns
    -------
    x: numpy array of shape (n_timeseries, n_timestamps, n_features)
        Time series dataset
    y: numpy array of shape (n_timeseries, )
        Vector of targets

    Raises
    ------
    Exception: on any failure, e.g. if the given file does not exist or is
               corrupted
    """
    data = numpy.loadtxt(dataset_path)
    X = to_time_series_dataset(data[:, 1:])
    y = data[:, 0].astype(numpy.int)
    return X, y
