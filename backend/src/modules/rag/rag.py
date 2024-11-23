import os
from langchain_unstructured import UnstructuredLoader
from langchain_community.document_loaders import DirectoryLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings


def load(path:str, loader:str='unstructured') -> list[Document]:
    """
    Function that uses the UnstructuredLoader to load the files a given directory

    Args:
        path (str): The path to the directory containing the files
        loader (str): The loader to use

    Returns:
        list[Document]: A list of Document objects
    """
    if loader == 'unstructured':
        file_paths = list()
        for root, dirs, files in os.walk(path):
            for file in files:
                file_paths.append(os.path.join(root, file))
        loader = UnstructuredLoader(file_paths)
    elif loader == 'directory':
        # does not work if .txt files are in subdirectories
        loader = DirectoryLoader(path)
    return loader.load()

def split(documents: list[Document]) -> list[str]:
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

def ingest(documents:list[Document]) -> list[Document]:
    """
    Function that ingests the documents in a local ChromaDB instance

    Args:
        documents (list[Document]): A list of Document objects

    Returns:
        list[Document]: A list of Document objects
    """
    embeddings = OllamaEmbeddings(
        model="mxbai-embed-large",
    )
    vectorstore = Chroma(
        collection_name="notes",
        embedding_function=embeddings,
        persist_directory="./db/chroma_db",  
    )
    vectorstore.add_documents(documents)

def retrieve(query:str) -> list[Document]:
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
        collection_name="notes",
        embedding_function=embeddings,
        persist_directory="./db/chroma_db",  
    )
    return vectorstore.similarity_search(query)

# Functions below just to see how it works
def main():
    # documents = load(path='./files/Session6/COMP302', loader='directory')
    # documents = split(documents)
    # ingest(documents)
    query = "who is the client in the snow removal problem"
    results = retrieve(query)
    print(results)

if __name__ == '__main__':
    main()