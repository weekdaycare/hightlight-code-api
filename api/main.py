# -*- coding:utf-8 -*-
from re import findall

import requests
import uvicorn
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer_for_filename
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
    if url != "":
        filename = url.split('/')[-1]
        code = requests.get(url).text
        # 进行转义
        code = code.replace('\\', '\\\\')
        if lang == "":  # 如果没有指定语言，则尝试根据文件名推断
            try:
                lexer = guess_lexer_for_filename(filename, code)
            except ValueError:
                lexer = get_lexer_by_name("text")  # 如果无法推断语言，则默认使用纯文本
        else:
            lexer = get_lexer_by_name(lang)
    else:
        if lang == "":
            lang = "python"  # 默认语言为 Python
        lexer = get_lexer_by_name(lang)
    
    formatter = HtmlFormatter(linenos=True)
    result = highlight(code, lexer, formatter)
    result = result.replace('<div class="highlight">', '<div class="highlight ' + lexer.name + '"><figcaption><span>' + filename + '</span></figcaption>')
    result = result.replace('class="linenos"', 'class="linenos" style="padding: 0 1em;"')
    result = result.replace('\n', '<br>')[:-4]
    output = 'document.write(\''+ result + '\') '
    if withcss:
        output = output + '''\ndocument.write('<link rel="stylesheet" href="https://jsd.hzchu.top/gh/thun888/asstes@master/files/pygments-css/default.css">')'''
    return output

if __name__ == "__main__":
        uvicorn.run("main:app", host="0.0.0.0", reload=True)
