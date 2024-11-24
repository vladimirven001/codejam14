import os
from langchain_unstructured import UnstructuredLoader
from langchain_community.document_loaders import DirectoryLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores.utils import filter_complex_metadata

from flask import request, jsonify

from __main__ import app

from files.file import File, create_file, get_files_by_user_id, updateProcces, delete_documents_by_id
from .rag_helpers import delete_documents_by_source, vector_db

def load(file_paths:list[str], loader:str='unstructured') -> list[Document]:
    """
    Function that uses the UnstructuredLoader to load the files a given directory

    Args:
        path (str): The path to the directory containing the files
        loader (str): The loader to use

    Returns:
        list[Document]: A list of Document objects
    """
    if loader == 'unstructured':
        loader = UnstructuredLoader(file_paths)
    # elif loader == 'directory':
    #     # does not work if .txt files are in subdirectories
    #     loader = DirectoryLoader(path)
    return loader.load()

def split(documents: list[Document]) -> list[Document]:
    """
    Function that splits documents into chunks

    Args:
        documents (list[Document]): A list of Document objects

    Returns:
        list[Document]: A list of split Document objects
    """
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1024,
        chunk_overlap=1000,
        length_function=len,
        is_separator_regex=False,
    )
    return text_splitter.split_documents(documents)

def ingest(documents: list[Document]) -> None:
    """
    Function that ingests the documents into a local ChromaDB instance.

    Args:
        documents (list[Document]): A list of Document objects.
    """
    embeddings = OllamaEmbeddings(
        model="mxbai-embed-large",
    )
    vectorstore = Chroma(
        collection_name="user1",
        embedding_function=embeddings,
        persist_directory="./db/chroma_db",
    )

    documents = filter_complex_metadata(documents)
    # Filter complex metadata
    # for document in documents:
    #     print(type(document))
    #     if hasattr(document, "metadata"):
    #         document.metadata = filter_complex_metadata(document.metadata)
    
    # Add documents to vectorstore
    vectorstore.add_documents(documents)

def retrieve(userId:int, query:str) -> list[Document]:
    """
    Function that retrieves the documents from a local ChromaDB instance

    Args:
        query (str): The query to use

    Returns:
        list[Document]: A list of Document objects
    """
    embeddings = OllamaEmbeddings(
        model="mxbai-embed-large",
    )
    vectorstore = Chroma(
        collection_name="user" + str(userId),
        embedding_function=embeddings,
        persist_directory="./db/chroma_db",  
    )
    return vectorstore.similarity_search(query)

# Functions below just to see how it works
def main():
    documents = load(path='./files/1/data/', loader='unstructured')
    documents = split(documents)
    ingest(documents)
    query = "why is the bohdi tree important"
    results = retrieve(1, query)
    print(results)

@app.route('/process/<int:id>', methods=['POST'])
def process(id):
    try:
        if id is None:
            return jsonify({'error': 'Id is required'}), 400
        
        base_path = os.path.normpath(os.path.join('./files', str(id), 'data'))

        file_paths = set()
        for root, dirs, files in os.walk(base_path):
            for file in files:
                file_paths.add(os.path.join(os.getcwd(), root, file))

        for file in file_paths:
            create_file(file, id)

        files = get_files_by_user_id(id)

        vectorstore = vector_db(id)

        files_to_be_processed = []
        
        for file in files:
            if file['path'] not in file_paths:
                delete_documents_by_source(vectorstore, file['path'])   # delete from vector db
                delete_documents_by_id(file['id'])                      # delete from table
            if not file['processed']:
                files_to_be_processed.append(file)
                delete_documents_by_source(vectorstore, file['path'])
        
        # load -> split -> ingest
        documents = load([file['path'] for file in files_to_be_processed], loader='unstructured')
        if documents:
            documents = split(documents)
        if documents:
            ingest(documents)

        for file in files_to_be_processed:
            updateProcces(file['id'])

        return jsonify({'message': 'files processed'}), 200
    except Exception as e:
        return jsonify({'error': 'An error occurred', 'details': str(e)}), 500
    
@app.route('/files/<int:userId>', methods=['GET'])
def get_files(userId):
    try:
        return jsonify(get_files_by_user_id(userId))
    except Exception as e:
        return jsonify({'error': 'An error occurred', 'details': str(e)}), 500
   
@app.route('/files', methods=['GET'])
def get_all_files():
    try:
        files = File.query.all()
        return jsonify([file.to_dict() for file in files])
    except Exception as e:
        return jsonify({'error': 'An error occurred', 'details': str(e)}), 500