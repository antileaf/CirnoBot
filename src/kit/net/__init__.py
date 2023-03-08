import requests

def save_image(url : str, path : str) -> bool:
	try:
		r = requests.get(url)
		with open(path, 'wb') as f:
			f.write(r.content)

		return True
	except:
		return False
