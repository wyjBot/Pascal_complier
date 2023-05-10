import os,os.path as pth
import sys
import subprocess as subproc,subprocess
pwd=pth.dirname(pth.abspath(__file__))
cwd=pth.dirname(pwd)
sys.path.append(cwd)
from cfg import *
def execute(codePth,inPth,outPth=None,binPth=None,timeout=3):
  name=pth.basename(codePth).split('.')[0]
  if not binPth: 
    # No suffix required, compatible with Windows and Linux
    binPth=pth.join(pth.dirname(codePth),pth.basename(codePth).split('.')[0])
  gccPth="gcc"
  cmd1=f"{gccPth} {codePth} -o {binPth}" # print(cmd1)
  p1=subproc.Popen(cmd1, shell=True,
              stdin=subprocess.PIPE,
              stdout=subprocess.PIPE,
              stderr=subprocess.PIPE
    )
  p1.wait()
  binErr=(p1.stdout.read()+b'\n'+p1.stderr.read()).decode().strip()
  if binErr:
    print('- 中间代码->机器码 错误',binErr)
    return False,binErr
  else: print('+ 机器码生成',binPth)
  p2=subproc.Popen(binPth, shell=True,
              stdin=subprocess.PIPE,
              stdout=subprocess.PIPE,
              stderr=subprocess.PIPE
    )
  outStr=p2.communicate(open(inPth).read().encode())
  return True, (outStr[0]+outStr[1]).decode().strip()
    

if __name__=="__main__":
  ret=execute(cwd+"/Data/example.c",cwd+"/Data/example.in",cwd+"/Data/example.out")
  print(ret)
