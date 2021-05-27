from urllib.request import urlretrieve
from urllib.error import HTTPError
import requests
from requests.exceptions import MissingSchema, InvalidURL
from bs4 import BeautifulSoup
import os, sys

URL = input("4chan thread URL: ")
folder_name = input("Folder to save images: ")

def download_image(image_url,  name):
    try:
        urlretrieve(image_url, name)
        print(f"{image_url} is downloaded")
    except HTTPError:
        print(f"{image_url} returned HTTP error.")

def format_image_link(img_url):
    img_url = img_url["src"]
    img_url = img_url.replace("s.", '.')
    img_url = f"https:{img_url}"
    return img_url


def main(url, foldername):
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Status: {response.status_code} — Invalid URL I guess.\n")
        sys.exit()

    bs = BeautifulSoup(response.content, 'lxml')
    images = bs.find_all("img", attrs={"loading":"lazy"})
    try:
        os.mkdir(foldername)
    except FileExistsError:
        pass
    os.chdir(foldername)

    for image in images:
        image_src = format_image_link(image)
        name_ = image_src.split('/')[4]
        download_image(image_src, name_)

if __name__ == '__main__':
    main(URL, folder_name)
