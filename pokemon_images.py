#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

font_size = 128
nameFont = ImageFont.truetype('arial.ttf', font_size)

def parse_pokemon(filename):
	with open(filename) as f:
		lines = f.readlines()

	content = u','.join([l.decode('utf-8') for l in lines])
	return [pokemon.strip() for pokemon in content.split(',')]

def open_url(url):
	try:
		return opener.open(url)
	except urllib2.HTTPError:
		print 'Error with url ' + url
		raise

def resize_to_height(img, height):
	width = height * img.width / img.height
	return img.resize([width, height], Image.BICUBIC)

def get_pokemon_image_url(poke_id):
	return u'https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other-sprites/official-artwork/{}.png'.format(poke_id)

def safe_name(name):
	name = name.lower()
	name = re.sub(r'\s*\'\s*', '', name)
	name = re.sub(r'\s*\.\s*', '-', name)
	name = name.replace(u' ♀', '-f')
	name = name.replace(u' ♂', '-m')
	return name

def get_pokemon_image(pokemon):
	pokemon = safe_name(pokemon)
	url = u'http://pokeapi.co/api/v2/pokemon/{}/'.format(pokemon)

	response = open_url(url)
	data = json.load(response)

	url = get_pokemon_image_url(data['id'])
	img = Image.open(open_url(url))

	return resize_to_height(img, 400)

def build_pokemon_image(pokemon, progress):
	img = get_pokemon_image(pokemon)

	result = bg.copy()
	result.paste(img, [int(0.5 * bg.width - 0.5 * img.width), int(0.45 * bg.height - 0.5 * img.height)], img)

	nameSize = nameFont.getsize(pokemon)
	draw = ImageDraw.Draw(result)
	draw.text([int(0.5 * bg.width - 0.5 * nameSize[0]), 0.9 * bg.height - font_size], pokemon, font=nameFont)

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
	img.save(u'output/{0:04d}_{1}.png'.format(i, safe_name(data[1])))
	print safe_name(data[1])

if __name__ == '__main__':
	pokemon = parse_pokemon('pokemon.txt')

	p = Pool(16)
	p.map(partial(worker, len(pokemon)), enumerate(pokemon))