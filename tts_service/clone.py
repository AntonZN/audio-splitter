from bark.generation import load_codec_model, generate_text_semantic
from encodec.utils import convert_audio

import torchaudio
import torch
from hubert.hubert_manager import HuBERTManager
from hubert.pre_kmeans_hubert import CustomHubert
from hubert.customtokenizer import CustomTokenizer
import numpy as np

device = 'cpu'
model = load_codec_model(use_gpu=True if device == 'cuda' else False)



hubert_manager = HuBERTManager()
hubert_manager.make_sure_hubert_installed()
hubert_manager.make_sure_tokenizer_installed()

hubert_model = CustomHubert(checkpoint_path='data/models/hubert/hubert.pt').to(device)

tokenizer = CustomTokenizer.load_from_checkpoint('data/models/hubert/tokenizer.pth').to(device)

audio_filepath = 'test.wav'

wav, sr = torchaudio.load(audio_filepath)
wav = convert_audio(wav, sr, model.sample_rate, model.channels)
wav = wav.to(device)

semantic_vectors = hubert_model.forward(wav, input_sample_hz=model.sample_rate)
semantic_tokens = tokenizer.get_token(semantic_vectors)

with torch.no_grad():
    encoded_frames = model.encode(wav.unsqueeze(0))
codes = torch.cat([encoded[0] for encoded in encoded_frames], dim=-1).squeeze()

codes = codes.cpu().numpy()
semantic_tokens = semantic_tokens.cpu().numpy()

voice_name = 'test'
output_path = 'bark/assets/prompts/' + voice_name + '.npz'
np.savez(output_path, fine_prompt=codes, coarse_prompt=codes[:2, :], semantic_prompt=semantic_tokens)