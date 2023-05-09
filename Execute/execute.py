import subprocess as subproc
pwd=os.dirname(__file__)
def execute(codePth,inPth,outPth,timeout=3):
  p1=subproc.Popen(f"gcc {inPth} -o {pwd}/a", shell=True,
              stdin=subprocess.PIPE,
              stdout=subprocess.PIPE,
              stderr=subprocess.PIPE
    )
  p1.run