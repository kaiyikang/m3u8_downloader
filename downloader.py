# public packages
import m3u8
import requests
import os
import shutil
import time
import threading
import random
import sys
from tqdm import tqdm
from natsort import natsorted
from Crypto.Cipher import AES
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

# private packages
from config import *
# requests.adapters.DEFAULT_RETRIES = 5

# local header information
# headers = {
#     'Origin': 'https://www.shiguangkey.com',
#     'Referer': 'https://www.shiguangkey.com/video/2321?videoId=40168&classId=4179&playback=1',
#     'Sec-Fetch-Mode': 'cors',
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'
# }

def random_headers():
    
    headers = [{'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36'},
               {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36"}
               ]
    return random.choice(headers)
    

def random_proxies():
    proxy = ['51.158.165.18:8761',
             '47.242.255.170:7071',
             '62.210.203.211:8080']
    proxy = random.choice(proxy)
    proxies = {
        "http": "http://%(proxy)s/" % {'proxy': proxy},
       
    }
    #  "https": "http://%(proxy)s/" % {'proxy': proxy}
    return proxies


class Downloader():
    
    def __init__(self, opt=None):
        if not opt: raise Exception('No configurations!')
        
        self.url = opt['url']
        self.num_threads = int(opt['num_threads'])
        self.is_proxy = opt['is_proxy']
        
        self.url_parser(opt['url'])
        self.init_env()
        self.get_meta_info() # 关键步骤，获得解码器
        self.multi_files()
        
        self.get_error_count = 5
        
    def url_parser(self,url):
        """读取url中的源码，并进行解析与基本文件和目录的初始化

        Args:
            url (str): from jable.tv website
        """
        # 获得 html 的内容
        data = self.get_url_content(url)
        soup = BeautifulSoup(data, 'html.parser')
        
        # 获取 影片名称（临时文件夹名称）
        self.ts_name = soup.title.text.split('- ')[0].strip()
        print('- ID   : ',soup.title.text.split()[0])
        print('- Title: ',self.ts_name)
        
        # 获取 m3u8 地址
        self.m3u8_url = ""
        for link in soup.find_all('link')[::-1]:
            if "m3u8" in link['href']:
                self.m3u8_url = link['href']
                break

        
    def run(self):
        """ 主入口：开启多线程
        """
        # 标记开始时间
        time_start=time.time()
        print('- 开始下载 ...')
          
        thread_list = []
        for i in range(self.num_threads):
            t = threading.Thread(target=self.single_run, args=(i,))
            thread_list.append(t)
        
        for t in thread_list:
            t.setDaemon(True)
            t.start()

        for t in thread_list:
            t.join()
            
        # 打印总时间，别忘记加空行，空行数等于 num_threads
        print('- 下载结束！总共用时: ',time.time()-time_start,'s')    
        
        # 合并文件        
        self.merge_ts()
        
        # 删除临时文件夹
        self.reset_env()
        
        # 退出程序
        sys.exit()


    def single_run(self,i):
        """每个线程内的主函数

        Args:
            i (int): 第几号线程
        """
        # test = 0
        total = len(self.mul_video_files[i])
        # time.sleep(i)
        
        # # 初始化未完成 list
        not_done_lst = set() 
        
        pbar = tqdm(total=total, position=i)
        for file_name in self.mul_video_files[i]:
            single_ts_url = self.pure_url + '/' + file_name
            # self.video_saver(single_ts_url)
            # pbar.update(1)
            # 如果下载失败，存入未完成list
            if not self.video_saver(single_ts_url):
                not_done_lst.add(single_ts_url)
            else: # 成功
                pbar.update(1)
            
            # test += 1
            # if test == 10: break 

        # 循环统一处理未完成的内容  

        while not_done_lst:
            for single_ts_url in not_done_lst.copy():
                if self.video_saver(single_ts_url):
                   not_done_lst.remove(single_ts_url) 
            
        pbar.clear()   
        pbar.close()


    
    def multi_files(self):
        """视频块list，根据线程的数量进行分组
        """
        # 获得视频块的个数
        length = len(self.video_files)
        
        # 获取步长
        step = int(length / self.num_threads) + 1
        
        # 储存为 list(list) 形式
        self.mul_video_files = []
        for i in range(0, length, step):
            self.mul_video_files.append(self.video_files[i: i + step])

            
    def init_env(self):
        """初始化环境: 根据影片名称创建临时文件夹，用于存储临时影片文件
        """
        # 获取脚本根目录
        folder_path = os.path.abspath('.')
        
        # 获取保存的目录：根目录/影片名称
        self.temp_path = os.path.join(folder_path, self.ts_name)
        
        # 如果发现同名路径，删除旧路径
        if os.path.exists(self.temp_path):
            print('>> 发现同名路径 {}，删除并创建新的'.format(self.temp_path))
            shutil.rmtree(self.temp_path)
        time.sleep(1)
        
        # 创建新路径
        os.makedirs(self.temp_path)
        
    def merge_ts(self):
        """读取所有视频块，合并并输出最终成品
        """
        # 合并完的文件路径
        self.ts_file = os.path.join('.',self.ts_name + '.ts')
        ts_files=[self.temp_path+'\{}.ts'.format(str(ij)) for ij in natsorted([int(str_1[:str_1.find('.')]) for str_1 in os.listdir(self.temp_path)])]
        
        print("- 准备合并文件")
        pbar = tqdm(total=len(ts_files))
        for ts_files in ts_files:
            pbar.update(1)
            with open(file=ts_files,mode='rb') as f:
                content=f.read()
            with open(file=self.ts_file ,mode='ab') as fp:
                fp.write(content)
    
    def reset_env(self):
        if os.path.exists(self.temp_path):
            print('- 完成合并，删除 {} 文件夹'.format(self.temp_path))
            shutil.rmtree(self.temp_path)
            

    def get_meta_info(self):
        """
        获得 meta 数据，decoder 器
        """
        # 载入 m3u8，并通过解析器
        self.meta_info = m3u8.load(self.m3u8_url)
        
        # 获得视频小块路径（list），idx = 0 位置是 key.ts #TODO: 可能会变化
        self.video_files = self.meta_info.files[1:]
        
        # 获取 m3u8 纯路径
        self.pure_url = "/".join(i for i in self.m3u8_url.split('/')[:-1])
        
        # 获得 meta key 值，以用作之后解析
        for key in self.meta_info.keys:
            key_uri = None 
            if key:  # First one could be None
                key_uri = key.uri
                key_method = key.method
                key_iv = key.iv
                break
        
        if key_uri:
            # 获取 key url
            key_url = self.pure_url + '/' + key_uri
            key = self.get_url_content(key_url)
            
            # 获取 key iv
            key_iv = self.hexStringTobytes(key_iv)
            
            print("- Key_url: ",key_url)
            print("- Key: ",key)
            print("- Key_iv: ",key_iv)

            # 通过 key 信息获得解码器
            self.decoder = AES.new(key, AES.MODE_CBC, iv=key_iv)
        else:
            self.decoder = None
        
        
    def get_decoder_(self, data, key, iv):
        """
        加密破解。该函数功能整合进了 get_meta_info() 函数，以下信息仅供参考和搜索学习。
        :param data:直接请求加密视频链接获取的数据流
        :param key: 获取到的key，注意必须是bytes格式且长度是16，24，32，等
        :param iv:偏移量也是bytes格式
        :return:
        """
        pass
        
        
    def video_saver(self, video_url):
        """根据给定的视频连接，下载视频

        Args:
            video_url (string): 视频块的连接
        Return:
            bool: 成功 or 失败
        """
        # 获取视频名字
        file_name = video_url.split('/')[-1]
        
        # 获得数据
        data = self.get_url_content(video_url)
        
        # 如果数据获取失败，返回 False
        if data == False: return False
        
        # 根据解码器，解析数据
        if self.decoder:
            data = self.decoder.decrypt(data)
        
        # 存储数据
        with open(os.path.join(self.temp_path, file_name),'wb')as f:
            f.write(data)
            
        return True
    
    def get_url_content(self,url):
        """通过给定链接，获得 url 中的原始内容

        Args:
            url (string): 链接

        Returns:
            内容: 经过加密/未加密的内容，这里为加密的内容
        """
        # 是否开启代理
        if self.is_proxy: proxies = random_proxies()
        else: proxies = None 
        
        # 发送 get 请求，获得响应
        while True:
            try:
                response = requests.get(url, headers=random_headers(), proxies=proxies)
                break
            except requests.exceptions.ConnectionError:
                print('ConnectionError -- please wait 3 seconds')
                time.sleep(3)
            except requests.exceptions.ChunkedEncodingError:
                print('ChunkedEncodingError -- please wait 3 seconds')
                time.sleep(3)    
            except:
                print('Unfortunitely -- An Unknow Error Happened, Please wait 3 seconds')
                time.sleep(3)

        # 提取响应的信息
        data = response.content

        # 如果错误发生，则循环持续requests #TODO 不同网站，错误情况不一样，这里需要分情况讨论
        while len(data) == 552 and self.get_error_count != 0:
            response = requests.get(url, headers=random_headers(), proxies=proxies, timeout=60)
            data = response.content
            time.sleep(1)
            self.get_error_count -= 1

        # 如果最终还是错误发生，返回 False
        if len(data) == 552: return False
              
        return data
        
    def hexStringTobytes(self,key_iv):
        """
        :param key_iv: 就是要传入的 iv
        
        :return: 返回的是16位的bytes
        """
        # 需要把前面的0X去掉
        if key_iv[:2] == '0x': key_iv = key_iv[2:]
        # convert
        key_iv = key_iv.replace(" ", "")
        return bytes.fromhex(key_iv)


def test():
    opt = {'url':'https://jable.tv/videos/ipx-176/',
           'num_threads':4,
           'is_proxy':False}
    dl = Downloader(opt)
    dl.run()

if __name__ == "__main__":
    test()
