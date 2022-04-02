# create the dir
mkdir raw

# download time-series measurement data
wget https://www.physionet.org/files/challenge-2012/1.0.0/set-a.tar.gz?download -O raw/set-a.tar.gz
wget https://www.physionet.org/files/challenge-2012/1.0.0/set-b.tar.gz?download -O raw/set-b.tar.gz
wget https://www.physionet.org/files/challenge-2012/1.0.0/set-c.tar.gz?download -O raw/set-c.tar.gz
# download outcome data
wget https://www.physionet.org/files/challenge-2012/1.0.0/Outcomes-a.txt?download -O raw/Outcomes-a.txt
wget https://www.physionet.org/files/challenge-2012/1.0.0/Outcomes-b.txt?download -O raw/Outcomes-b.txt
wget https://www.physionet.org/files/challenge-2012/1.0.0/Outcomes-c.txt?download -O raw/Outcomes-c.txt
