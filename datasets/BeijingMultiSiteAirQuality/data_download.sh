# set URL
DOWNLOAD_URL=http://archive.ics.uci.edu/ml/machine-learning-databases/00501/PRSA2017_Data_20130301-20170228.zip

# create the dir
mkdir raw

# download data
wget "$DOWNLOAD_URL" -O raw/data.zip
