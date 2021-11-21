import os,json,time
from flask import config
import pyautogui as gui
import logging
import sys
from threading import Timer
import components.srtParser.draft_content as draft_content
import components.srtParser.simple_srt as simple_srt
import components.global_var as gl
sys.path.append('../')
class GetSrt():

    Config = {}
    videoList = []
    audioList = []
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
        self.audioList = [fn for fn in os.listdir(self.AbsPath)
         if any(fn.endswith(formats) for formats in ['m4a'])
        ]
        self.confidence = self.Config["confidence"]
        self.theme = self.Config["theme"]

    def is_in_used(self,path):
        ret = False
        try:
            handle = open(path,"rb")
            ret = False
        except PermissionError:
            ret = True
        finally:
            handle.close()
        return ret

    def parseSrtPart(self,path)->bool:
        #解析单个字幕
        name = path.split(".")[0]
        print("start parsing srt for " + path)
        #1.导入素材
        try:
            x,y,width,height = gui.locateOnScreen("components/position/add.png",confidence=self.confidence)
            gui.click(x+width/2,y+height/2)
        except:
            #有可能是被ForeceKill,先尝试移除文件,之后清除缓存
            x,y,width,height = gui.locateOnScreen("components/position/add_small.png",confidence=self.confidence)
            gui.click(x+width,y+height*10)
            time.sleep(1*self.Config["delay_times"])
            gui.press("backspace")
            time.sleep(1*self.Config["delay_times"])
            x,y,width,height = gui.locateOnScreen("components/position/confirm.png",confidence=self.confidence)
            gui.click(x+width/4,y+height*6/7)
            logging.error("error in finding add button!")
            return False
            #选择媒体资源
            #路径框识别
        time.sleep(2*self.Config["delay_times"])
        try:
            x,y,width,height = gui.locateOnScreen("components/position/PathBar_"+self.theme+".png",confidence=self.confidence)
            gui.click(x+width/2,y+height/2)
            gui.typewrite(self.AbsPath)
            time.sleep(3*self.Config["delay_times"])
            #Windows11 好像有点不一样
            gui.press("enter")
                #文件名框选择
            x,y,width,height = gui.locateOnScreen("components/position/FileName_"+self.theme+".png",confidence=self.confidence)
            gui.click(x+width/2+50,y+height/2)
            gui.typewrite(path)
                #打开按钮
            x,y,width,height = gui.locateOnScreen(f"components/position/Open_{self.theme}.png",confidence=self.confidence)
            gui.click(x+width/2,y+height/2)
            time.sleep(2*self.Config["delay_times"])
        except:
            logging.error(f"error in selecting files,please check system {self.theme} Dark/Light , filepath")
            return False
            #选择第一个媒体元素
        try:
            x,y,width,height = gui.locateOnScreen("components/position/add_small.png",confidence=self.confidence)
            gui.moveTo(x+width,y+height*10)
                #拖拽到空轨道
            x,y,width,height = gui.locateOnScreen("components/position/empty_Track.png",confidence=self.confidence)
            self.empty_track_x = x+width/2
            self.empty_track_y = y+height/2
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
            time.sleep(1*self.Config["delay_times"])
            x,y,width,height = gui.locateOnScreen("components/position/AutoSrt.png",confidence=self.confidence)
            gui.click(x+width/2,y+height/2)
                #清空已有字幕
            time.sleep(0.5*self.Config["delay_times"])
            x,y,width,height = gui.locateOnScreen("components/position/ClearSrts.png",confidence=self.confidence)
            gui.click(x+width/2,y+height/2)
                #开始识别
            x,y,width,height = gui.locateOnScreen("components/position/srt.png",confidence=self.confidence)
            gui.click(x+width/2,y+height*6/7)
        except:
            logging.error("error in start parsing srt")
            return False
        time.sleep(1*self.Config["delay_times"])
        mtime = time.ctime(os.path.getmtime(self.Config["draftContentPath"]))
        self.Srt_Rolling(mtime)

        #3.字幕提取
        self.SrtMain((self.Config["draftContentPath"],name))
            #点击“媒体”  
        
        
        time.sleep(3*self.Config["delay_times"])
        x,y,width,height = gui.locateOnScreen("components/position/media.png",confidence=self.confidence)
        gui.click(x+width/2,y+height/2)
        #4.移除媒体文件
        time.sleep(1*self.Config["delay_times"])
        x,y,width,height = gui.locateOnScreen("components/position/add_small.png",confidence=self.confidence)
        gui.click(x+width,y+height*10)
        time.sleep(1*self.Config["delay_times"])
        gui.press("backspace")
        time.sleep(1*self.Config["delay_times"])
        x,y,width,height = gui.locateOnScreen("components/position/confirm.png",confidence=self.confidence)
        gui.click(x+width/4,y+height*6/7)

        #移除音频字幕
        gui.click(self.empty_track_x,self.empty_track_y)
        with gui.hold('ctrl'):
            gui.press('a')
        time.sleep(0.5*self.Config["delay_times"])
        gui.press('backspace')
        try:
            pass
        except:
            logging.error("error in removing media file")
            return False
        self.FinishedList.append(name)
        return True

    def parseSrt(self):
        #解析字幕(Main)
        self.to_m4a(self.videoList,self.AbsPath)
        self.audioList = [fn for fn in os.listdir(self.AbsPath)
         if any(fn.endswith(formats) for formats in ['m4a'])
        ]
        all = gl.get('Status')
        for i in self.audioList:
            result = self.parseSrtPart(i)
            time.sleep(2)
            if result != True:
                logging.error(f"error in handeling video {i}")
                all[gl.get('bv')]["status"] = "error"
                break
            else:
                all[gl.get('bv')]["status"] = "done"
                print(f"{i} is done")
        print(f"finished:  {self.FinishedList}")
        gl.set('Status',all)
        self.ClearTmp()

    def SrtMain(self,args):
        name = args[1]
        draft_content_directory = args[0]
        tracks = draft_content.read_draft_content_src(draft_content_directory)

        with open("components/tmp/"+name+".srt", 'w', encoding='utf-8') as f:
            f.write(simple_srt.tracks_to_srt_string(tracks))
            
    def Srt_Rolling(self,mtime)->bool:
        #通过检测上次修改时间来判断是否识别完成
        if time.ctime(os.path.getmtime(self.Config["draftContentPath"])) != mtime:
            return True
        else:
            time.sleep(1)
            self.Srt_Rolling(mtime)

    def to_m4a(self,filelist:list,path:str):
        #利用ffmpeg将视频转换为m4a音频文件
        for file in filelist:
            command =  f"ffmpeg -i {path}/{file} -vn -codec copy {path}/{file.split('.')[0]}.m4a -y"
            os.system(command)

    def ClearTmp(self):
        #清空临时文件
        os.system('%s%s' % ("taskkill /F /IM ","JianYingPro.exe"))
        time.sleep(1*self.Config["delay_times"])
        for i in self.videoList+self.audioList:
            os.remove(self.AbsPath+'/'+i)
        logging.info("clear tmp files")
        os.system(self.Config["jianyingPath"])
        time.sleep(5*self.Config["delay_times"])
        x,y,width,height = gui.locateOnScreen("components/position/draftcontents.png",confidence=self.confidence)
        gui.click(x+width/2,y+height/2+100)

if __name__ == "__main__":
    from srtParser import draft_content as draft_content
    from srtParser import simple_srt as simple_srt
    GetSrt()
