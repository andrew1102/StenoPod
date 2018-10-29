import numpy as np
import io
import os
# Imports the Google Cloud client library
from google.cloud import speech_v1p1beta1 as speech
from google.cloud.speech_v1p1beta1 import enums
from google.cloud.speech_v1p1beta1 import types

from nltk import ConditionalFreqDist

from data_handler import dataHandler
from cache_utility import cacheUtility

class speechWrapper(object):

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
        dh = dataHandler()
        ngram = dh.getNGram(num_gram=num_gram)
        self.num_speakers = num_speakers
        self.cfreq_ngram = ConditionalFreqDist(ngram) 
        self.title = title 

        self.path = os.environ.get('REPO')
        self.path = os.path.join(self.path,'.cache/')

    def configureAPI(self):

        if self.title.find('.flac') != -1:
            with open(os.path.join(self.path, self.title), 'rb') as audio_file:
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
    def produceScript(self, rerank=True):

        script_name = self.title+'_scripts.pkl'
        score_name = self.title+'_scores.pkl'

        cache_handler = cacheUtility(name=script_name)
        script, stop = cache_handler.cacheLoad()
        cache_handler = cacheUtility(name=score_name)
        score, stop = cache_handler.cacheLoad()

        if stop: #Stop if files already exist in cache
            self.scripts, self.scores = script, score
            return self.scripts, self.scores

        self.transcribe()

        if rerank: self.rerank() #Perform n-gram reranking

        return self.scripts, self.scores #Return most probable one

    def rerank(self):

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

    def transcribe(self):

        name = self.title+'_result.pkl'
        cache_handler = cacheUtility(name=name)
        responses, stop = cache_handler.cacheLoad()

        if stop: 
            self.results = responses.results
            return self.results

        self.configureAPI()

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

        cache_handler.cacheSave(item=responses)

    #Currently only supports labeling for 2 speakers
    def produceDiarScript(self):

        self.Transcribe()
        word_list = self.results[-1].alternatives[0].words

        self.scripts, self.scores = [], []
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
        self.scripts.append(speech)
        self.scores.append(score)
        return scripts
