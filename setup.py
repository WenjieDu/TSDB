from setuptools import setup, find_packages

from tsdb.__version__ import version

with open('./README.md', encoding='utf-8') as f:
    README = f.read()

setup(
    name='tsdb',
    version=version,
    description='TSDB (Time-Series DataBase): A Python Toolbox Helping Load Open-Source Time-Series Datasets',
    long_description=README,
    long_description_content_type='text/markdown',
    license='GPL-3.0',
    author='Wenjie Du',
    author_email='wenjay.du@gmail.com',
    url='https://github.com/WenjieDu/TSDB',
    download_url='https://github.com/WenjieDu/TSDB/archive/main.zip',
    keywords=[
        'time series', 'time series database', 'time series datasets',
        'datasets', 'database', 'dataset downloading', 'data mining',
    ],
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    install_requires=[
        'numpy',
        'scikit_learn',
        'pandas',
        'scipy'
    ],
    setup_requires=['setuptools>=38.6.0'],
)
