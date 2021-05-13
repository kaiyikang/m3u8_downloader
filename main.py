from downloader import Downloader
from config import BasicParam  

# test data
# m3u8_url = 'https://qfindg.cdnlab.live/hls/T55YcJQUYYJyAherdoVu2w/1616251687/14000/14383/14383.m3u8'
# "https://jable.tv/videos/heyzo-2476/"
# TEMP_FOLDER = 'temp'

# init parameters class
arg = BasicParam()
# load para from consoles
opt = arg.return_param()
# init downloader
dl = Downloader(opt)
# run it
dl.run()
