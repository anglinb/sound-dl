import requests
import json
# import sanitize
import os

r = requests.post('http://sounddrain.com/api.php',{'url':'https://soundcloud.com/candylanddjs/cash-cash-overtime-candyland'})
j = json.loads(r.content)
if 'url' in j:
	print 'got url'
	request = requests.get(j['url'], stream=True)
	print j['title']
	filepath = os.path.join(os.curdir, 'test.mp3')
	with open(filepath, "wb") as code:
	    for chunk in request.iter_content(1024):
	        if not chunk:
	            break

	        code.write(chunk)
else:
	print 'error'