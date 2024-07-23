import httpx
import openai
import tiktoken
import json
import uvicorn
import signal
import numpy as np
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
torch.manual_seed(0)



path = 'qwen/Qwen-14B-Chat'
tokenizer = AutoTokenizer.from_pretrained(path,trust_remote_code=True)
model = AutoModelForCausalLM.from_pretrained(path, torch_dtype=torch.float32, device_map='auto', trust_remote_code=True)
history=None
# connections.connect(alias="default",
#                     uri="https://in01-487e267ef1ccb1e.ali-cn-hangzhou.vectordb.zilliz.com.cn:19530",
#                     token="db_admin:Ng1$f4/<x2eppL}n")
#47.100.166.210:19530 ipbd  milvus离线数据库
connections.connect("default", host="47.100.166.210", port="19530", user='root', password='')
# connections.connect("default", host="47.100.166.210", port="19530", user='root', password='')
collection_name = 'chat_qw'
collection = Collection(collection_name)




import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer,AutoModel
import json
tokenizer_bge = AutoTokenizer.from_pretrained('/home/zhengwen/huzhuoyue/minicpm/model/bge-large-zh-v1.5')
model_bge = AutoModel.from_pretrained('/home/zhengwen/huzhuoyue/minicpm/model/bge-large-zh-v1.5')

def get_embedding(file_path):
    texts = []
    max_length=512
    def process_texts(sentences):
        encoded_input = tokenizer_bge(sentences, padding=True, truncation=True, return_tensors='pt')
        with torch.no_grad():
            model_output = model_bge (**encoded_input)
            sentence_embedding = model_output[0][:, 0]
            print(f"############ 62 这是sentence_embedding.shape的值",sentence_embedding.shape)
        return sentence_embedding.tolist()


    with open(file_path, encoding='utf-8') as f:
        for line in f:
            text = line.strip()
            if len(text)<15:
                continue
            #texts.append(text)
            if len(text) > max_length:  
                split_texts = [text[j:j+max_length] for j in range(0, len(text), max_length)]
                for split_text in split_texts:
                    texts.append(split_text)
            else:  
                texts.append(text)  # 文本长度未超过512，直接添加到texts列表中  
    texts=[text for text in texts if text]
 
    res_feature=process_texts(texts)

    print("################  res_feature ########")
    # print(res_feature)
    print(f"######  84这是res_feature 的单个句子的特征向量的长度 {len(res_feature[0])} #######3")

    print("##### ok 147 ###")
    print("Total embeddings processed:", len(res_feature))
    with open('insert_feature.json', 'w') as f:
        json.dump(res_feature, f)
        print('提取完成')
    return res_feature,texts
    



def get_query_embedding(query_text):

    def process_texts(sentences):
        encoded_input = tokenizer_bge(sentences, padding=True, truncation=True, return_tensors='pt')
        with torch.no_grad():
            model_output = model_bge (**encoded_input)
            sentence_embedding = model_output[0][:, 0]
        return sentence_embedding.tolist()
   
    embeddings_list=process_texts([query_text])
    print(f"*****这是get_query_embedding中的问题的embedding****")
    print(embeddings_list)
    # res=[embeddings_list]
    # print(res)
    return embeddings_list   

    # def process_texts(texts):
    #     encoded_inputs = tokenizer_bert(texts, padding=True, truncation=True, return_tensors='pt')
    #     model_outputs = model_bert(**encoded_inputs)
    #     sentence_embeddings = mean_pooling(model_outputs, encoded_inputs['attention_mask'])
    #     sentence_embeddings_norm = sentence_embeddings / sentence_embeddings.norm(p=2, dim=-1, keepdim=True)
    #     sentence_embeddings_norm = sentence_embeddings_norm.squeeze(0)
    #     return sentence_embeddings_norm.cpu().detach().numpy().tolist()
        
    # embeddings_list = []
    # embeddings_list.extend(process_texts([query_text]))
    # print(f"*****这是get_query_embedding中的问题的embedding****")
    # print(embeddings_list)
    # # res=[embeddings_list]
    # # print(res)
    # return embeddings_list





def read_embedding():
    #embedding向量的存储路径
    embedding_path = 'insert_feature.json'
    with open(embedding_path, 'r') as f:
        embedding = json.load(f)

    #文本文件存储路径
    file_path = 'test.txt'
    texts = []
    with open(file_path, encoding='utf-8') as f:
        for line in f:
            text = line.strip()
            texts.append(text)

    return embedding, texts

