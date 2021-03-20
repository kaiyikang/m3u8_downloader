# m3u8_downloader

## 测试环境
基于 Windows10 操作系统。
如果想运行在 Linux 平台，可能会出现路径相关的错误，毕竟两个系统的分割符号都不一样。

## 如何使用
### 1. 创建虚拟环境
在 terminal 中输入, 创建虚拟环境
~~~bash
python -m venv venv
~~~
然后根据 IDE 的情况，开启虚拟环境。然后你可以在 terminal 中看到：
~~~bash
(venv) D:\\aaa\\bbb\\ccc>
~~~
最后在 venv 中安装必须要的库：
~~~bash
pip install -r requirements.txt
~~~

### 2. 运行 main.py 程序
打开命令行，进入 venv，输入
~~~
python main.py --url [网址] --num_threads [数字]
~~~
即可开始下载。

## 版本说明
- 0.0 version
实现基本的多线程下载，ts 视频合并功能。