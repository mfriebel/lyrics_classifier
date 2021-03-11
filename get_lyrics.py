#%%
"""
Downloads lyrics of artist from metrolyrics
"""
import requests, time, re, os
import urllib.request
from bs4 import BeautifulSoup
from pyfiglet import Figlet
from tqdm import tqdm
# Identifier 
header = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:83.0) Gecko/20100101 Firefox/83.0"}

def get_page_buttons(url):
    """Checks the button class of page and return its content"""
    http_request = requests.get(url, headers=header)

    if http_request.status_code == 404:
        raise Exception(f'Artist name ("{artist}") does not exists or input could not be handled.')

    pages_soup = BeautifulSoup(http_request.text, 'html.parser')
    pages = pages_soup.body.find_all(attrs={'class':'pagination'})[0]

    return pages

def get_all_lyrics_pages(artist):
    """Collects lyrics links from all artists pages"""
    lyrics_url = f"https://www.metrolyrics.com/{artist}-lyrics.html"

    # Retrieve section of html page buttons
    pages = get_page_buttons(lyrics_url)
    # Get links to lyrics
    all_links = get_lyrics_links(lyrics_url, artist)

    # Loop trough all next pages up to the end
    while pages.find_all(attrs={'class':'button next'}):
        # Get link to next page of artist
        next_page = pages.find_all(attrs={'class':'button next'})[0].get('href')
        # Update links list with lyrics links of next page
        all_links += get_lyrics_links(next_page, artist)
        time.sleep(1)
        # Go to next page and repeat
        pages = get_page_buttons(next_page)

    return all_links

def get_lyrics_links(url, artist):
    """Collects lyrics from an artists page"""

    http_request = requests.get(url, headers=header)

    # find each lyrics URL inside the artist page using RE and save to a list
    pattern = f'<a href=\"(.+-lyrics-{artist}\.html)\"'
    lyrics_links = re.findall(pattern, http_request.text)

    return lyrics_links

def download_lyrics_html(artist):
    """Collect lyrics links and download them as html """
    # retrive lyrics links of given artist
    lyric_links = get_all_lyrics_pages(artist)
    # Create new folder for a new artist  
    path = f'artists/{artist}/' 
    if not os.path.exists(path):
        os.mkdir(path)
        # Loop through lyrics URL list and write for each song a new html file 
        print(f'\n Downloading songs of artist: {artist}')
        for url in tqdm(lyric_links):
            time.sleep(1)
            song_title = re.findall(f'com/(.+)-lyrics-{artist}', url)[0]        # Get song title
            song_html= requests.get(url, headers=header)                         # Get song lyrics html
            #print(re.findall('<p class=\'verse\'>(.*)<br>|^(.*)</p>|^(.*)<br>', song_html.text))                             
            with open(f'artists/{artist}/{song_title}.html', 'w') as f:  # Write lyrics page to ".html" file
                f.write(song_html.text)
                f.close()
    else:
        print(f'Songs for {artist} already exists')


def retrieve_artists():
    """Collect artists to download via keyboard input"""
    artists = []
    banner = Figlet()
    print(banner.renderText('LYRICS SCRAPER'))
    name = 'start value' # need to start the loop
    while name:
        name = input(f'Please enter the artist: ')
        name = re.sub('[\s]', '-', name).lower()
        artists.append(name)
    return artists[:-1]

def slugify(name): # TODO: needs work
    pass

#%%
if __name__ == "__main__":
    artists = retrieve_artists()
    if not os.path.exists('artists'):
        os.mkdir('artists')
    for artist in artists:
        download_lyrics_html(artist)
    print('\n DOWNLOAD FINISHED!')