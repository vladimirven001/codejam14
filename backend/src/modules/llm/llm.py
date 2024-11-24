from langchain_community.chat_models import ChatOllama

from __main__ import app
from users.user import get_user_by_id_controller
from rag.rag import retrieve
from users.user import User

from langchain_core.documents import Document


import os

# the prompts are kept separate in order to make it easier to change them and customize based on the amount of user information available

BASE_PROMPT = """
You are an assistant for question-answering tasks. 
Use the following pieces of retrieved context to answer the question. 
If you don't know the answer, just say that you don't know.
If the answer is not in the context, DO NOT answer the question.

Question: {question} 

Context: {context} 

Answer:
"""

BASE_PROMPT_WITH_NAME = """
You are an assistant for question-answering tasks. 
You are assisting {user_name}, talk to them with this name.
Use the following pieces of retrieved context to answer the question. 
If you don't know the answer, just say that you don't know.
If the answer is not in the context, DO NOT answer the question.

Question: {question} 

Context: {context} 

Answer:
"""

BASE_PROMPT_WITH_NAME_AND_SCHOOL = """
You are an assistant for question-answering tasks. 
You are assisting {user_name}, talk to them with this name.
{user_name} is a student at {user_school}.
Use the following pieces of retrieved context to answer the question. 
If you don't know the answer, just say that you don't know.
If the answer is not in the context, DO NOT answer the question.

Question: {question} 

Context: {context} 

Answer:
"""

BASE_PROMPT_WITH_NAME_AND_SCHOOL_AND_MAJOR = """
You are an assistant for question-answering tasks. 
You are assisting {user_name}, talk to them with this name.
{user_name} is a student at {user_school}.
They are majoring in {user_major}, take this into consideration.
Use the following pieces of retrieved context to answer the question. 
If you don't know the answer, just say that you don't know.
If the answer is not in the context, DO NOT answer the question.

Question: {question} 

Context: {context} 

Answer:
"""


@app.route('/answer', methods=['POST'])
def answer_user_prompt(userId, prompt):
    user = get_user_by_id_controller(userId)
    if not user:
        raise Exception("User with id {} not found".format(userId))
    documents = retrieve(user.id, prompt)
    return summarize_rag(user, prompt, documents)


def summarize_rag(user:User, query:str, documents:list[Document]):
    prompt = BASE_PROMPT
    if user.name:
        prompt = BASE_PROMPT_WITH_NAME
    elif user.name and user.school:
        prompt = BASE_PROMPT_WITH_NAME_AND_SCHOOL
    elif user.name and user.school and user.major:
        prompt = BASE_PROMPT_WITH_NAME_AND_SCHOOL_AND_MAJOR

    documents = listify_documents(documents)
    formatted_prompt = prompt.format(question=query, context="\n".join(documents), user_name=user.name, user_school=user.school, user_major=user.major)
    llm = ChatOllama(
        model="llama3.2",
        temperature=0,
    )
    result = llm.invoke(formatted_prompt)

    return result.content

def listify_documents(documents:list[Document]):
    return [doc.content for doc in documents]

if __name__ == "__main__":
    documents = [
        "was conceived by computer scientist Edsger W. Dijkstra in 1956 and published three years later.[4][5][6]  Dijkstra's algorithm finds the shortest path from a given source node to every other node.[7]:196206 It can also be used to find the shortest path to a specific destination node, by terminating the algorithm once the shortest path to the destination node is known. For example", 
        "Path First). It is also employed as a subroutine in other algorithms such as Johnson's algorithm.  The algorithm uses a min-priority queue data structure for selecting the shortest paths known so far. Before more advanced priority queue structures were discovered, Dijkstra's original algorithm ran in  Θ ( | V | 2 ) {displaystyle Theta (|V|^{2})} time, where  | V | {displaystyle |V|} is the number of nodes.[8] The idea of this algorit"
    ]

    user_query = "What is dijkstras algorithm"

    print(summarize_rag(user_query, documents))