def insert_embedding(embedding,texts):

    # print("这是insert_embedding里的特征向量:",embedding)
    print(f"############ 151 这是embedding的的长度",len(embedding[0]))
    print("这是insert_embedding里的文本:",texts)
    print(len(embedding),print(len(texts)))
    mr = collection.insert([embedding,texts])

    collection.flush()
    print("ok116")
    return mr.succ_count


def query_db(query_str,topk=8):
    collection.load()
    search_params = {"metric_type": "IP", "params": {"nprobe": 64}}
    
    #query_data = openai.Embedding.create(input=query_str, model=model_embedding)["data"][0]["embedding"]
    query_data =get_query_embedding(query_str)
    print("#############[query_data]##########")
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
            if score >= 150:
                res.append({
                    "score": score,
                    "text": hit.entity.get('text')
                })
    print("Successfully searched similar texts!")
    print(res)
    return res

def retrieve(query_str):
    limit = 3750
    res = query_db(query_str,topk=15)
    print(f"这是retrieve的res: {res}")
    prompt_start = (
            "请结合下面我给你的已知材料信息回答我的问题，如果是总结或者报告类的问题，回答越详细越好,不少于500字.\n\n"+"段落:\n"
    )
    prompt_end = (
         f"\n\n问题: {query_str}\n回答:"
    )
    #取出相似地向量
    contexts =[x['text'] for x in res]
    print(f"这是retrieve的contexts: {contexts}")
    prompt = 'None'
    if len(res) == 0:
        #如果没有从数据库中找到相似的文本向量结果
        prompt = prompt

    #如果查找到了相似向量返回文本
    else:
        for i in range(0, len(contexts)):
            if len("\n\n---\n\n".join(contexts[:i])) >= limit:
                prompt = (
                        prompt_start +
                        "\n\n---\n\n".join(contexts[:i - 1])+"\n\n"+
                        prompt_end
                )
                break
            elif i == len(contexts) - 1:
                prompt = (
                        prompt_start +
                        "\n\n---\n\n".join(contexts)+"\n\n"+
                        prompt_end
                )
        print(f"这是retrieve的prompt : {prompt}")
    return prompt

#{"role": "system", "content": "你是个根据描述信息进行回答的机器人，尽量使用自己的话术"},
def enhance_chatgpt(prompt):
    history=None
    res= model.chat(tokenizer,prompt, system="你是一个根据已知信息进行回答和总结并润色答案的机器人，结合材料的时候尽可能保留材料，总结性的回答越详细越好",temperature=0.9, top_p=0.8,history=history)
    return res


#你是个基础问答机器人
def ori_chatgpt(query_str):
    history=None
    res, history = model.chat(tokenizer, query_str, system="你是个基础问答机器人,请你根据自己的信息进行回答，越详细越好",temperature=0.9, top_p=0.8,history=history)
    return res




app = FastAPI()
# 允许所有来源的跨域请求
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#增强提问接口
class Item(BaseModel):
    query: str
@app.post('/api/chatgpt/')
def enhance_gpt(item: Item):
    prompt = retrieve(item.query)
    result_enhance= enhance_chatgpt(prompt)
    return {"code": 200, "enhance_qw":result_enhance}


# 创建WebSocket连接，参数为ws:WebSocket对象
#通以千问原始回答
executor_raw = ThreadPoolExecutor()
@app.websocket("/api/raw_socket")  
async def websocket_endpoint(websocket: WebSocket):  
    await websocket.accept()  
    while True:  
        data = await websocket.receive_text()  
        item = Item(**json.loads(data))  

  
        # 使用线程池执行器来运行同步生成器  
        loop = asyncio.get_running_loop()  
        async for txt in run_in_executor(executor_raw, model.chat_stream, tokenizer,item.query, history=history, system='你是一个根据已知信息进行回答和总结并润色答案的机器人，结合材料的时候尽可能保留材料，总结性的回答越详细越好'):  
            await websocket.send_text(txt)  
  
        await websocket.send_json({'ans': 'DONE'})  
        # 如果打算在发送DONE后继续监听新的请求，就不要关闭websocket连接  
        # 如果这是单次请求响应模式，则可以关闭  
        await websocket.close()  



