import argparse
import json
import locale
import shutil
import socket
import subprocess
import time
from functools import partial
from pathlib import Path
from typing import List

import requests
import xlrd
from pywebio import start_server
from pywebio.output import *
from pywebio.session import hold, set_env, info, local

import bytes_util
from bytes_util import *
from haiou_protocol import VoProtocol

title = '前端版本工具'


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


class VoProject:
    project_name = ''
    root_work = ''
    url_proto = ''
    cfg_source = ''
    port = 0
    # 老项目标识
    old = 0
    urls = []

    def __init__(self):
        self.urls = []


project_list: List[VoProject] = []


class VoKey:
    col_index = 0
    key_type = ''
    name = ''
    des = ''

    def parse_value(self, cell):
        if self.key_type == 'INT' or self.key_type == 'LONG':
            if cell.ctype == 2:  # number
                if cell.value % 1 == 0.0:
                    value = int(cell.value)
                else:
                    value = cell.value
            else:
                value = int(cell.value)
        elif self.key_type == 'JSON' or self.key_type == 'INT[][]':
            value = json.loads(str(cell.value))
        else:  # STRING
            if cell.ctype == 2:  # number
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


ext_type_map = {
    '.png': 'image',
    '.jpg': 'image',
    '.jpeg': 'image',
    '.gif': 'image',

    '.mp3': 'sound',
    '.wav': 'sound',

    '.json': 'json',

    '.txt': 'text',

    '.xml': 'xml',
}


def get_type(p_suffix):
    if p_suffix in ext_type_map:
        return ext_type_map[p_suffix]
    else:
        return 'bin'


