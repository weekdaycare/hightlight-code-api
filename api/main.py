# -*- coding:utf-8 -*-

import requests
import uvicorn
import re
from fastapi import FastAPI, Response
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

@app.get("/api/v1/generate", response_class=Response)
def vOneGenerate(response: Response, code: str = "", url: str = "", lang: str = "", withcss: bool = True):
    filename = 'InputCode'
    if url:
        filename = url.split('/')[-1]
        code = requests.get(url).text
        code = code.replace('\\', '\\\\')  # 进行转义

    try:
        if lang:
            lexer = get_lexer_by_name(lang, stripall=True)
        else:
            lexer = get_lexer_for_filename(filename, code, stripall=True)
    except ClassNotFound:
        lexer = get_lexer_by_name("text", stripall=True)  # 如果无法识别语言，则默认使用纯文本

    formatter = HtmlFormatter(linenos=True)
    result = highlight(code, lexer, formatter)
    pattern = re.compile(r'<td class="linenos">.*?</td>', re.DOTALL) # 删除行号
    result = pattern.sub('', result)
    result = result.replace('<div class="highlight">', '<div class="highlight ' + lexer.name.lower() + '"><figcaption><span>' + filename + '</span></figcaption>')
    result = result.replace('\n', '<br>')[:-4]
    output = 'document.write(\''+ result + '\') '
    if withcss:
        output += '''\ndocument.write('<link rel="stylesheet" href="https://jsd.hzchu.top/gh/thun888/asstes@master/files/pygments-css/default.css">')'''
    
    return output

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", reload=True)