#通义千问增强回答·
# @app.websocket('/api/enhance_socket')
# async def enhance_gpt(websocket: WebSocket):
#     await websocket.accept()
#     while True:
#         data = await websocket.receive_text()
#         item = Item(**json.loads(data))
#         prompt = retrieve(item.query)
#         tmp=''
#         # res = model.chat_stream(tokenizer, prompt , history=history, system='你是一个根据已知信息进行回答和总结并润色答案的机器人，结合材料的时候尽可能保留材料，总结性的回答越详细越好')
#         # print("ok 340")

#         async for txt in model.chat_stream(tokenizer, prompt , history=history, system='你是一个根据已知信息进行回答和总结并润色答案的机器人，结合材料的时候尽可能保留材料，总结性的回答越详细越好'):  
#             await websocket.send_text(txt[len(tmp):])
#         # for txt in res: 
#         #     print("### 342 ###")
#         #     # print(txt[len(tmp):], end='', flush=True)
#         #     await websocket.send_text(txt[len(tmp):])
#         #     print("### 345 ###")
#         #     tmp = txt
#         print('\n', end='')
#         await websocket.send_json({'ans': 'DONE'})
#         await websocket.close()
executor_enhance = ThreadPoolExecutor()  
@app.websocket('/api/enhance_socket')  
async def enhance_gpt(websocket: WebSocket):  
    await websocket.accept()  
  
    while True:  
        data = await websocket.receive_text()  
        item = Item(**json.loads(data))  
        prompt = retrieve(item.query)  
  
        # 使用线程池执行器来运行同步生成器  
        loop = asyncio.get_running_loop()  
        async for txt in run_in_executor(executor_enhance, model.chat_stream, tokenizer, prompt, history=history, system='你是一个根据已知信息进行回答和总结并润色答案的机器人，结合材料的时候尽可能保留材料，总结性的回答越详细越好'):  
            await websocket.send_text(txt)  
  
        await websocket.send_json({'ans': 'DONE'})  
        # 如果打算在发送DONE后继续监听新的请求，就不要关闭websocket连接  
        # 如果这是单次请求响应模式，则可以关闭  
        await websocket.close()  

# 异步包装器来在线程中运行同步生成器  
async def run_in_executor(executor, fn, *args, **kwargs):  
    loop = asyncio.get_event_loop()  
    queue = asyncio.Queue()  
  
    def run():  
        try:  
            for item in fn(*args, **kwargs):  
                loop.call_soon_threadsafe(queue.put_nowait, item)  
            loop.call_soon_threadsafe(queue.put_nowait, None)  # Sentinel to stop iteration  
        except Exception as e:  
            loop.call_soon_threadsafe(queue.put_nowait, e)  
  
    executor.submit(run)  
  
    while True:  
        item = await queue.get()  
        if item is None:  # Sentinel detected  
            break  
        elif isinstance(item, Exception):  
            raise item  
        else:  
            yield item






#返回相似向量的接口
class Item(BaseModel):
    query: str
@app.post('/api/similartext/')
def similar_text(item: Item):
    res = query_db(item.query,topk=15)
    if res:
        texts='## 😆已为您在本地知识向量数据库检索到相似文本🛎️🛎️🚀  \n'
        texts+=f'*===检索内容:{item.query}===*  \n'
        #取出相似地向量
        for i,text in enumerate(res):
            texts+=f"**{i+1}."+str(text['text']).strip()+"**  \n"
        print(f"这是similar_text的texts: {texts}")
        return {"code": 200, "similar_texts":texts}
    else:
        texts="## 🤔抱歉，数据库中暂时没有检索到相似文本  \n**您可以选择联系管理员进行上传语料的操作**"
        print(f"这是similar_text的texts: {texts}")
        return {"code": 200, "similar_texts":texts}




#数据库接口
@app.post('/api/upload/')
def insert_database(file: UploadFile = File(...)):
    with open('test.txt', 'wb') as f:
        f.write(file.file.read())

    #固定的写死的
    #get_embedding("test.txt")
    # embedding, texts = read_embedding()
    embedding, texts=get_embedding("test.txt")
    print("****************************263********************")
    num = insert_embedding(embedding, texts)
    print('数据上传成功，上传%s条语料！！！' % num)
    return {"code": 200,'msg':f'成功上传 {num} 条语料'}






@app.delete('/api/delete/')
def delete_collection():
    if utility.has_collection(collection_name):
        utility.drop_collection(collection_name)
    fields = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1536),
        FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=2000)
    ]
    schema = CollectionSchema(fields, collection_name)
    collection = Collection(collection_name, schema)
    index_params = {
        "index_type": "IVF_FLAT",
        "metric_type": "IP",
        "params": {"nlist": 1536},
    }
    collection.create_index(field_name="embedding", index_params=index_params)
    collection.load()
    print("success Create collection: ", collection_name)


