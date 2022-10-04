#!/usr/bin/python3

from gtts import gTTS
import pysrt
from pydub import AudioSegment
from pathlib import Path
from tqdm import tqdm
from zipfile import ZipFile
from urllib.request import urlopen
from io import BytesIO
import sys
import click
import json

TAG = "0.0.4"

class dataset_ECE6179:
    def __init__(self):
        self.audio_directory = Path().absolute() / "raw_data" / "audio"
        self.subtitle_directory = Path().absolute() / "raw_data" / "subtitles"

        self.cut_dir = Path().absolute() / "data" / "attenborough"
        self.cut_dir.mkdir(parents=True, exist_ok=True)
        self.gtts_dir = Path().absolute() / "data" / "gtts"
        self.gtts_dir.mkdir(parents=True, exist_ok=True)
        self.text_dir = Path().absolute() / "data" / "text"
        self.text_dir.mkdir(parents=True, exist_ok=True)

    def filter_text(self, sub):
        sub_text = sub.text.replace('\n', ' ')
        sub_text = sub_text.replace('...', '')
        is_valid = ((sub_text[0].isalpha() or sub_text[0].isnumeric()) 
                        and len(sub_text.split()) > 2)
        return sub_text, is_valid

    def generate_on_name(self, video_name):

        audio_file = self.audio_directory / f"{video_name}.mp3"
        sub_file = self.subtitle_directory / f"{video_name}.srt"

        if audio_file.is_file() and sub_file.is_file():
            subs = pysrt.open(sub_file)
            audio = AudioSegment.from_mp3(audio_file)

            valid_sub = []
            invalid_sub = []

            print(f"\nProcessing video \"{video_name}\":")
            for i, sub in enumerate(tqdm(subs)):
                sub_text, is_valid = self.filter_text(sub)
                if not is_valid:    
                    invalid_sub.append(sub_text)
                else:
                    valid_sub.append(f"{video_name}_{i}: {sub_text}")
                    
                    exported_filename = f"{video_name}_{i}.mp3"
                
                    startTime = sub.start.ordinal
                    endTime = sub.end.ordinal
                    extract = audio[startTime:endTime]
                    extract.export(self.cut_dir / exported_filename, format="mp3")

                    tts = gTTS(sub_text)
                    tts.save(self.gtts_dir / exported_filename)

            with open(self.text_dir / f"{video_name}_valid.txt", "w") as f:
                for line in valid_sub:
                    f.write(f"{line}\n")
            with open(self.text_dir / f"{video_name}_invalid.txt", "w") as f:
                for line in invalid_sub:
                    f.write(f"{line}\n")

        else:
            print(f"{video_name} is not a valid video")

    def generate_all(self):
        videos_list = Path().absolute() / "raw_data" / "videos.json"
        with open(videos_list, "r") as f:
            video_names = json.load(f)
        for video in video_names:
            self.generate_on_name(video)

def download_and_unzip(url, extract_to='.'):
        http_response = urlopen(url)
        zipfile = ZipFile(BytesIO(http_response.read()))
        zipfile.extractall(path=extract_to)

@click.command()
@click.option('--fetch-processed', '-fp', default = False, is_flag=True, show_default=True, help = "Fetch processed data")
@click.option('--generate-all', '-ga', default = False, is_flag=True, show_default=True, help = "generate the processed data on ALL audio the raw_data folder")
@click.option('--generate-on-name', '-gon', help = "generate on specific video only")
def ECE6179_data(fetch_processed, generate_all, generate_on_name):
    if fetch_processed:
            print("Downloading dataset")
            download_and_unzip(f"https://github.com/tinsirius/ECE6179_Project/releases/download/{TAG}/data.zip")
            sys.exit()
    else:
        raw_data_dir = Path().absolute() / "raw_data"
        if not raw_data_dir.exists():
            print("folder raw_data is not found in current directory, Downloading ...")
            download_and_unzip(f"https://github.com/tinsirius/ECE6179_Project/releases/download/{TAG}/raw_data.zip")
        
        gen = dataset_ECE6179()
        if not generate_on_name is None:
            gen.generate_on_name(generate_on_name)
        if generate_all:
            gen.generate_all()

if __name__ == "__main__":
    ECE6179_data()
