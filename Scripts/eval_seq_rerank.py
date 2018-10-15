import nltk
import pickle
import numpy as np
import matplotlib.pyplot as plt
from distance import nlevenshtein
from Data_Handler import Data_Handler
from scipy.stats import ttest_rel

dh = Data_Handler()
ngram_model = dh.Get_NGram(num_gram = 2)
cfreq_2gram = nltk.ConditionalFreqDist(ngram_model)
api_weight = 0.9

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
    true2 = true_scripts[i-1]
    if true == '':
        continue
    true = true.split(' ')
    true = true[1:-1]
    guesses = []
    num = i
    num_str = ''
    if num < 10: num_str = '00'+str(num)
    elif num >= 10 and num<100: num_str = '0'+str(num)
    elif num >= 100 and num < len(true_scripts): num_str = str(num)
    else: break
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
