import sys
import os
from google_speech_wrapper import Speech_Wrapper

title  = sys.argv[1]
length = sys.argv[2]

path = os.environ.get('REPO')

wrap = Speech_Wrapper()
script = wrap.Get_Scripts(title=title, rerank=True)

path = os.path.join(path,'Split_Files/'+title)
if not(os.path.exists(path)): os.mkdir(path)
path = os.path.join(path, title+'.txt')

with open(path, 'w') as f:
    f.write(script[0])
