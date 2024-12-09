import uuid
import chromadb

chroma_client = chromadb.PersistentClient(path="./DB")

working_context = chroma_client.get_or_create_collection(name="memory")

def print_memories(memories):
    memories_string = "### Inserted memories:\n"
    memories_string +=  "\n".join([f"- {memory}" for memory in memories])
    print(memories_string, "\n")


def results_to_string(results):
    result_string = "### Memory recall results:\n"
    result_string += "\n".join([f"- {entry['document']}" for entry in results])
    print(result_string, "\n")
    return result_string

def process_results(results):
    return [
        {
            "id": results["ids"][0][i], 
            "document": results["documents"][0][i] 
        }
        for i in range(len(results["ids"][0]))
    ]


def insert_memories(memories):
    working_context.add(
        documents=memories,
        ids=[f"{uuid.uuid4()}" for _ in range(len(memories))]
    )
    print_memories(memories)
    

def recall_memories(query, num_results=2):
    print(f"recall: {query}")
    if num_results is None:
        num_results = 2

    results = working_context.query(
        query_texts = [query], 
        n_results = num_results
    )
    processed_results = process_results(results)
    return results_to_string(processed_results)

def get_core_memory():
    with open("core_memory.txt", "r") as f:
        core_memory = f.read()

    print(f"\n\n###CORE MEMORY:\n{core_memory}\n\n")
    return core_memory


def core_memory_append(memory):
    print(f"\n\n### CORE MEMORY APPENED:\nadded the following:\n{memory}\n\n")
    if not memory.startswith("\n"):
        memory = "\n- " + memory
        
    with open("core_memory.txt", "a+") as f:
        f.write(memory)

def core_memory_replace(target_text, replacement_text):
    print(f"\n\n### CORE MEMORY replaced:\nnew text:\n{replacement_text}\n\n")
    content = get_core_memory()
    content = content.replace(target_text, replacement_text)
    
    with open("core_memory.txt", "a+") as f:
        f.write(content)

def get_memory_tools():
     return [
         {
            "type": "function",
            "function": {
                "name": "recall_memories",
                "description": "Retrieve relevant memories based on a given query",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "A text query to search and retrieve relevant memories"
                        },
                        "num_results": {
                            "type": "integer",
                            "description": "The maximum number of memory results to return (optional, defaults to 3)",
                            "default": 3
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "insert_memories",
                "description": "Insert one or multiple memories into the collection",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "memories": {
                            "type": "array",
                            "items": {
                                "type": "string"
                            },
                            "description": "A list of memory contents to be inserted. Can be a single memory or multiple memories."
                        }
                    },
                    "required": ["memories"]
                }
            }
        },
        {
            "type": "function", 
            "function": {
                "name": "core_memory_append",
                "description": "Appends a new line to the core memory ",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "memory": {
                            "type": "string",
                            "description": "The new line of text to append to the core memory "
                        }
                    },
                    "required": ["memory"]
                }
            }
        },
        {
            "type": "function", 
            "function": {
                "name": "core_memory_replace",
                "description": "Replaces text in the core memory with new text",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "target_text": {
                            "type": "string",
                            "description": "The exact string you want to replace from the core memory"
                        },
                        "replacement_text": {
                            "type": "string",
                            "description": "The new value you want to replace the string with"
                        }
                        
                    },
                    "required": ["memory"]
                }
            }
        },

    ]