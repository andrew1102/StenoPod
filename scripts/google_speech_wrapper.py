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
                       num_gram=2,
                       num_speakers=2,
                       title=''):
       
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
        self.num_speakers = num_speakers
        self.cfreq_ngram = ConditionalFreqDist(ngram) 
        self.title = title 

    def Configure_API(self):

        if self.title.find('.flac') != -1:
            path = os.path.join(self.path, 'audio/'+self.title)
#            path = os.path.join(self.path,'.cache/'+self.title+'.flac')
            with open(path, 'rb') as audio_file:
                content = audio_file.read()
                self.audio = types.RecognitionAudio(content=content)   

        else: 
            self.audio = types.RecognitionAudio(uri="gs://twiml-mp3/"+self.title+".flac")

        self.config = types.RecognitionConfig(encoding=self.encoding,
                                 sample_rate_hertz=self.sample_rate,
                                 language_code=self.language_code,
                                 enable_automatic_punctuation=self.punctuation,
                                 enable_speaker_diarization=self.diarization,
                                 diarization_speaker_count=self.num_speakers,
                                 audio_channel_count=1,
                                 use_enhanced=self.enhanced,
                                 model=self.model,
                                 enable_word_time_offsets=self.time_offsets,
                                 enable_word_confidence=self.word_confidence,
                                 max_alternatives=self.max_alternatives,
                                 metadata=self.metadata,
                                 speech_contexts=[types.SpeechContext(phrases=self.phrases)])

    #Use if you don't care about speaker labeling
    def Produce_Script(self, rerank=True):

        script_name = self.title+'_scripts.pkl'
        score_name = self.title+'_scores.pkl'

        script, stop = Cache_Load(name=script_name)
        score, stop = Cache_Load(name=score_name)

        if stop: #Stop if files already exist in cache
            self.scripts, self.scores = script, score
            return self.scripts, self.scores

        self.Transcribe()

        if rerank: self.Rerank() #Perform n-gram reranking

        return self.scripts[0] #Return most probable one

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

    def Transcribe(self):

        name = self.title+'_result.pkl'
        responses, stop = Cache_Load(name=name)

        if stop: 
            self.results = responses.results
            return self.results

        self.Configure_API()

        # Detects speech and words in the audio file
        operation = self._client.long_running_recognize(self.config, self.audio)

        print('Waiting for operation to complete...')
        responses = operation.result(timeout=None)
        self.results = responses.results

        self.scripts, self.scores = [], []

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

        Cache_Save(item=responses, name=name)

    #Currently only supports labeling for 2 speakers
    def Produce_DiarScript(self):

        self.Transcribe()
        word_list = self.results[-1].alternatives[0].words

        script = []
        sam = word_list[0].speaker_tag
        tag = sam
        speech = 'Sam:\n'
        stop = 0
        for itr,word in enumerate(word_list):
            if tag != word.speaker_tag:
                script.append(speech)
                speech = ''
                if word.speaker_tag == sam: speech += '\n\nSam:\n'
                else: speech += '\n\nGuest:\n'
                stop = itr
            speech += word.word + ' '
            tag = word.speaker_tag
#            script.append(word.word)
        speech = '\nSam:\n'
        for word in word_list[stop:]:
            speech += word.word + ' '
        script.append(speech)
        return script
