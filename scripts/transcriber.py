import sys
import os
from google_speech_wrapper import Speech_Wrapper

title  = sys.argv[1]
path = os.environ.get('REPO')

wrap = Speech_Wrapper(title=title)
script = wrap.Produce_DiarScript()
path = os.path.join(path,'.cache/'+title+'.txt')

with open(path, 'w') as f:
    for line in script:
        f.write(line)
