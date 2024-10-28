import uvicorn
from starlette.middleware.cors import CORSMiddleware
from pymilvus import connections, Collection
from fastapi import  WebSocket
from pydantic import BaseModel
from fastapi import FastAPI
from modelscope import AutoModelForCausalLM, AutoTokenizer
import torch
from concurrent.futures import ThreadPoolExecutor
import asyncio
import torch
from transformers import AutoTokenizer, AutoModel
import json

torch.manual_seed(0)
#add/replace your localpath to Qwen Model
path = './model/qwen7b'
tokenizer = AutoTokenizer.from_pretrained(path, trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(path, torch_dtype=torch.float32, device_map='auto', trust_remote_code=True)
history = None

#remember to add
connections.connect("default", host="localhost", port="19530", user='', password='')


#add/replace ypur localpath of embedding model
tokenizer_bge = AutoTokenizer.from_pretrained('./model/bge-large-zh-v1.5')
model_bge = AutoModel.from_pretrained('./model/bge-large-zh-v1.5')

def get_query_embedding(query_text):
    def process_texts(sentences):
        encoded_input = tokenizer_bge(sentences, padding=True, truncation=True, return_tensors='pt')
        with torch.no_grad():
            model_output = model_bge(**encoded_input)
            sentence_embedding = model_output[0][:, 0]
        return sentence_embedding.tolist()

    embeddings_list = process_texts([query_text])
    return embeddings_list



def query_db(collection_name, pids, query_str, topk=5):
    #loading collection
    collection = Collection(collection_name)
    #search all partitions pids->list
    collection.load(partition_names=pids)
    search_params = {"metric_type": "IP", "params": {"nprobe": 64}}
    query_data = get_query_embedding(query_str)
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


def sig_retrieve(collection_name, pid, query_str):
    limit = 3750
    res = query_db(collection_name, pid, query_str, topk=15)
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



def muti_retrieve(personal_collection,personal_pids,pub_pids, query_str,top_k=5):
    limit = 3750
    res_list=[]
    #pids->list
    if personal_pids:
        res = query_db(personal_collection, personal_pids, query_str, topk=top_k)
        res_list.extend(res)
    if pub_pids:
        res = query_db("pub_kdb", pub_pids, query_str, topk=top_k)
        res_list.extend(res)
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

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



class Raw(BaseModel):
    query: str
    temperature: float
    top_p: float
executor_raw = ThreadPoolExecutor()
@app.websocket("/model/raw_socket")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await websocket.accept()
        while True:
            data = await websocket.receive_text()
            raw = Raw(**json.loads(data))
    
            loop = asyncio.get_running_loop()
            async for txt in run_in_executor(executor_raw, model.chat_stream, tokenizer, raw.query, history=history,temperature=raw.temperature,top_p=raw.top_p,
                                             system='你是一个根据已知信息进行回答和总结并润色答案的机器人，结合材料的时候尽可能保留材料，总结性的回答越详细越好'):
                await websocket.send_text(txt)
    
            await websocket.send_json({'ans': 'DONE'})
    except Exception as e:
        print(f"遇到错误:{e}")


class Item(BaseModel):
    account: str
    type: str
    pid: str
    query: str

executor_sig_enhance = ThreadPoolExecutor()
@app.websocket('/model/single/enhance_socket')
async def enhance_gpt(websocket: WebSocket):
    try:
        await websocket.accept()
        while True:
            data = await websocket.receive_text()
            item = Item(**json.loads(data))
            account = item.account
            pid = item.pid
            #Type of selected knowledgeBase
            type = item.type
            print(f"enhance_socket:####   account:{account}      pid:{pid}")
    
            if type == 'personal':
                collection_name = f'psl_{account}'
                prompt = sig_retrieve(collection_name, pid, item.query)
            elif type == 'public':
                collection_name = "pub_kdb"
                prompt = sig_retrieve(collection_name, pid, item.query)
            loop = asyncio.get_running_loop()
            async for txt in run_in_executor(executor_sig_enhance, model.chat_stream, tokenizer, prompt, history=history,temperature=0.5,top_p=0.5,
                                             system='你中科院微小卫星研究所的辅助机器人,你需要根据已知信息进行回答和总结并润色答案的机器人，结合材料的时候尽可能保留材料，总结性的回答越详细越好'):
                await websocket.send_text(txt)
    
            await websocket.send_json({'ans': 'DONE'})
    except Exception as e:
        print(f"遇到错误:{e}")




class Muti(BaseModel):
    account: str
    personal:list
    public:list
    query: str
    top_p: float
    top_k: int
    temperature: float
executor_muti_enhance = ThreadPoolExecutor()
@app.websocket('/model/muti/enhance_socket')
async def muti_enhance_gpt(websocket: WebSocket):
    try:
        await websocket.accept()
        while True:
            data = await websocket.receive_text()
            muti = Muti(**json.loads(data))
            account = muti.account
            personal_collection=f"psl_{account}"
            prompt = muti_retrieve(personal_collection,muti.personal,muti.public,muti.query,muti.top_k)
    
            loop = asyncio.get_running_loop()
            if len(prompt)==4:
              async for txt in run_in_executor(executor_muti_enhance, model.chat_stream,tokenizer,muti.query,history=history,temperature=muti.temperature,top_p=muti.top_p,
                      system="你中科院微小卫星研究所的辅助机器人,请根据用户的提问回答问题"):
                  await websocket.send_text(txt)
              await websocket.send_json({'ans': 'DONE'})
            else:
              async for txt in run_in_executor(executor_muti_enhance, model.chat_stream, tokenizer,prompt, history=history,
                      system='你中科院微小卫星研究所的辅助机器人，请你根据已知信息进行回答和总结并润色答案的机器人，结合材料的时候尽可能保留材料，总结性的回答越详细越好'):
                  await websocket.send_text(txt)
              await websocket.send_json({'ans': 'DONE'})
              
    except Exception as e:
        print(f"遇到错误:{e}")

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


class Sim(BaseModel):
    account: str
    personal:list
    public:list
    top_k: int
    query: str

#API: return similar DOCU
@app.post('/model/similartext/')
def similar_text(sim:Sim):
    account = sim.account
    personal_collection = f"psl_{account}"
    res_list=[]
    #pids->list
    if sim.personal:
        res = query_db(personal_collection, sim.personal, sim.query, topk=sim.top_k)
        res_list.extend(res)
    if sim.public:
        res = query_db("pub_kdb", sim.public, sim.query, topk=sim.top_k)
        res_list.extend(res)
    if res:
        texts = '## 已为您在本地知识向量数据库检索到相似文本\n'
        texts += f'*===检索内容:{sim.query}===* \n'
        # 取出相似地向量
        for i, text in enumerate(res):
            texts += f"**{i + 1}." + str(text['text']).strip() + "**  \n"
        return {"code": 200, "similar_texts": texts}
    else:
        texts = "## 抱歉，数据库中暂时没有检索到相似文本  \n**您可以选择联系管理员进行上传语料的操作**"
        return {"code": 200, "similar_texts": texts}

if __name__ == '__main__':
    #replace your running port
    uvicorn.run(app="main:app", host="0.0.0.0", port=9873, reload=True)
