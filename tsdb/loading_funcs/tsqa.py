"""
Scripts related to dataset TSQA (Time Series Question Answering) from Time-MQA.
TSQA is a pretraining dataset for time-series large language models (LLMs) containing
multi-task question answering pairs over time-series data.

For more information please refer to:
https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/tsqa
"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: BSD-3-Clause

import os

import pandas as pd

from ..utils.logging import logger

# Mapping of task name -> relative path inside the HuggingFace repo
_TSQA_CSV_FILES = {
    "anomaly_detection": "Anomaly_Detection/anomaly_detection.csv",
    "classification": "Classification/classification.csv",
    "forecasting_imputation_1": (
        "Forecasting+Imputation/Forecasting+Imputation_1/forecasting_imputation1.csv"
    ),
    "forecasting_imputation_2": (
        "Forecasting+Imputation/Forecasting+Imputation_2/forecasting_imputation2.csv"
    ),
    "open_ended_qa": "Open_Ended_QA/open_ended_QA.csv",
}


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
        Keys are the task names:
        'anomaly_detection', 'classification', 'forecasting_imputation_1',
        'forecasting_imputation_2', 'open_ended_qa'.

    Notes
    -----
    This dataset requires the `huggingface_hub` package.
    Install it with: pip install huggingface_hub
    """
    try:
        from huggingface_hub import snapshot_download
    except ImportError as e:
        raise ImportError(
            "The 'huggingface_hub' package is required to load the TSQA dataset. "
            "Please install it with: pip install huggingface_hub"
        ) from e

    logger.info("Downloading TSQA dataset from HuggingFace (Time-MQA/TSQA)...")
    repo_local_path = snapshot_download(
        repo_id="Time-MQA/TSQA",
        repo_type="dataset",
        cache_dir=local_path,
    )

    data = {}
    for task_name, rel_path in _TSQA_CSV_FILES.items():
        file_path = os.path.join(repo_local_path, rel_path)
        logger.info(f"Loading task '{task_name}' from {file_path}...")
        data[task_name] = pd.read_csv(file_path)

    return data
