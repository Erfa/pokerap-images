import urllib2
import json

opener = urllib2.build_opener()
opener.addheaders = [('User-Agent', 'Pokemon')]

def parse_pokemon(filename):
	with open(filename) as f:
		lines = f.readlines()

	content = u','.join(lines)
	return [pokemon.strip() for pokemon in content.split(',')]

def get_pokemon_image_url(pokemon):
	url = u'http://pokeapi.co/api/v2/pokemon/{}/'.format(pokemon.lower())
	response = opener.open(url)
	data = json.load(response)
	return u'https://github.com/PokeAPI/sprites/blob/master/sprites/pokemon/other-sprites/official-artwork/{}.png'.format(data['id'])

if __name__ == '__main__':
	pokemon = parse_pokemon('pokemon.txt')
	url = get_pokemon_image_url(pokemon[0])
	print url
