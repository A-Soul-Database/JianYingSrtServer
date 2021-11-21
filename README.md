# JianYingSrtServer
部署剪映到 Win Server 上

## Support version : =>2.4.0 tested

## 使用方法
1.安装必要依赖
```bash
pip install -r requirements.txt -i https://pypi.douban.com/simple/
```
安装ffmpeg  
2.修改 `Server/config.json` 和 `Server/components/config.json` 中的文件  
3.参照 `Server/componnets/position` 中的截图自行修改  
4.运行 `flask run` 或 `py app.py`

## 调用方法
`GET` `~/addItem?token=(optional)&bv=BV号&p=分P数目(1,2,3)` 执行任务  
`GET` `~/download?name=BV号.srt` 下载生成的字幕  
`GET` `~/` 查看服务器日志 
`GET` `~/ping` 查看服务器运行状态  

## Mind Map
![Whiteboard.png](https://i.loli.net/2021/11/13/JFBts3m6cOlZIqN.png)

## 保持winserver rdp connection
```bat
tscon %sessionname% /dest:console 
```
在远程计算机中创建

# License
GPL-V3.0
# Libirary
[Jianying-to-srt](https://github.com/YDX-2147483647/Jianying-to-srt) MIT License
