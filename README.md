# 🤖 Lumina AI Assistant

A full-stack AI-powered assistant built with **FastAPI, JavaScript, SQLite, and OpenRouter** that combines conversational AI, document analysis, image understanding, voice interaction, chat management, and AI image generation into a single platform.

---

## ✨ Features

### 🔐 Authentication & Security

* User Registration and Login
* JWT-based Authentication
* Protected API Routes
* User-specific Chat History

### 💬 Advanced Chat System

* Create Multiple Chats
* Rename Chats
* Delete Chats
* Pin Important Chats
* Archive Conversations
* Search Through Chat History
* Real-Time Streaming AI Responses

### 🧠 Multi-Model AI Support

Choose between multiple AI models:

* OpenAI GPT Models
* Claude Models
* Gemini Models
* DeepSeek Models
* Additional OpenRouter-supported Models

### 🌐 Web Search Integration

* Automatic Search Detection
* Real-Time Internet Search
* AI Responses Enhanced with Web Results
* Up-to-Date Information Retrieval

### 📄 Document Intelligence

Upload and analyze:

* PDF Files
* DOCX Documents
* TXT Files

Capabilities:

* Document Summarization
* Question Answering
* Context-Aware Responses
* Document-Aware Conversations

### 🖼️ Vision AI

Upload images and ask questions about them.

Supported formats:

* PNG
* JPG
* JPEG

Capabilities:

* Image Understanding
* Visual Question Answering
* Scene Analysis

### 🎨 AI Image Generation

Generate images directly from chat prompts.

Examples:

* "Generate an image of a futuristic city"
* "Draw a cyberpunk robot"
* "Create an illustration of a dragon"

### 🎤 Voice Features

#### Speech-to-Text

* Voice Input
* Browser-Based Speech Recognition

#### Text-to-Speech

* AI Responses Read Aloud
* Voice Toggle Support
* Multi-Language Voice Support

### 📤 Export & Sharing

#### Export Chats

* TXT Export
* PDF Export

#### Share Chats

* Public Shareable Links
* Conversation Sharing

### 💻 Developer-Friendly Features

* Markdown Rendering
* Syntax Highlighting
* Copy Code Buttons
* Code Language Detection
* Streaming Responses

### 🎨 Modern User Experience

* Dark Mode
* Light Mode
* Responsive Design
* Drag-and-Drop File Upload
* Upload Progress Tracking
* Welcome Screen
* Clean Chat Interface

---

## 🏗️ System Architecture

User
↓
Frontend (HTML, CSS, JavaScript)
↓
FastAPI Backend
↓
Authentication Layer (JWT)
↓
AI Services & Tools
↓
OpenRouter Models
↓
Database (SQLite)

Additional Services:

* Web Search
* Document Processing
* Vision Analysis
* Image Generation
* Speech Services

---

## 🛠️ Technology Stack

### Frontend

* HTML5
* CSS3
* JavaScript (Vanilla JS)
* Marked.js
* Highlight.js

### Backend

* FastAPI
* Python

### Database

* SQLite

### Authentication

* JWT (JSON Web Tokens)
* Passlib (bcrypt)

### AI & LLM

* OpenRouter API
* GPT Models
* Claude Models
* Gemini Models
* DeepSeek Models

### Document Processing

* PyPDF
* python-docx

### Image Processing

* Vision Models
* Base64 Encoding

### PDF Export

* ReportLab

---

## 📁 Project Structure

```text
live-ai-assistant/

├── backend/
│   ├── agents/
│   ├── services/
│   ├── tools/
│   ├── database/
│   ├── uploads/
│   ├── main.py
│   └── requirements.txt
│
├── frontend/
│   ├── css/
│   ├── js/
│   ├── assets/
│   ├── home.html
│   ├── login.html
│   ├── register.html
│   └── chat.html
│
├── README.md
└── .gitignore
```

---

## 🚀 Installation

### Clone Repository

```bash
git clone https://github.com/yourusername/lumina-ai-assistant.git

cd lumina-ai-assistant
```

### Backend Setup

```bash
cd backend

python -m venv venv

venv\Scripts\activate

pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file:

```env
OPENROUTER_API_KEY=your_api_key_here
```

### Run Backend

```bash
python -m uvicorn main:app --reload
```

Backend URL:

```text
http://127.0.0.1:8000
```

### Run Frontend

Open the frontend folder using VS Code Live Server or any local web server.

---

## 📸 Screenshots

Add screenshots here:

### Home Page

![Home](screenshots/home.png)

### Chat Interface

![Chat](screenshots/chat.png)

### Document Analysis

![Document](screenshots/document.png)

### Image Generation

![Image Generation](screenshots/image-generation.png)

### Dark Mode

![Dark Mode](screenshots/dark-mode.png)

---

## 🎯 Key Learning Outcomes

This project demonstrates:

* Full-Stack Development
* REST API Design
* JWT Authentication
* Database Management
* AI Model Integration
* Streaming Responses
* File Processing
* Speech Recognition
* Text-to-Speech
* Image Generation
* Vision AI
* Prompt Engineering
* Software Architecture

---

## 🔮 Future Enhancements

* RAG (Retrieval-Augmented Generation)
* Vector Database Integration
* Long-Term AI Memory
* Multi-Agent Architecture
* Mobile Application
* Team Collaboration
* Cloud Deployment
* Docker Support
* OAuth Login
* Real-Time Collaboration

---

## 👨‍💻 Author

Developed by Cheeku

A full-stack AI assistant project showcasing modern AI application development with FastAPI and Large Language Models.
