# SciHub Download by PMID

从 Sci-Hub 下载 PDF 论文的工具，支持通过 PMID 或 DOI 批量下载。

## 功能特性

- **灵活的输入格式**：支持 CSV、TXT、XLSX 文件，自动识别 PMID/DOI 列
- **智能列识别**：支持小写列名 (pmid/doi)，自动识别只有 PMID 或只有 DOI 的文件
- **自动 ID 识别**：TXT 文件中自动区分 PMID（数字）和 DOI（含"/"）
- **多格式输入**：支持 CSV、TXT、XLSX 文件和单个 PMID/DOI
- **智能源管理**：自动发现、测试和排序可用的 Sci-Hub 镜像源
- **错误分类**：自动识别 404、网络错误、验证失败并采取不同策略
- **源故障转移**：当一个源失败时自动切换到下一个源
- **多线程下载**：支持并行下载，可配置线程数
- **文件名控制**：支持 PMID、DOI、原始名称三种命名模式
- **完整性检查**：自动跳过已存在的有效文件，检测并重新下载损坏的文件
- **详细日志**：支持详细输出和静默模式

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
| `--delete-corrupted` | - | 删除损坏文件后重新下载 | false |
| `--refresh-sources` | - | 强制刷新源缓存 | false |
| `--verbose` | `-v` | 详细输出 | - |
| `--quiet` | `-q` | 静默模式 | - |

### 详细选项说明

#### `--output` / `-o`
指定 PDF 文件的保存目录。如果目录不存在，会自动创建。
```bash
scihub-download --file papers.csv --output /path/to/pdfs
```

#### `--format`
选择生成文件名的模式：
- `pmid`（默认）：使用 PMID 作为文件名，如 `12345678.pdf`
- `doi`：使用 DOI 作为文件名，如 `10.1234_example.pdf`（斜杠被替换为下划线）
- `original`：保留原始标识符（无 `.pdf` 后缀）

```bash
# 使用 DOI 作为文件名
scihub-download --file papers.csv --format doi

# 使用原始名称
scihub-download --file papers.csv --format original
```

#### `--delete-corrupted`
启用后，如果检测到已存在的 PDF 文件损坏，会自动删除并重新下载。
```bash
scihub-download --file papers.csv --delete-corrupted
```

#### `--refresh-sources`
强制刷新 Sci-Hub 源缓存，放弃已缓存的源列表，重新获取最新源。
```bash
scihub-download --file papers.csv --refresh-sources
```

#### `--workers` / `-w`
控制并行下载的线程数。增加线程数可以提高下载速度，但可能增加被封禁的风险。
```bash
# 使用 10 个线程
scihub-download --file papers.csv --workers 10
```

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

# 启用损坏文件检测和重新下载
scihub-download --file papers.csv --delete-corrupted

# 强制刷新源列表
scihub-download --file papers.csv --refresh-sources

