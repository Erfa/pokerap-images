import urllib
import urllib2
import cStringIO
import json
from PIL import Image, ImageDraw, ImageFont


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
	url = u'http://pokeapi.co/api/v2/pokemon/{}/'.format(pokemon.lower())
	response = opener.open(url)
	data = json.load(response)
	return u'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other-sprites/official-artwork/{}.png'.format(data['id'])

def get_pokemon_image(url):
	img = Image.open(opener.open(url))
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

if __name__ == '__main__':
	pokemon = parse_pokemon('pokemon.txt')

	img = build_pokemon_image(pokemon[0], 0.3)

	img.save('out.png')
