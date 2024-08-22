import httpx
import openai
import tiktoken
import json
import uvicorn
import signal
import numpy as np
from PyPDF2 import PdfReader
from pymilvus.orm import utility
from starlette.middleware.cors import CORSMiddleware
from pymilvus import connections, Collection
from transformers import BertTokenizer, BertModel
import torch
import json
from tqdm import tqdm
import torch
from transformers import BertTokenizer, BertModel
from tqdm import tqdm
from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility
from fastapi import FastAPI, WebSocket
from pydantic import BaseModel
from fastapi import FastAPI, UploadFile, File
from extract_feature import feature_bart
from data_preprocess import load_data
from modelscope import AutoModelForCausalLM, AutoTokenizer
import torch
from concurrent.futures import ThreadPoolExecutor
import asyncio
import pdfplumber
from typing import Union
from docx import Document
import io
import PyPDF2

torch.manual_seed(0)

path = 'qwen/Qwen-14B-Chat'
tokenizer = AutoTokenizer.from_pretrained(path, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(path, torch_dtype=torch.float32, device_map='auto', trust_remote_code=True)
history = None

connections.connect("default", host="47.100.166.210", port="19530", user='root', password='')
collection_name = 'chat_qw'
collection = Collection(collection_name)

import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer, AutoModel
import json

tokenizer_bge = AutoTokenizer.from_pretrained('/home/zhengwen/huzhuoyue/minicpm/model/bge-large-zh-v1.5')
model_bge = AutoModel.from_pretrained('/home/zhengwen/huzhuoyue/minicpm/model/bge-large-zh-v1.5')


def get_embedding(file_path):
    texts = []
    max_length = 512

    def process_texts(sentences):
        print(sentences)
        encoded_input = tokenizer_bge(sentences, padding=True, truncation=True, return_tensors='pt')
        with torch.no_grad():
            model_output = model_bge(**encoded_input)
            sentence_embedding = model_output[0][:, 0]
        return sentence_embedding.tolist()

    with open(file_path, encoding='utf-8') as f:
        text = ""
        for line in f:
            status, txt_back = length_detection(text, line)
            if status:
                text += line.strip()
                print(f"text length:{len(text)}")
            else:
                texts.append(text)
                text = txt_back

    texts = [text for text in texts if text]

    res_feature = process_texts(texts)


    with open('insert_feature.json', 'w') as f:
        json.dump(res_feature, f)
        print('提取完成')
    return res_feature, texts


def get_query_embedding(query_text):
    def process_texts(sentences):
        encoded_input = tokenizer_bge(sentences, padding=True, truncation=True, return_tensors='pt')
        with torch.no_grad():
            model_output = model_bge(**encoded_input)
            sentence_embedding = model_output[0][:, 0]
        return sentence_embedding.tolist()

    embeddings_list = process_texts([query_text])
    print(embeddings_list)
    return embeddings_list


def length_detection(a_str, line_str):
    ori_str = a_str
    a_str = a_str + " " + line_str
    if len(a_str) >= 105:
        return False, line_str
    else:
        return True, a_str


def pdf_upload(file):
    output_path = "/home/zhengwen/huzhuoyue/minicpm/test.txt"
    try:
        with file.file as pdf_file:
            reader = PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)

    except Exception as e:
        print(f"PDF 写入text.txt 遇到问题{e}")
        return False
    return True


def read_embedding():
    embedding_path = 'insert_feature.json'
    with open(embedding_path, 'r') as f:
        embedding = json.load(f)

    file_path = 'test.txt'
    texts = []
    with open(file_path, encoding='utf-8') as f:
        for line in f:
            text = line.strip()
            texts.append(text)

    return embedding, texts


def insert_embedding(embedding, texts):
    mr = collection.insert([embedding, texts])

    collection.flush()
    print("ok116")
    return mr.succ_count


def query_db(collection_name, pid, query_str, topk=8):
    collection = Collection(collection_name)
    collection.load(partition_names=[pid])
    search_params = {"metric_type": "IP", "params": {"nprobe": 64}}

    query_data = get_query_embedding(query_str)
    print([query_data][0])
    results = collection.search(
        data=query_data,
        anns_field="embedding",
        param=search_params,
        limit=topk,
        output_fields=["text"]
    )
    res = []
    for hits in results:
        for hit in hits:
            score = round(hit.distance, 3)
            if score >= 185:
                res.append({
                    "score": score,
                    "text": hit.entity.get('text')
                })
    collection.release()
    return res


def retrieve(collection_name, pid, query_str):
    limit = 3750
    res = query_db(collection_name, pid, query_str, topk=15)
    print(f"这是retrieve的res: {res}")
    prompt_start = (
            "请结合下面我给你的已知材料信息回答我的问题，如果是总结或者报告类的问题，回答越详细越好,不少于500字.\n\n" + "段落:\n"
    )
    prompt_end = (
        f"\n\n问题: {query_str}\n回答:"
    )
    # 取出相似地向量
    contexts = [x['text'] for x in res]
    prompt = 'None'
    if len(res) == 0:
        prompt = prompt

    else:
        for i in range(0, len(contexts)):
            if len("\n\n---\n\n".join(contexts[:i])) >= limit:
                prompt = (
                        prompt_start +
                        "\n\n---\n\n".join(contexts[:i - 1]) + "\n\n" +
                        prompt_end
                )
                break
            elif i == len(contexts) - 1:
                prompt = (
                        prompt_start +
                        "\n\n---\n\n".join(contexts) + "\n\n" +
                        prompt_end
                )
    return prompt

