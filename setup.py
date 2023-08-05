from setuptools import setup, find_packages

from tsdb import __version__

with open("./README.md", encoding="utf-8") as f:
    README = f.read()

setup(
    name="tsdb",
    version=__version__,
    description="TSDB (Time-Series DataBase): A Python Toolbox Helping Load Open-Source Time-Series Datasets",
    long_description=README,
    long_description_content_type="text/markdown",
    license="GPL-3.0",
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
    ],
    packages=find_packages(exclude=["tests"]),
    include_package_data=True,
    install_requires=[
        "numpy",
        "scikit-learn",
        "pandas",
        "scipy",
    ],
    setup_requires=["setuptools>=38.6.0"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Database",
    ],
)
