from elasticsearch import Elasticsearch
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

es_client = Elasticsearch(f"http://{os.getenv('ES_HOST')}:{os.getenv('ES_PORT')}")
client = OpenAI(
    base_url=os.getenv('OLLAMA_BASE_URL'),
    api_key=os.getenv('OLLAMA_API_KEY')
)

def elastic_search(query, course, index_name="course-questions"):
    search_query = {
        "size": 5,
        "query": {
            "bool": {
                "must": {
                    "multi_match": {
                        "query": query,
                        "fields": ["question^3", "text", "section"],
                        "type": "best_fields"
                    }
                },
                "filter": {
                    "term": {
                        "course": course
                    }
                }
            }
        }
    }
    response = es_client.search(index=index_name, body=search_query)
    
    return [hit['_source'] for hit in response['hits']['hits']]

def build_prompt(query, search_results):
    prompt_template = """
You're a course teaching assistant. Answer the QUESTION based on the CONTEXT from the FAQ database.
Use only the facts from the CONTEXT when answering the QUESTION.
QUESTION: {question}
CONTEXT: 
{context}
""".strip()
    
    context = "\n\n".join(f"section: {doc['section']}\nquestion: {doc['question']}\nanswer: {doc['text']}" for doc in search_results)
    
    return prompt_template.format(question=query, context=context).strip()

def llm(prompt):
    response = client.chat.completions.create(
        model='phi3',
        messages=[{"role": "user", "content": prompt}]
    )
    
    return response.choices[0].message.content

def rag(query, course):
    search_results = elastic_search(query, course)
    prompt = build_prompt(query, search_results)
    answer = llm(prompt)
    return answer