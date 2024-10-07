import os
import sys

sys.path.append(os.getcwd())

from dotenv import load_dotenv
from configs.config import Config
from infer.modules.vc.modules import VC
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