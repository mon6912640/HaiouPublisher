import subprocess
import time
from functools import partial

from pywebio import start_server
from pywebio.output import *
from pywebio.session import hold, set_env


def log(content, scope=None):
    scope = 'content'
    # put_scrollable(put_markdown(content, scope=scope))
    put_markdown(content, scope=scope)


def print_now():
    return '>{0}'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))


def run_cmd(cmd, err_str):
    try:
        out_bytes = subprocess.check_output(cmd, shell=True,
                                            stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        out_bytes = e.output
        code = e.returncode
        out_text = out_bytes.decode('utf-8')
        log('>>`{0}`'.format(err_str))
        log('>><font color="#ff0000">{0}</font>'.format(out_text))
    else:
        out_text = out_bytes.decode('utf-8')
        log('>>{0}'.format(out_text))


def build(btn_val):
    scope = 'content'
    put_markdown(print_now(), scope=scope)
    put_markdown(">>开始编译...请耐心等待...", scope=scope)
    run_cmd('egret clean I:/newQz/client/yxqz -sourcemap', '编译错误')


def update(btn_val):
    scope = 'content'
    # scroll_to(scope, position=Position.BOTTOM)
    put_markdown(print_now(), scope=scope)
    put_markdown(">>开始更新...请耐心等待...", scope=scope)
    run_cmd('svn up I:/newQz/client/yxqz', '更新错误')


async def main():
    set_env(title="前端版本服工具")

    put_table([
        ['新枪战', ''],
        ['更新资源和代码', put_buttons(['更新'], onclick=partial(update))],
        ['编译代码', put_buttons(['编译'], onclick=partial(build))],
        ['打包配置', put_buttons(['打包'], onclick=...)],
        [put_link('版本服地址（新枪战）', url='http://192.168.61.64:5555/index.html', new_window=True), '']
    ])

    put_markdown('## 日志信息')
    with use_scope('content'):
        pass

    # 这句是保持网页连接状态，否则按钮点击的回调不能正常显示
    await hold()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    start_server(main, debug=True, port=5000)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
