import transformers
import torch

model_id = 'ISTA-DASLab/Meta-Llama-3-8B-Instruct-AQLM-2Bit-1x16'
hf_token = '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'

pipeline = transformers.pipeline(model=model_id, device='cuda', model_kwargs={'max_length': 200})

print(pipeline('Hello'))