if __name__ == '__main__':
    # insert_cache_path = './dataset/insertdata_cache_3.json'
    # text2embedding(insert_cache_path)
    # file_path = './dataset/netse.txt'
    # openai_embedding(file_path)
    # embedding, texts = read_embedding()
    # num = insert_embedding(embedding, texts)
    # str = "我的个人信息会因为登录网站而泄露吗"
    # query_str,prompt = retrieve(str)
    # print("prompt:",prompt)
    # print("---------小助手回答----------")
    # res,all_price = chatgpt(query_str, prompt)
    # reply = res["choices"][0]["message"]["content"]
    # print(reply+'\n'+'该问题花费 %f 美元'%all_price)
    uvicorn.run(app="main:app", host="0.0.0.0", port=9001, reload=True)
    signal.signal(signal.SIGCHLD, signal.SIG_IGN)


"""
while True:
    tmp = ''
    ask=input('user:')
    responds = model.chat_stream(tokenizer, ask,history=history,system='你是一个猫娘，每次回答完问题要喵一声')
    for txt in responds: 
        print(txt[len(tmp):],end='',flush=True)
        tmp = txt
        #print(1)
    print('\n',end='')
"""

# def openai_embedding(file_path,batch_size=100):
#     openai.api_key = 'sk-4aFYZcF2pcogyNgOCdDfE0D4E14b4d6eBdEe336772AdF6Be'
#     openai.api_base = "https://api.dreamger.com/v1"

#     print("开始进行openai_embedding")
#     texts = []
#     res_feature = []
#     with open(file_path, encoding='utf-8') as f:
#         for line in f:
#             text = line.strip()
#             texts.append(text)

#     for i in tqdm(range(0, len(texts), batch_size)):
#         batch = texts[i:i + batch_size]
#         embed_data = openai.Embedding.create(input=batch, model=model_embedding)
#         feature = embed_data["data"]
#         print(feature)
#         for j in feature:
#             res_feature.append(j['embedding'])
#     print('提取特征数量：',len(res_feature))
#     # with open('./dataset/insert_feature.json', 'w') as f:
#     #覆盖写入新的embedding向量然后上传到数据库中
#     with open('insert_feature3.json', 'w') as f:
#         json.dump(res_feature, f)
#         print('提取完成')



# def estimate_embedding_price(text, price_per_1k=0.04):
#     enc = tiktoken.get_encoding("gpt2")
#     num_tokens = len(enc.encode(text))
#     price = num_tokens / 1000 * price_per_1k / 100
#     return num_tokens,price

#def enhance_chatgpt(prompt):
    # res = openai.ChatCompletion.create(
    #   model="gpt-4-turbo-2024-04-09",
    #   messages=[
    #         {"role": "system", "content": "请根据所给信息回答问题"},
    #         {"role": "user", "content": prompt},
    #         #{"role": "assistant", "content": prompt}
    #     ]
    # )
    # query_str_tokens,query_price = estimate_embedding_price(query_str)
    # ans_tokens = res["usage"]["total_tokens"]
    # ans_price = ans_tokens / 1000 * 0.002 / 100
    # all_price = query_price + ans_price
    # return res,all_price



#你是个基础问答机器人
#def ori_chatgpt(query_str):
    # res = openai.ChatCompletion.create(
    #   model="gpt-4-turbo-2024-04-09",
    #   messages=[
    #         {"role": "system", "content": "你是个基础问答机器人"},
    #         {"role": "user", "content": query_str}
    #     ]
    # )
    # ans_tokens = res["usage"]["total_tokens"]
    # ans_price = ans_tokens / 1000 * 0.002 / 100
    # return res,ans_price
    # res = model.chat_stream(tokenizer, ask,history=history,system='你是个基础问答机器人,请你根据自己的信息进行回答，越详细越好')
    # for txt in responds: 
    #     print(txt[len(tmp):],end='',flush=True)
    #     tmp = txt
    #     #print(1)
    # print('\n',end='')
    # history=None
    # res, history = model.chat(tokenizer, query_str, system="你是个基础问答机器人,请你根据自己的信息进行回答，越详细越好",temperature=0.9, top_p=0.8,history=history)
    # return res

    # openai.api_key = 'sk-4aFYZcF2pcogyNgOCdDfE0D4E14b4d6eBdEe336772AdF6Be'
