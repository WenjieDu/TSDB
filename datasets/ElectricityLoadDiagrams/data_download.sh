# set URL
DOWNLOAD_URL=https://archive.ics.uci.edu/ml/machine-learning-databases/00321/LD2011_2014.txt.zip

# create the dir
mkdir raw

# download data
wget "$DOWNLOAD_URL" -O raw/data.zip
