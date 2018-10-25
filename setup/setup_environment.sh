echo "export GOOGLE_APPLICATION_CREDENTIALS='$HOME/api-key.json'" >> ~/.bashrc
echo "export REPO='$PWD'" >> ~/.bashrc
echo "alias newcache='rm -rf $REPO/.cache/*'" >> ~/.bashrc
echo "alias convert_all_audio='./scripts/convert_all_audio.sh'" >> ~/.bashrc
source ~/.bashrc
pip install -r setup/requirements.txt
python setup/nltk_download.py
mkdir .cache
