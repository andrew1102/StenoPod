from cache_utility import cacheUtility

from nltk import ngrams
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

import string
import os
from tika import parser

class dataHandler():

    def __init__(self,
                 categories=['podcast', 'machine learning']): 

        self.categories = categories
        self.path = os.environ.get('REPO')
        self.corpus_raw = u""

    #Support for podcast, machine learning, dialogue
    def addCategory(self, category=''):
        if category == '': return
        os.remove(os.path.join(self.path, '.cache/Word_List.pkl'))
        self.categories.append(category)

    def appendCorpus(self, folder, lines):

        #Remove punctuation
        translate_table = dict((ord(char), None) for char in string.punctuation)
        #Remove stop words
        stoplist = set(stopwords.words('english'))

        for line in lines:

            line = line.replace('\n','')

            raw = parser.from_file(os.path.join(self.path, 'corpus/'+folder+'/'+line+'.pdf'))

            text = raw['content']
            text = text.translate(translate_table)
            text = self.fixString(text)

            cache_handler = cacheUtility(name=line+'.pkl')
            cache_handler.cacheSave(item=text)

            self.corpus_raw += text 

    #Function to return the text from all of the true transcripts
    def createCorpus(self):
 
        name = 'Word_List.pkl'
        cache_handler = cacheUtility(name=name)
        corpus, stop = cache_handler.cacheLoad()

        if stop: return corpus      

        for category in self.categories:
       
            #Must add your own 
            if category == 'podcast':  

                print('Adding podcast transcripts...')        
                  
                #Name of your particular titles file
                name = os.path.join(self.path,'titleslist.txt')

                with open(name,'r') as f:

                    guests = f.readlines()   
                    self.appendCorpus(folder='podcasts', lines=guests)

            elif category == 'machine learning': 

                print('Adding machine learning papers...')        

                name = os.path.join(self.path,'paperlist.txt')

                with open(name,'r') as f:

                    guests = f.readlines()   
                    self.appendCorpus(folder='ml_papers', lines=guests)
                 
            # Tokenize
            corpus = word_tokenize(self.corpus_raw)

            # convert to lower case
            tokens = [w.lower() for w in corpus]
            # remove punctuation from each word
            table = str.maketrans('', '', string.punctuation)
            stripped = [w.translate(table) for w in tokens]
            # remove remaining tokens that are not alphabetic
            words = [word for word in stripped if word.isalpha()]
            # filter out stop words
            stop_words = set(stopwords.words('english'))
            corpus = [w for w in words if not w in stop_words]
  
            cache_handler = cacheUtility(name='Word_List.pkl')
            cache_handler.cacheSave(corpus)

        return corpus
    
    def getNGram(self,num_gram):
       
        name = str(num_gram) + '_gram_model.pkl'

        cache_handler = cacheUtility(name=name)
        ngram_model, stop = cache_handler.cacheLoad()
        
        if stop:
            return ngram_model
        
        print('Building vocab..') 
        corpus = self.createCorpus()

        # extracting the n-grams and sorting them according to their frequencies
        ngram_model = ngrams(corpus,num_gram)
        ngram_model = sorted(ngram_model, key=lambda item: item[1], reverse=True)

        cache_handler.cacheSave(item=ngram_model)

        return ngram_model

    def braces(self,test_str):
    
        test_str = str(test_str)
        spot1 = test_str.find('[')
        spot2 = test_str.find(']')
        test_str = test_str[:spot1]+test_str[spot2+1:]
        return test_str
    
    def fixString(self,line):
    
        line = line[54:].lstrip()
        line = self.braces(line)
        line = line.strip(".,?")
        line = line.encode('ascii','ignore')
        line = str(line)
        line = line.replace("b'","")
        line = line.replace('b"',"")
        line = line.replace("\n", " ")
        line = line.replace(r"\n", "")
        line = line.replace("--", "")
        line = line.replace(r".'",".")
        line = line.replace(r",'",",")
        line = line.replace(r'."',".")
        line = line.replace(r"\'","'")
        line = line.replace("?'","?")
        line = line.replace('?"',"?")
        line = line.replace('FR:','Guest:')
        line = line.replace('EPISODE','')
        line = line.replace('TWIML','')
        line = line.replace('Transcript','')
        return line
