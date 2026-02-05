from http.server import BaseHTTPRequestHandler
import os
import sys

# 将项目根目录添加到 python path
# 当前文件在 api/index.py，通过两次 dirname 获取项目根目录
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

from web.router import get_router
from web.server import WebRequestHandler

# 初始化全局路由
# 注意：Vercel Function 是无状态的，但全局变量可以在热启动的实例中复用
router = get_router()

class handler(WebRequestHandler):
    """
    Vercel Serverless Function 入口类
    
    必须命名为 'handler' 并继承自 BaseHTTPRequestHandler
    """
    # 将路由实例注入到 handler 类中
    router = router
    
    def __init__(self, *args, **kwargs):
        # 显式调用父类初始化
        super().__init__(*args, **kwargs)
