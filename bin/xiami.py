# -*- coding: utf-8 -*-
import os
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
import re
import urllib2
import urllib
from BeautifulSoup import BeautifulSoup
from mutagen.mp3 import MP3
import mutagen.id3
from mutagen.easyid3 import EasyID3
                             
class XiamiDownload(object):
                             
    """虾米音乐下载"""
                             
    def __init__(self, url_song):
                             
        """ 初始化，得到请求xml和加密的下载地址 """
                             
        self.url_song = url_song       
        self.url_xml = self.__get_xml()
        self.info = self. __get_info()
        self.url_location = self.info[0]
        self.lyc = self.info[1]
        self.pic = self.info[2]
        self.songName = self.info[3]
        self.albumName = self.info[4]
        self.artist = self.info[5]
                                 
    def __get_xml(self):
                             
        """ 得到请求的 xml 地址 """
                             
        return 'http://www.xiami.com/song/playlist/id/%s/object_name/default/object_id/0' % re.search('\d+', self.url_song).group()
                             
    def __get_info(self):
                             
        """ 伪装浏览器请求，处理xml，得到加密的 location """
                             
        headers = {
            'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'
        }
        req = urllib2.Request(
            url = self.url_xml,
            headers = headers
        )
        try:
            xml = urllib2.urlopen(req).read()
        except Exception, e:
            raise u'Request error. Please try again'
        try:
            location = re.search(r'(<location>)(.+)(<\/location>)', xml).group(2)
            #lyc = re.search(r'(<lyric>)(.+)(<\/lyric>)', xml).group(2) 
            pic = re.search(r'(<album_pic>)(.+)(<\/album_pic>)', xml).group(2) 
            songName = re.search(r'(<title>)<!\[CDATA\[(.*)\]\]>(<\/title>)', xml).group(2)
            album_name = re.search(r'(<album_name>)<!\[CDATA\[(.*)\]\]>(<\/album_name>)', xml).group(2)  
            artist = re.search(r'(<artist>)<!\[CDATA\[(.*)\]\]>(<\/artist>)', xml).group(2)
        except Exception ,e:
            raise u'The file is missing!'
        return (location,None, pic,songName,album_name,artist)
                             
    def get_url(self):
                             
        """ 解密 location 获得真正的下载地址 """
                             
        strlen = len(self.url_location[1:])
        rows = int(self.url_location[0])
        cols = strlen / rows
        right_rows = strlen % rows
        new_str = self.url_location[1:] 
        url_true = ''
                             
        for i in xrange(strlen):
            x = i % rows
            y = i / rows
            p = 0
            if x <= right_rows:
                p = x * (cols + 1) + y
            else:
                p = right_rows * (cols + 1) + (x - right_rows) * cols + y
            url_true += new_str[p]
        return urllib2.unquote(url_true).replace('^', '0')
    

########################################################################
class ParsePlayUrl(object):
    """得到一张专辑每首歌的URL"""
    #----------------------------------------------------------------------
    def __init__(self,album_url):
        """初始化程序"""
        self.album_url = album_url
        self.url_songList = self.get_playSongUrl()
       
    
    def get_playSongUrl(self):
        '''获取一张专辑每首歌的播放url'''
        '''添加给浏览器配置header'''
        headers = {
                    'User-Agent':'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'
                }
        req = urllib2.Request(
            url = self.album_url,
            headers = headers
        )
        try:
            html = urllib2.urlopen(req).read()
            page = html.decode('UTF-8')
            soup = BeautifulSoup(page)
            urlList= soup.findAll("td",attrs={"class":"song_name"})
            song_urlList=[]
            for eachUrl in urlList:
                #print(eachUrl)
                song_url = eachUrl.find('a').attrs[0]
                song_url = "http://www.xiami.com"+song_url[1]
                #print(song_url)
                song_urlList.append(song_url)
            #print(song_urlList) 
            return song_urlList
        except Exception, e:
            raise u'Request error. Please try again'
    
if __name__ == '__main__':
                             
    AlbumPageURL = raw_input('please enter the url of the AlbumPageURL: ')
    parseplayUrl = ParsePlayUrl(AlbumPageURL)
    songUrlList = parseplayUrl.url_songList
    flagJPG = False
    flagPath = False    
    for url in songUrlList:
        xi = XiamiDownload(url)
        url_download = xi.get_url()
        url_pic = xi.pic
        url_lyc = xi.lyc
        url_songName = xi.songName
        url_albumName = xi.albumName.decode("UTF-8")
        url_artist = xi.artist.decode("UTF-8")
        Currentpath = os.getcwd()
        local = os.path.join(Currentpath,url_albumName)        
        if(flagPath == False):
            filepath = os.mkdir(local) 
            flagPath = True
        #print u'DownLoading URL: %s' % url_download
        try:
            if(flagJPG == False):
		print u'album picture loading...'
                urllib.urlretrieve(url_pic,local + os.sep + url_albumName + '.jpg')
                flagJPG = True
            #print u"Album:"+url_albumName+" Song Name:"+url_songName+" DownLoading Starting..."
            urllib.urlretrieve(url_download,local + os.sep + url_songName + '.mp3')
	    print url_songName + " loading..."

	    audiofile = MP3(local + os.sep + url_songName + '.mp3',ID3 = EasyID3)
            audiofile['title'] = url_songName
            audiofile['album'] = url_albumName
            audiofile['artist'] = url_artist

	    print('%-13s\t%s' % ('Field','Value'))
	    print('-' * 70)
            for k,v in audiofile.items():
		print('%-13s\t%s' % (k , v and v[0]))
	    print
            audiofile.save()

            #urllib.urlretrieve(url_lyc, url_songName+'.lyc')
        except:
            #print(u'Request error. Please try again')
            pass 
                                     
    print u'The Task is Done!'
 
