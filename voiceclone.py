import os
import shutil
import sys
sys.path.append(os.getcwd())
from dotenv import load_dotenv
from configs.config import Config
from infer.modules.vc.modules import VC
from pydub import AudioSegment
load_dotenv()

class VoiceClone:
    def __init__(self, model, index):
        self.f0up_key = 0
        self.f0method = "pm"
        self.index_rate = 0.66
        self.filter_radius = 3
        self.resample_sr = 0
        self.rms_mix_rate = 1
        self.protect = 0.33
        self.index = index
        self.model = model
        self.config = Config()
        self.vc = VC(self.config)
        self.vc.get_vc(self.model)
        self.split_folder = "split_audio"
    
    def offload(self):
        self.voice = None
        
    def convert(self, input_path):
        _, wav_opt = self.vc.vc_single(
            0,
            input_path,
            self.f0up_key,
            None,
            self.f0method,
            self.index,
            None,
            self.index_rate,
            self.filter_radius,
            self.resample_sr,
            self.rms_mix_rate,
            self.protect,
        )
        return wav_opt

    def split_audio(self, audio_path, output_folder, chunk_size_ms):
        if os.path.exists(output_folder):
            shutil.rmtree(output_folder)
        os.makedirs(output_folder,exist_ok=True)
        audio = AudioSegment.from_file(audio_path)
        duration_ms = len(audio)
        chunks = []
        for i in range(0, duration_ms, chunk_size_ms):
            chunk = audio[i:i + chunk_size_ms]
            chunk_name = f"{output_folder}/{os.path.basename(audio_path).split('.')[0]}_{i // 1000 + 1}.mp3"
            chunk.export(chunk_name, format="mp3")
            chunks.append(chunk_name)
            print("/",end="",flush=True)
        print("\n")
        return chunks

    def convert_chunks(self, input_audio,chunk_size=10):
        chunks = self.split_audio(input_audio, self.split_folder, chunk_size_ms=chunk_size * 1000)
        full_data = []
        for chunk in chunks:
            rate, data = self.convert(chunk)
            full_data.append(data)
            print(".",end="",flush=True)
        print("\n")
        full_data = [item for sublist in full_data for item in sublist]
        return rate, full_data
