import numpy as np
import io
import os
# Imports the Google Cloud client library
from google.cloud import speech_v1p1beta1 as speech
from google.cloud.speech_v1p1beta1 import enums
from google.cloud.speech_v1p1beta1 import types

from nltk import ConditionalFreqDist

from data_handler import Data_Handler
from cache_utility import Cache_Save, Cache_Load

class Speech_Wrapper(object):

    def __init__(self, model='phone_call',
                       language_code='en-US',
                       time_offsets=False,
                       punctuation=True,
                       diarization=True,
                       enhanced=True, #Need to enable GCP data logging
                       confidence=True,
                       max_alternatives=30, #30 seems to be maximum
                       phrases=['TWIML','twimlai.com','Charrington','AI'], #Hint words
                       num_gram=2):
       
                       
        self._service_account = 'twiml-transcribe@data-shard-217405.iam.gserviceaccount.com'
        self._key_file = os.path.join(os.environ.get('HOME'), 'api-key.json')
        # Add Authentication to Environment Vars
        os.environ['GOOGLE_APPLICATION_CREDENTIALS']=self._key_file 
        self._client = speech.SpeechClient()
        self.model = model
        self.path = os.environ.get('REPO')
        self.encoding=enums.RecognitionConfig.AudioEncoding.FLAC
        self.sample_rate = 16000
        self.language_code = language_code
        self.time_offsets = time_offsets
        self.punctuation = punctuation
        self.diarization = diarization
        self.enhanced = enhanced
        self.word_confidence = confidence
        self.max_alternatives = max_alternatives

        #Specific to TWiML&AI Podcast
        self.metadata = speech.types.RecognitionMetadata()
        self.metadata.interaction_type = (
          speech.enums.RecognitionMetadata.InteractionType.DISCUSSION)
        self.metadata.microphone_distance = (
          speech.enums.RecognitionMetadata.MicrophoneDistance.NEARFIELD)

        self.phrases = phrases 
        dh = Data_Handler()
        ngram = dh.Get_NGram(num_gram=num_gram)
        self.cfreq_ngram = ConditionalFreqDist(ngram)  

    def Configure_API(self, title):

         #Uncomment this for audio longer than 1 minute
        self.audio = types.RecognitionAudio(uri="gs://twiml-mp3/"+title+".flac")
    
        self.config = types.RecognitionConfig(encoding=self.encoding,
                                 sample_rate_hertz=self.sample_rate,
                                 language_code=self.language_code,
                                 enable_automatic_punctuation=self.punctuation,
                                 enable_speaker_diarization=self.diarization,
                                 audio_channel_count=1,
                                 use_enhanced=self.enhanced,
                                 model=self.model,
                                 enable_word_time_offsets=self.time_offsets,
                                 enable_word_confidence=self.word_confidence,
                                 max_alternatives=self.max_alternatives,
                                 metadata=self.metadata,
                                 speech_contexts=[types.SpeechContext(phrases=self.phrases)])

    def Get_Scripts(self, title, rerank=True):

        script_name = title+'_scripts.pkl'
        score_name = title+'_scores.pkl'

        script, stop = Cache_Load(name=script_name)
        score, stop = Cache_Load(name=score_name)

        if stop:
            self.scripts, self.scores = script, score
            return self.scripts, self.scores

        self.Transcribe(title=title)
  
        self.scripts = []
        self.scores = []   
        splits = []    
        speakers = []
        stop = 0

        words = self.results[-1].alternatives[0].words

        for i in range(1,len(words)-2):
            if words[i-1].speaker_tag != words[i].speaker_tag: 
                txt = words[i-1].word+' '+words[i].word+' '+words[i+1].word
                splits.append(txt)
                speakers.append(words[i-1].speaker_tag)

        for result in self.results:
            script = []
            score = []
            it2 = 0
            for alternative in result.alternatives:
                script.append(alternative.transcript)   
                score.append(alternative.confidence)   
                score, script = (list(t) \
                     for t in zip(*sorted(zip(score, script), reverse=True)))
            self.scripts.append(script)
            self.scores.append(score)

        if rerank: self.Rerank()

        final_script = []
        sam_tag = speakers[0]
        k = 0
        old_spot = 0

        for i in range(len(self.scripts)):
            script = self.scripts[i][0]
            for j in range(k,len(splits)):
                split = splits[j]
                split = split.split(' ')
                word0, word1, word2 = split[0], split[1], split[2]
                speaker = speakers[j]
                tag = '\nSam: \n'
                if speaker != sam_tag: tag = '\nGuest: \n' 
                tmp = script.replace(word1+' '+word2, tag + word1 + ' ' + word2)
                final_script.append(tmp)
                k += 1
                break
                
#                spot = script.find(split)
#                if spot != -1:
#                    tmp = split.split(' ')
#                    spot += len(tmp[0])
#                    if speaker == sam_tag: final_script.append('Sam:\n' + script[old_spot:spot]) 
#                    else: final_script.append('Guest:\n' + script[old_spot:spot]) 
#                    old_spot = spot
#                    k += 1
#            final_script.append(script)
#        Cache_Save(item = self.scores, name = score_name)
#        Cache_Save(item = self.scripts, name = script_name)

        return final_script

    def Rerank(self):

        epsilon = 1e-8
        api_weight = 0.9 #Maybe make trainable?

        new_scores = []

        #Loop over speaker transitions
        for i in range(0,len(self.scores)):
            scripts, scores = self.scripts[i], self.scores[i]
            prob_vec = []
            api_weight = 0.9
            #Loop over API predictions for sequence
            for j in range(0,len(scores)):
                script, score = scripts[j], scores[j]
                probs = 0
                #Loop over word pairs
                for k in range(0,len(script)-1):
                    word = script[k]
                    nextword = script[k+1]    
                    freq = self.cfreq_ngram[word].freq(nextword)
                    probs += freq
                prob_vec.append(probs)
            scores = np.asarray(scores)
            prob_vec = np.asarray(prob_vec)
            new_score = api_weight*scores + (1-api_weight)*prob_vec
            new_score,self.scripts[i][j]  = (list(t) \
                   for t in zip(*sorted(zip(new_score, scripts), reverse=True)))

    def Transcribe(self, title):

        name = title+'_result.pkl'
        responses, stop = Cache_Load(name=name)

        if stop: 
            self.results = responses.results
            return self.results

        self.Configure_API(title=title)

        # Detects speech and words in the audio file
        operation = self._client.long_running_recognize(self.config, self.audio)

        print('Waiting for operation to complete...')
        responses = operation.result(timeout=None)
        self.results = responses.results
        Cache_Save(item=responses, name=name)
