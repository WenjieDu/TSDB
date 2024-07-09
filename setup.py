from setuptools import setup, find_packages

from tsdb import __version__

with open("./README.md", encoding="utf-8") as f:
    README = f.read()

setup(
    name="tsdb",
    version=__version__,
    description="TSDB (Time Series Data Beans): a Python toolbox helping load 172 open-source time-series datasets",
    long_description=README,
    long_description_content_type="text/markdown",
    license="BSD-3-Clause",
    author="Wenjie Du",
    author_email="wenjay.du@gmail.com",
    url="https://github.com/WenjieDu/TSDB",
    project_urls={
        "Documentation": "https://tsdb.readthedocs.io/",
        "Source": "https://github.com/WenjieDu/TSDB/",
        "Tracker": "https://github.com/WenjieDu/TSDB/issues/",
        "Download": "https://github.com/WenjieDu/TSDB/archive/main.zip",
    },
    keywords=[
        "data mining",
        "time series",
        "time-series analysis",
        "time-series database",
        "time-series datasets",
        "database",
        "datasets",
        "dataset downloading",
        "imputation",
        "classification",
        "forecasting",
        "partially observed",
        "irregularly sampled",
        "partially-observed time series",
        "incomplete time series",
        "missing data",
        "missing values",
        "pypots",
    ],
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    install_requires=[
        "tqdm",
        "numpy",
        "scipy",
        "pandas",
        "pyarrow",
        "requests",
        "scikit-learn",
    ],
    setup_requires=["setuptools>=38.6.0"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Database",
    ],
)
