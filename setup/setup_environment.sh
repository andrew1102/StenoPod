echo "export GOOGLE_APPLICATION_CREDENTIALS='$HOME/api-key.json'" >> ~/.bashrc
echo "export REPO='$HOME/StenoPod'" >> ~/.bashrc
source $HOME/.bashrc
echo "alias git-ignore='echo $1 >> $REPO/.gitignore'" >> $HOME/.bashrc
echo "alias dump='$REPO/scripts/dump.sh $1'" >> $HOME/.bashrc
echo "alias newcache='$REPO/scripts/newcache.sh'" >> $HOME/.bashrc
echo "alias empty='$REPO/scripts/emptyTrash.sh'" >> $HOME/.bashrc
echo "alias convert_all_audio='$REPO/scripts/convert_all_audio.sh'" >> $HOME/.bashrc
source $HOME/.bashrc
pip install -r $REPO/setup/requirements.txt
python $REPO/setup/nltk_download.py
mkdir -p $REPO/.rmv
mkdir -p $REPO/.cache

#write out current crontab
crontab -l > mycron
#echo new cron into cron file
echo "00 00 * * * empty" >> mycron
#install new cron file
crontab mycron
rm mycron
