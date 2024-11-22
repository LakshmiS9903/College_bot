from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from langchain_groq import ChatGroq
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from .models import ChatHistory, Course
from django.db import models
import os
import time
from datetime import datetime
from dotenv import load_dotenv


# Load environment variables
load_dotenv()
groq_api_key = os.getenv('GROQ_API_KEY')
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# Initialize Chat Model
llm = ChatGroq(groq_api_key=groq_api_key, model_name="Llama3-8b-8192")

# Define Prompt Template for Chatbot
prompt_template = """
    You are an AI assistant designed to answer user queries accurately and concisely using the provided context. 
    Respond only with information derived from the context. 
    If the answer is not present in the context, reply with: "I'm sorry, the information you are looking for is not available in the provided context."

    Context:
    {context}

    User Query:
    {input}

    Answer:
"""
template = PromptTemplate(input_variables=["context", "input"], template=prompt_template)

# Create a document processing chain
document_chain = create_stuff_documents_chain(llm, template)

# Initialize Embeddings and Document Loading for Chatbot
def initialize_vector_store():
    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    loader = PyPDFDirectoryLoader("./us_census")
    docs = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    final_documents = text_splitter.split_documents(docs[:20])
    vector = FAISS.from_documents(final_documents, embeddings)
    return vector

# Initialize the vector store globally for efficiency
vector = initialize_vector_store()

# Static Page Views
def aiml_view(request):
    return render(request, 'chat/aiml.html')

def aids_view(request):
    return render(request, 'chat/aids.html')

def bio_view(request):
    return render(request, 'chat/bio.html')

def csd_view(request):
    return render(request, 'chat/csd.html')

def civ_view(request):
    return render(request, 'chat/civ.html')

# Index Page
def index(request):
    return render(request, 'chat/index.html')

# Streamlit Chat View (only for logged-in users)
@login_required
def streamlit_chat(request):
    return render(request, 'chat/streamlit_chat.html')

# Courses View - Static Data
@login_required
def courses_view(request):
    courses = [
        {"title": "Artificial Intelligence And Data Science", "description": "Learn to analyze and model data, combining AI and data science."},
        {"title": "Artificial Intelligence And Machine Learning", "description": "Gain expertise in AI and advanced data-driven applications."},
        {"title": "Civil And Environmental Engineering", "description": "Study the construction, design, and maintenance of infrastructure."},
        {"title": "Computer Science And Design Engineering", "description": "Master computer science principles with a focus on digital design."},
        {"title": "Biomedical And Robotics", "description": "Explore biomedical technology and robotics for advancements in healthcare."},
    ]
    return render(request, 'chat/courses.html', {"courses": courses})

# Chatbot View
def chatbot_view(request):
    response = None
    response_time = None

    if request.method == "POST":
        question = request.POST.get("question")

        if question:
            start_time = time.time()

            # Fetch context from vector store
            context = vector.similarity_search(question, k=1)
            context_text = " ".join([doc.page_content for doc in context])

            # Define your prompt template
            prompt_template = """
                Answer the questions based on the provided context only.
                Please provide the most accurate response based on the question.
                <context>
                {context}
                </context>
                Question: {input}
            """
            template = PromptTemplate(input_variables=["context", "input"], template=prompt_template)

            # Create an LLMChain
            llm_chain = LLMChain(prompt=template, llm=llm)

            # Run the chain
            response = llm_chain.run({"context": context_text, "input": question})

            response_time = round(time.time() - start_time, 2)

            # Save the question and response to the history
            ChatHistory.objects.create(
                question=question,
                answer=response,
                timestamp=datetime.now()
            )

    # Get the last 10 questions and answers from the history
    history = ChatHistory.objects.all().order_by('-timestamp')[:10]

    return render(request, "chat/chat.html", {
        "response": response,
        "response_time": response_time,
        "history": history
    })

# Dynamic Course List from Database
def course_list(request):
    courses = Course.objects.all()
    return render(request, 'courses.html', {'courses': courses})
