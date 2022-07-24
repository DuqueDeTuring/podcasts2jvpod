import os
from pathlib import Path
import requests
from urllib.request import urlopen
from xml.etree.ElementTree import parse

EPISODE_FILENAME_PADDING=3  

def rssFiles(xmls_dir):
    files = []
    with os.scandir(xmls_dir) as it:
        for entry in it:
            if not entry.name.startswith('.') and entry.is_file():
                files.append(entry.path)
    return files

def downloadFile(url, destination):
    print("downloading:" + destination)
    data = requests.get(url)
    with open(destination, "wb") as file:
        file.write(data.content)

def episodeFilename(number):
    # we need a specific format for the files, from 000.mp3 to 999.mp3
    return str(number).rjust(EPISODE_FILENAME_PADDING, "0")+".mp3"

def podcasts2jvpod(xmls_dir, mp3s_dir):
    files=rssFiles(xmls_dir)
    
    podcastNumber = 1

    with open("indice.txt", "wt", encoding="utf-8") as indexDoc:
        for f in files:
            doc = parse(f)

            podcastTitle = doc.findtext("channel/title")
            podcastDescription = doc.findtext("channel/description")
            print(f"# Podcast: {podcastNumber}. {podcastTitle}",file=indexDoc)
            print(f"## {podcastDescription}", file=indexDoc)
            file_path=Path(os.path.join(mp3s_dir,str(podcastNumber).rjust(2,"0")))
            file_path.mkdir(parents=True, exist_ok=True)

            podcastEpisode = 1
            for item in doc.iterfind("channel/item"):
                title = item.findtext("title")
                date = item.findtext("pubDate")
                link = item.findtext("link")
                enclosure = item.find("enclosure")
                mp3url = enclosure.get("url")
                if "?" in mp3url:
                    # remove url params
                    mp3url = mp3url[:mp3url.index("?")]

                print(f"+ Episodio: {podcastEpisode}. {title}",file=indexDoc)
                print(mp3url)
                downloadFile(mp3url, os.path.join(file_path, episodeFilename(podcastEpisode)))
                podcastEpisode += 1
            print("\n\n", file=indexDoc)
            podcastNumber += 1


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--xmls', metavar='path', required=True,
                        help='the path to workspace')
    parser.add_argument('--mp3s', metavar='path', required=True,
                        help='path to schema')
    args = parser.parse_args()
    podcasts2jvpod(args.xmls, args.mp3s)
