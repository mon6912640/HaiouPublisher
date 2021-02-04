import socket
from functools import partial

from pywebio import start_server
from pywebio.output import *
from pywebio.session import hold, set_env, run_js

project_name = '测试项目'
port = 5000


def get_host_ip():
    """
    查询本机ip地址
    :return: ip
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def log(content, scope=None):
    msg_box.append(put_markdown(content))
    run_js(
        '$("#pywebio-scope-content>div").stop().animate({ scrollTop: $("#pywebio-scope-content>div").prop("scrollHeight")}, 1000)')  # hack: to scroll bottom


def one_key(btn_val=None):
    log('>><font color="#0000ff">...一键发布完成</font>')
    print('脚本执行成功 >>>>>>>>>>>>>>>')
    pass


async def main():
    global msg_box

    set_env(title='前端版本服工具({0})'.format(project_name))

    put_markdown('## {0}'.format(project_name))

    put_table([
        [put_buttons(['一键发布'], onclick=partial(one_key)), ''],
    ])

    put_markdown('## 日志信息')
    msg_box = output()
    with use_scope('content'):
        style(put_scrollable(msg_box, max_height=400), 'height:400px')
        pass

    # 这句是保持网页连接状态，否则按钮点击的回调不能正常显示
    await hold()


if __name__ == '__main__':
    my_ip = get_host_ip()
    print('服务器启动成功...（关闭本窗口即关闭服务器）')
    print('访问地址：\nhttp://{0}:{1}'.format(my_ip, port))
    print('==================')
    start_server(main, debug=True, port=port)

# pywebio github at https://github.com/wang0618/PyWebIO
# pywebio docs at https://pywebio.readthedocs.io/zh_CN/latest/index.html
