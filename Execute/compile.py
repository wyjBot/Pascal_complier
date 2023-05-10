import os,os.path as pth
import sys
import subprocess as subproc,subprocess
pwd=pth.dirname(pth.abspath(__file__))
cwd=pth.dirname(pwd)
sys.path.append(cwd)
from Parser.Parser import Parser
from Generate.program import code_generate
import json as js


parser = Parser()

def compile(pasPth,cPth=None,astPth=None,genAstFil=True,showDebugInf=True):
  src = open(pasPth).read()
  if not cPth:
    cPth=pth.join(pth.dirname(pasPth),pth.basename(pasPth).split('.')[0]+'.c')
    if showDebugInf: print("set default cPth to",cPth)
  if genAstFil and not astPth:
    astPth=pth.join(pth.dirname(pasPth),pth.basename(pasPth).split('.')[0]+'.ast')
  errPth=pth.join(pth.dirname(pasPth),pth.basename(pasPth).split('.')[0]+'.err')
  ast,symb,warn,err = parser.run(src)
  if showDebugInf and (warn):
    print(warn)
  if showDebugInf and (err):
    print(err)
  result = code_generate(ast,symb)
  if genAstFil:
    with open(astPth,"w+") as fw:
      js.dump(astPth,fw,indent=2)
  if err:
    with open(errPth,"w+") as fw:
      js.dump(err,fw,indent=2)
    return False,err
    #err,abort
  else:
    with open(cPth,"w+") as fw:
      fw.write(result)
  #All information writed,Finally return
  return True,ast,result,warn

if __name__=="__main__":
  compile(r"Data\example.pas")