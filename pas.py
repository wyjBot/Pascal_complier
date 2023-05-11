from Execute import execute
import sys

if len(sys.argv)!=3:
  print("使用方法: python3 pas.py '源代码路径' '输入文件位置'")
  exit(0)
print(execute.fromSrc(sys.argv[1], sys.argv[2]))
