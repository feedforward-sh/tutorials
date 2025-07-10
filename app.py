from langchain_core.messages import (
    AIMessageChunk, HumanMessage)
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langgraph.prebuilt import ToolNode
from langchain_core.messages import AnyMessage
from typing import TypedDict, List, Annotated
from dotenv import load_dotenv
from langgraph.graph import StateGraph, START, END, \
    add_messages
from langchain_mcp_adapters.client import MultiServerMCPClient


load_dotenv()


from langchain_core.tools import tool

@tool
def get_time() -> str:
    """Returns the current time."""
    from datetime import datetime
    return datetime.now().strftime("%H:%M:%S")


class State(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]


async def get_simple_graph_agent():
    llm = ChatOpenAI(
        name="gpt-4o-mini",
        temperature=0
    )

    mcp_client = MultiServerMCPClient({
        "toolkit": {
            "url": "http://localhost:8000/mcp/",
            "transport": "streamable_http"
        }
    })
    tools = await mcp_client.get_tools()
    llm = llm.bind_tools(tools)
    tool_node = ToolNode(tools)

    async def llm_node(state: State) -> State:
        resp = await llm.ainvoke(state["messages"])
        state["messages"].append(resp)
        return state
    
    async def tool_handler(state: State):
        last = state["messages"][-1]
        if getattr(last, "tool_calls", None):
            return "tool_node"      
        return END

    # Build graph
    graph = StateGraph(State)
    graph.add_node("llm_node", llm_node)
    graph.add_node("tool_node", tool_node)
    graph.set_entry_point("llm_node")
    graph.add_conditional_edges(
        "llm_node",
        tool_handler
    )
    graph.add_edge("tool_node", "llm_node")
    graph.set_finish_point("llm_node")
    return graph.compile()


async def main():
    graphai = await get_simple_graph_agent()
    config = {
        "configurable": {"thread_id": f"test"}
    }
        
    while True:
            
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            return
        
        input_message = HumanMessage(content=user_input)

        print("\nAssistant:", end="", flush=True)
        async for chunk_type, stream_data in graphai.astream(
            {"messages": [input_message]},
            config=config,
            stream_mode=["messages", "values"]):
            
            if chunk_type == "messages":
                chunk, metadata = stream_data
                if isinstance(chunk, AIMessageChunk):
                    if chunk.content:
                        print(chunk.content, end="", flush=True)
        print("\n")




if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
