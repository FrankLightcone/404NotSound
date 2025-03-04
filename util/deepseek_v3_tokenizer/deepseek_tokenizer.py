# DeepSeek V3 Tokenizer
# Source: https://api-docs.deepseek.com/zh-cn/quick_start/token_usage/
import transformers

"""
Source File: deepseek_tokenizer.py
"""
# chat_tokenizer_dir = "./"
#
# tokenizer = transformers.AutoTokenizer.from_pretrained(
#         chat_tokenizer_dir, trust_remote_code=True
#         )
#
# result = tokenizer.encode("Hello!")
# print(result)

"""
Attention:
It spends a lot of time to calaulate the length of the tokenized text.
Do not use it in the runtime main loop.
Or the program will be stuck.
"""
# Author: Ruijie Fan

chat_tokenizer_dir = "./"

def deepseek_tokenize_length(text: str):
    tokenizer = transformers.AutoTokenizer.from_pretrained(
        chat_tokenizer_dir, trust_remote_code=True
    )
    return len(tokenizer.encode(text))

def deepseek_tokenize_length_from_file(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()
    return deepseek_tokenize_length(text)


if __name__ == "__main__":
    text = "Hello!"
    print(deepseek_tokenize_length(text))