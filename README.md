# **Chatbot Project with Flask and ChromaDB**
![ai](https://github.com/user-attachments/assets/8dc6e09a-50bc-4921-beee-a6021d28f9ec)

This project implements a **document-based chatbot** capable of answering questions using a combination of:

- **Flask** (as the web framework)  
- **ChromaDB** (for document storage and querying)  
- **OpenAI** (for embeddings and natural language responses)  
- and a custom **frontend** for user interaction.

---

## **Overview**

The goal of this project is to build a chatbot that processes documents, generates embeddings, stores them in a database (**ChromaDB**), and retrieves the most relevant context to answer user queries. The project integrates backend functionality with a dynamic frontend for seamless interaction.

---

## **Project Features**

### **1. Document Processing**
- Documents (e.g., text files) are loaded from a directory.  
- Each document is split into smaller chunks for efficient storage and querying.  
- Preprocessing ensures all chunks are clean and ready for embeddings.

### **2. Embedding Generation**
- Embeddings for each document chunk are generated using **OpenAI's embedding model** (`text-embedding-3-small`).  
- These embeddings represent the semantic meaning of each chunk.

### **3. Database Storage**
- **ChromaDB** is used as the vector database to store document embeddings and metadata.  
- Each document chunk is stored with its embedding for quick and efficient retrieval.

### **4. Query and Response**
- When the user asks a question, the system:
  1. Converts the question into an embedding.  
  2. Queries **ChromaDB** for the most relevant document chunks.  
  3. Passes these chunks to **OpenAI's GPT model** to generate a concise response.

### **5. Frontend**
- A responsive and user-friendly chatbot interface.  
- Users can type their questions and receive **AI-powered answers dynamically**.

---

## **Setup**

### **1. Clone the Repository**
```bash
git clone https://github.com/marslanalvi/ChromaDocBot.git
cd ChromaDocBot
```

### **2. Install Required Dependencies**
```bash
pip install -r requirements.txt
```

### **3. Add Environment Variables**
Create a `.env` file in the root directory and add your OpenAI API key:
```plaintext
OPENAI_API_KEY=your_openai_api_key
```

---

## **How It Works**

### **Backend Workflow**
1. **Document Preprocessing**:  
   - Documents from the `data` directory are chunked and embedded using **OpenAI**.  
   - These embeddings are stored in **ChromaDB**.

2. **Query Handling**:  
   - The user query is embedded and compared with stored embeddings in **ChromaDB**.  
   - The most relevant document chunks are retrieved and sent to **OpenAI's GPT** for response generation.

### **Frontend Workflow**
- The `index.html` provides a chatbot interface.  
- The user input is sent to the `/chat` API endpoint.  
- The AI response is displayed dynamically.

---

## **Key Achievements**

- **Integration of ChromaDB and OpenAI**:  
  Efficient storage and retrieval of document embeddings for high-performance querying.

- **Customizable Document Pipeline**:  
  The system allows for dynamic addition of documents.

- **Interactive Frontend**:  
  A responsive, user-friendly chatbot interface.

---

## **Future Improvements**

1. **Authentication**:  
   Add user authentication for secure access.

2. **Advanced Query Parsing**:  
   Improve query handling with natural language preprocessing.

3. **Multi-File Support**:  
   Enable support for other file types (e.g., PDFs, Word documents).

4. **Deployment**:  
   Deploy the project on a cloud platform like **Heroku**, **AWS**, or **GCP**.

---

## **Why This Project?**

### **Purpose**
- Simplify access to information within large document repositories.  
- Demonstrate the integration of advanced AI and database technologies.

### **Technologies Used**
- **Flask**: For backend APIs and routing.  
- **ChromaDB**: For storing and retrieving document embeddings.  
- **OpenAI**: For semantic understanding and response generation.  
- **HTML, CSS, JS**: For building a responsive frontend.

---

## **Contributing**
Contributions are welcome! Please fork the repository, make changes, and submit a pull request.  
*Courtesy to*: [RAG Intro Chat with Docs](https://github.com/pdichone/rag-intro-chat-with-docs)
