import os,json,time
from flask import config
import pyautogui as gui
import logging
import sys
import components.srtParser.draft_content as draft_content
import components.srtParser.simple_srt as simple_srt
import components.global_var as gl
sys.path.append('../')
class GetSrt():

    Config = {}
    videoList = []
    FinishedList = []

    def __init__(self):
        with open("components/config.json","r",encoding="utf-8")as f:
            self.Config = json.loads(f.read())
        #获取视频列表
        self.AbsPath = os.path.abspath(os.getcwd()+"/components/"+self.Config["videoDir"])
        videoFormat = ["mp4","flv"]
        self.videoList = [fn for fn in os.listdir(self.AbsPath)
         if any(fn.endswith(formats) for formats in videoFormat)
        ]
        self.confidence = self.Config["confidence"]
        self.theme = self.Config["theme"]
        self.parseSrt()

    def parseSrtPart(self,path)->bool:
        name = path.split(".")[0]
        print("start parsing srt for " + path)
        #1.导入素材
        try:
            x,y,width,height = gui.locateOnScreen("components/position/add.png",confidence=self.confidence)
            gui.click(x+width/2,y+height/2)
        except:
            logging.error("error in finding add button!")
            return False
            #选择媒体资源
            #路径框识别
        time.sleep(2)
        try:
            x,y,width,height = gui.locateOnScreen("components/position/PathBar_"+self.theme+".png",confidence=self.confidence)
            gui.click(x+width/2,y+height/2)
            gui.typewrite(self.AbsPath)
            time.sleep(3)
            #Windows11 好像有点不一样
            gui.press("enter")
                #文件名框选择
            x,y,width,height = gui.locateOnScreen("components/position/FileName_"+self.theme+".png",confidence=self.confidence)
            gui.click(x+width/2+50,y+height/2)
            gui.typewrite(path)
                #打开按钮
            x,y,width,height = gui.locateOnScreen(f"components/position/Open_{self.theme}.png",confidence=self.confidence)
            gui.click(x+width/2,y+height/2)
            time.sleep(2)
        except:
            logging.error(f"error in selecting files,please check system {self.theme} Dark/Light , filepath")
            return False
            #选择第一个媒体元素
        try:
            x,y,width,height = gui.locateOnScreen("components/position/add_small.png",confidence=self.confidence)
            gui.moveTo(x+(width/2)*3,y+height/2)
                #拖拽到空轨道
            x,y,width,height = gui.locateOnScreen("components/position/empty_Track.png",confidence=self.confidence)
            gui.dragTo(x+width/2,y+height/2,button="left",duration=0.4)
        except:
            logging.error("error in drag media into tracks")
            return False
        #2.字幕识别
            #文本按钮
        try:
            x,y,width,height = gui.locateOnScreen("components/position/text.png",confidence=self.confidence)
            gui.click(x+width/2,y+height/2)
                #智能字幕
            time.sleep(1)
            x,y,width,height = gui.locateOnScreen("components/position/AutoSrt.png",confidence=self.confidence)
            gui.click(x+width/2,y+height/2)
                #清空已有字幕
            time.sleep(0.5)
            x,y,width,height = gui.locateOnScreen("components/position/ClearSrts.png",confidence=self.confidence)
            gui.click(x+width/2,y+height/2)
                #开始识别
            x,y,width,height = gui.locateOnScreen("components/position/srt.png",confidence=self.confidence)
            gui.click(x+width/2,y+height*6/7)
        except:
            logging.error("error in start parsing srt")
            return False
        time.sleep(1)
        while True:
            #持续中
            try:
                with open(self.Config["draftContentPath"],"rb") as f:
                    f.close()
            except PermissionError:
                time.sleep(2)
                break


        #3.字幕提取
        self.SrtMain((self.Config["draftContentPath"],name))
            #点击“媒体”  
        
        
        time.sleep(3)
        x,y,width,height = gui.locateOnScreen("components/position/media.png",confidence=self.confidence)
        gui.click(x+width/2,y+height/2)
        #4.移除媒体文件
        time.sleep(1)
        x,y,width,height = gui.locateOnScreen("components/position/add_small.png",confidence=self.confidence)
        gui.click(x+(width/2)*3,y+height/2)
        time.sleep(1)
        gui.press("backspace")
        time.sleep(1)
        x,y,width,height = gui.locateOnScreen("components/position/confirm.png",confidence=self.confidence)
            
        gui.click(x+width/4,y+height*6/7)
        try:
            pass
        except:
            logging.error("error in removing media file")
            return False
        self.FinishedList.append(name)
        return True

    def parseSrt(self):
        for i in self.videoList:
            result = self.parseSrtPart(i)
            time.sleep(2)
            if result != True:
                logging.error(f"error in handeling video {i}")
                break
            else:
                print(f"{i} is done")
        status = gl.get("Status")
        AllStatus = gl.get("AllStatus")
        status["status"] = "done"
        AllStatus.append(status)
        gl.set("AllStatus",AllStatus)
        print(f"finished:  {self.FinishedList}")
        self.ClearTmp()

    def SrtMain(self,args):
        name = args[1]
        draft_content_directory = args[0]
        tracks = draft_content.read_draft_content_src(draft_content_directory)

        with open("components/tmp/"+name+".srt", 'w', encoding='utf-8') as f:
            f.write(simple_srt.tracks_to_srt_string(tracks))
            

    def ClearTmp(self):
        os.system('%s%s' % ("taskkill /F /IM ","JianYingPro.exe"))
        time.sleep(1)
        for i in self.videoList:
            print(self.AbsPath+'/'+i)
            os.remove(self.AbsPath+'/'+i)
        logging.info("clear tmp files")
        os.system(self.Config["jianyingPath"])
        time.sleep(5)
        x,y,width,height = gui.locateOnScreen("components/position/draftcontents.png",confidence=self.confidence)
        gui.click(x+width/2,y+height/2+100)

if __name__ == "__main__":
    from srtParser import draft_content as draft_content
    from srtParser import simple_srt as simple_srt
    GetSrt()
