"""
Scripts related to dataset TSQA (Time Series Question Answering) from Time-MQA.
TSQA is a pretraining dataset for time-series large language models (LLMs) containing
multi-task question answering pairs over time-series data.

For more information please refer to:
https://github.com/WenjieDu/TSDB/tree/main/dataset_profiles/tsqa
"""

# Created by Wenjie Du <wenjay.du@gmail.com>
# License: BSD-3-Clause

from pathlib import Path

import pandas as pd

from ..utils.logging import logger
from ..utils.tsqa import TSQA_CSV_FILES, has_tsqa_files, snapshot_download


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
    Install it with: pip install "tsdb[tsqa]"
    """
    repo_local_path = Path(local_path)
    if not has_tsqa_files(repo_local_path):
        # Older TSDB releases stored the Hugging Face hub cache here instead
        # of a directly materialized raw dataset. Preserve that read path.
        repo_local_path = Path(snapshot_download(repo_id="Time-MQA/TSQA", repo_type="dataset", cache_dir=local_path))

    data = {}
    for task_name, rel_path in TSQA_CSV_FILES.items():
        file_path = repo_local_path / rel_path
        logger.info(f"Loading task '{task_name}' from {file_path}...")
        data[task_name] = pd.read_csv(file_path)

    return data
