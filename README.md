# Code Debloater with DeepSeek-Coder

An AI-powered tool to analyze and remove bloat from code files while maintaining functionality. Optimized for Windows systems with 8GB RAM.

## Features
- 🧹 Automatic code debloating
- 📊 LOC metrics comparison
- ⏱️ Execution time tracking
- 💾 Automatic backups (.bak files)
- 🖥️ CPU-only operation support
- 🔄 Chunked processing for large files

## Installation

### Prerequisites
- Python 3.8+
- 8GB+ RAM
- 2GB+ free disk space (for model caching)

1. **Clone repository**
```bash
git clone https://github.com/devangb3/llm-debloat.git
```
2. **Install requirements**
```bash
pip install -r requirements.txt --prefer-binary
```
3. Setup environment(Windows)
```bash
mkdir D:\huggingface_cache
```

## Usage

***Basic command***

```bash
python debloater.py path/to/your/file.py
```

**Example**
```bash
python .\debloater.py "D:\Devang Masters\Q2\260\Project\Project_Repos\jawiki-kana-kanji-dict\jawiki\post_validate.py"
```

# Debloat using API

## Clone the repo and install requirements like above in step 2

## Usage
llm-choice is the LLM you want to use for debloating this file, currently only GPT4o and Deepseek-Coder are supported,
For GPT4o llm-choice=0
For Deepseek Coder llm-choice=1
*** Basic Command***

```bash
python .\debloater_api.py path/to/your/file.py --llm llm-choice
```
***Example using GPT4o***
```
python .\debloater_api.py "D:\Devang Masters\Q2\260\Project\Project_Repos\jawiki-kana-kanji-dict\jawiki\post_validate.py" --llm 0
```
***Example using Deepseek***
```
python .\debloater_api.py "D:\Devang Masters\Q2\260\Project\Project_Repos\jawiki-kana-kanji-dict\jawiki\post_validate.py" --llm 1
```
