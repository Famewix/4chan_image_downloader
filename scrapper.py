import re
from urllib.request import urlretrieve, urlopen
from urllib.error import HTTPError
import os, sys
import json
from colorama import Fore, init
import argparse

###########################################
# https://github.com/xonsium/
###########################################

# all arguments
arg_parser = argparse.ArgumentParser(prog='Scrape 4chan thread images', usage='%(prog)s [options]')
arg_parser.add_argument('-u', '--url', type=str, help='4chan thread url')

args = arg_parser.parse_args()


init(autoreset=True)

count = 1
downloaded_files = 0
total = 1

try:
    os.mkdir("threads")
except FileExistsError:
    pass
os.chdir('threads')

current_dir = os.getcwd()


def download_image(image_url,  name):
    global count, downloaded_files
    try:
        urlretrieve(image_url, name)
        downloaded_files += 1
        print(f"{count}. Downloaded {Fore.GREEN}{image_url}{Fore.RESET} -- {round((downloaded_files*100)/total, 2)}%")
    except HTTPError:
        print(f"{Fore.RED}{image_url}{Fore.RESET} returned HTTP error.")
    count += 1

def sanitize_folder_name(name):
    # Characters not allowed in Windows folder names
    forbidden_chars = r'[<>:"/\\|?*\x00-\x1f]'
    # Replace forbidden characters with underscore
    sanitized_name = re.sub(forbidden_chars, '_', name)
    return sanitized_name

def fetch_json_from_api(url):
    try:
        response = urlopen(url)
    except HTTPError:
        print(f"url {url} returned a HTTP error. Bad url.")
        sys.exit()
    data = response.read()
    json_data = json.loads(data)
    return json_data

def generate_image_urls(url):
        # https://boards.4chan.org/hr/thread/4526451
        # https://i.4cdn.org/[board]/[4chan%20image%20ID].[file%20extension]
        BASE_URL = "https://a.4cdn.org/"
        MEDIA_URL = "https://i.4cdn.org/"
        image_urls = []
        board, id = url.split('/')[-3], url.split('/')[-1]
        api_url = BASE_URL + board + '/thread/' + id + '.json'
        json_data = fetch_json_from_api(api_url)
        current_thread_name = json_data.get('posts', 0)[0].get("sub", 0)
        posts = json_data.get('posts', 0)
        for post in posts:
            image_id = post.get('tim', 0)
            image_ext = post.get('ext', 0)
            if not image_id:
                continue
            image_url = f"{MEDIA_URL}{board}/{image_id}{image_ext}"
            image_urls.append(image_url)
        return current_thread_name, image_urls

def main(url):
    ### https://boards.4chan.org/hr/thread/4551968
    global total, count
    board, thread_id = url.split('/')[-3], url.split('/')[-1]

    try:
        os.mkdir(board)
    except FileExistsError:
        pass
    os.chdir(board)

    foldername, img_urls = generate_image_urls(url)
    if foldername:
        foldername = sanitize_folder_name(foldername)
    else:
        foldername = ''

    try:
        os.mkdir(f"{foldername}_{thread_id}")
    except FileExistsError:
        pass
    os.chdir(f"{foldername}_{thread_id}")
    files = os.listdir()
    total = len(img_urls)
    print(f"{Fore.RED}################## DOWNLOADING thread {url}{Fore.RESET}")
    print(f"{Fore.BLUE}Found {total} media files.{Fore.RESET}")
    print('')

    for url in img_urls:
        name_ = url.split('/')[4]
        if name_ not in files:
            download_image(url, name_)
        else:
            print(f"{count}.Skipping {Fore.GREEN} {url}.{Fore.RESET}")
            total -= 1
            count += 1

if __name__ == '__main__':
    if args.url:
        main(args.url)
    else:
        with open('threads.txt', "r") as f:
            for t_url in f.readlines():
                print(f"{Fore.RED}################## DOWNLOADING thread {t_url}{Fore.RESET}")
                main(t_url.replace('\n', ''))
                print('')
                print(f"{Fore.BLUE}Downloaded {downloaded_files} files.{Fore.RESET}")
                count = 1
                downloaded_files = 0
                total = 1
                os.chdir(current_dir)
    print('')
    print(f"{Fore.BLUE}Downloaded {downloaded_files} files.{Fore.RESET}")

