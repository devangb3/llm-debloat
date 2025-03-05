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
Set up environment (Windows)
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
