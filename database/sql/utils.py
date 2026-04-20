import os
import csv
import base64
import sqlite3
import numpy as np
from openai import OpenAI
from tqdm import tqdm
from dotenv import load_dotenv
from typing import Union, List, Any
from sklearn.metrics.pairwise import cosine_similarity

# 1. 환경 설정 및 클라이언트 초기화
load_dotenv()
client = OpenAI()

# --- [임베딩 및 복원 도구] ---

def get_embedding(text: str):
    """문자열을 입력받아 OpenAI 벡터(np.array)로 반환"""
    if text is None or text.strip() == "":
        text = " "
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return np.array(response.data[0].embedding, dtype=np.float32)

def decode_embedding(encoded_str: str):
    """Base64로 인코딩된 문자열을 넘파이 벡터로 복원"""
    if not encoded_str:
        return None
    blob = base64.b64decode(encoded_str)
    return np.frombuffer(blob, dtype=np.float32)

# --- [데이터베이스 및 검색 도구] ---

def query_sender(db_path: str, query: Union[str, List[str]]) -> Any:
    """DB에 쿼리를 보내고 결과를 반환"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    try:
        if isinstance(query, list):
            results = []
            for q in query:
                cursor.execute(q)
                results.append(cursor.fetchall() if q.strip().upper().startswith("SELECT") else None)
            conn.commit()
            return results
        else:
            cursor.execute(query)
            if query.strip().upper().startswith("SELECT"):
                return cursor.fetchall()
            conn.commit()
            return None
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        conn.close()

def search_embedding(db_path: str, table_name: str, query_text: str, top_n: int = 5):
    """질문을 받아 DB 내 유사한 행의 _code 리스트 반환"""
    # 내부에서 위에 정의된 get_embedding 호출
    query_vec = get_embedding(query_text)
    
    # DB에서 데이터 가져오기 (query_sender 대신 직접 연결하거나 query_sender 활용)
    base_name = table_name[:-1] if table_name.endswith('s') else table_name
    code_column = f"{base_name}_code"
    
    # 모든 임베딩을 가져옴 (간결함을 위해 query_sender 활용 예시)
    rows = query_sender(db_path, f"SELECT {code_column}, embedding FROM {table_name}")
    
    if not rows: return []

    codes, embs = [], []
    for code, blob in rows:
        if blob:
            codes.append(code)
            embs.append(decode_embedding(blob)) # 내부에서 decode_embedding 호출
            
    # 유사도 계산
    similarities = cosine_similarity(query_vec.reshape(1, -1), np.array(embs))[0]
    top_indices = similarities.argsort()[-top_n:][::-1]
    
    return [codes[i] for i in top_indices]