import nltk
import string
import pickle
import numpy as np
import matplotlib.pyplot as plt
from distance import nlevenshtein
#import editdistance
from Data_Handler import Data_Handler
#import streamlit as st

def only_numerics(seq):
    seq_type= type(seq)
    return seq_type().join(filter(seq_type.isdigit, seq))

dh = Data_Handler()
bigram_model = dh.Build_Vocab()
cfreq_2gram = nltk.ConditionalFreqDist(bigram_model)
fdist = nltk.FreqDist(bigram_model)

# Output top 50 words
print("Word|Freq:")
for word, frequency in fdist.most_common(50):
    print(u'{}|{}'.format(word, frequency))

true_scripts = []
guest = 'Ross_Fadely'
dists,redists = [],[]

with open('Split_Files/'+guest+'/True_'+guest+'.txt','r') as f:
    true_scripts = f.read().lower()
    true_scripts = true_scripts.replace('. ',' ')
    true_scripts = true_scripts.replace('? ',' ')
    true_scripts = true_scripts.replace(', ',' ')
    true_scripts = true_scripts.split('\n')

for i in range(1,len(true_scripts)-1):
    true = true_scripts[i-1]
    if true == '': continue
    true = true.split(' ')
    true = true[1:-1]
#    print('true: '+str(true))
    guesses = []
    num = i
    num_str = ''
    if num < 10: num_str = '00'+str(num)
    elif num >= 10 and num<100: num_str = '0'+str(num)
    elif num >= 100 and num < len(true_scripts): num_str = str(num)
    else: break
    with open('Split_Files/'+guest+'/'+guest+'_'+num_str+'_single_word.txt','r') as f:
        guesses = f.read()
        guesses = guesses[1:]
        guesses = guesses.split(' ')
    with open('Split_Files/'+guest+'/'+guest+'_'+num_str+'_single_score.txt','r') as f:
        scores = f.read()
        scores = scores[1:]
        scores = scores.split(' ')
    for j in range(1,len(scores)-1):
        guess1 = guesses[j]
        guess2 = guesses[j+1]
        alternative = cfreq_2gram[guess1].most_common(5)
        score1 = float(scores[j])
        score2 = float(scores[j+1])
#        if score1>0.9 and score2 < 0.9:
#            print('#'*75)
#            print('guess 1: {}, with score: {}'.format(guess1,score1))
#            print('guess 2: {}, with score: {}'.format(guess2,score2))
#            print('alternatives: '+str(alternative))
#            print('#'*75)
