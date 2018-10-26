import sys
import os
import nltk
import numpy as np
#import matplotlib.pyplot as plt
from distance import nlevenshtein
from data_handler import dataHandler
from scipy.stats import ttest_rel

title = sys.argv[1]
path = os.environ.get('REPO')
path = os.path.join(path, '.cache')

#for file in files:
for filename in os.listdir(path):
    if not(title in filename): continue 
    print(filename)

api_weight = 0.9

if False:

    with open('Split_Files/'+guest+'/'+guest+'_'+num_str+'_script.txt','r') as f:
        guess = f.read()
        guess = guess.lower()
        guesses = guess.split('\n')
    with open('Split_Files/'+guest+'/'+guest+'_'+num_str+'_scores.pkl','rb') as f:
        scores = pickle.load(f)
    scores, guesses = (list(t) for t in zip(*sorted(zip(scores, guesses),reverse=True)))
    best_guess = guesses[0]
    rescores = []
    for ii in range(0,len(scores)):
        score = scores[ii]
        guess = guesses[ii].split(' ')
        guess = guess[1:-1]
        if ii==0:
            dist = nlevenshtein(guess,true,method=1)
            dist2 = nlevenshtein(guess,true,method=2)
            dist = 0.5*(dist+dist2)
            dists.append(dist)
        score_sum = 0
        for j in range(0,len(guess)-1):
            word1 = guess[j]
            word2 = guess[j+1]
            freq = cfreq_2gram[word1].freq(word2)
            score_sum += freq
        rescores.append(score_sum)
    scores = np.asarray(scores)
    rescores = np.asarray(rescores)
    rescores = (scores*api_weight + rescores*(1-api_weight))/(sum(scores)+sum(rescores))
    rescores, reguesses = (list(t) for t in zip(*sorted(zip(rescores, guesses),reverse=True)))
    reguess = reguesses[0]
    reguess2 = reguesses[0]
    reguess = reguess.split(' ')
    reguess = reguess[1:-1]
    redist = nlevenshtein(reguess,true,method=1)
    redist2 = nlevenshtein(reguess,true,method=2)
    redist = 0.5*(redist+redist2)
    redists.append(redist)

print('Original avg dist: '+str(sum(dists)/len(dists)))
print('New avg dist: '+str(sum(redists)/len(redists)))

new_guest = guest.split('_')
fig = plt.hist([dists,redists],label=['Nominal','Augmented'],bins=20)
print('numerator: '+str(np.sum(numerator)))
plt.title('Levenshtein Distance for '+new_guest[0]+' '+new_guest[1]+' Interview')
plt.legend(loc='upper right')
plt.xlabel("Distance")
plt.ylabel("Frequency")
plt.savefig(guest+"_dists.png")
print('Significance: '+str(ttest_rel(np.asarray(dists),np.asarray(redists))))