async def main():
    def get_user_ip():
        return info.user_ip

    def log(p_content, scope=None):
        msg_box.append(put_markdown(p_content))

    def error(p_content):
        log('<font color="#ff0000">{0}</font>'.format(p_content))

    def print_now():
        return '>{0}'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))

    def run_cmd(cmd, err_str, showlog=True):
        """
        运行外部命令行
        :param cmd:
        :param err_str:错误提示
        :return:返回非零则执行错误
        """
        try:
            # 如果 capture_output 设为 true，stdout 和 stderr 将会被捕获。在使用时，内置的 Popen 对象将自动用 stdout=PIPE 和 stderr=PIPE 创建。stdout 和 stderr 参数不应当与 capture_output 同时提供。如果你希望捕获并将两个流合并在一起，使用 stdout=PIPE 和 stderr=STDOUT 来代替 capture_output。
            out_bytes = subprocess.run(cmd, text=False, check=True, shell=True, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT).stdout
        except subprocess.CalledProcessError as e:
            out_bytes = e.output
            code = e.returncode
            try:
                # svn命令，含有中文路径的话，不能使用utf-8解码
                out_text = out_bytes.decode('utf-8')
            except:
                out_encoding = locale.getdefaultlocale()[1]
                out_text = out_bytes.decode(out_encoding)
            finally:
                if showlog:
                    log('>>`{0}`'.format(err_str))
                    log('>><font color="#ff0000">{0}</font>'.format(out_text))
            return 1
        else:
            try:
                # svn命令，含有中文路径的话，不能使用utf-8解码
                out_text = out_bytes.decode('utf-8')
            except:
                out_encoding = locale.getdefaultlocale()[1]
                out_text = out_bytes.decode(out_encoding)
            finally:
                if showlog:
                    log('>>{0}'.format(out_text))
            return 0

    def build(btn_val=None):
        log(print_now())
        log(">>开始编译...请耐心等待...")
        run_cmd('egret clean {0} -sourcemap'.format(local.cur_project.root_work), '编译错误')

    def clean(btn_val=None):
        """
        清理（更新前执行的清理资源的操作，避免冲突）
        :param btn_val:
        :return:
        """
        root_url = local.cur_project.root_work
        plist = [
            Path(root_url, 'src/protocol/IProtocol.ts'),
            Path(root_url, 'src/config'),
            Path(root_url, 'resource/config'),
            Path(root_url, 'resource/ani.json'),
            Path(root_url, 'resource/default.res.json'),
        ]
        for v in plist:
            if not v.exists():
                continue
            if v.is_dir():
                # 删除目录
                shutil.rmtree(str(v), True)
            else:
                # 删除文件
                v.unlink()
            pass
        pass

    def update_res(btn_val=None):
        """
        更新资源
        :param btn_val:
        :return:
        """
        log(print_now())
        log(">>开始更新...请耐心等待...")
        run_cmd('svn up --accept p {0}'.format(local.cur_project.root_work + 'resource'), '更新错误')
        log('>>...更新完毕')
        pass

    def update_code(btn_val=None):
        """
        更新代码
        :param btn_val:
        :return:
        """
        log(print_now())
        log(">>开始更新...请耐心等待...")
        run_cmd('svn up --accept p {0}'.format(local.cur_project.root_work + 'src'), '更新错误')
        log('>>...更新完毕')
        pass

    def update(btn_val=None):
        log(print_now())
        log(">>开始更新...请耐心等待...")
        clean()
        run_cmd('svn up --accept p {0}'.format(local.cur_project.root_work), '更新错误')
        log('>>...更新完毕')

    def protocol(btn_val=None):
        cur_project: VoProject = local.cur_project
        if cur_project.old:
            error('老项目不需要导出协议')
            return
        log(print_now())
        log(">>导出协议...请耐心等待...")
        try:
            response = requests.get(cur_project.url_proto + '/protocol.do?method=proExtExport', timeout=2)
        except:
            error('请求超时，请检查协议地址是否正确')
            return
        try:
            response.raise_for_status()
        except:
            error('请求错误，请检查协议地址是否正确')
            return
        # print(response)
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
        root_url = cur_project.root_work
        bin_path = Path(root_url, 'resource/config/clientProtocol.bin')
        with bin_path.open('wb') as fs:
            fs.write(bin_by)

        code_path = Path(root_url, 'src/protocol/IProtocol.ts')
        with code_path.open('wt', encoding='utf-8') as fs:
            fs.write(info)

        log('>>...协议生成完毕')

    def update_bone(btn_val=None):
        cur_project: VoProject = local.cur_project
        if cur_project.old:
            error('老项目不需要更新骨骼资源')
            return
        log(print_now())
        log(">>开始更新骨骼资源...请耐心等待...")
        # modify_default(['boneAnimation', 'UI'], True)
        modify_default(['boneAnimation'], True)
        log(">>...骨骼资源更新并打包完毕")

    def modify_default(paths, showlog=False):
        """
        修改default文件
        :param paths:相对resource目录的路径列表
        :return:
        """
        root_url = local.cur_project.root_work
        path_default = Path(root_url, 'resource/default.res.json')
        path_res = Path(root_url, 'resource')
        path_list = []
        for v in paths:
            pv = Path(path_res, v)
            if pv.exists():
                path_list.append(pv)
                run_cmd('svn up --accept p {0}'.format(str(pv)), '更新错误', showlog=showlog)
        if len(path_list) < 1:
            return
        if not path_default.exists():
            if showlog:
                error('default.res.json不存在')
            return
        # # 先删除default文件，避免冲突
        # path_default.unlink()
        # # svn恢复default文件，避免冲突
        # run_cmd('svn revert {0}'.format(str(path_default)), '恢复错误', showlog=showlog)

        str_json = path_default.read_text(encoding='utf-8')
        obj_default = json.loads(str_json)

        del_flag = False  # default删除标识
        new_list = []
        for v in obj_default['resources']:
            path_obj = path_res / v['url']
            if path_obj.exists():
                new_list.append(v)
        if len(obj_default['resources']) != len(new_list):
            obj_default['resources'] = new_list
            del_flag = True

        obj_map = {}
        key_obj_map = {}
        for v in new_list:
            url = v['url']
            if url not in obj_map:
                obj_map[url] = v
                key_obj_map[v['name']] = v

        add_flag = False  # default新增标识
        list_file = []
        for v in path_list:
            list_file += sorted(v.rglob('*.*'))
        for v in list_file:
            # 计算相对路径
            url = v.relative_to(path_res).as_posix()
            if url in obj_map:
                pass
            else:
                # parent_dir = v.parent.relative_to(path_res)
                if v.parent.name == 'UI':  # fgui的资源需要做特殊处理
                    name = v.name.split('.')[0]
                else:
                    name = v.name.replace('.', '_')
                t_type = get_type(v.suffix)
                obj = {'url': url, 'type': t_type, 'name': name}
                obj_default['resources'].append(obj)
                obj_map[url] = obj
                if name in key_obj_map:
                    if showlog:
                        error('...[warning]出现重复资源命名 {0}'.format(name))
                else:
                    key_obj_map[name] = obj
                add_flag = True

        if add_flag or del_flag:
            if del_flag:
                # 资源组中删除无用的key
                groups = obj_default['groups']
                for v in groups:
                    keys = v['keys'].split(',')
                    new_keys = []
                    for k in keys:
                        if k in key_obj_map:
                            new_keys.append(k)
                    if len(keys) != len(new_keys):
                        v['keys'] = ','.join(new_keys)
            str_result = json.dumps(obj_default, indent=4, ensure_ascii=False)
            str_result = str_result.replace('    ', '\t')  # 把四个空格转换成\t
            path_default.write_text(str_result)

    def pack_cfg(btn_val=None):
        log(print_now())
        source_path = Path(local.cur_project.cfg_source)
        if btn_val:
            log(">>更新配置...请耐心等待...")
            runcode = run_cmd('svn up --accept p {0}'.format(str(source_path)), '更新错误')
            if runcode != 0:
                return
        log(">>开始打包配置...请耐心等待...")
        list_file = sorted(source_path.rglob('*.xlsx'))
        vo_cfg_map = {}
        obj_map = {}
        ts1_str = ''
        ts2_str = ''
        temp_ts2_str1 = ''
        temp_ts2_str2 = ''
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
            temp_ts1_str = ''
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
                # ts文件1
                temp_ts1_str += '\n/**' + key_vo.des + '*/' + key_vo.name + ';'
                # count += 1
            if len(vo.key_list) < 1:
                # 不导出没有键的表
                del obj_map[cfg_name]
                continue
            ts1_str += '\ninterface I' + cfg_name + ' {' + temp_ts1_str + '\n}'

            temp_ts2_str1 += '\t/**{0} */private static _{1}: Record<string, I{2}>;\n'.format(v.name.split('.')[0],
                                                                                              cfg_name, cfg_name)
            temp_ts2_str2 += '\tstatic get ' + cfg_name + '(){\n' \
                             + '\t\tvar self = this;\n' \
                             + '\t\tif(!self._' + cfg_name + '){\n' \
                             + '\t\t\tself._' + cfg_name + ' = self.t(\'' + cfg_name + '\') as Record<string, I' + cfg_name + '>;\n' \
                             + '\t\t}\n' \
                             + '\t\treturn self._' + cfg_name + ';\n' \
                             + '\t}\n\n'

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
                    except BaseException as err:
                        error('{0} 表格数值类型解析错误，请检查 {1}行{2}列\n'.format(v.name, i + 1, kv.col_index + 1))
                        value_list.append(sheet.cell(i, kv.col_index).value)
                    else:
                        value_list.append(value)
                obj['data'].append(value_list)
            # break

        # print(obj_map)
        root_url = local.cur_project.root_work
        json_str = json.dumps(obj_map, ensure_ascii=False, separators=(',', ':'))
        json_path = Path(root_url, 'resource/config/config0.json')
        json_path.write_text(json_str, encoding='utf-8')

        ts1_path = Path(root_url, 'src/config/IConfig.ts')
        ts1_path.write_text(ts1_str, encoding='utf-8')

        temp_ts2_str3 = '\tstatic dataLib;\n' \
                        + '\tstatic t = ConfigHelp.decodeConfig;\n' \
                        + '\tstatic init(lib) {\n' \
                        + '\t\tthis.dataLib = lib;\n' \
                        + '\t}\n\n'
        ts2_str = 'class Config {\n' \
                  + temp_ts2_str1 \
                  + temp_ts2_str3 \
                  + temp_ts2_str2 \
                  + '}'
        ts2_path = Path(root_url, 'src/config/Config.ts')
        ts2_path.write_text(ts2_str, encoding='utf-8')
        log('>>...配置打包完毕')

    def pack_ani(btn_val=None):
        log(print_now())
        log(">>开始打包动画配置...请耐心等待...")
        root_url = local.cur_project.root_work
        model_path = Path(root_url, 'resource/model/')
        list_file = sorted(model_path.rglob('*.json'))
        ani_obj = {}
        for v in list_file:
            json_str = v.read_text()
            url = str(v.absolute())
            if 'hurt' in url or 'ice' in url or 'fire' in url or 'poison' in url or 'thunder' in url:
                ii = 0
                res_obj = json.loads(json_str)
                if 'res' in res_obj:
                    for key in res_obj['res']:
                        ii += 1
                        if ii > 4:
                            error('发现异常动画文件，联系水爷：[{0}]'.format(url))
                            return
            key_name = v.name.split('.')[0]
            ani_obj[key_name] = json.loads(json_str)
        ani_json = json.dumps(ani_obj, ensure_ascii=False, separators=(',', ':'))
        ani_path = Path(root_url, 'resource/ani.json')
        ani_path.write_text(ani_json)
        log('>>...动画配置打包完毕')

    def on_tab_click(btn_val):
        vo = project_list[btn_val]
        local.cur_project = vo
        set_env(title='{0}({1})'.format(title, vo.project_name))
        name_com.reset(put_markdown('## {0}'.format(vo.project_name)))

        links = []
        if vo.urls and len(vo.urls) > 0:
            for v in vo.urls:
                links.append(put_link(v[0], url=v[1], new_window=True))
        urls_com.reset(put_column(links))

        for i in range(len(tabs)):
            v = tabs[i]
            vo = project_list[i]
            if i == btn_val:
                v.reset(
                    put_buttons([dict(label=vo.project_name, value=i, color='danger')], onclick=partial(on_tab_click)))
            else:
                v.reset(
                    put_buttons([dict(label=vo.project_name, value=i, color='success')], onclick=partial(on_tab_click)))
        return vo

    def one_key(btn_val=None):
        cur_project: VoProject = local.cur_project
        if cur_project.old:  # 老项目
            # 老项目不用更新骨骼和导出协议
            update()
            pack_ani()
            pack_cfg(True)
            build()
            pass
        else:  # 新项目
            update()
            update_bone()
            pack_ani()
            protocol()
            pack_cfg(True)
            build()
            pass
        log('>><font color="#0000ff">...一键发布完成</font>')
        popup('通知', '{0} 一键发布完成'.format(cur_project.project_name), size=PopupSize.SMALL)

    name_com = output()
    urls_com = output()

    right = put_table([
        [name_com, put_buttons([dict(label='一键发布', value=0, color='warning')], onclick=partial(one_key))],
        ['更新骨骼', put_buttons(['更新'], onclick=partial(update_bone))],
        ['更新资源和代码', put_buttons(['清理并更新工作目录', '更新资源（不清理）', '更新代码（不清理）'],
                                onclick=[partial(update), partial(update_res), partial(update_code)])],
        ['打包动画', put_buttons(['打包动画'], onclick=partial(pack_ani))],
        ['导出协议', put_buttons(['协议'], onclick=partial(protocol))],
        ['打包配置', put_buttons([('更新并打包', True), ('只打包配置', False)], onclick=partial(pack_cfg))],
        ['编译代码', put_buttons(['编译'], onclick=partial(build))],
        ['相关地址', urls_com],
    ])

    # 根据配置的项目列表显示tab按钮
    tabs = []
    str_size = ''
    for i in range(len(project_list)):
        v = project_list[i]
        tab = output(put_buttons([dict(label=v.project_name, value=i, color='success')], onclick=partial(on_tab_click)))
        tabs.append(tab)
        if i == 0:
            str_size += '50px'
        else:
            str_size += ' 50px'
    left = put_column(tabs, size=str_size)

    put_row([left, None, right], size='15% 10px 85%')

    put_markdown('## 日志信息')
    msg_box = output()
    with use_scope('content'):
        put_scrollable(msg_box, height=400, keep_bottom=True)
        pass

    on_tab_click(0)

    cur_project = local.cur_project

    # 这句是保持网页连接状态，否则按钮点击的回调不能正常显示
    await hold()


