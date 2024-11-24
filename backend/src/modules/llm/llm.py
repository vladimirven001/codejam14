from langchain_community.chat_models import ChatOllama
from flask import request, jsonify

from __main__ import app
from conversations.message import get_messages_by_conversation_id
from users.user import get_user_by_id_controller
from rag.rag import retrieve
from users.user import User
import json

from langchain_core.documents import Document


import os

# the prompts are kept separate in order to make it easier to change them and customize based on the amount of user information available

BASE_PROMPT = """
You are an assistant for question-answering tasks. 
Use the following pieces of retrieved context to answer the question. 
If you don't know the answer, just say that you don't know.
If the answer is not in the context, DO NOT answer the question.

Provide your answer in json using this format:

"answer": answer,
"sources": list of sources from the provided context


The sources provided in the context are file paths, you can provide them as is.

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

Provide your answer in json using this format:

"answer": answer,
"sources": list of sources from the provided context

The sources provided in the context are file paths, you can provide them as is.
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

Provide your answer in json using this format:

"answer": answer,
"sources": list of sources from the provided context

The sources provided in the context are file paths, you can provide them as is.

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

Provide your answer in json using this format:

"answer": answer,
"sources": list of sources from the provided context

The sources provided in the context are file paths, you can provide them as is.

Question: {question} 

Context: {context} 

Answer:
"""

BASE_PROMPT_WITH_CHAT_HISTORY = """
Given a chat history and the latest user question, 
which might reference context in the chat history, 
formulate a standalone question that can be understood 
without the chat history. Do NOT answer the question; 
just reformulate it if needed.
Your answer should ONLY be the reformulated question encapsulated in quotes.

Chat history:\n {chat_history}

Current Question: {question}

Answer:
"""

@app.route('/answer', methods=['POST'])
def answer_user_prompt():
    conversationId = request.json.get('conversationId')
    userId = request.json.get('userId')
    prompt = request.json.get('prompt')
    if not conversationId or not userId or not prompt:
        return jsonify({'error': 'ConversationId, userId, and prompt are required'}), 400
    user = get_user_by_id_controller(userId)
    if not user:
        return jsonify({'error': 'User with id ' + userId + 'not found'}), 404
    messages = get_messages_by_conversation_id(conversationId)
    chat_history = [
            f"{'Human' if message.isHuman else 'AI'}: {message.text}" for message in messages
        ]
    
    if not chat_history:
        chat_history_str = "No prior chat history available."
    else:
        chat_history_str = "\n".join(chat_history)  

    context_prompt = BASE_PROMPT_WITH_CHAT_HISTORY.format(
        chat_history=chat_history_str,
        question=prompt
    )

    llm = ChatOllama(
        model="llama3.2",
        temperature=0,
    )
    response = llm.invoke(context_prompt)
    # print("reformulated answer", response.content)
    contextualized_prompt = response.content
    
    documents = retrieve(user.id, contextualized_prompt)

    return jsonify({
        "answer": summarize_rag(user, contextualized_prompt, documents)
        })


def summarize_rag(user: User, query: str, documents: list[Document]):
    if user.username and user.school and user.major:
        prompt = BASE_PROMPT_WITH_NAME_AND_SCHOOL_AND_MAJOR
    elif user.username and user.school:
        prompt = BASE_PROMPT_WITH_NAME_AND_SCHOOL
    elif user.username:
        prompt = BASE_PROMPT_WITH_NAME
    else:
        prompt = BASE_PROMPT

    documents_str = json.dumps(listify_documents(documents))

    # Provide default values for missing fields
    formatted_prompt = prompt.format(
        question=query,
        context=documents_str,
        user_name=user.username or "User",
        user_school=user.school or "Unknown School",
        user_major=user.major or "Undeclared Major",
    )

    llm = ChatOllama(
        model="llama3.2",
        temperature=0,
    )
    received_result = llm.invoke(formatted_prompt).content
    try:
        result = json.loads(received_result)
        parsed_sources = [
            source.split("data", 1)[1] for source in result.get("sources", [])
        ]
        result["sources"] = parsed_sources
    except (json.JSONDecodeError, KeyError):
        result = received_result  # Return raw result if JSON parsing fails

    return json.dumps(result) if isinstance(result, dict) else result


def listify_documents(documents:list[Document]):
    result = {}
    for i in range(len(documents)):
        doc = documents[i]
        result[i] = {
            "content": doc.page_content,
            "source": doc.metadata.get("source", "Unknown")
            }
        
    # print("found context:", result)
    return result
        

if __name__ == "__main__":
    documents = [
        "was conceived by computer scientist Edsger W. Dijkstra in 1956 and published three years later.[4][5][6]  Dijkstra's algorithm finds the shortest path from a given source node to every other node.[7]:196206 It can also be used to find the shortest path to a specific destination node, by terminating the algorithm once the shortest path to the destination node is known. For example", 
        "Path First). It is also employed as a subroutine in other algorithms such as Johnson's algorithm.  The algorithm uses a min-priority queue data structure for selecting the shortest paths known so far. Before more advanced priority queue structures were discovered, Dijkstra's original algorithm ran in  Θ ( | V | 2 ) {displaystyle Theta (|V|^{2})} time, where  | V | {displaystyle |V|} is the number of nodes.[8] The idea of this algorit"
    ]

    user_query = "What is dijkstras algorithm"

    print(summarize_rag(user_query, documents))