# 使用 Python 模块运行
python -m scihub_download --file papers.csv
```

## 输入文件格式详解

### CSV 文件

第一行必须是表头，支持以下列名（大小写均可）：
- `PMID`、`pmid`
- `DOI`、`doi`

**完整格式（PMID 和 DOI 都有）：**
```csv
PMID,DOI
12345678,10.1234/example
87654321,10.5678/test
```

**只有 PMID 列：**
```csv
pmid
12345678
87654321
```

**只有 DOI 列：**
```csv
doi
10.1234/example
10.5678/test
```

**PMID 和 DOI 混合（自动识别）：**
```csv
id
12345678
10.1234/example
```

### TXT 文件

每行一个 ID，自动识别 PMID 和 DOI：
- **PMID**: 纯数字
- **DOI**: 包含 "/" 字符

```
12345678
10.1234/example/doi
87654321
10.5678/test
```

### Excel 文件

使用 pandas 读取，支持任意包含 PMID 或 DOI 列的 Excel 文件。

## 核心功能详解

### 智能源管理

工具会自动从 sci-hub.pub 获取可用的 Sci-Hub 镜像源，并按响应速度排序。首次使用时会获取并缓存源列表，后续使用会直接使用缓存的源。

源管理功能包括：
- **自动发现**：从可靠的源列表网站自动获取可用镜像
- **测试排序**：测试每个源的响应时间，选择最快的源优先使用
- **缓存机制**：本地缓存源列表，避免频繁网络请求
- **手动覆盖**：可通过 `--sources` 参数手动指定源列表

### 错误分类与处理

下载过程中遇到不同类型的错误会采取不同的处理策略：

| 错误类型 | 说明 | 处理策略 |
|----------|------|----------|
| `NOT_FOUND` (404) | 论文在当前源不可用 | 立即尝试下一个源 |
| `NETWORK_ERROR` | 网络连接问题 | 尝试下一个源 |
| `VALIDATION_FAILED` | 下载的文件验证失败 | 尝试下一个源 |
| `SUCCESS` | 下载成功 | 保存文件，记录成功 |

### 文件完整性

- **跳过已存在文件**：如果目标文件已存在且有效（可正常打开的 PDF），自动跳过下载
- **损坏检测**：使用 PyMuPDF 验证 PDF 文件完整性
- **损坏处理**：可选择 `--delete-corrupted` 自动删除损坏文件并重新下载

### 日志记录

- 详细模式 (`-v`)：显示每个论文的下载进度、源尝试详情
- 静默模式 (`-q`)：仅显示最终摘要
- 日志文件：保存下载日志到 `download_log.txt`

## 编程接口

### 作为 Python 模块使用

```python
from scihub_download import downloader, source_manager, input_parser

# 解析输入文件
df = input_parser.parse_file("papers.csv")

# 获取可用源
sources = source_manager.get_sources()

# 下载单个论文
result = downloader.download_single_source(
    pmid="12345678",
    doi="10.1234/example",
    save_dir="./pdfs",
    sources=sources
)

# 清理文件名
filename = downloader.clean_filename("12345678", pattern="pmid")
# 结果: "12345678.pdf"

# 验证 PDF 文件
is_valid = downloader.is_pdf_valid("path/to/file.pdf")
```

### 错误类型枚举

```python
from downloader import DownloadErrorType

# DownloadErrorType 包含:
# - SUCCESS: 下载成功
# - NOT_FOUND: 404 错误，论文不可用
# - NETWORK_ERROR: 网络错误
# - VALIDATION_FAILED: 文件验证失败
```

### 源管理器

```python
from scihub_download.source_manager import SourceManager

# 创建源管理器
sm = SourceManager()

# 获取最佳源
sources = sm.get_best_sources()

# 刷新源缓存
sm.refresh_sources()

# 手动设置源
sources = ["sci-hub.se", "sci-hub.tw"]
```

## 依赖

- Python >= 3.8
- requests >= 2.0.0
- pandas >= 2.0.0
- pymupdf >= 1.20.0
- tqdm >= 4.0.0
- openpyxl >= 3.0.0
- beautifulsoup4 >= 4.0.0
- lxml >= 4.0.0

开发依赖：
- pytest >= 8.0.0
- pytest-cov >= 4.0.0

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

## 项目结构

```
scihub_download/
├── __init__.py          # 包初始化
├── __main__.py          # 模块入口
├── cli.py               # CLI 参数解析
├── downloader.py       # 下载核心逻辑
├── input_parser.py     # 输入文件解析
├── source_manager.py   # Sci-Hub 源管理
└── reporter.py          # 报告生成（预留）
```

## 许可证

MIT License

## 注意事项

1. 请确保遵守 Sci-Hub 的使用条款和相关法律法规
2. 下载的论文仅供个人学习研究使用
3. 部分论文可能因版权问题无法下载
4. 请合理设置并发数，避免对 Sci-Hub 服务器造成过大压力