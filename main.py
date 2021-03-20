from downloader import Downloader
from config import *

m3u8_url = 'https://qfindg.cdnlab.live/hls/bJMVBuk9PyBQSU8JJwl3vw/1616248980/14000/14356/14356.m3u8'


dl = Downloader(m3u8_url,8)
dl.run()