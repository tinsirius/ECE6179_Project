#!/usr/bin/python3

from gtts import gTTS
import pysrt
from pydub import AudioSegment
from pathlib import Path
from tqdm import tqdm

class dataset_ECE6169:
    def __init__(self, generate_new = False):

        self.cut_dir = Path().absolute() / "data" / "attenborough"
        self.cut_dir.mkdir(parents=True, exist_ok=True)
        self.gtts_dir = Path().absolute() / "data" / "gtts"
        self.gtts_dir.mkdir(parents=True, exist_ok=True)
        self.text_dir = Path().absolute() / "data" / "text"
        self.text_dir.mkdir(parents=True, exist_ok=True)

        self.audio_directory = Path().absolute() / "raw_data" / "audio"
        self.subtitle_directory = Path().absolute() / "raw_data" / "subtitles"

    def filter_text(self, sub):
        sub_text = sub.text.replace('\n', ' ')
        sub_text = sub_text.replace('...', '')
        is_valid = ((sub_text[0].isalpha() or sub_text[0].isnumeric()) 
                        and len(sub_text.split()) > 2)
        return sub_text, is_valid

    def generate_on_name(self, video_name):

        audio_file = self.audio_directory / f"{video_name}.mp3"
        sub_file = self.subtitle_directory / f"{video_name}.srt"

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

if __name__ == "__main__":
    gen = dataset_ECE6169(generate_new = True)
    gen.generate_on_name("our_planet_1")









