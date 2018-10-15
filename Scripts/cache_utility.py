import os
import pickle

def Cache_Load(name):

    home = os.environ.get('REPO')
    path = os.path.join(home,'.cache/'+name)
    stop = False

    if os.path.exists(path):
        stop = True
        with open(path,'rb') as f:
            item = pickle.load(f)
        return item, stop

    else:
        stop = False
        return None, stop

def Cache_Save(item, name):
    home = os.environ.get('REPO')
    path = os.path.join(home,'.cache/'+name)

    with open(path,'wb') as f:
        pickle.dump(item,f)
    return
