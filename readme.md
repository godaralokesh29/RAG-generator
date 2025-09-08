# 🧠 NodeMind

> **"Break any topic into structured, visual knowledge graphs using AI + RAG."**

Lumino is an AI-powered application that automatically breaks down any topic into a **node-based diagram** using **Retrieval-Augmented Generation (RAG)**. It's a powerful tool for students, researchers, and content creators to visualize knowledge, brainstorm ideas, and explore complex concepts in a structured, interactive way.

---

## 🚀 Features

- ✅ **AI-generated Node Graphs**
- 🔄 **RAG-powered Topic Breakdown**
- 🧩 **Unordered / Ordered List Support**
- 🎨 **Customizable Node Appearance**
- ♿ **Accessibility Support**
- 🚫 **Common Mistake Detection**
- 💡 **Best Practices Hints**

---

## 🧠 How It Works

1. **User inputs a topic**  
   Example: `"Machine Learning"` or `"Climate Change"`

2. **RAG Pipeline kicks in**
   - **Retrieve:** Relevant documents are fetched from trusted sources (e.g., Wikipedia, ArXiv, academic APIs)
   - **Generate:** An LLM generates structured subtopics and explanations based on context

3. **Visualize as Nodes**
   - The result is displayed as an **interactive, draggable node graph**
   - Each node contains a subtopic or detail with expandable information

---



## 📚 Example

> **Input:** `"Photosynthesis"`

Generated Node Graph:


---

## 🛠 Tech Stack

| Layer        | Tools                                |
|--------------|--------------------------------------|
| **Frontend** | React, React Flow          |
| **Backend**  | Python, FastAPI               |
| **LLM**      | Gemini-AI-Flash-API      |
| **RAG**      | LangChain, LlamaIndex                |
| **Data Sources** | Wikipedia, Research APIs, Custom uploads |

---

## 📦 Installation (Dev)

```bash
cd nodemind
npm install
npm run dev
