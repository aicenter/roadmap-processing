import os

from typing import Callable
from tqdm import tqdm


def process_dir(dir_path: str, function: Callable[[str], None]):
	walk = list(os.walk(dir_path))[0]
	path = walk[0]
	files = walk[2]

	# # remove the link to parent dir
	# files = files[1:]
	for filename in tqdm(files, desc="Processing directory"):
		function(path + filename)