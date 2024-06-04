from colorama import init, Fore
from typing import Dict
import urllib.parse as url_parser
from bs4 import BeautifulSoup
from lxml import etree
import datetime
import requests
import json
import os
from werkzeug.utils import secure_filename

init(autoreset=True)


class ScrapeContent:
    logpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), "log.json")
    allowed_netlocs = ["9anime.gs", "aniwave.to"]

    def __init__(self): ...

    def save(self, content: bytes, filename: str, force: bool = False) -> bool:
        """Download file from the web to local disk (folder)

        Args:
            content (bytes): Content of the file to write to local copy.
            filename (str): Name of the file to save as.
            force (bool, optional): If force is enabled, existing file will be overwritten with new one. Defaults to False.

        Returns:
            bool: Download state of the file (True means success and False mean failure.)
        """
        print(f"{Fore.LIGHTCYAN_EX}Writing file to Disk\r", end="")
        if os.path.exists(filename) and not force:
            return False

        with open(filename, "wb") as file:
            file.write(content)

        print(f"{Fore.LIGHTCYAN_EX}File has been written to {filename}")
        return True

    def writeLog(self, data: Dict) -> None:
        """Create Log of the process

        Args:
            data (Dict): What to write in the log - record data.
        """
        with open(self.logpath, "r+") as file:
            record = list(json.load(file))
            record.append(data)
            file.seek(0)
            file.truncate()
            json.dump(record, file, indent=4)

    def scrape(self, url: str, download_path: str = "Downloads"):
        parsed_result: url_parser.ParseResult = url_parser.urlparse(url)
        if parsed_result.netloc not in self.allowed_netlocs:
            print(f"{Fore.LIGHTRED_EX}Only domains under 9animes are allowed for now.")
            return

        print(
            f"{Fore.CYAN}Sending request to {parsed_result.scheme}://{parsed_result.netloc}"
        )


        response = requests.Response = requests.get(url)
        soup: BeautifulSoup = BeautifulSoup(response.text, features="html.parser")

        image_source: str = (
            soup.find("div", {"id": "player"})["style"]
            .split("('")[1]
            .removesuffix("')")
        )
        image_title: str = (
            etree.HTML(str(soup))
            .xpath(
                "/html/body/div[1]/div/div[1]/div/div/aside[1]/div[2]/div[1]/div[2]/h1"
            )[0]
            .text
        )
        filename = secure_filename(image_title + os.path.splitext(image_source)[1])

        os.makedirs(download_path, exist_ok=True)
        fullpath = os.path.join(download_path, filename)

        print(f"{Fore.CYAN}Downloading...", filename)
        result = self.save(requests.get(image_source).content, fullpath)
        if not result:
            print(f"{' ':>{len('Writting File to Disk')}}\r", end="")
            print(
                f"{Fore.LIGHTRED_EX}\nFile \n'{fullpath}' already exists.\nDo you want to overide it?"
            )
            if input("[Y/N] ").upper() in ["N", "NO"]:
                print(f"{Fore.LIGHTRED_EX}Download is cancled by the User.")
                return
            print()
            result = self.save(requests.get(image_source).content, fullpath, True)
        print(
            f"{Fore.LIGHTGREEN_EX}File downloaded successfully."
        )
        self.writeLog(
            {
                "name": image_title,
                "root": f"{parsed_result.scheme}://{parsed_result.netloc}",
                "url": url,
                "image_url": image_source,
                "filename": filename,
                "filepath": fullpath,
                "storage_directory": download_path,
                "file_url": f"file:///{fullpath.replace(os.sep, '/')}",
                "date": datetime.datetime.today().strftime("%d of %B, %Y, %I:%M %p"),
            }
        )


if __name__ == "__main__":
    scraper = ScrapeContent()
    scraper.scrape(
        "https://aniwave.to/watch/hikikomari-kyuuketsuki-no-monmon.m2j17/ep-12"
    )
