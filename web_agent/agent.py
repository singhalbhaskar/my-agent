import vertexai
#import cloudpickle
from google.adk.agents import Agent
from google.adk.tools import VertexAiSearchTool, AgentTool
import os
import requests
from vertexai.agent_engines import AdkApp
# import asyncio



# 1. Initialize Vertex AI
#PROJECT_ID = "agentic-adc-dp"
#LOCATION = "us-central1"
#file_path = "agent.pkl"
#agent_framework = "google-adk"
#vertexai.init(project=PROJECT_ID, location=LOCATION)


def web_fetch_tool(url: str) -> str:
    """
    Useful for fetching web content through the corporate proxy on port 443.

    Args:
        url: The full URL of the website to fetch (e.g., 'https://google.com').
    """
    # Get the Proxy IP from environment variables
    proxy_ip = os.environ.get("PROXY_IP")
    
    # If PROXY_IP is present, configure the proxy dictionary using port 443
    proxies = None
    if proxy_ip:
        # Note: Even if the proxy is on 443, the protocol for the 
        # proxy connection itself is usually defined as http://
        proxy_address = f"http://{proxy_ip}:443"
        proxies = {
            "http": proxy_address,
            "https": proxy_address,
        }
    
    try:
        # 3. Perform the request
        # Setting verify=True is recommended; SWP uses certificates for TLS inspection if configured
        response = requests.get(url, proxies=proxies, timeout=10)
        
        return {
            "status": "success",
            "target_url": url,
            "proxy_used": proxy_ip,
            "http_code": response.status_code,
            "content_preview": response.text[:100] # First 100 chars
        }

    except Exception as e:
        return {
            "status": "failed",
            "target_url": url,
            "proxy_used": proxy_ip,
            "error": str(e)
        }






# 3. The Master Agent (The Orchestrator)
def create_master_agent():
    # rag_sub_agent = create_rag_agent()
    # web_sub_agent = create_web_agent()
    #search_path = "projects/agentic-adc-dp/locations/global/collections/default_collection/dataStores/agentic-rag-datastore"


    #rag_tool = VertexAiSearchTool(data_store_id=search_path, bypass_multi_tools_limit=True)


    master = Agent(
        model="gemini-2.5-flash",
        name="personal_assistant",
        description="I am the entry point for all requests.",
        instruction = """
        You are a professional assistant for the ADC team.
        
        GUIDELINES FOR TOOL USAGE:
        1. For any factual questions about company policies, technical documentation, or internal data, 
        ALWAYS use the 'rag_tool'.
        2. If user asks to search for a web page, use the web_fetch_tool.
        3. If the information is not found in the search results, state clearly that you do not know 
        based on the available documentation. But you can still use your own knowledge base to answer questions.
        
        GROUNDING & CITATIONS:
        - Every claim you make based on the search tool MUST include a citation.
        - Format citations as [Source Name or Index].
        - Summarize findings clearly and professionally.
        """,
        # This is the key: we pass agents into sub_agents
        # sub_agents=[rag_sub_agent, web_sub_agent]
        #tools=[rag_tool, web_fetch_tool]
        tools=[web_fetch_tool]
    )
    
    return AdkApp(agent=master)

def main():
    app = create_master_agent()
    # 3. Serialize the agent application using cloudpickle
    #with open(file_path, "wb") as f:
    #    cloudpickle.dump(app, f)
    # async for event in app.async_stream_query(
    #     user_id="USER_ID",  # Required
    #     message="can you try calling google.com",
    #     ):
    #     print(event)

if __name__ == "__main__":
    # asyncio.run(main())
    main()