def enhance_chatgpt(prompt):
    history = None
    res = model.chat(tokenizer, prompt,
                     system="你是一个根据已知信息进行回答和总结并润色答案的机器人，结合材料的时候尽可能保留材料，总结性的回答越详细越好",
                     temperature=0.9, top_p=0.8, history=history)
    return res


def ori_chatgpt(query_str):
    history = None
    res, history = model.chat(tokenizer, query_str, system="你是个基础问答机器人,请你根据自己的信息进行回答，越详细越好",
                              temperature=0.9, top_p=0.8, history=history)
    return res


def get_text_from_file(file: UploadFile) -> Union[bool, None]:
    """
    根据文件类型提取文本内容，并将内容写入test.txt。
    如果文件格式不支持，则返回False。
    """
    filename = file.filename
    try:
        with open('/home/zhengwen/huzhuoyue/minicpm/test.txt', 'w', encoding='utf-8') as f:
            if filename.lower().endswith('.txt'):
                content = file.file.read().decode()
                f.write(content)
            elif filename.lower().endswith(('.docx', '.doc')):
                doc = Document(io.BytesIO(file.file.read()))
                content = '\n'.join([para.text for para in doc.paragraphs])
                f.write(content)
            elif filename.lower().endswith('.json'):
                content = file.file.read().decode()
                f.write(content)
            elif filename.lower().endswith('.pdf'):
                with io.BytesIO(file.file.read()) as file_obj:
                    reader = PyPDF2.PdfFileReader(file_obj)
                    content = '\n'.join([page.extract_text() for page in reader.pages if page.extract_text()])
                    f.write(content)
            else:
                return False
    except Exception as e:
        print(f"Error processing file {filename}: {e}")
        return False

    return True


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




class Item2(BaseModel):
    query: str


executor_raw = ThreadPoolExecutor()


@app.websocket("/model/raw_socket")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        item = Item2(**json.loads(data))

        loop = asyncio.get_running_loop()
        async for txt in run_in_executor(executor_raw, model.chat_stream, tokenizer, item.query, history=history,
                                         system='你是一个根据已知信息进行回答和总结并润色答案的机器人，结合材料的时候尽可能保留材料，总结性的回答越详细越好'):
            await websocket.send_text(txt)

        await websocket.send_json({'ans': 'DONE'})

        await websocket.close()


executor_enhance = ThreadPoolExecutor()


@app.websocket('/model/enhance_socket')
async def enhance_gpt(websocket: WebSocket):
    await websocket.accept()

    while True:
        data = await websocket.receive_text()
        item = Item(**json.loads(data))
        account = item.account
        pid = item.pid
        # 提问的知识库类型
        type = item.type
        print(f"enhance_socket:####   account:{account}      pid:{pid}")

        if type == 'personal':
            collection_name = f'psl_{account}'
        elif type == 'public':
            collection_name = "pub_kdb"
        prompt = retrieve(collection_name, pid, item.query)

        # 使用线程池执行器来运行同步生成器
        loop = asyncio.get_running_loop()
        async for txt in run_in_executor(executor_enhance, model.chat_stream, tokenizer, prompt, history=history,
                                         system='你是一个根据已知信息进行回答和总结并润色答案的机器人，结合材料的时候尽可能保留材料，总结性的回答越详细越好'):
            await websocket.send_text(txt)

        await websocket.send_json({'ans': 'DONE'})
        # 如果这是单次请求响应模式，则可以关闭
        await websocket.close()



async def run_in_executor(executor, fn, *args, **kwargs):
    loop = asyncio.get_event_loop()
    queue = asyncio.Queue()

    def run():
        try:
            for item in fn(*args, **kwargs):
                loop.call_soon_threadsafe(queue.put_nowait, item)
            loop.call_soon_threadsafe(queue.put_nowait, None)
        except Exception as e:
            loop.call_soon_threadsafe(queue.put_nowait, e)

    executor.submit(run)

    while True:
        item = await queue.get()
        if item is None:
            break
        elif isinstance(item, Exception):
            raise item
        else:
            yield item


# 返回相似向量的接口
class Item(BaseModel):
    account: str
    type: str
    pid: str
    query: str


@app.post('/model/similartext/')
def similar_text(item: Item):
    if item.type == 'personal':
        collection_name = f'psl_{item.account}'
    elif item.type == 'public':
        collection_name = "pub_kdb"
    res = query_db(collection_name, item.pid, item.query, topk=15)
    if res:
        texts = '## 😆已为您在本地知识向量数据库检索到相似文本🛎️🛎️🚀  \n'
        texts += f'*===检索内容:{item.query}===*  \n'
        # 取出相似地向量
        for i, text in enumerate(res):
            texts += f"**{i + 1}." + str(text['text']).strip() + "**  \n"
        print(f"这是similar_text的texts: {texts}")
        return {"code": 200, "similar_texts": texts}
    else:
        texts = "## 🤔抱歉，数据库中暂时没有检索到相似文本  \n**您可以选择联系管理员进行上传语料的操作**"
        print(f"这是similar_text的texts: {texts}")
        return {"code": 200, "similar_texts": texts}



if __name__ == '__main__':
    uvicorn.run(app="main:app", host="0.0.0.0", port=9001, reload=True)
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)

device2 = "cpu"
tokenizer_bert = BertTokenizer.from_pretrained('/home/zhengwen/huzhuoyue/minicpm/model/text2vec-base-chinese')
model_bert = BertModel.from_pretrained('/home/zhengwen/huzhuoyue/minicpm/model/text2vec-base-chinese').to(device2)


def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0]
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

