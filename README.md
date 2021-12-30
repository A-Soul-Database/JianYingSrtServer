# JianYingSrtServer
部署剪映到 Win Server 上

## Support version : =>2.4.0 tested


1.安装必要依赖
```bash
pip install -r requirements.txt -i https://pypi.douban.com/simple/
```
2.修改 `config.json` 和 `components/ui.py` 中的文件  

## 远程调用运行

运行 `flask run` 或 `py app.py`

## 单独运行(不通过Web调用,仅本地)
配置好`components/ui.py` 中的`CONFIG`后运行 `components/ui.py`

## 调用方法
`GET` `/addItem?token=(optional)&bv=BV号&p=分P数目(1,2,3)` 执行任务    
`GET` `/download?name=BV号.srt` 下载生成的字幕    
`GET` `/` 查看服务器日志   
`GET` `/ping` 查看服务器运行状态    
`GET` `/forceKill` 强制清除缓存并重启剪映客户端(这并不会清除剪映缓存和srt文件,仅用于清理下载的视频和转换的音频)
`GET` `/all` 列出已经解析的字幕文件   

## Mind Map
![Whiteboard.png](https://i.loli.net/2021/11/13/JFBts3m6cOlZIqN.png)

## 保持winserver rdp connection
```bat
tscon %sessionname% /dest:console 
```
在远程计算机中创建为`.bat` 文件执行即可

# License
GPL-V3.0
# Libirary
[Jianying-to-srt](https://github.com/YDX-2147483647/Jianying-to-srt) MIT License  
[UiAutomation](https://github.com/yinkaisheng/Python-UIAutomation-for-Windows)  Apache-2.0 License 
