from flask import Flask,send_file
from flask import request
from flask import render_template
import logging
import json
from threading import Thread
import components.video_Down as video_Down
import components.srt as srt
import components.srtParser.draft_content as draft_content
import components.srtParser.simple_srt as simple_srt
import sys
import components.global_var as gl
sys.path.append("..")
sys.path.append("./components")
config = json.loads(open("./config.json","r",encoding="utf-8").read())

Status = {}
bv = ""


gl.__init__()
gl.set("Status",Status)
gl.set("bv",bv)

app = Flask(__name__)

logging.basicConfig(filename='app.log', level=logging.INFO)

def getBvs(bv,p)->list:
    #格式化bv和p的文件名
    if p == "1":
        return [bv+".srt"]
    else:
        returning = []
        if type(p) == str:
            return [p]
        for i in p:
            returning.append(bv+"-"+i[0]+".srt")
        return returning

@app.route('/',methods = ['GET'])
def give_stastic():
    #访问主页会查看队列,即Status
    return render_template('index.html',status=str(Status)),200


@app.route('/addItem',methods=["GET"])
def addItem():
    #添加视频字幕
    if len(request.args) == 0:
        return 'error request' , 403
    logging.info('get /addItem',request.args)
    if request.args.get('token') == None:
        pass
    elif request.args.get('token') != config["token"]:
        return "token error", 403
    bv = request.args.get('bv')
    gl.set("bv",bv)
    if request.args.get('p') == None:
        p = "1"
    p = [request.args.get('p')] if request.args.get('p').isnumeric() else request.args.get('p').split(',')
    #更改分P使其符合规则
    Status[bv]={"bv":bv,"p":p,"status":"pending"}
    gl.set("Status",Status)
    t = Thread(target=video_Down.down,args=(bv,p))
    t.start()
    Status[bv]["status"] = "Working"
    gl.set("Status",Status)
    #后台处理文件
    link = ""
    for i in getBvs(bv,p):
        link += f"<a href='/download?name={i}'>{i}</a><br>"
    return f"Task Added to list </br> please Check </br> {link} </br> <b>later.</b>",200

@app.route('/download',methods=['GET'] )
def getSrt():
    logging.info('get /download',request.args)
    if request.args.get('name')==None:
        return "Name is None",403
    name = request.args.get('name')
    try:
        return send_file("components/tmp/"+name,as_attachment=True)
    except FileNotFoundError:
        return "File Not Found",404


@app.route('/ping',methods=['GET'])
def Alive():
    return "pong",200

@app.route('/forceKill',methods=['GET'])
def forceKill():
    t = Thread(target=srt.GetSrt().ClearTmp)
    t.start()
    return "Ok",200


if __name__ == "__main__":
    app.run(port=config["port"],debug=config["debug"])