def init_project(args):
    ok_flag = True

    obj = args

    if type(args) == dict:
        pass
    else:
        obj = vars(args)

    vo = VoProject()

    while True:
        if obj['project']:
            vo.project_name = obj['project']
        else:
            ok_flag = False
            break

        if obj['root']:
            vo.root_work = obj['root']
            root_path = Path(vo.root_work)
            if not root_path.exists():
                print('[warning] {0} 项目根目录不存在'.format(vo.project_name))
                ok_flag = False
                break
        else:
            ok_flag = False
            break

        if obj['proto']:
            vo.url_proto = obj['proto']
        else:
            ok_flag = False
            break

        if obj['cfg']:
            vo.cfg_source = str(obj['cfg'])
        else:
            ok_flag = False
            break

        break

    if 'urls' in obj:
        vo.urls = obj['urls'];

    if 'old' in obj:
        vo.old = obj['old']

    if ok_flag:
        project_list.append(vo)

    return ok_flag


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='帮助信息')
    parser.add_argument('--cfgs', type=str, default=None, help='多项目配置')
    parser.add_argument('--project', type=str, default='默认项目名', help='项目名')
    parser.add_argument('--root', type=str, default=None, help='项目根目录')
    parser.add_argument('--proto', type=str, default=None, help='协议url地址')
    parser.add_argument('--cfg', type=str, default=None, help='策划配置表目录')
    parser.add_argument('--port', type=int, default=5000, help='访问端口')

    args = parser.parse_args()
    port = args.port

    if args.cfgs is not None:
        path_cfgs = Path(args.cfgs)
        if path_cfgs.exists():
            str_cfgs = path_cfgs.read_text(encoding='utf-8')
            obj_cfgs = json.loads(str_cfgs)
            title = obj_cfgs['title']
            for v in obj_cfgs['projects']:
                init_project(v)

    init_project(args)

    if len(project_list) > 0:
        for k, v in enumerate(project_list):
            print('===== 配置{0}参数 ====='.format(k + 1))
            print(v.project_name)
            print(v.root_work)
            print(v.url_proto)
            print(v.cfg_source)
            print('=====================\n')
        server_ip = get_host_ip()
        print('服务器启动成功...（关闭本窗口即关闭服务器）')
        print('访问地址：\nhttp://{0}:{1}'.format(server_ip, port))
        print('==================')
        start_server(main, debug=True, port=port)
    else:
        print('[error] 服务器启动失败，初始化配置失败，请检测配置格式或者数据')

# pywebio github at https://github.com/wang0618/PyWebIO
# pywebio docs at https://pywebio.readthedocs.io/zh_CN/latest/index.html
