echo "export GOOGLE_APPLICATION_CREDENTIALS='$HOME/api-key.json'" >> ~/.bashrc
echo "export REPO='$PWD'" >> ~/.bashrc
source ~/.bashrc
pip install -r $REPO/requirements.txt
python setup/nltk_downloads.py
mkdir .cache
