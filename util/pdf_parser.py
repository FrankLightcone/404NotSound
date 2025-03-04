import fitz  # PyMuPDF

def pdf_to_markdown(pdf_path):
    # 打开 PDF 文件
    doc = fitz.open(pdf_path)
    md_lines = []

    # 遍历每一页
    for page in doc:
        # 用一级标题标记页面编号
        md_lines.append(f"# Page {page.number + 1}\n")
        # 提取整页文本（纯文本模式）
        page_text = page.get_text("text").strip()
        md_lines.append(page_text)
        # 用分隔线分隔不同页面
        md_lines.append("\n---\n")

    doc.close()
    return "\n".join(md_lines)
