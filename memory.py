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

def get_core_memory(path):
    with open(path, "r") as f:
        core_memory = f.read()

    print(f"\n\n###CORE MEMORY:\n{core_memory}\n\n")
    return core_memory


def update_core_memory(new_line):
    print(f"\n\n### CORE MEMORY UPDATED:\nadded the following:\n{new_line}\n\n")
    if not new_line.startswith("\n"):
        new_line = "\n- " + new_line
        
    with open("core_memory.txt", "a+") as f:
        f.write(new_line)
    