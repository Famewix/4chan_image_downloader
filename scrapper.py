from urllib.request import urlretrieve
from urllib.error import HTTPError
import requests
from bs4 import BeautifulSoup
import os, sys
from colorama import Fore, init
import argparse

###########################################
# https://github.com/xonsium/
###########################################

# all arguments
arg_parser = argparse.ArgumentParser(prog='Scrape 4chan thread images', usage='%(prog)s [options]')
arg_parser.add_argument('-u', '--url', type=str, help='4chan thread url', required=True, metavar='')

args = arg_parser.parse_args()

init(autoreset=True)

URL = args.url
count = 1
downloaded_files = 0
total = 1


def download_image(image_url,  name):
    global count, downloaded_files
    try:
        urlretrieve(image_url, name)
        downloaded_files += 1
        print(f"{count}. Downloaded {Fore.GREEN}{image_url}{Fore.RESET} -- {round((downloaded_files*100)/total, 2)}%")
    except HTTPError:
        print(f"{Fore.RED}{image_url}{Fore.RESET} returned HTTP error.")
    count += 1

def format_image_link(image_tag):
    image_tag = image_tag.a["href"]
    image_tag = f"https:{image_tag}"
    return image_tag


def main(url):
    ### https://boards.4chan.org/hr/thread/4551968
    global total, count
    thread_id = url.split("/")[-1]
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Status: {response.status_code} — Invalid URL I guess.\n")
        sys.exit()

    bs = BeautifulSoup(response.content, 'html.parser')
    div_with_image = bs.find_all("div", attrs={"class":"fileText"})
    subject = bs.find('div', attrs={'class': 'postInfo desktop'}).find('span', attrs={'class': 'subject'}).text
    foldername = subject
    try:
        os.mkdir(f"{foldername}_{thread_id}")
    except FileExistsError:
        pass
    os.chdir(f"{foldername}_{thread_id}")
    files = os.listdir()
    total = len(div_with_image)
    print(f"{Fore.BLUE}Found {total} media files.{Fore.RESET}")

    for tags in div_with_image:
        image_url = format_image_link(tags)
        name_ = image_url.split('/')[4]
        if name_ not in files:
            download_image(image_url, name_)
        else:
            print(f"{count}.{Fore.GREEN} Skipping {image_url}.{Fore.RESET}")
            total -= 1
            count += 1

if __name__ == '__main__':
    main(URL)
    print('')
    print(f"{Fore.BLUE}Downloaded {downloaded_files} files.{Fore.RESET}")

