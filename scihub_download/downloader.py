import os
import re
import argparse
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

import requests
import fitz
import pandas as pd
from tqdm import tqdm

# ------------------- 配置 -------------------
DEFAULT_SCI_HUB_SOURCES = [
    "https://sci-hub.se",
    "https://sci-hub.ru",
    "https://sci-hub.red",
    "https://sci-hub.ee",
    "https://sci-hub.vg",
    "https://sci-hub.shop",
]

REQUESTS_SESSION = requests.Session()
REQUESTS_SESSION.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
})

# ------------------- 日志 -------------------
def setup_logging(log_file: str):
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, mode='w', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )

# ------------------- 工具函数 -------------------
def clean_filename(pmid: str) -> str:
    """用 PMID 创建合法文件名"""
    return re.sub(r'[\\/*?:"<>|]', '_', pmid) + ".pdf"

def is_pdf_valid(filepath: str) -> bool:
    """检查 PDF 是否有效"""
    if not os.path.exists(filepath):
        return False
    try:
        doc = fitz.open(filepath)
        valid = doc.page_count > 0
        doc.close()
        return valid
    except Exception:
        return False

def download_file(url: str, filepath: str) -> bool:
    """下载 PDF 文件"""
    try:
        with REQUESTS_SESSION.get(url, stream=True, timeout=120) as resp:
            resp.raise_for_status()
            total_size = int(resp.headers.get('content-length', 0))
            if total_size > 0 and total_size < 5 * 1024:  # 小于5KB的文件忽略
                logging.warning(f"文件 {url} 太小，跳过")
                return False
            with open(filepath, "wb") as f:
                for chunk in resp.iter_content(chunk_size=8192):
                    f.write(chunk)
        return True
    except requests.exceptions.RequestException as e:
        logging.warning(f"下载失败 {url}: {e}")
        return False

# ------------------- 下载 Worker -------------------
def download_worker(row, save_dir: str, sources: List[str]) -> bool:
    """下载单个 DOI 对应的 PDF"""
    doi = row['DOI']
    pmid = row['PMID']
    filename = clean_filename(pmid)
    filepath = os.path.join(save_dir, filename)

    for base_url in sources:
        try:
            url_to_fetch = f"{base_url.rstrip('/')}/{doi}"
            resp = REQUESTS_SESSION.get(url_to_fetch, timeout=90)
            resp.raise_for_status()

            match = re.search(r'(?:iframe|embed).*?src="([^"]+\.pdf)', resp.text)
            if not match:
                continue

            pdf_url = match.group(1)
            if pdf_url.startswith("//"):
                pdf_url = "https:" + pdf_url
            elif not pdf_url.startswith("http"):
                pdf_url = f"{base_url.rstrip('/')}/{pdf_url.lstrip('/')}"

            if download_file(pdf_url, filepath):
                if is_pdf_valid(filepath):
                    return True
                else:
                    os.remove(filepath)
        except Exception:
            continue
    return False

# ------------------- 主函数 -------------------
def main():
    parser = argparse.ArgumentParser(description="CSV DOI Sci-Hub 下载器（增强版）")
    parser.add_argument("csv_file", help="包含 PMID 和 DOI 的 CSV 文件")
    parser.add_argument("save_dir", help="PDF 保存目录")
    parser.add_argument("--failed_csv", default=None, help="下载失败记录 CSV 文件路径（可指定目录和名称）")
    parser.add_argument("-w", "--workers", type=int, default=5, help="并行线程数")
    parser.add_argument("-s", "--sources", nargs='+', default=DEFAULT_SCI_HUB_SOURCES, help="Sci-Hub 源列表")
    parser.add_argument("--delete-corrupted", action='store_true', help="删除损坏文件后重下载")
    parser.add_argument("-l", "--log_file", default="download_log.txt", help="日志文件")
    args = parser.parse_args()

    setup_logging(args.log_file)
    os.makedirs(args.save_dir, exist_ok=True)

    # --- 读取 CSV ---
    try:
        df = pd.read_csv(args.csv_file, dtype=str)
    except FileNotFoundError:
        logging.error(f"CSV 文件不存在: {args.csv_file}")
        return
    
    df.columns = df.columns.str.upper()

    if 'PMID' not in df.columns or 'DOI' not in df.columns:
        logging.error("CSV 文件必须包含 'PMID' 和 'DOI' 列")
        return

    # --- 清理 DOI 空值 & 去重 DOI ---
    df = df[df['DOI'].notna() & df['DOI'].str.strip().ne('')]
    df = df.drop_duplicates(subset='DOI')
    if df.empty:
        logging.info("没有可下载的 DOI")
        return

    # --- 预检查已存在文件 ---
    df_to_download = []
    for _, row in df.iterrows():
        filepath = os.path.join(args.save_dir, clean_filename(row['PMID']))
        if os.path.exists(filepath):
            if not is_pdf_valid(filepath):
                logging.warning(f"[CORRUPTED] {row['PMID']}")
                if args.delete_corrupted:
                    os.remove(filepath)
                    df_to_download.append(row)
                else:
                    logging.info(f"[SKIP] {row['PMID']}，损坏文件未删除")
            else:
                logging.info(f"[EXISTS] {row['PMID']}")
        else:
            df_to_download.append(row)

    if not df_to_download:
        logging.info("所有文件已存在且有效，无需下载")
        return

    # --- 并行下载 ---
    failed_records = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(download_worker, row, args.save_dir, args.sources): row for row in df_to_download}
        for future in tqdm(as_completed(futures), total=len(futures), desc="下载 PDF", ncols=100):
            row = futures[future]
            try:
                success = future.result()
                if success:
                    logging.info(f"[SUCCESS] {row['PMID']}")
                else:
                    logging.warning(f"[FAILED] {row['PMID']}")
                    failed_records.append({'PMID': row['PMID'], 'DOI': row['DOI']})
            except Exception as e:
                logging.error(f"[CRITICAL] {row['PMID']} 下载异常: {e}")
                failed_records.append({'PMID': row['PMID'], 'DOI': row['DOI']})

    # --- 保存失败记录 ---
    if failed_records:
        failed_df = pd.DataFrame(failed_records)
        failed_csv_path = args.failed_csv or os.path.join(args.save_dir, "failed_records.csv")
        os.makedirs(os.path.dirname(failed_csv_path), exist_ok=True)
        failed_df.to_csv(failed_csv_path, index=False)
        logging.info(f"未成功下载 {len(failed_records)} 条记录，已保存到 {failed_csv_path}")

if __name__ == "__main__":
    main()
