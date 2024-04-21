# -*- coding:utf-8 -*-
from re import findall

import requests
import uvicorn
from fastapi import FastAPI,Response
from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name
app = FastAPI(docs_url=None, redoc_url=None)

origins = [
    "",
    "blog.hzchu.top",
    "hzchu.top",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/generate", response_class=Response)
def vOneGenerate(response: Response,code: str = "",url: str = "",lang: str = "python",withcss: bool = True):
    filename = 'InputCode'
    if url != "":
        filename = url.split('/')[-1]
        code = requests.get(url).text
        
    lexer = get_lexer_by_name(lang)
    # 使用HTML formatter进行格式化
    formatter = HtmlFormatter(linenos=True)
    # 进行高亮
    result = highlight(code, lexer, formatter)
    # 添加文件名字及语言类型
    result = result.replace('<div class="highlight">', '<div class="highlight ' + lang + '"><figcaption><span>' + filename + '</span></figcaption>')
    result = result.replace('class="linenos"', 'class="linenos" style="padding: 0 1em;"')
    # 压缩成一行
    # 只去掉末尾的一个<br>
    result = result.replace('\n', '<br>')[:-4] + '<div class="highlightcode-meta"><a href="'+url+'" style="float:right">view raw</a><a href="'+url+'">'+filename+'</a> transformed with ❤️ by <a href="https://hzchu.top">Hzchu.top</a></div>'
    output = 'document.write(\''+ result + '\') '
    if withcss:
        output = output + '''\ndocument.write('<link rel="stylesheet" href="https://jsd.hzchu.top/gh/thun888/asstes@master/files/pygments-css/default.css">')'''
    response.headers["Vercel-CDN-Cache-Control"] = "max-age=3600"
    return output

if __name__ == "__main__":
        uvicorn.run("main:app", host="0.0.0.0", reload=True)
