import os

def to_m4a(filelist:list,path:str):
    for file in filelist:
        command =  f"ffmpeg -i {path}/{file} -vn -codec copy {file.split('.')[-1]}.m4a"
        os.system(command)