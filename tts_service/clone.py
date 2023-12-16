import logging

from bark.generation import load_codec_model
from encodec.utils import convert_audio

import torchaudio
import torch
import numpy as np

from hubert.hubert_manager import HuBERTManager
from hubert.pre_kmeans_hubert import CustomHubert
from hubert.customtokenizer import CustomTokenizer

from models import Prompt

device = "cpu"
model = load_codec_model(use_gpu=True if device == "cuda" else False)


hubert_manager = HuBERTManager()
hubert_manager.make_sure_hubert_installed()
hubert_manager.make_sure_tokenizer_installed()

hubert_model = CustomHubert(checkpoint_path="data/models/hubert/hubert.pt").to(device)

tokenizer = CustomTokenizer.load_from_checkpoint(
    "data/models/hubert/tokenizer.pth", map_location=torch.device("cpu")
).to(device)


async def clone_voice(prompt_id: str):
    prompt = await Prompt.get(id=prompt_id)

    try:
        wav, sr = torchaudio.load(prompt.voice_path)
        wav = convert_audio(wav, sr, model.sample_rate, model.channels)
        wav = wav.to(device)

        semantic_vectors = hubert_model.forward(wav, input_sample_hz=model.sample_rate)
        semantic_tokens = tokenizer.get_token(semantic_vectors)

        with torch.no_grad():
            encoded_frames = model.encode(wav.unsqueeze(0))

        codes = torch.cat([encoded[0] for encoded in encoded_frames], dim=-1).squeeze()

        codes = codes.cpu().numpy()
        semantic_tokens = semantic_tokens.cpu().numpy()

        output_path = f"bark/assets/prompts/{prompt.id}.npz"

        np.savez(
            output_path,
            fine_prompt=codes,
            coarse_prompt=codes[:2, :],
            semantic_prompt=semantic_tokens,
        )
        status = True
    except Exception as e:
        status = False
        logging.debug(f"ERROR clone voice {e}")

    if status:
        prompt.is_efficient = True
        await prompt.save(update_fields=["is_efficient"])
