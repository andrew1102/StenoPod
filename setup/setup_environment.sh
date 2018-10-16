echo "export GOOGLE_APPLICATION_CREDENTIALS=path/to/api-key.json" >> ~/.bashrc
echo "export REPO=$PWD" >> ~/.bashrc
echo "alias convert_audio='./$REPO/Scripts/convert_audio.sh'" >> ~/.bashrc
echo "alias transcribe1='python $REPO/Scripts/transcriber.py'" >> ~/.bashrc
echo "alias transcribe2='python $REPO/Scripts/eval_seq_rerank.py'" >> ~/.bashrc
echo "alias transcribe=transcribe1;transcribe2"
source ~/.bashrc
pip install -r $REPO/requirements.txt
mkdir .cache
