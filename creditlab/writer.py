"""One pinned Qwen writer and identical decoding for both experiment arms."""
import hashlib
import time
import torch
from transformers import AutoTokenizer


class SharedWriter:
    def __init__(self, model, tokenizer_path, max_tokens=320):
        self.model = model
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_path,local_files_only=True,trust_remote_code=True)
        self.max_tokens = max_tokens
        self.calls = []

    def __call__(self, system, user):
        prompt_hash = hashlib.sha256((system+'\0'+user).encode()).hexdigest()
        encoded = self.tokenizer.apply_chat_template(
            [{'role':'system','content':system},{'role':'user','content':user}],
            tokenize=True,add_generation_prompt=True,return_tensors='pt',return_dict=True,
            enable_thinking=False)
        started = time.perf_counter()
        with torch.inference_mode():
            output = self.model.generate(**encoded,do_sample=False,max_new_tokens=self.max_tokens)
        text = self.tokenizer.decode(output[0,encoded['input_ids'].shape[1]:],skip_special_tokens=True).strip()
        self.calls.append({'prompt_sha256':prompt_hash,'response':text,
                           'seconds':time.perf_counter()-started,
                           'new_tokens':int(output.shape[1]-encoded['input_ids'].shape[1])})
        return text
