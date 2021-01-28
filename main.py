import subprocess
import time
from functools import partial

import requests
from pywebio import start_server
from pywebio.output import *
from pywebio.session import hold, set_env, run_js

import bytes_util
from bytes_util import *
from haiou_protocol import VoProtocol
from pathlib import Path

root = 'I:/newQz/client/yxqz/'
url = 'http://192.168.61.142:8080/ProtocolNewQZ/'


def log(content, scope=None):
    msg_box.append(put_markdown(content))
    run_js(
        '$("#pywebio-scope-content>div").stop().animate({ scrollTop: $("#pywebio-scope-content>div").prop("scrollHeight")}, 1000)')  # hack: to scroll bottom
    # pprint(content)


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
    run_cmd('egret clean {0} -sourcemap'.format(root), '编译错误')


def update(btn_val):
    log(print_now())
    log(">>开始更新...请耐心等待...")
    run_cmd('svn up {0}'.format(root), '更新错误')


def test(btn_val):
    log(print_now())
    log(">>导出协议...请耐心等待...")
    response = requests.get(url + '/protocol.do?method=proExtExport')
    # 返回二进制流
    by = response.content
    # log('二进制长度=' + str(len(by)))
    proto_count = 0
    info = ''
    br = BytesReader(by)
    count = br.read_short()
    bin_by = bytes()
    for i in range(count):
        info += '\n'
        vo = VoProtocol()
        vo.sys_id = br.read_short()
        vo.sys_name = br.read_utf()
        vo.cmd = br.read_short()
        vo.type = br.read_byte()
        vo.title = br.read_utf()
        vo.des = br.read_utf()
        vo.read_types = br.read_utf()
        vo.fields = br.read_utf()
        vo.class_name = br.read_utf()

        if vo.type == 1:  # 过滤前端发到后端的
            continue

        proto_count += 1

        info += vo.create_interface()
        bin_by += bytes_util.write_int(vo.cmd)
        bin_by += bytes_util.write_utf(vo.get_fields())
        bin_by += bytes_util.write_utf(vo.get_protocol_variable())

    bin_by = bytes_util.write_int(proto_count) + bin_by
    bin_path = Path(root, 'resource/config/clientProtocol.bin')
    with bin_path.open('wb') as fs:
        fs.write(bin_by)

    code_path = Path(root, 'src/protocol/IProtocol0.ts')
    with code_path.open('wt', encoding='utf-8') as fs:
        fs.write(info)

    log('>>...协议生成完毕')
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
