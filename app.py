# 导入Flask类库
from flask import Flask,jsonify,request
import time,random
import os.path as pth,os
# 创建应用实例
app = Flask(__name__)
# 视图函数（路由）

@app.route("/v2/example")
def initData():
    return open("Data/example/wk.pas").read()

@app.route("/v2/compile",methods=['POST'])
def v2_compile():
  from Execute.compile import compile
  workId=str(time.time()*1000)+"a"+str(random.randint(10000,99999))
  workDir=pth.join('Data',workId)
  srcPth=pth.join(workDir,'work.pas')
  try:
    os.makedirs(workDir)
    fw=open(srcPth,'wb+')
    fw.write(request.data)
    fw.close()
  except Exception as e:
    os.remove(workDir)
    return '参数错误'
  try:
    ret=compile(srcPth)
    if ret[0]:
      data={
        'id':workId,
        'state':'suc',
        'ast':ret[1],
        'code':ret[2],
        'warning':ret[3],
        'error':[],
      }
    else:
      data={
        'id':workId,
        'state':'err',
        'error':ret[1],
        'warning':ret[2],
      }
    return jsonify(data)
  except Exception as e:
    return '编译c错误'+str(e)

@app.route("/v2/execute",methods=['POST'])
def v2_execute():
  try:
    import json as js
    data=js.loads(request.data)
  except Exception as e:
    return "参数错误"+str(e)
  workId=data['id']
  workDir=pth.join('Data',workId)
  inPth=pth.join(workDir,'work.in')
  codePth=pth.join(workDir,'work.c')
  try:
    fw=open(inPth,'w+')
    fw.write(data['input'])
    fw.close()
  except Exception as e:
    print(e)
    return "会话已超时,请重新compile"

  from Execute.execute import execute
  try:
    ret=execute(codePth,inPth)
    data={
      'id':workId,
      'output':ret[1],
    }
    return jsonify(data)
  except Exception as e:
    return '编译c错误'+str(e)
  

# 启动服务
if __name__ == '__main__':
   app.run(debug = True,threaded=True,host='0.0.0.0')