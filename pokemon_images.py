import urllib
import urllib2
import cStringIO
import json
from PIL import Image


opener = urllib2.build_opener()
opener.addheaders = [('User-Agent', 'Pokemon')]

bg = Image.open('bg.png')

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

if __name__ == '__main__':
	pokemon = parse_pokemon('pokemon.txt')
	url = get_pokemon_image_url(pokemon[0])
	img = get_pokemon_image(url)

	bg.paste(img, [int(0.5 * bg.width - 0.5 * img.width), int(0.6 * bg.height - 0.5 * img.height)], img)

	bg.save('out.png')
