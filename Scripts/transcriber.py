import sys
import os
from google_speech_wrapper import Speech_Wrapper

title  = sys.argv[1]
length = sys.argv[2]

path = os.environ.get('REPO')

wrap = Speech_Wrapper()
script = []

if length == 'long': 
    path = os.path.join(path,'.cache/'+title+'.txt')
    script = wrap.Get_Scripts(title=title, rerank=True)

elif length == 'short':
    path = os.path.join(path,'Split_Files/'+title)
    if not(os.path.exists(path)): os.mkdir(path)
    path = os.path.join(path, title+'.txt')
with open(path, 'w') as f:
    for line in script:
        f.write(line)
