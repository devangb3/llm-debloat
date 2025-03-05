from llama_cpp import Llama
import argparse
import os
import sys
from pathlib import Path
import time

# Configuration
MAX_CONTEXT = 16384
CHUNK_SIZE = 4096
TEMPERATURE = 0.1

os.environ['GGML_CACHE'] = os.path.join('D:\\', 'huggingface_cache')

def count_loc(code: str) -> int:
    """Count lines of code ignoring comments and blanks"""
    return sum(1 for line in code.split('\n') 
              if line.strip() and not line.strip().startswith(('#', '//')))

def load_model():
    print("\n📚 Loading the model...")
    model_file = "deepseek-coder-1.3b-instruct.Q4_K_M.gguf"
    model_path = os.path.join(os.environ['GGML_CACHE'], model_file)
    
    if not os.path.exists(model_path):
        print("⬇️  Downloading model from HuggingFace...")
        from huggingface_hub import hf_hub_download
        hf_hub_download(
            repo_id="TheBloke/deepseek-coder-1.3b-instruct-GGUF",
            filename=model_file,
            local_dir=os.environ['GGML_CACHE'],
            resume_download=True
        )
    else:
        print("✓ Using cached model")

    print("🚀 Initializing model...")
    return Llama(
        model_path=model_path,
        n_ctx=MAX_CONTEXT,
        n_threads=4,
        n_gpu_layers=0,
        verbose=False
    )

def process_chunk(llm: Llama, original: str) -> str:
    print("📝 Processing code chunk...")
    response = llm.create_chat_completion(
        messages=[{
            "role": "user",
            "content": f"""Refactor this code to remove bloat while maintaining functionality.
Return ONLY the cleaned code wrapped in ``` delimiters, no analysis.

Original code:
{original}

Cleaned code:"""
        }],
        max_tokens=CHUNK_SIZE + 500,
        temperature=TEMPERATURE
    )
    print("✓ Chunk processed")
    
    result = response['choices'][0]['message']['content']
    if '```' in result:
        return result.split('```')[1].strip().lstrip('python\n')
    return result

def process_file(file_path: str) -> dict:
    print(f"\n📂 Opening file: {file_path}")
    with open(file_path, 'r+', encoding='utf-8') as f:
        original_code = f.read()
        original_loc = count_loc(original_code)
        print(f"📊 Original LOC: {original_loc}")
        
        llm = load_model()
        processed_chunks = []
        
        total_chunks = len(original_code) // (CHUNK_SIZE//2) + 1
        print(f"\n🔄 Processing {total_chunks} chunks...")
        
        # Process in overlapping chunks
        for i in range(0, len(original_code), CHUNK_SIZE//2):
            chunk_num = (i // (CHUNK_SIZE//2)) + 1
            print(f"\n⚙️  Processing chunk {chunk_num}/{total_chunks}")
            chunk = original_code[i:i+CHUNK_SIZE]
            processed = process_chunk(llm, chunk)
            processed_chunks.append(processed)
            
        print("\n💾 Saving results...")
        new_code = '\n'.join(processed_chunks)
        new_loc = count_loc(new_code)
        
        # Create backup
        backup_path = f"{file_path}.bak"
        print(f"📑 Creating backup at: {backup_path}")
        with open(backup_path, 'w', encoding='utf-8') as backup:
            backup.write(original_code)
        
        # Write debloated code
        print("✍️  Writing debloated code...")
        f.seek(0)
        f.write(new_code)
        f.truncate()
        
        return {
            'original_loc': original_loc,
            'new_loc': new_loc,
            'reduction': ((original_loc - new_loc)/original_loc)*100
        }

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Code Debloater')
    parser.add_argument('file_path', help='Path to code file')
    args = parser.parse_args()

    print("\n🔧 Code Debloater Starting...")
    start_time = time.time()

    try:
        print("\n🔍 Analyzing and refactoring code...")
        
        metrics = process_file(args.file_path)
        
        elapsed_time = time.time() - start_time
        print(f"\n⏱️  Process completed in {elapsed_time:.2f} seconds")
        
        print(f"\n=== Code Metrics ===")
        print(f"Original LOC: {metrics['original_loc']}")
        print(f"New LOC:      {metrics['new_loc']}")
        print(f"Reduction:    {metrics['reduction']:.2f}%")
        print(f"Backup saved: {args.file_path}.bak")
        print("====================")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)