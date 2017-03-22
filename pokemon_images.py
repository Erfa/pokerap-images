import urllib
import urllib2
import cStringIO
import json
from PIL import Image, ImageDraw, ImageFont
from multiprocessing import Pool
from functools import partial
import re


opener = urllib2.build_opener()
opener.addheaders = [('User-Agent', 'Pokemon')]

bg = Image.open('bg.png')

progressEmpty = Image.open('progress_empty.png')
progressFull = Image.open('progress_full.png')

nameFont = ImageFont.truetype('arial.ttf', 128)

def parse_pokemon(filename):
	with open(filename) as f:
		lines = f.readlines()

	content = u','.join(lines)
	return [pokemon.strip() for pokemon in content.split(',')]

def get_pokemon_image_url(pokemon):
	if pokemon.lower() == 'nidoran':
		pokemon = 'nidoran-f'

	pokemon = pokemon.lower()
	pokemon = re.sub(r'\s*\'\s*', '', pokemon)
	pokemon = re.sub(r'\s*\.\s*', '-', pokemon)

	url = u'http://pokeapi.co/api/v2/pokemon/{}/'.format(pokemon)

	try:
		response = opener.open(url)
		data = json.load(response)
	except urllib2.HTTPError:
		print 'Error with url ' + url
		raise

	return u'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other-sprites/official-artwork/{}.png'.format(data['id'])

def get_pokemon_image(url):
	try:
		img = Image.open(opener.open(url))
	except urllib2.HTTPError:
		print 'Error with url ' + url
		raise

	height = 400
	width = height * img.width / img.height
	return img.resize([width, height], Image.BICUBIC)

def build_pokemon_image(pokemon, progress):
	url = get_pokemon_image_url(pokemon)
	img = get_pokemon_image(url)

	result = bg.copy()
	result.paste(img, [int(0.5 * bg.width - 0.5 * img.width), int(0.45 * bg.height - 0.5 * img.height)], img)

	nameSize = nameFont.getsize(pokemon)
	draw = ImageDraw.Draw(result)
	draw.text([int(0.5 * bg.width - 0.5 * nameSize[0]), 0.9 * bg.height - nameSize[1]], pokemon, font=nameFont)

	result.paste(
		progressEmpty,
		[int(0.5 * bg.width - 0.5 * progressEmpty.width), int(0.1 * bg.height - 0.5 * progressEmpty.height)],
		progressEmpty,
	)

	bar = progressFull.crop([0, 0, int(progress * progressFull.width), progressFull.height])

	result.paste(
		bar,
		[int(0.5 * bg.width - 0.5 * progressEmpty.width), int(0.1 * bg.height - 0.5 * progressEmpty.height)],
		bar,
	)

	return result

def worker(n_total, data):
	i, pokemon = data
	img = build_pokemon_image(data[1], float(i + 1) / n_total)
	img.save('output/{0:04d}_{1}.png'.format(i, pokemon))
	print pokemon

if __name__ == '__main__':
	pokemon = parse_pokemon('pokemon.txt')

	p = Pool(16)
	p.map(partial(worker, len(pokemon)), enumerate(pokemon))
