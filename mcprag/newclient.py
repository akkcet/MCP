from mcp_use import MCPClient, MCPAgent
import os
import asyncio
import json
import tempfile
from langchain_google_genai import ChatGoogleGenerativeAI
from mcp_rag_router import retrieve_relevant_mcps
from dotenv import load_dotenv
load_dotenv()

os.environ["PYTHONHTTPSVERIFY"] = "0"
os.environ["GOOGLE_CLOUD_PROJECT"] = os.getenv("google_project_id")
os.environ["GOOGLE_CLOUD_LOCATION"] = os.getenv("google_region")
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"   # 🔥 CRITICAL

config_file = os.getenv("MCP_CONFIG_PATH", "config.json")


def build_filtered_config(selected_mcps):
    with open(config_file, "r") as f:
        base = json.load(f)

    filtered = {
        "mcpServers": {
            k: base["mcpServers"][k]
            for k in selected_mcps
            if k in base["mcpServers"]
        }
    }

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    #print("TEMP FILE", temp.read)
    with open(temp.name, "w") as f:
        json.dump(filtered, f)

    return temp.name


async def run_query(user_input, llm):
    # ✅ RAG selection
    selected_mcps = retrieve_relevant_mcps(user_input)

    print("🎯 Using MCPs:", selected_mcps)

    config_path = build_filtered_config(selected_mcps)
    print("Temp config file: ", config_path)
    
    with open(config_path, "r") as f:
        data = json.load(f)

    print(data)

    client = MCPClient(config_path)

    agent = MCPAgent(
        client=client,
        llm=llm,
        memory_enabled=True
    )

    response = await agent.run(user_input)

    await client.close_all_sessions()

    return response


async def main():
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3
    )

    while True:
        query = input("You: ")

        if query.lower() in ["exit", "quit"]:
            break

        response = await run_query(query, llm)
        print("Agent:", response)


if __name__ == "__main__":
    asyncio.run(main())
