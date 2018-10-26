import os
import pickle

class cacheUtility:

    def __init__(self, name):

        self.name = name.replace('.flac', '')
        self.path = os.environ.get('REPO')
        self.path = os.path.join(self.path, '.cache/'+ self.name)

    def cacheLoad(self):    
    
        if os.path.exists(self.path):
            with open(self.path,'rb') as f:
                item = pickle.load(f)
            return item, True
    
        else:
            return None, False
    
    def cacheSave(self, item):
    
        with open(self.path,'wb') as f:
            pickle.dump(item,f)
        return
