#!/usr/bin/env python

"""Generate an image to accompany the literature summary
---

This script reads in the ChatGPT publication summary and generates an 
accompanying DALL-E image. The prompt for DALL-E is designed by 
ChatGPT based on the summary and some additional keywords.

Usage:
python dalle.py \
	-s | --summary: path to the text file with the publication 
					summary for which the images need to be 
					generated. This text needs to be included into the 
					prompt for DALL-E.
	-o | --output: file where the generated image is stored

"""

import getopt
import openai
import os
import requests
import sys
import yaml

from dotenv import load_dotenv


def build_dalle_prompt(text):
	response = openai.ChatCompletion.create(
		model="gpt-4",
		messages=[
			{'role': 'system', 'content': 'Your job is to take some scientific text and generate a \
				prompt for DALL-E to create a captivating image to accompany the text.'},
			{'role': 'user', 'content': f"""
				Below is the summary of a scientific publication, enclosed by triple backticks.
				Based on this summary, create a prompt for DALL-E so that it can generate a beautiful and 
				captivating image to accompany the summary. This prompt cannot be longer than 50 words.
				It also has to be simple, descriptive, and specific.
				At the end of the prompt, include the words "captivating", "scientific", "nature", 
				"publication-ready", and "science".

				```{text}```
				"""}
		]
	)
	return response['choices'][0]['message']['content']


def generate_image(prompt):
	try:
		response = openai.Image.create(
			prompt=prompt,
			n=1,
			size='1024x1024'
		)
		image_url = response['data'][0]['url']
		return image_url
	except openai.error.OpenAIError as e:
		print(e.http_status)
		print(e.error)
		return False


def main(argv):
	output_file = 'image.jpg'
	try:
		opts, args = getopt.getopt(argv, 's:o:', ['summary=', 
			'output='])
	except getopt.GetoptError:
		print('Input argument error')
		quit()
	for opt, arg in opts:
		if opt in ('-s', '--summary'):
			summary_file = arg
		elif opt in ('-o', '--output'):
			output_file = arg

	# Get the OpenAI secret key.
	load_dotenv()
	openai.api_key = os.environ.get("OPENAI_API_KEY")

	# Before we can generate an image with DALL-E, we need a prompt. 
	# We build this prompt using ChatGPT and pass it the summary 
	# together with some additional keywords. It's important to note 
	# that DALL-E prompts are capped at somewhere between 50 to 70 
	# words (there is some ambiguity on how they count words or 
	# tokens).
	print('\nReading the summary...')
	text = read_summary(summary_file)
	print('\nGenerating DALL-E prompt...')
	dalle_prompt = build_dalle_prompt(text)
	print(f'Prompt:\n{dalle_prompt}')
	print('\nGenerating DALL-E images...')
	image_url = generate_image(dalle_prompt)
	if image_url:
		save_image_from_url(image_url, output_file)
		print(f'\nYour image is ready 🥳 and stored here: {output_file}')
	else:
		print('\nCould not generate a DALL-E image 💀')


def read_summary(file):
	with open(file, 'r') as fh:
		file_content = yaml.safe_load(fh)
	return file_content['summary']


def save_image_from_url(url, file):
	data = requests.get(url).content
	with open(file, 'wb') as fh:
		fh.write(data)


if __name__ == '__main__':
	main(sys.argv[1:])
