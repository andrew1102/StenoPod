import sys
import os
from google_speech_wrapper import speechWrapper
from cache_utility import cacheUtility

title  = sys.argv[1]
path = os.environ.get('REPO')

wrap = speechWrapper(title=title)
script = wrap.produceScript()

title = title.replace('.flac','.pkl')
cache_handler = cacheUtility(name=title)
cache_handler.cacheSave(script)
