from mcp_use import MCPClient, MCPAgent
import os
import asyncio
import json
import tempfile
from langchain_google_genai import ChatGoogleGenerativeAI
import tiktoken
from dotenv import load_dotenv
load_dotenv()

# ✅ Tokenizer (Gemini uses SentencePiece → approximate via tiktoken fallback)
try:
    
    enc = tiktoken.get_encoding("cl100k_base")
except:
    enc = None


# ========================
# ✅ ENV SETUP
# ========================

os.environ["PYTHONHTTPSVERIFY"] = "0"
os.environ["GOOGLE_CLOUD_PROJECT"] = os.getenv("google_project_id")
os.environ["GOOGLE_CLOUD_LOCATION"] = os.getenv("google_region")
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"


# ========================
# ✅ BASE MCP CONFIG
# ========================
"""
BASE_CONFIG = {
    "mcpServers": {
        "playwright": {
            "command": "npx",
            "args": ["@playwright/mcp@latest"]
        },
        "airbnb": {
            "command": "npx",
            "args": ["-y", "@openbnb/mcp-server-airbnb"]
        }
    }
}
"""

with open("/home/aru_khuntia/mcpclient/config.json", "r") as f:
    BASE_CONFIG = json.load(f)

# ========================
# ✅ CREATE TEMP CONFIG
# ========================
def create_config(selected_mcps):
    filtered = {
        "mcpServers": {
            k: BASE_CONFIG["mcpServers"][k]
            for k in selected_mcps
        }
    }

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
    with open(temp_file.name, "w") as f:
        json.dump(filtered, f)

    return temp_file.name


# ========================
# ✅ TOKEN COUNT FUNCTION
# ========================
def count_tokens(text):
    if enc:
        return len(enc.encode(text))
    return int(len(text) / 4)  # fallback


# ========================
# ✅ ANALYZE MCP LOAD
# ========================


def analyze_tools(agent):
    print("\n========== MCP LOAD STATS ==========")

    # ✅ get tools properly
    if hasattr(agent, "_tools"):
        tools = agent._tools
    elif hasattr(agent, "tools"):
        tools = agent.tools
    else:
        print("❌ Cannot access tools")
        return ""

    tool_count = len(tools)
    print(f"Total Tools Loaded: {tool_count}")

    all_tools_text = ""
    total_chars = 0

    for tool in tools:
        # ✅ Extract REAL fields instead of str(tool)
        name = getattr(tool, "name", "")
        desc = getattr(tool, "description", "")
        args = ""

        try:
            if hasattr(tool, "args_schema") and tool.args_schema:
                args = str(tool.args_schema.schema())
        except:
            args = ""

        tool_text = f"{name}\n{desc}\n{args}\n"

        all_tools_text += tool_text
        total_chars += len(tool_text)

    tool_tokens = count_tokens(all_tools_text)

    print(f"Total Tool Description Size (chars): {total_chars}")
    print(f"✅ Tool Tokens: {tool_tokens}")

    print("====================================\n")

    return all_tools_text


# ========================
# ✅ RUN EXPERIMENT
# ========================
async def run_experiment(selected_mcps, query):
    print(f"\n🚀 Running with MCPs: {selected_mcps}\n")

    config_path = create_config(selected_mcps)
    client = MCPClient(config_path)

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.3
    )

    agent = MCPAgent(
        client=client,
        llm=llm,
        memory_enabled=False
    )

    # ✅ STEP 1: force initialization
    print("⚡ Initializing tools...")
    await agent.run("say hello")   # dummy call

    # ✅ STEP 2: now tools exist → analyze
    tools_text = analyze_tools(agent)

    # ✅ STEP 3: estimate prompt tokens
    full_prompt = tools_text + "\nUser: " + query
    prompt_tokens = count_tokens(full_prompt)

    print("📊 PROMPT TOKEN USAGE")
    print(f"Total Prompt Tokens (approx): {prompt_tokens}\n")

    # ✅ STEP 4: actual query
    #response = await agent.run(query,max_iterations=3 )

    print(f"Query: {query}")
    #print(f"Agent Response: {response}")

    await client.close_all_sessions()


# ========================
# ✅ MAIN
# ========================
async def main():
    query = "open google.com"

    # ✅ Case 1: Single MCP
    await run_experiment(
        selected_mcps=["playwright"],
        query=query
    )

    # ✅ Case 2: Multiple MCPs
    await run_experiment(
        selected_mcps=["playwright", "airbnb","memory","puppeteer","notionApi","dockerhub","fetch-as-markdown","mock-stdio","rss","fetch-as-markdown","mlflow"],
        query=query
    )


if __name__ == "__main__":
    asyncio.run(main())