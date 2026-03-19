# SciHub Download by PMID

从 Sci-Hub 下载 PDF 论文的工具，支持通过 PMID 或 DOI 批量下载。

## 功能特性

- 支持多种输入格式：CSV、TXT、XLSX
- 支持单个 PMID/DOI 下载
- 多线程并行下载
- 多种文件名命名模式
- 详细的输出控制

## 安装

### 方法一：pip 安装（推荐）

```bash
pip install scihub-download
```

### 方法二：从源码安装

```bash
# 克隆仓库
git clone https://github.com/spongxin/scihub-download-by-pmid.git
cd scihub-download-by-pmid

# 安装依赖
pip install -e .

# 或安装完整开发版本
pip install -e ".[dev]"
```

### 方法三：使用 pip 直接安装

```bash
pip install git+https://github.com/spongxin/scihub-download-by-pmid.git
```

## 使用方法

### 命令行基本用法

```bash
# 查看帮助
scihub-download --help

# 使用 python -m 运行
python -m scihub_download --help
```

### 输入方式

#### 1. 从文件输入

**CSV 格式：**
```csv
PMID,DOI
12345678,10.1234/example
87654321,
```

**TXT 格式（每行一个 ID）：**
```
12345678
10.1234/example
87654321
```

**Excel 格式：**
```bash
scihub-download --file papers.xlsx
```

#### 2. 单个 ID 输入

```bash
# 使用 PMID
scihub-download --id 12345678

# 使用 DOI
scihub-download --id 10.1234/example
```

### 选项说明

| 选项 | 简写 | 说明 | 默认值 |
|------|------|------|--------|
| `--file` | `-f` | 输入文件路径 (CSV/TXT/XLSX) | - |
| `--id` | - | 单个 PMID 或 DOI | - |
| `--output` | `-o` | 输出目录 | `./pdfs` |
| `--workers` | `-w` | 并行下载线程数 | `5` |
| `--format` | - | 文件名格式 (pmid/doi/original) | `pmid` |
| `--verbose` | `-v` | 详细输出 | - |
| `--quiet` | `-q` | 静默模式 | - |

### 使用示例

```bash
# 从 CSV 文件下载，设置输出目录和线程数
scihub-download --file papers.csv --output ./pdfs -w 10

# 从 TXT 文件下载，使用 DOI 作为文件名
scihub-download --file ids.txt --format doi

# 下载单个论文
scihub-download --id 12345678 --output /path/to/pdfs

# 启用详细输出
scihub-download --file papers.csv -v

# 使用 Python 模块运行
python -m scihub_download --file papers.csv
```

## 输入文件格式详解

### CSV 文件

第一行必须是表头，支持以下列名：
- `PMID` 或 `pmid`
- `DOI` 或 `doi`

```csv
PMID,DOI
12345678,10.1234/example
87654321,
```

### TXT 文件

每行一个 ID，可以是 PMID 或 DOI：
```
12345678
10.1234/example/doi
PMID:87654321
DOI:10.5678/test
```

### Excel 文件

使用 pandas 读取，支持任意包含 PMID 或 DOI 列的 Excel 文件。

## 依赖

- Python >= 3.8
- requests >= 2.0.0
- pandas >= 2.0.0
- pymupdf >= 1.20.0
- tqdm >= 4.0.0
- openpyxl >= 3.0.0

## 开发

```bash
# 克隆项目
git clone https://github.com/spongxin/scihub-download-by-pmid.git
cd scihub-download-by-pmid

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 带覆盖率运行测试
pytest --cov=scihub_download
```

## 许可证

MIT License

## 注意事项

1. 请确保遵守 Sci-Hub 的使用条款和相关法律法规
2. 下载的论文仅供个人学习研究使用
3. 部分论文可能因版权问题无法下载