import subprocess
import time
from functools import partial
from pprint import pprint
import struct

import requests
from pywebio import start_server
from pywebio.output import *
from pywebio.session import hold, set_env, run_js


def log(content, scope=None):
    # msg_box.append(put_markdown(content))
    # run_js(
    #     '$("#pywebio-scope-content>div").animate({ scrollTop: $("#pywebio-scope-content>div").prop("scrollHeight")}, 1000)')  # hack: to scroll bottom
    pprint(content)


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
    log(print_now())
    log(">>开始编译...请耐心等待...")
    run_cmd('egret clean I:/newQz/client/yxqz -sourcemap', '编译错误')


def update(btn_val):
    log(print_now())
    log(">>开始更新...请耐心等待...")
    run_cmd('svn up I:/newQz/client/yxqz', '更新错误')


def test(btn_val):
    url = 'http://192.168.61.142:8080/ProtocolNewQZ/'
    response = requests.get(url + '/protocol.do?method=proExtExport')
    # 返回二进制流
    # pprint(response.content)
    by = response.content
    log('二进制长度=' + str(len(by)))
    cmd_len = 0
    info = ''
    offset = 0
    count = struct.unpack_from('>h', by, offset)[0]
    offset += 2
    for i in range(count):
        sys_id = struct.unpack_from('>h', by, offset)[0]
        offset += 2
        log(str(sys_id))

        utfl = struct.unpack_from('>H', by, offset)[0]
        tby = by[offset + 2:offset + 2 + utfl]
        sys_name = tby.decode('utf-8', errors='ignore')
        offset += 2 + utfl
        log(sys_name)

        t = struct.unpack_from('>hb', by, offset)
        log('协议号：' + str(t[0]))
        log('协议类型：' + str(t[1]))
        offset += 2 + 1

        utfl = struct.unpack_from('>H', by, offset)[0]
        tby = by[offset + 2:offset + 2 + utfl]
        title = tby.decode('utf-8', errors='ignore')
        offset += 2 + utfl
        log(title)

        utfl = struct.unpack_from('>H', by, offset)[0]
        tby = by[offset + 2:offset + 2 + utfl]
        desc = tby.decode('utf-8', errors='ignore')
        offset += 2 + utfl
        log(desc)

        utfl = struct.unpack_from('>H', by, offset)[0]
        tby = by[offset + 2:offset + 2 + utfl]
        read_types = tby.decode('utf-8', errors='ignore')
        offset += 2 + utfl
        log(read_types)

        utfl = struct.unpack_from('>H', by, offset)[0]
        tby = by[offset + 2:offset + 2 + utfl]
        fields = tby.decode('utf-8', errors='ignore')
        offset += 2 + utfl
        log(fields)

        utfl = struct.unpack_from('>H', by, offset)[0]
        tby = by[offset + 2:offset + 2 + utfl]
        fields = tby.decode('utf-8', errors='ignore')
        offset += 2 + utfl
        log(fields)
        # break

    log(str(count))

    # s1 = '你好啊\'我\''
    # s1 = s1.replace('\'', '\"')
    # log(s1)
    # o1 = {'key1': 1, 'key2': 2, 'key3': 3}
    # for key in o1:
    #     print(key, o1[key])
    pass


async def main():
    global msg_box

    set_env(title="前端版本服工具")

    put_table([
        ['新枪战', ''],
        ['更新资源和代码', put_buttons(['更新'], onclick=partial(update))],
        ['导出协议', put_buttons(['协议'], onclick=partial(test))],
        ['编译代码', put_buttons(['编译'], onclick=partial(build))],
        ['打包配置', put_buttons(['打包'], onclick=...)],
        [put_link('版本服地址（新枪战）', url='http://192.168.61.64:5555/index.html', new_window=True), '']
    ])

    put_markdown('## 日志信息')
    msg_box = output()
    with use_scope('content'):
        style(put_scrollable(msg_box, max_height=400), 'height:400px')
        pass

    # 这句是保持网页连接状态，否则按钮点击的回调不能正常显示
    await hold()


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    start_server(main, debug=True, port=5000)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
