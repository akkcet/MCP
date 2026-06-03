from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
from dotenv import load_dotenv
load_dotenv()

PROJECT_ID = "project-339ed267-1361-44c4-a89"   # <-- change this
REGION = "us-central1"          # or your preferred region
os.environ["PYTHONHTTPSVERIFY"] = "0"
os.environ["GOOGLE_CLOUD_PROJECT"] = os.getenv("google_project_id")
os.environ["GOOGLE_CLOUD_LOCATION"] = os.getenv("google_region")
os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"   # 🔥 CRITICAL
embeddings = GoogleGenerativeAIEmbeddings(
    model= "gemini-embedding-001"
)

vectorstore = FAISS.load_local(
    "mcp_faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)


def retrieve_relevant_mcps(query, top_k=5, threshold=1.0):
    results = vectorstore.similarity_search_with_score(query, k=top_k)
    print("Results:  ",results)
    selected_mcps = set()

    print("\n🔎 Retrieval Results:")
    for doc, score in results:
        print(f"MCP: {doc.metadata['mcp']} | Score: {score}")

        # ✅ FILTER HERE
        if score < threshold:
            selected_mcps.add(doc.metadata["mcp"])

    selected = list(selected_mcps)

    # ✅ fallback (important)
    if not selected:
        selected = ["playwright"]

    print("🎯 Final MCPs:", selected)

    return selected[:1]