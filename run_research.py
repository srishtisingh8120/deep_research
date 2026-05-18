#!/usr/bin/env python3
import sys
import json
import time
import requests
from typing import Optional

BASE_URL = "http://127.0.0.1:2024"

def print_header(title: str):
    print("=" * 60)
    print(f" {title:^58}")
    print("=" * 60)

def main():
    print_header("Open Deep Research CLI Client 🚀")
    
    # Get user query
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        try:
            query = input("Enter your research topic/query: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            return

    if not query:
        print("Error: Query cannot be empty.")
        return

    print(f"\n[1/3] Initializing new research thread...")
    try:
        # 1. Create a new thread
        thread_response = requests.post(f"{BASE_URL}/threads", json={})
        if thread_response.status_code != 200:
            print(f"Failed to create thread: {thread_response.text}")
            return
        thread_data = thread_response.json()
        thread_id = thread_data["thread_id"]
        print(f"✓ Thread created successfully (ID: {thread_id})")
        
        # 2. Start deep research run
        print(f"\n[2/3] Submitting query to Deep Researcher: '{query}'")
        print("Note: The agent will use Tavily search and Llama-3.3-70b via Groq to synthesize the report.")
        print("Research in progress... (this may take 1-2 minutes, please wait)\n")
        
        # We use the wait endpoint which blocks until the run completes
        run_payload = {
            "assistant_id": "Deep Researcher",
            "input": {
                "messages": [
                    {"role": "human", "content": query}
                ]
            },
            "config": {
                "configurable": {
                    "research_model": "groq:llama-3.1-8b-instant",
                    "final_report_model": "groq:llama-3.1-8b-instant",
                    "compression_model": "groq:llama-3.1-8b-instant",
                    "summarization_model": "groq:llama-3.1-8b-instant",
                    "research_model_max_tokens": 1000,
                    "final_report_model_max_tokens": 1000,
                    "compression_model_max_tokens": 1000,
                    "summarization_model_max_tokens": 1000,
                    "allow_clarification": False
                }
            },
            "stream_mode": ["values"],
            "durability": "async"
        }
        
        start_time = time.time()
        
        # Add a simple console spinner/wait simulator while waiting for response
        response = requests.post(f"{BASE_URL}/threads/{thread_id}/runs/wait", json=run_payload, timeout=600)
        
        elapsed = time.time() - start_time
        
        if response.status_code != 200:
            print(f"Error during execution: {response.text}")
            return
            
        print(f"✓ Research complete! (Took {elapsed:.1f} seconds)\n")
        print_header("Research Results")
        
        # 3. Retrieve final thread state to extract final report
        state_response = requests.get(f"{BASE_URL}/threads/{thread_id}/state")
        if state_response.status_code != 200:
            print(f"Failed to get thread state: {state_response.text}")
            return
            
        state_data = state_response.json()
        values = state_data.get("values", {})
        
        # Get final report from state
        final_report = values.get("final_report")
        if final_report:
            print(final_report)
        else:
            # Fallback to messages
            messages = values.get("messages", [])
            if messages:
                # Find last AI message content
                ai_messages = [msg for msg in messages if msg.get("type") == "ai"]
                if ai_messages:
                    print(ai_messages[-1].get("content"))
                else:
                    print("No final report generated. Raw state:")
                    print(json.dumps(values, indent=2))
            else:
                print("No output found in state values.")
                print(json.dumps(values, indent=2))
                
        print("\n" + "=" * 60)
        print(f"You can also visualize this execution in LangSmith Studio:")
        print(f"https://smith.langchain.com/studio/thread/{thread_id}?baseUrl={BASE_URL}")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to the local LangGraph server at http://127.0.0.1:2024.")
        print("Please make sure the development server is running. You can start it with:")
        print("uvx --refresh --from \"langgraph-cli[inmem]\" --python 3.11 langgraph dev --allow-blocking")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
