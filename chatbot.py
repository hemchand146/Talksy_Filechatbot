import streamlit as st
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain

# -------------------------------
# Azure OpenAI Configuration
# -------------------------------
# Azure OpenAI configuration
AZURE_OPENAI_ENDPOINT = ""
AZURE_OPENAI_API_KEY = ""
AZURE_DEPLOYMENT_NAME = ""  # The deployment name you configured on Azure
AZURE_API_VERSION = ""  # Adjust as per your setup

# -------------------------------
# Streamlit UI
# -------------------------------
st.set_page_config(page_title="Talksy", page_icon="💬")

st.header("💬 Welcome to Talksy!")
st.subheader("Your personal document whisperer 🤫📄")

with st.sidebar:
    st.title("📚 Upload Zone")
    st.markdown("**Drop a PDF, and start chatting with it!**")
    file = st.file_uploader("🚀 Upload your PDF to begin the conversation", type="pdf")

# Always show input box
user_question = st.text_input("Ask Anything")

# Only run when a file is uploaded and question is asked
if file is not None and user_question:
    # Extract text from PDF
    text = ""
    pdf_reader = PdfReader(file)
    for page in pdf_reader.pages:
        content = page.extract_text()
        if content:
            text += content

    # Split the text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n"],
        chunk_size=1000,
        chunk_overlap=150,
        length_function=len
    )
    chunks = text_splitter.split_text(text)

    # Generate embeddings using Azure
    embeddings = AzureOpenAIEmbeddings(
        azure_endpoint="",
        api_key="",
        azure_deployment="",
        api_version=AZURE_API_VERSION
    )

    # Create FAISS vector store
    vector_store = FAISS.from_texts(chunks, embeddings)

    # Chat model from Azure
    llm = AzureChatOpenAI(
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY,
        azure_deployment=AZURE_DEPLOYMENT_NAME,
        api_version=AZURE_API_VERSION,
        temperature=0,
        max_tokens=1000
    )

    # Search for relevant chunks
    match = vector_store.similarity_search(user_question)
    #st.write(match)

    # Run the QA chain
    chain = load_qa_chain(llm, chain_type="stuff")
    response = chain.run(input_documents=match, question=user_question)
    st.write(response)
