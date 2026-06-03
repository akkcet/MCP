import json
import numpy as np
from mcp_use import MCPClient, MCPAgent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
import asyncio
import os

CONFIG_PATH = "/home/aru_khuntia/mcpclient/config.json" 
PROJECT_ID = "project-339ed267-1361-44c4-a89"   # <-- change this
REGION = "us-central1"          # or your preferred region
os.environ["PYTHONHTTPSVERIFY"] = "0"
os.environ["GOOGLE_CLOUD_PROJECT"] = PROJECT_ID
os.environ["GOOGLE_CLOUD_LOCATION"] = REGION
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"   # 🔥 CRITICAL

# ✅ Extract tools dynamically from MCP
async def extract_mcp_metadata():
    with open(CONFIG_PATH, "r") as f:
        full_config = json.load(f)

    all_mcps = full_config["mcpServers"].keys()

    documents = []

    for mcp_name in all_mcps:
        print(f"\n🔹 Processing MCP: {mcp_name}")

        # ✅ Create config with ONLY this MCP
        single_config = {
            "mcpServers": {
                mcp_name: full_config["mcpServers"][mcp_name]
            }
        }

        # ✅ write temp config
        import tempfile
        temp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        with open(temp.name, "w") as f:
            json.dump(single_config, f)

        client = MCPClient(temp.name)

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0
        )

        agent = MCPAgent(client=client, llm=llm, memory_enabled=False)

        await agent.run("initialize")

        tools = agent._tools if hasattr(agent, "_tools") else []

        print(f"✅ Found {len(tools)} tools for {mcp_name}")

        for tool in tools:
            try:
                name = getattr(tool, "name", "")
                desc = getattr(tool, "description", "")

                schema = ""
                if hasattr(tool, "args_schema") and tool.args_schema:
                    try:
                        schema = str(tool.args_schema.model_json_schema())
                    except:
                        pass

                documents.append({
                    "mcp": mcp_name,
                    "tool": name,
                    "content": f"""
                    MCP: {mcp_name}
                    Tool: {name}
                    Description: {desc}
                    Schema: {schema}
                    """
                })

            except Exception as e:
                print(f"❌ Error in tool {name}: {e}")

        await client.close_all_sessions()

    print(f"\n✅ Total extracted tools: {len(documents)}")

    return documents


# ✅ Build FAISS DB
async def build_faiss_index():
    metadata = await extract_mcp_metadata()
    print("✅ Extracted MCP metadata", metadata)
    embeddings = GoogleGenerativeAIEmbeddings(
        model="gemini-embedding-001"
    )

    docs = [
        Document(
            page_content=item["content"],
            metadata={"mcp": item["mcp"]}
        )
        for item in metadata
    ]
    
    vectorstore = FAISS.from_documents(docs, embeddings)

    vectorstore.save_local("mcp_faiss_index")

    print("✅ FAISS index created with MCP metadata")


# ✅ Entry point
if __name__ == "__main__":
    asyncio.run(build_faiss_index())