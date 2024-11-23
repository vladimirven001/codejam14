from langchain_community.chat_models import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain import hub
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import GPT4AllEmbeddings

import os

def summarize_rag(query, documents):
    llm = ChatOllama(
        model="llama3.1",
        temperature=0,
    )
    prompt = """
    You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. 
    If you don't know the answer, just say that you don't know.
    If the answer is not in the context, DO NOT answer the question.

    Question: {question} 

    Context: {context} 

    Answer:
    """
    formatted_prompt = prompt.format(question=query, context="\n".join(documents))
    result = llm.invoke(formatted_prompt)

    return result.dict()["content"]

if __name__ == "__main__":
    documents = [
        "was conceived by computer scientist Edsger W. Dijkstra in 1956 and published three years later.[4][5][6]  Dijkstra's algorithm finds the shortest path from a given source node to every other node.[7]:196206 It can also be used to find the shortest path to a specific destination node, by terminating the algorithm once the shortest path to the destination node is known. For example", 
        "Path First). It is also employed as a subroutine in other algorithms such as Johnson's algorithm.  The algorithm uses a min-priority queue data structure for selecting the shortest paths known so far. Before more advanced priority queue structures were discovered, Dijkstra's original algorithm ran in  Θ ( | V | 2 ) {displaystyle Theta (|V|^{2})} time, where  | V | {displaystyle |V|} is the number of nodes.[8] The idea of this algorit"
    ]

    user_query = "What is dijkstras algorithm"

    print(summarize_rag(user_query, documents))