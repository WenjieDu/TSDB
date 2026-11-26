"""Raw Hugging Face access for the TSQA dataset."""

# License: BSD-3-Clause

from pathlib import Path

TSQA_CSV_FILES = {
    "anomaly_detection": "Anomaly_Detection/anomaly_detection.csv",
    "classification": "Classification/classification.csv",
    "forecasting_imputation_1": "Forecasting+Imputation/Forecasting+Imputation_1/forecasting_imputation1.csv",
    "forecasting_imputation_2": "Forecasting+Imputation/Forecasting+Imputation_2/forecasting_imputation2.csv",
    "open_ended_qa": "Open_Ended_QA/open_ended_QA.csv",
}


def has_tsqa_files(root: Path) -> bool:
    return all((root / name).is_file() and (root / name).stat().st_size > 0 for name in TSQA_CSV_FILES.values())


def snapshot_download(**kwargs):
    try:
        from huggingface_hub import snapshot_download as download
    except ImportError as exc:
        raise ImportError('TSQA requires huggingface_hub; install it with pip install "tsdb[tsqa]".') from exc
    return download(**kwargs)


def download_tsqa(repo_id: str, root: Path) -> None:
    snapshot_download(repo_id=repo_id, repo_type="dataset", local_dir=str(root))
    if not has_tsqa_files(root):
        raise RuntimeError("TSQA snapshot is missing required CSV files")
