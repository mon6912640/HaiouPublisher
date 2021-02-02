import subprocess
import time
from functools import partial
import xlrd
from typing import List
import json

import requests
from pywebio import start_server
from pywebio.output import *
from pywebio.session import hold, set_env, run_js

import bytes_util
from bytes_util import *
from haiou_protocol import VoProtocol
from pathlib import Path

root_work = 'I:/newQz/client/yxqz/'
url_proto = 'http://192.168.61.142:8080/ProtocolNewQZ/'
cfg_source = 'I:/newQz/策划/配置表/'


def log(content, scope=None):
    msg_box.append(put_markdown(content))
    run_js(
        '$("#pywebio-scope-content>div").stop().animate({ scrollTop: $("#pywebio-scope-content>div").prop("scrollHeight")}, 1000)')  # hack: to scroll bottom
    # pprint(content)


def error(content):
    log('<font color="#ff0000">{0}</font>'.format(content))


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
    run_cmd('egret clean {0} -sourcemap'.format(root_work), '编译错误')


def update(btn_val):
    log(print_now())
    log(">>开始更新...请耐心等待...")
    run_cmd('svn up {0}'.format(root_work), '更新错误')


def protocol(btn_val):
    log(print_now())
    log(">>导出协议...请耐心等待...")
    response = requests.get(url_proto + '/protocol.do?method=proExtExport')
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
    bin_path = Path(root_work, 'resource/config/clientProtocol.bin')
    with bin_path.open('wb') as fs:
        fs.write(bin_by)

    code_path = Path(root_work, 'src/protocol/IProtocol.ts')
    with code_path.open('wt', encoding='utf-8') as fs:
        fs.write(info)

    log('>>...协议生成完毕')


class VoKey:
    col_index = 0
    key_type = ''
    name = ''
    des = ''

    def parse_value(self, cell):
        if self.key_type == 'INT':
            if cell.ctype == 2:  # number
                if cell.value % 1 == 0.0:
                    value = int(cell.value)
                else:
                    value = cell.value
            else:
                value = 0
        else:
            if cell.ctype == 2:
                if cell.value % 1 == 0.0:
                    value = str(int(cell.value))
                else:
                    value = str(cell.value)
            else:
                value = str(cell.value)
        return value


class VoCfg:
    # 导出的配置名
    cfg_name = ''
    # 配置源文件名
    fname = ''
    key_list: List[VoKey] = None

    def __init__(self):
        self.key_list = []


def pack_cfg(btn_val):
    log(print_now())
    log(">>开始打包配置...请耐心等待...")
    source_path = Path(cfg_source)
    list_file = sorted(source_path.rglob('*.xlsx'))
    vo_cfg_map = {}
    obj_map = {}
    for v in list_file:
        file_url = v.absolute()
        if v.name.find('~$') > -1:  # 跳过临时打开的xlsx文件
            continue
        wb = xlrd.open_workbook(filename=file_url)
        sheet = wb.sheet_by_index(0)
        if sheet.cell_type(0, 0) != 1 or sheet.cell_value(0, 0).upper() == 'NO':
            continue
        if sheet.cell_type(0, 0) != 1:
            error('{0} 没有导出表名，不能导出'.format(v.name))
            continue
        row_client = sheet.row(0)
        row_key_name = sheet.row(2)
        row_key_des = sheet.row(3)
        cfg_name = row_key_name[0].value
        if cfg_name in vo_cfg_map:
            error('FBI warning，发现重复表，提交者：死肥仔；表名冲突者：[{0}]与[{1}]'.format(vo_cfg_map[cfg_name].fname, v.name))
            continue
        vo_cfg_map[cfg_name] = vo = VoCfg()
        obj_map[cfg_name] = obj = {'key': [], 'data': []}
        vo.cfg_name = cfg_name
        vo.fname = v.name
        # count = 0
        for i in range(1, len(row_client)):
            if row_client[i].ctype != 1:
                continue
            key_type = row_client[i].value.upper()
            if key_type == 'NO':
                continue
            key_vo = VoKey()
            key_vo.col_index = i
            key_vo.key_type = key_type
            key_vo.name = row_key_name[i].value
            key_vo.des = row_key_des[i].value
            vo.key_list.append(key_vo)
            obj['key'].append(key_vo.name)
            # count += 1

        for i in range(4, sheet.nrows):
            # 首列为0的行不导出
            cell0 = sheet.cell(i, 0)
            if cell0.ctype == 2:  # number
                if cell0.value % 1 == 0.0:
                    value0 = int(cell0.value)
                else:
                    value0 = cell0.value
            else:
                value0 = 0
            if value0 == 0:
                continue

            value_list = []
            for kv in vo.key_list:
                try:
                    value = kv.parse_value(sheet.cell(i, kv.col_index))
                except:
                    error('出错 {0} {1}行{2}列'.format(v.name, i, kv.col_index))
                else:
                    value_list.append(value)
            obj['data'].append(value_list)
        # break

    # print(obj_map)
    json_str = json.dumps(obj_map, ensure_ascii=False, separators=(',', ':'))
    json_path = Path(root_work, 'resource/config/config1.json')
    with json_path.open('w', encoding='utf-8') as fs:
        fs.write(json_str)
    log('>>...配置打包完毕')


async def main():
    global msg_box

    set_env(title="前端版本服工具")

    put_table([
        ['新枪战', ''],
        ['更新资源和代码', put_buttons(['更新'], onclick=partial(update))],
        ['导出协议', put_buttons(['协议'], onclick=partial(protocol))],
        ['编译代码', put_buttons(['编译'], onclick=partial(build))],
        ['打包配置', put_buttons(['打包'], onclick=partial(pack_cfg))],
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
