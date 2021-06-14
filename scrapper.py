from urllib.request import urlretrieve
from urllib.error import HTTPError
import requests
from requests.exceptions import MissingSchema, InvalidURL
from bs4 import BeautifulSoup
import os, sys
from colorama import Fore, init
import keyboard

init(autoreset=True)

URL = input("4chan thread URL: ")
folder_name = input("Folder to save images: ")
count = 0

def download_image(image_url,  name):
	global count
	try:
		urlretrieve(image_url, name)
		print(f"{Fore.GREEN}{image_url}{Fore.RESET} is downloaded")
		count += 1
	except HTTPError:
		print(f"{Fore.RED}{image_url}{Fore.RESET} returned HTTP error.")

def format_image_link(image_tag):
	image_tag = image_tag.a["href"]
	image_tag = f"https:{image_tag}"
	return image_tag

def display_status(div):
	global count, img_num
	print(f"{Fore.BLUE}Downloaded {count} files out of {len(div)} | remaining: {round(count/len(div)*100)}% {Fore.RESET}")

def main(url, foldername):
	response = requests.get(url)
	if response.status_code != 200:
		print(f"Status: {response.status_code} — Invalid URL I guess.\n")
		sys.exit()

	bs = BeautifulSoup(response.content, 'lxml')
	div_with_image = bs.find_all("div", attrs={"class":"fileText"})
	try:
		os.mkdir(foldername)
	except FileExistsError:
		pass
	os.chdir(foldername)

	for tags in div_with_image:
		if keyboard.is_pressed('space'):
			display_status(div_with_image)
		image_url = format_image_link(tags)
		name_ = image_url.split('/')[4]
		download_image(image_url, name_)

if __name__ == '__main__':
	main(URL, folder_name)
	print('')
	print(f"{Fore.BLUE}Downloaded {count} files.{Fore.RESET}")
