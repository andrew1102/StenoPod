import sys
import os
from google_speech_wrapper import Speech_Wrapper
from cache_utility import Cache_Save

title  = sys.argv[1]
path = os.environ.get('REPO')

wrap = Speech_Wrapper(title=title)
script = wrap.Produce_Script()
title = title.replace('.flac','.pkl')
Cache_Save(script, title)
