# 创建人：QI-BRO
# 开发时间：2024-08-06  13:52
import json
import os
from io import BytesIO
import PyPDF2

from PyPDF2 import PdfReader
from modelscope import AutoModelForCausalLM, AutoTokenizer, AutoModel
import torch
from docx import Document
import io

torch.manual_seed(0)

tokenizer_bge = AutoTokenizer.from_pretrained('/home/zhengwen/huzhuoyue/minicpm/model/bge-large-zh-v1.5')
model_bge = AutoModel.from_pretrained('/home/zhengwen/huzhuoyue/minicpm/model/bge-large-zh-v1.5')


# 参数：本地文件路径 输出的存储文件路径
def get_text_from_file(file_path: str, output_file_path: str) -> bool:
    # 确保文件路径不为空
    if not file_path:
        return False

    # 使用 os.path 来处理路径，增加跨平台兼容性
    import os
    filename, file_extension = os.path.splitext(os.path.basename(file_path))
    file_extension = file_extension.lower()[1:]  # 去除点号

    try:
        if file_extension == 'txt':
            with open(file_path, 'r', encoding='utf-8') as file:
                file_content = file.read()
        elif file_extension in ('docx', 'pdf'):
            with open(file_path, 'rb') as file:
                file_content = file.read()
                if file_extension == 'docx':
                    doc = Document(BytesIO(file_content))
                    file_content = '\n'.join([para.text for para in doc.paragraphs])
                elif file_extension == 'pdf':
                    reader = PyPDF2.PdfFileReader(BytesIO(file_content))
                    file_content = '\n'.join([page.extract_text() for page in reader.pages if page.extract_text()])
        elif file_extension == 'json':
            with open(file_path, 'r', encoding='utf-8') as file:
                file_content = file.read()
        else:
            return False

        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(file_content)

        return True

    except Exception as e:
        print(f"遇到错误:{e}")
        return False


def get_embedding(file_path):
    texts = []

    def process_texts(sentences):
        # print(sentences)
        encoded_input = tokenizer_bge(sentences, padding=True, truncation=True, return_tensors='pt')
        with torch.no_grad():
            model_output = model_bge(**encoded_input)
            sentence_embedding = model_output[0][:, 0]
            print(f"############ 62 这是sentence_embedding.shape的值", sentence_embedding.shape)
        return sentence_embedding.tolist()

    with open(file_path, encoding='utf-8') as f:
        line_number = 0
        text = ""
        for line in f:
            status, txt_back = length_detection(text, line)
            if status:
                text += line.strip()
                print(f"text length:{len(text)}")
            else:
                texts.append(text)
                text = txt_back
            line_number += 1
    if line_number == 1:
        texts.append(line)
    texts = [text for text in texts if text]

    res_feature = process_texts(texts)
    print(f"######  84这是res_feature 的单个句子的特征向量的长度 {len(res_feature[0])} #######3")
    print("Total embeddings processed:", len(res_feature))
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
    print(f"*****这是get_query_embedding中的问题的embedding****")
    print(embeddings_list)
    return embeddings_list


# 单次长度检测，如果单行文本长度始终小于则不断添加下一行信息
def length_detection(a_str, line_str):
    ori_str = a_str
    a_str = a_str + " " + line_str
    # 如果长度超过450，返回未添加句子长度前的句子
    if len(a_str) >= 200:
        return False, line_str
    # 长度未超过则返回已经添加line以后的句子
    else:
        return True, a_str


def pdf_upload(file):
    output_path = "/home/zhengwen/huzhuoyue/minicpm/test.txt"
    # 读取 PDF 文件内容
    try:
        with file.file as pdf_file:
            reader = PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()

                # 将提取的文本写入到指定的输出文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)

    except Exception as e:
        print(f"PDF 写入text.txt 遇到问题{e}")
        return False
    return True


def read_embedding():
    # embedding向量的存储路径
    embedding_path = 'insert_feature.json'
    with open(embedding_path, 'r') as f:
        embedding = json.load(f)

    # 文本文件存储路径
    file_path = 'test.txt'
    texts = []
    with open(file_path, encoding='utf-8') as f:
        for line in f:
            text = line.strip()
            texts.append(text)

    return embedding, texts


def get_text_from_localfile(input_file_path: str, output_file_path: str) -> bool:
    filename = os.path.basename(input_file_path)
    file_extension = filename.lower().rsplit('.', 1)[-1] if '.' in filename else ''

    try:
        with open(input_file_path, 'rb') as file:
            file_content = file.read()

        with open(output_file_path, 'w', encoding='utf-8') as f:
            if file_extension in ('txt',):
                # 对于.txt文件，直接写入文件内容（这里假设file_content已经是解码后的字符串，但因为是二进制模式读取，所以应该是bytes）
                f.write(file_content.decode('utf-8'))
            elif file_extension in ('docx',):
                # 对于.docx文件，使用python-docx库提取文本
                doc = Document(io.BytesIO(file_content))
                f.write('\n'.join([para.text for para in doc.paragraphs]))
            elif file_extension == 'pdf':
                # 对于.pdf文件，使用PyPDF2库提取文本
                reader = PyPDF2.PdfFileReader(io.BytesIO(file_content))
                f.write('\n'.join([page.extract_text() for page in reader.pages if page.extract_text()]))
            else:
                # 如果文件格式不支持，返回False
                print(f"Unsupported file format: {file_extension}")
                return False

        return True

    except Exception as e:
        # 处理可能的异常
        print(f"Error processing file {filename}: {e}")
        return False
