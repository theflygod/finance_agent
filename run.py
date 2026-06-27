"""启动入口：右键运行此文件即可启动服务"""
import os
import sys

# 确保项目根目录在 sys.path 中
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="localhost", port=8000, reload=False)