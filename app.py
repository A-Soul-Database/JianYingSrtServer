from flask import Flask,send_file,render_template,request
import json
import _thread
import components.video_Down as video_Down
import components.ui as ui
import components.srtParser.draft_content as draft_content
import components.srtParser.simple_srt as simple_srt
import sys
import os
import time
sys.path.append("..")
sys.path.append("./components")
config = json.loads(open("./config.json","r",encoding="utf-8").read())

app = Flask(__name__)
Progress_Info = {"Server_Status":0}
#logging.basicConfig(filename='app.log', level=logging.INFO)

def getBvs(bv,p:list)->list:
    #格式化bv和p的文件名
    if p == ["1"]:
        return [bv+".srt"]
    else:
        return [bv+"-"+i+".srt" for i in p]

@app.route('/',methods = ['GET'])
def give_stastic():
    #访问主页会查看队列,即Status
    return render_template('index.html'),200

@app.route('/api/v1/home',methods = ['GET'])
def give_home():
    srts = json.loads(getAllSrt()[0])
    if len(srts) == 0:
        return render_template("index.html",ParseStatus=f"No Srt </br> Queue is : </br> {Progress_Info}")

    for i in srts:
        bv = i.split(".")[0].split("-")[0]
        if bv not in Progress_Info.keys():
            Progress_Info[bv] = {"Status":"Done","Name":i}
        else:
            Progress_Info[bv]["Status"] = "Done"
    Progress_Info["Server_Status"] = ui.LocateStatusProxy()

    return json.dumps(Progress_Info,ensure_ascii=False),200

@app.route('/addItem',methods=["GET"])
def addItem():
    #添加视频字幕
    if len(request.args) == 0:
        return 'error request' , 403
    if request.args.get('token') == None:
        pass
    elif request.args.get('token') != config["token"]:
        return "token error", 403
    bv = request.args.get('bv')
    if request.args.get('p') == None:
        p = "1"
        _thread.start_new_thread(video_Down.down,(bv,p))
    else:
        p = request.args.get('p')
        _thread.start_new_thread(video_Down.down,(bv,p))
    p = [p] if p.isnumeric() else p.split(',')

    #如果P的请求是 1 则为 ["1"] , 若为 1,2 则为["1","2"] 返回值为list
    #更改分P使其符合规则
    #后台处理文件
    link = []
    for i in getBvs(bv,p):
        #link += f"<a href='/download?name={i}'>{i}</a><br>"
        link.append(i)
    #return f"Task Added to list </br> please Check </br> {link} </br> <b>later.</b>",200
    Progress_Info[bv] = {
        "P":p,
        "Status":"Progressing",
        "Time":time.time(),
        "Name":link
    }
    return json.dumps(link,ensure_ascii=False),200

@app.route('/download',methods=['GET'] )
def getSrt():
    """下载某一个字幕文件"""
    if request.args.get('name')==None:
        return "Name is None",403
    name = request.args.get('name')
    try:
        return send_file("components/tmp/"+name,as_attachment=True)
    except FileNotFoundError:
        return "File Not Found",404

@app.route('/all',methods=['GET'])
def getAllSrt():
    """获取所有已转换的字幕文件"""
    srtlists = [fn for fn in os.listdir("components/tmp") if fn.endswith(".srt")]
    return json.dumps(srtlists,ensure_ascii=False),200

@app.route('/forceKill',methods=['GET'])
def forceKill():
    """强制结束进程"""
    _thread.start_new_thread(ui.Restart_Client,())
    return "Ok",200


if __name__ == "__main__":
    app.run(port=config["port"],debug=config["debug"])