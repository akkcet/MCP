
# 🚀 MCP RAG Router

A production-ready **RAG-based routing layer for Model Context Protocol (MCP)** that dynamically selects relevant MCP servers, reducing token usage and improving agent efficiency.

---

## 🧠 Problem

By default, MCP agents load **all available tools from all MCP servers** into the LLM context.

This leads to:

- 🚫 Large prompt sizes (token explosion)
- 💸 Increased cost
- 🐌 Slower responses
- 🤯 Confused tool selection by the agent

---


---
## ✅ Solution

This project introduces a **tool-level RAG router** for MCP:

1. Index all MCP tools using embeddings (FAISS)
2. Retrieve relevant tools based on user query
3. Select only relevant MCP servers
4. Dynamically build filtered MCP configuration
5. Execute agent using only selected MCPs

👉 Result: Only relevant tools are passed to the LLM

---

## ⚡ Key Features

- ✅ Tool-level semantic indexing (FAISS)
- ✅ Dynamic MCP selection per query
- ✅ Automatic MCP config filtering
- ✅ Works seamlessly with `mcp_use`
- ✅ Token usage tracking (prompt + response)
- ✅ Plug-and-play architecture
- ✅ Compatible with multiple MCP servers

---

## 🧠 Architecture

User Query  
↓  
RAG Retriever (FAISS)  
↓  
Relevant Tools  
↓  
MCP Selection  
↓  
Filtered MCP Config  
↓  
MCPAgent Execution  

---

## 🔧 Example

### Input

\`\`\`python
query = "open google.com"
\`\`\`

### Routing

\`\`\`
🎯 Using MCPs: ['playwright']
\`\`\`

### Output

\`\`\`
📊 INPUT TOKENS: 2100
📊 OUTPUT TOKENS: 120
📊 TOTAL TOKENS: 2220
\`\`\`

✅ Only browser tools are loaded  
❌ Other MCPs are excluded  

---

## 📊 Token Efficiency (Example)

| Setup | Tools Loaded | Tokens |
|------|-------------|--------|
| All MCPs | ~80+ tools | ❌ High |
| RAG-selected MCPs | ~20 tools | ✅ Reduced |

✅ Up to ~50-80% reduction in token usage  

---

## 🧩 Why This Project?

| Feature | Existing Solutions | This Project |
|--------|------------------|-------------|
| RAG-based MCP routing | ✅ | ✅ |
| Tool-level indexing | ⚠️ | ✅ |
| Works with real MCP servers | ⚠️ | ✅ |
| Plug-and-play with mcp_use | ❌ | ✅ |
| Dynamic MCP config filtering | ❌ | ✅ |
| Token tracking | ❌ | ✅ |

---

## ⚙️ Installation

\`\`\`bash
git clone https://github.com/akkcet/MCP.git
cd mcp-rag-router
pip install -r requirements.txt
\`\`\`

---

## 🚀 Usage

\`\`\`bash
python run.py
\`\`\`

---

## ⚙️ Configuration

Edit:

\`\`\`
config.json
\`\`\`

---

## 🧪 Benchmarking

\`\`\`bash
python testtoken.py
\`\`\`

---

## ⚠️ Limitations

- Approximate token counting
- Some MCP tools need input sanitization
- Single-MCP routing by default

---

## 🚀 Future Work

- Multi-MCP planning
- Better routing confidence
- Cost + latency tracking
- UI dashboard

---

## 🤝 Contributing

PRs and suggestions are welcome!

---

## ⭐ Support

If this helps you, please star the repo ⭐
