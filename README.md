# StenoPod
__AI Stenographer__ 

Welcome to StenoPod! Let's save some time by leveraging the power of AI to transcribe our favorite podcasts. The podcast in this repository is "This Week in Machine Learning & AI" (TWiML&AI). Feel free to choose your own podcast.

![alt text](https://ih1.redbubble.net/image.12551589.7724/sticker,375x360-bg,ffffff.u1.png)
![alt text](https://twimlai.com/files/2017/09/TWiML_banner_wide.png)

## Requisites
- Python: https://www.python.org
- Google Speech API: https://cloud.google.com/speech-to-text/
- NLTK: https://www.nltk.org
- Java: https://www.java.com/en/
- Tika: http://tika.apache.org

## Setup
Clone repository and set up environment. Note: setup_environment script only needs to be run once.
```
git clone https://github.com/andrew1102/StenoPod
cd StenoPod
chmod u+x setup/setup_environment.sh
./setup/setup_environment.sh (Need to change path for API key)
```
## Build Vocabulary
Now that your environment is set up, you're ready to build a vocabulary to do N-Gram reranking.
By default, your podcast pdf files will be used for your vocabulary. In order to effectively realize the power of n-gram reranking, more files are needed. For the TWiML&AI Podcast, I used a handful of deep learning papers in order to increase the frequency of machine learning terminology. In order to use your own custom vocabulary, the following steps must be taken:
```
- Create and populate new directory in the "corpus" directory
- Make a txt file with the names of the titles: ls *.pdf > new_list.txt (Remove the .pdf at the ends of the names in the file)
- In scripts/data_handler.py feed category list in constructor or call Add_Category function to clear the cache and add the new category
```
That's it! Now you're ready to use your new vocabulary.
## Preprocess Audio
Convert your audio files into FLAC files, as requested by Google Speech
```
cd audio
ffmpeg -i {your audio file} -{options} -ac 1 -ar 16000 {file name}.flac
```
If you'd like to convert all of the files in your audio directory, simply run from any location:
```
convert_all_audio
```
Now your aduio is ready to be handled by the Google Speech API!

## Run Transcription
By default, the wrapper is configured to separate sequences by speaker transitions. This can be changed in the Speech_Wrapper constructor. Audio transcription is quite simple, however. Just make sure your audio files are in a google cloud storage bucket, and be sure to change the path to your files in scripts/google_speech_wrapper.py line 60. To transcribe, do the following:
```
transcribe {title}
```
This can take some time, so it might be a good idea to perform this operation in a screen session. Congratulations, you now have a pdf transcript!

## Performance Evaluation
Let's now see how well the n-gram reranking performed. Running the transcribe script will produce overlapping histograms of the normalized Levenshtein Distance for baseline and reranked transcriptions. You should see a graph like this:

![Alt text](plots/Ross_Fadely_dists.png?raw=true "Title")

## Inference Pipeline
![Alt text](plots/inference_pipeline.png?raw=true "Title")
