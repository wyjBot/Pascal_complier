import os,os.path as pth
import sys
import subprocess as subproc,subprocess
pwd=pth.dirname(pth.abspath(__file__))
cwd=pth.dirname(pwd)
sys.path.append(cwd)
from cfg import *
def execute(codePth,inPth,outPth=None,binPth=None,timeout=3):
  name=pth.basename(codePth).split('.')[0]
  if not binPth: binPth=pth.join(pwd,f"{name}.run")
  cmd1=f"{gccPth} {codePth} -o {binPth}" # print(cmd1)
  p1=subproc.Popen(cmd1, shell=True,
              stdin=subprocess.PIPE,
              stdout=subprocess.PIPE,
              stderr=subprocess.PIPE
    )
  binErr=(p1.stdout.read()+b'\n'+p1.stderr.read()).decode()
  p1=subproc.Popen(cmd1, shell=True,
              stdin=subprocess.PIPE,
              stdout=subprocess.PIPE,
              stderr=subprocess.PIPE
    )

if __name__=="__main__":
  execute("Data/example.c","./Data/example.in","Data/example.out")
