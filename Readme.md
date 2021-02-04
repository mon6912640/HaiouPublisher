# HaiouPublisher
> 海鸥工作室版本发布工具（web）


## 使用方式1
> 直接运行目录内的bat入口文件，例如“start_qz2.bat”   
> 
>> 每个bat文件都是一个项目的入口，同时也是一个项目配置   
>> 多个项目入口时，注意端口需要设置不一样


## 使用方法2（命令行）
```cmd
python main.py --project xxx --root xxx --porto xxx --cfg xxx --port xxx
```

```yaml
参数说明：
--project   项目名称，会在页面中显示
--root      项目根目录
--proto     协议url地址
--cfg       策划配置表目录
--port      访问端口
```