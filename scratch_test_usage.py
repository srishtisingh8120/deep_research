from langchain_core.messages import AIMessage
from langgraph.types import Command
import sys

# add path to sdk.py
sys.path.append("/Users/sv-mac-0284/Logging_library")
from smartllmops.sdk import SDKTracer

tracer = SDKTracer(telemetry=None)

# mock command
msg = AIMessage(content="hello", usage_metadata={"input_tokens": 10, "output_tokens": 20, "total_tokens": 30})
cmd = Command(update={"researcher_messages": [msg]})

raw_usage = tracer._find_usage_in_object(cmd)
print("raw_usage:", raw_usage)
if raw_usage:
    print("normalized:", tracer._normalize_usage(raw_usage))
