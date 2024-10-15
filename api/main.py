# -*- coding:utf-8 -*-

import requests
import uvicorn
import re
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, get_lexer_for_filename
from pygments.util import ClassNotFound

app = FastAPI(docs_url=None, redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_lines(code: str, lines_param: str):
    lines = code.splitlines()
    
    # 尝试解析行号，移除 'L' 并转换为整数
    try:
        line_numbers = [int(num[1:]) for num in lines_param.split('-')]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid line number format.")
    
    # 确保行号在有效范围内并支持反向范围
    line_numbers = sorted(min(num, len(lines)) for num in line_numbers)

    if len(line_numbers) == 1:
        return lines[line_numbers[0] - 1]
    elif len(line_numbers) == 2:
        return '\n'.join(lines[line_numbers[0] - 1:line_numbers[1]])
    else:
        raise HTTPException(status_code=400, detail="Invalid line number input.")

@app.get("/api/v1/generate")
def vOneGenerate(url: str, lang: str = "", withcss: bool = False, lines: str = Query(None)):
    filename = 'InputCode'
    if url:
        try:
            response = requests.get(url)
            response.raise_for_status()  # 确保请求成功
            code = response.text
            code = code.replace('\\', '\\\\')  # 进行转义
            filename = url.split('/')[-1]
        except requests.RequestException as e:
            # 如果请求失败，返回错误信息
            raise HTTPException(status_code=400, detail=str(e))

    if lines:
        try:
            code = extract_lines(code, lines)
        except HTTPException as e:
            return e

    try:
        if lang:
            lexer = get_lexer_by_name(lang, stripall=True)
        else:
            lexer = get_lexer_for_filename(filename, code, stripall=True)
    except ClassNotFound:
        lexer = get_lexer_by_name("text", stripall=True)  # 如果无法识别语言，则默认使用纯文本

    formatter = HtmlFormatter(linenos=True)
    result = highlight(code, lexer, formatter)
    result = result[:-2].replace('\n', '<br>')[:-4]  # 换行符的 HTML 表示，只去掉末尾的一个<br>
    pattern = re.compile(r'<td class="linenos">.*?</td>', re.DOTALL) # 去掉行号
    result = pattern.sub('', result)
    result = re.sub(r'(<td class="code">)(.*?)(</td>)', r'\1\2<div class="copy-btn">Copy</div>\3', result, flags=re.DOTALL) # 添加 copy 按钮
    result = result.replace('<div class="highlight">', '<div class="highlight ' + lexer.name.lower() + '"><figcaption><span>' + filename + '</span></figcaption>')

    # 包装结果为 JSON 格式
    return {
      "result": result
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", reload=True)
