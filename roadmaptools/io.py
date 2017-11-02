import urllib.request
import shutil


def download_file(url: str, file_name: str):
	with urllib.request.urlopen(url) as response, open(file_name, 'wb') as out_file:
		shutil.copyfileobj(response, out_file)

def get_osm_from_mapzen():
