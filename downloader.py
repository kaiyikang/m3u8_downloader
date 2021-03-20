# public packages
import m3u8
import requests
import os
import shutil
import time
import threading
from tqdm import tqdm
from Crypto.Cipher import AES

# private packages
from config import headers

m3u8_url = 'https://qfindg.cdnlab.live/hls/bJMVBuk9PyBQSU8JJwl3vw/1616248980/14000/14356/14356.m3u8'

class Downloader():
    
    def __init__(self, m3u8_url, num_threads = 4):
        self.m3u8_url = m3u8_url
        self.num_threads = num_threads
        self.prepare_env()
        self.get_meta_info()
        self.multi_files(num_threads)
        
    def run(self):
        """ 多线程管理器
        """
        for i in range(self.num_threads):
            t = threading.Thread(target=self.single_run, args=(i,))
            t.start()

        
        
    def single_run(self,i):
        """每个线程内的主函数

        Args:
            i (int): 第几号线程
        """
        test = 0
        total = len(self.mul_video_files[i])

        pbar = tqdm(total=total, position=i)
        for file_name in self.mul_video_files[i]:
            single_ts_url = self.pure_url + '/' + file_name
            self.video_saver_(single_ts_url)
            pbar.update(1)
            test += 1
            # if test == 10: break
        # print(i,' threads done')
    
    
    def multi_files(self, num_threads):
        length = len(self.video_files)
        step = int(length / num_threads) + 1
        self.mul_video_files = []
        for i in range(0, length, step):
            self.mul_video_files.append(self.video_files[i: i + step])

            
    def prepare_env(self, folder_name = "temp"):
        folder_path = os.path.abspath('.')
        # 创建保存的根目录
        self.root_path = os.path.join(folder_path, folder_name)
        if os.path.exists(self.root_path):
            shutil.rmtree(self.root_path)
        time.sleep(1)
        os.makedirs(self.root_path)
        print('>> Create root path')
        

    def get_meta_info(self):
        """
        获得 meta数据
        """
        # load m3u8
        self.meta_info = m3u8.load(self.m3u8_url)
        # idx = 0 位置是 key.ts
        # TODO: 可能会变化
        self.video_files = self.meta_info.files[1:]
        # get pure url address
        self.pure_url = "/".join(i for i in self.m3u8_url.split('/')[:-1])
        # get meta key
        for key in self.meta_info.keys:
            if key:  # First one could be None
                key_uri = key.uri
                key_method = key.method
                key_iv = key.iv
                break
        # get key url
        key_url = self.pure_url + '/' + key_uri
        key = self.get_url_content(key_url)
        # get key iv
        key_iv = self.hexStringTobytes(key_iv)
        print(">> Key_url: ",key_url)
        print(">> key: ",key)
        print(">> key_iv: ",key_iv)

        # 通过 key 信息获得解码器
        self.decoder = AES.new(key, AES.MODE_CBC, iv=key_iv)
        
        
    def get_decoder_(self, data, key, iv):
        """
        加密破解
        :param data:直接请求加密视频链接获取的数据流
        :param key: 获取到的key，注意必须是bytes格式且长度是16，24，32，等
        :param iv:偏移量也是bytes格式
        :return:
        """
        pass
        
        
    def video_saver_(self, video_url):
        file_name = video_url.split('/')[-1]
        data = self.get_url_content(video_url)
        plain_data = self.decoder.decrypt(data) 
        with open(os.path.join(self.root_path, file_name),'wb')as f:
            f.write(plain_data)
            
    
    def get_url_content(self,url):        
        response = requests.get(url, headers=headers, timeout=5)
        data = response.content

        # 如果错误发生，则循环持续requests
        while len(data) == 552:
            response = requests.get(url, headers=headers,timeout=5)
            data = response.content
            time.sleep(5)
              
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


def main():
    dl = Downloader(m3u8_url,8)
    dl.run()

if __name__ == "__main__":
    main()
