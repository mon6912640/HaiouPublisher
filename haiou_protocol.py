import json


class VoProtocol:
    # 系统分类的唯一主键id
    sys_id = 0
    # 系统分类描述
    sys_name = ''
    # 协议号
    cmd = 0
    # 协议类型 1：CG前端到后端 2：GC后端到前端
    type = 0
    # 协议描述
    title = ''
    # 协议字段注释
    des = ''
    # 协议内容 例如：U-B
    read_types = ''
    # 详细描述
    fields = ''
    # 类名
    class_name = ''

    def create_interface(self):
        info = ''
        info += self.make_descript(self.title + '  ' + self.des)
        info += 'interface ICMD' + str(self.cmd) + ' {\n'
        if self.fields:
            self.fields = self.fields.replace('\'', '\"')
            try:
                cmd_desc = json.loads(self.fields)
            except:
                print('error')
                print(self.cmd)
                print('<' + self.fields + '>')
            else:
                if cmd_desc is not None and 'fields' in cmd_desc:
                    obj = cmd_desc['fields']
                    for item in obj:
                        field_type = item['fieldType']
                        note_name = item['noteName']
                        field_name = item['fieldName']
                        if field_type == 'I' or field_type == 'L' or field_type == 'B' or field_type == 'S':
                            info += self.get_nbsp(1) + self.make_descript(note_name) + self.get_nbsp(
                                1) + field_name + ':number;\n'
                        elif field_type == 'U':
                            info += self.get_nbsp(1) + self.make_descript(note_name) + self.get_nbsp(
                                1) + field_name + ':string;\n'
                        else:  # 数组格式不做映射
                            info += self.get_nbsp(1) + self.make_descript(note_name) + self.get_nbsp(
                                1) + field_name + ':any[];\n'
                    pass
                else:
                    print('fuck')
                    print(self.fields)
        info += '}\n'
        return info

    def get_fields(self):
        """
        I-B-I-I-I-I-[L-U-I-I-I-I-B-L-I]-[I]
        转换成
        ["I","B","I","I","I","I",["L","U","I","I","I","I","B","L","I"],["I"]]
        :return:
        """
        ret = ''
        need_flag = False
        if self.read_types != '':
            k = 0
            arr = list(self.read_types)
            # print(arr)
            for i in range(len(arr)):
                next_str = None
                # print(i)
                if (i + 1) < len(arr):
                    next_str = arr[i + 1]
                if arr[i] == '-':
                    continue
                if k != 0 and need_flag:
                    ret += ','
                    need_flag = False
                if arr[i] == '[' or arr[i] == ']':
                    ret += arr[i]
                    if arr[i] == ']' and (i + 1 < len(arr)) and next_str != ']':
                        need_flag = True
                else:
                    ret += '\"' + arr[i] + '\"'
                    if next_str != ']':
                        need_flag = True
                k += 1
        ret = '[' + ret + ']'
        # print(self.read_types)
        # print(ret)
        return ret

    def get_protocol_variable(self):
        """
        变量词典 返回JSON格式
        :return:
        """
        ret = ''
        if self.fields != '':
            self.fields = self.fields.replace('\'', '\"')
            cmd_desc = json.loads(self.fields)
            cmd_desc = cmd_desc['fields']
            k = 0
            for item in cmd_desc:
                if k != 0:
                    ret += ','
                ret += '\"' + item['fieldName'] + '\"'
                k += 1
        return '[' + ret + ']'

    def make_descript(self, des):
        return '/**' + des + '*/ \n'

    def get_nbsp(self, count):
        ret = ''
        for i in range(count):
            ret += '\t'
        return ret
