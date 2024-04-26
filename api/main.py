# -*- coding:utf-8 -*-

import requests
import uvicorn
import re
from fastapi import FastAPI, HTTPException
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

@app.get("/api/v1/generate")
def vOneGenerate(code: str = "", url: str = "", lang: str = "", withcss: bool = ""):
    filename = 'InputCode'
    if url:
        try:
            response = requests.get(url)
            response.raise_for_status()  # 确保请求成功
            code = response.text
            code = code.replace('\\', '\\\\')  # 进行转义
            filename = url.split('/')[-1]
        except requests.RequestException as e:
            raise HTTPException(status_code=400, detail=str(e)) # 如果请求失败，返回错误信息

    try:
        if lang:
            lexer = get_lexer_by_name(lang, stripall=True)
        else:
            lexer = get_lexer_for_filename(filename, code, stripall=True)
    except ClassNotFound:
        lexer = get_lexer_by_name("text", stripall=True)  # 如果无法识别语言，则默认使用纯文本

    formatter = HtmlFormatter(linenos=True)
    result = highlight(code, lexer, formatter)
    result = result.replace('\n', '<br>')  # 保持换行符的 HTML 表示
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
