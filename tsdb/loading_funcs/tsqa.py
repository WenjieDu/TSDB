"""
Scripts related to dataset TSQA (Time Series Question Answering) from Time-MQA.
TSQA is a pretraining dataset for time-series large language models (LLMs) containing
multi-task question answering pairs over time-series data.

For more information please refer to:
https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/tsqa
"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: BSD-3-Clause

from ..utils.logging import logger


def load_tsqa(local_path):
    """Load dataset TSQA from Time-MQA.

    Parameters
    ----------
    local_path : str,
        The local path of dir saving the raw data of TSQA.

    Returns
    -------
    data : dict
        A dictionary containing the TSQA dataset splits as pandas DataFrames.
        Keys are the available split names (e.g. 'train', 'validation', 'test')
        and values are the corresponding pandas DataFrames.

    Notes
    -----
    This dataset requires the `datasets` package from HuggingFace.
    Install it with: pip install datasets
    """
    try:
        from datasets import load_dataset
    except ImportError as e:
        raise ImportError(
            "The 'datasets' package is required to load the TSQA dataset. "
            "Please install it with: pip install datasets"
        ) from e

    logger.info("Loading TSQA dataset from HuggingFace (Time-MQA/TSQA)...")
    dataset = load_dataset("Time-MQA/TSQA", cache_dir=local_path)

    data = {}
    for split_name, split_data in dataset.items():
        logger.info(f"Converting split '{split_name}' to pandas DataFrame, shape: {split_data.shape}...")
        data[split_name] = split_data.to_pandas()

    return data
