def parse_pokemon(filename):
	with open(filename) as f:
		lines = f.readlines()

	content = u','.join(lines)
	return [pokemon.strip() for pokemon in content.split(',')]

if __name__ == '__main__':
	pokemon = parse_pokemon('pokemon.txt')
	print(pokemon)