# openai.api_base = "https://api.dreamger.com/v1"

device2 = "cpu"
tokenizer_bert = BertTokenizer.from_pretrained('/home/zhengwen/huzhuoyue/minicpm/model/text2vec-base-chinese')
model_bert = BertModel.from_pretrained('/home/zhengwen/huzhuoyue/minicpm/model/text2vec-base-chinese').to(device2)
    # print("开始进行openai_embedding")
    # texts = []
    # res_feature = []
    # with open(file_path, encoding='utf-8') as f:
    #     for line in f:
    #         text = line.strip()
    #         #['文本1','文本2','文本3'...]
    #         texts.append(text)
    
    # print(texts)
    # embed_data =[]
    # # for i in tqdm(range(0, len(texts), batch_size)):
    # #     #文本分批
    # #     batch = texts[i:i + batch_size]
    # #     print("78")
    # #     # print("####### process_txts ######")
    # for text in texts:
    #     embed_data.append(process_texts([text]))
    #     print("82")
    #     print("#########  embed_data  ########")
    #     print(embed_data)
    
    # res_feature.extend(embed_data)
    # print('提取特征数量：',len(res_feature))
    # print("########## res_feature#####")
    # # with open('./dataset/insert_feature.json', 'w') as f:
    # #覆盖写入新的embedding向量然后上传到数据库中
    # with open('insert_feature.json', 'w') as f:
    #     json.dump(res_feature, f)
    #     print('提取完成')
    # return res_feature

    #     # Process each batch
    #     for text in batch:
    #         # Check if text length exceeds max length
    #         if len(text) > 512:
    #             split_texts = [text[j:j+512] for j in range(0, len(text), 512)]
    #             for split_text in split_texts:
    #                 embeddings_list.append(process_texts([split_text]))
    #         else:
    #             embeddings_list.append(process_texts([text]))

    #     res_feature.extend(embeddings_list)

    # print("Total embeddings processed:", len(res_feature))
    # print(res_feature)
    # with open('insert_feature.json', 'w') as f:
    #     json.dump(res_feature, f)
    #     print('提取完成')
    # return res_feature
def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0]  # First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)

# def get_embedding(file_path, batch_size=1):
#     def process_texts(texts):
#         encoded_inputs = tokenizer_bert(texts, padding=True, truncation=True, return_tensors='pt')
#         model_outputs = model_bert(**encoded_inputs)
#         sentence_embeddings = mean_pooling(model_outputs, encoded_inputs['attention_mask'])
#         sentence_embeddings_norm = sentence_embeddings / sentence_embeddings.norm(p=2, dim=-1, keepdim=True)
#         sentence_embeddings_norm = sentence_embeddings_norm.squeeze(0)
#         return sentence_embeddings_norm.cpu().detach().numpy().tolist()
    
#     texts = []  
#     max_length = 400
#     res_feature=[]

#     with open(file_path, encoding='utf-8') as f:
#         for line in f:
#             text = line.strip()
#             #texts.append(text)
#             if len(text) > max_length:  
#                 split_texts = [text[j:j+max_length] for j in range(0, len(text), max_length)]
#                 for split_text in split_texts:
#                     texts.append(split_text)
#             else:  
#                 texts.append(text)  # 文本长度未超过512，直接添加到texts列表中  
#     texts=[text for text in texts if text]
#     print("######### texts  #########")
#     print(texts)
#     embeddings_list = []
#     print("##### ok 131 ###")
#     for item in texts:
#         print("##### ok 133 ###")
#     # for i in tqdm(range(0, len(texts), batch_size)):
#     #     #一批一批处理文本
#     #     batch = texts[i:i + batch_size]
#         embeddings_list.append(process_texts([item]))
#         #当前batch判断长度是否大于512
#         # for text in batch:
#         #     # Check if text length exceeds max length
#         #     if len(text) > 512:
#         #         #长度大于512重新切片
#         #         split_texts = [text[j:j+512] for j in range(0, len(text), 512)]
#         #         for split_text in split_texts:
#         #             embeddings_list.append(process_texts([split_text]))
#         #     else:
#         #         embeddings_list.append(process_texts([text]))
#     res_feature.extend(embeddings_list)
#     print("##### ok 147 ###")
#     print("Total embeddings processed:", len(res_feature))
#     print(res_feature)
#     with open('insert_feature.json', 'w') as f:
#         json.dump(res_feature, f)
#         print('提取完成')
#     return res_feature,texts
