import requests
import time
from multiprocessing import Pool, Manager, Lock
from bs4 import BeautifulSoup
import os
import threading
from selenium import webdriver
from  selenium.webdriver.firefox.options import Options
import sys
import csv
from itertools import product
from functools import partial

args = sys.argv

search_word = args[1].replace("_", " ")
end = 4000

manager = Manager()
Urls_list = manager.list()
Article_list = manager.list()
Comment_list = manager.list()
articleDict = manager.dict()
commentDict = manager.dict()

#UrlCnt = manager.Value('i', 1)

options = webdriver.ChromeOptions()
#options = Options()
#ff_dir = args[3]
#ff_profile = webdriver.FirefoxProfile(profile_directory=ff_dir)
prefs = {'profile.default_content_setting_values': {
    'images': 2, 'plugins': 2, 'popups': 2, 'geolocation': 2,
    'notifications': 2, 'auto_select_certificate': 2, 'fullscreen': 2,
    'mouselock': 2, 'mixed_script': 2, 'media_stream': 2, 'media_stream_mic': 2,
    'media_stream_camera': 2, 'protocol_handlers': 2, 'ppapi_broker': 2,
    'automatic_downloads': 2, 'midi_sysex': 2, 'push_messaging': 2,
    'ssl_cert_decisions': 2, 'metro_switch_to_desktop': 2,
    'protected_media_identifier': 2, 'app_banner': 2, 'site_engagement': 2,
    'durable_storage': 2}}
options.add_experimental_option('prefs', prefs)
options.add_argument("start-maximized")
options.add_argument("disable-infobars")
options.add_argument("--disable-extensions")
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
#options.headless = True
#driver = webdriver.Firefox(firefox_options=options)
#driver = webdriver.Chrome(args[3], chrome_options=options)
#driver = webdriver.Firefox(firefox_options=options)
#driver.implicitly_wait(3)

#writer1 = open(args[2] + args[1]+'_'+ 'E_article-long' +'.csv', 'a', encoding='euc-kr', newline='')
#writer2 = open(args[2] + args[1]+'_'+ 'E_comment' +'.csv', 'a', encoding='euc-kr', newline='')
#writer3 = open(args[2] + args[1]+'_'+ 'E_comment_cnt' +'.csv', 'a', encoding='euc-kr', newline='')

#wr1 = csv.writer(writer1)
#wr2 = csv.writer(writer2)
#wr3 = csv.writer(writer3)

#wr1.writerow(["id","press","date","title","article","web.addr","comment.cnt"])
#wr2.writerow(["urlId","comments.contents","comments.regTimeGmt","comments.sympathyCount","comments.antipathyCount"])
#wr3.writerow(["urlId","cnt"])

def getNewsUrls(start):
    global Urls_list
    # url making
    # url = 'https://search.naver.com/search.naver?where=news&sm=tab_jum&query={}&start={}'.format(search_word, start)
    url = 'https://search.naver.com/search.naver?where=news&sm=tab_jum&nso=so%3Ar%2Cp%3Afrom20180901to20191031%2Ca%3Aa&query={}&start={}'.format(
        search_word, start)
    req = requests.get(url)

    if req.ok:
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')
        
        titles = soup.select('ul.type01 > li > dl > dd > a' )

        for title in titles:
            Urls_list.append(title['href'])

def getNewsContents(UrlCnt,currentUrl):
    req = requests.get(currentUrl)
    isItAEntertain = 0
    #lock = Lock()
    if req.ok:
        html = req.text
        soup = BeautifulSoup(html, 'html.parser')
        #print("currentUrl = ", currentUrl)
        NewsTitle = ""
        articleTitle = ""

        
#        isItAEntertain = 1
##        print("entertain news")
#        NewsTitle = soup.select('div.end_ct_area > h2')
#            
#        for title in NewsTitle:
#            articleTitle = title.text.replace('\n',"").replace('\t',"")
##        print("title = ", articleTitle)
#
#        if len(articleTitle)<2:
#            isItAEntertain =0 
#            NewsTitle = soup.select('div.article_info > h3')
#
#            for title in NewsTitle:
#                articleTitle = title.text

        NewsTitle = soup.select('title')

        for title in NewsTitle:
            tempArticleTitle = title.text.replace('\n',"").replace('\t',"").split(":: 네이버")
            if len(tempArticleTitle) == 1:
                tempArticleTitle = title.text.replace('\n',"").replace('\t',"").split(": 네이버 뉴스")
            break
        articleTitle = tempArticleTitle[0].strip()
        for s in range (0, len(tempArticleTitle)):
            #print(tempArticleTitle[s])
            if (tempArticleTitle[s].find('연예')!=-1):
                print(currentUrl,"= 연예뉴스")
                isItAEntertain = 1
                break
        if isItAEntertain==0:
            print(currentUrl ,"=일반뉴스")

        press = soup.select('div.press_logo > a > img')
        articlePress = ""
        for title in press:
            #articlePress = title['title']
            articlePress = title['alt']
        if len(articlePress)<1:
 #           print('신문사 에러_', ex)

            press = soup.select('div.press_logo > a > img')
            for title in press:
                articlePress = title['alt']
        
        
        article = ""
        
        NewsContent = soup.select('div._article_body_contents')
        article = ""
        for content in NewsContent:
            tempStr = content.text.replace("// flash 오류를 우회하기 위한 함수 추가", "",1).replace("function _flash_removeCallback() {}","",1).replace("\n","").replace("\t","")
            article+=tempStr

        if len(article) <= 2:
            print("currentUrl = ", currentUrl)
            NewsContent = soup.select('div.article_body.font1.size3')
            article = ""
            for content in NewsContent:
                tempStr = content.text.replace("<br>", "").replace("\n"," ").replace("\t"," ")
                article+=tempStr
                article+="\n"
            #print(content.text.replace("// flash 오류를 우회하기 위한 함수 추가", "").replace("function _flash_removeCallback() {}",
            #print(content.text.replace("// flash 오류를 우회하기 위한 함수 추가", "").replace("function _flash_removeCallback() {}",
#                                                                                 ""))
            #print("article = ", article)
        if len(article) <=2:
            print(currentUrl, " is worng article. i'll return")
            return
        # CommentCnt = soup.select('div.article_btns_left > a > span.lo_txt')
        tempUrl = currentUrl
        commentUrlParser = currentUrl.split('?')
        commentUrl = commentUrlParser[0] + "?m_view=1&includeAllCount=true&" + tempUrl.replace(commentUrlParser[0], "").replace("?","")
        #print("current Url = ", currentUrl)
        #print("current commentUrl = ", commentUrl)
        articleDate = "error"
        try:
            articleDate2 = soup.select('div.sponsor > span.t11')
            dateParser3 = ""
            for i in articleDate2:
                dateParser3 = i.text
                #print(i.text)
                break
            #print("dateParser3 = ", dateParser3)
            #print("articleDate = ", articleDate2[0].text)
            dateParser = dateParser3.split('.')
            date = dateParser[0]+"-"+ dateParser[1] +"-" + dateParser[2] + " "
            dateParser = dateParser3.split(' ')
            timeParser = dateParser[2].split(':')
            hour = int(timeParser[0])
            minute = int(timeParser[1])
            convMinute = str(minute)
            convHour = str(hour)
            if '오후' in dateParser[1]:
                if hour != 12:
                    hour+=12
                convHour = str(hour)
            if minute < 10:
                convMinute = "0"+convMinute
            if hour < 10:
                convHour = "0"+convHour
            # resultDate는 기사 시간
            articleDate = date + convHour + ":" + convMinute
            #print("articleDate = ", articleDate)
#           print("resultDate = ", articleDate)
#           resultDate = NewsDate[0].text
        except Exception as ex: # 에러 종류
            #articleDate2 = soup.select('div.article_info > span.author > span.bar > em')
            articleDate2 = soup.select('div.article_info > span.author > em')
            dateParser3 = ""
            for i in articleDate2:
                dateParser3 = i.text
                break
            dateParser = dateParser3.split('.')
#            print("dataParser = " , dateParser3)
            try:
                date = dateParser[0]+"-"+ dateParser[1] +"-" + dateParser[2] + " "
            except:
                print()
                #print("dataParser = " , dateParser3)
            dateParser = dateParser3.split(' ')
            timeParser = dateParser[2].split(':')
            hour = int(timeParser[0])
            minute = int(timeParser[1])
            convMinute = str(minute)
            convHour = str(hour)
            if '오후' in dateParser[1]:
                if hour != 12:
                    hour+=12
                convHour = str(hour)
            if minute < 10:
                convMinute = "0"+convMinute
            if hour < 10:
                convHour = "0"+convHour
            # resultDate는 기사 시간
            articleDate = date + convHour + ":" + convMinute

        #selenium process
        try:
            #driver = webdriver.Firefox(firefox_profile=ff_profile,firefox_options=options,log_path = args[4])
            driver = webdriver.Chrome(args[3], chrome_options=options)
            driver.implicitly_wait(5)
            driver.get(commentUrl)
        except Exception as ex: # 에러 종류
            print('에러가 발생 했습니다', ex)
            print("can't Url = ", commentUrl)
            print("Ebsolutly Their isn't Comment Page")
            #UrlCnt.value+=1
            return
        commentTotalCnt = 0
        intCTC = 0
        try:
            commentTotalCnt = driver.find_element_by_css_selector('span[class=u_cbox_info_txt]').text.replace(",", "",1)
            intCTC=int(commentTotalCnt)
            #print("commentTotalCnt = ", commentTotalCnt)
        except Exception as ex: # 에러 종류
            #print('CommentTotalCnt 에서 에러가 발생 했습니다')
            commentTotalCnt = driver.find_element_by_css_selector('span[class=u_cbox_count]').text.replace(",", "",1)
            intCTC=int(commentTotalCnt)
            #print("commentTotalCnt = ", commentTotalCnt)

        comments = []

        if intCTC>0:
            try:
                try:
                    for i in range(0, 100000):
                        time.sleep(0.2)
                        driver.find_element_by_css_selector(".u_cbox_btn_more").click()
                except:
                    for i in range(0, 100000):
                        time.sleep(0.2)
                        driver.find_element_by_css_selector(".u_cbox_page_more").click()
            except:
                print()
                #print("no more ""moreButton"" ")
            cBox = "error!"
            if isItAEntertain==0:
                try:
                    #print("isitaentertain = 0")
                    cBox = driver.find_elements_by_css_selector('div[class=u_cbox_comment_box]')
                #print("cBox's size = ", len(cBox))
                    commentDate = ""
                    commentContent = ""
                    commentGood = 0
                    commentBad = 0
                    commCnt = 1
                    for i in cBox:
                        parser = i.text.split("\n")
                        try:
                            if len(parser)<=10 and parser[1].find('댓글모음')==-1:
                                #print("댓그모음 없고 내용이 없음")
                                parser.insert(1, "")
                            elif len(parser)>10 and parser[1].find('댓글모음')==-1:
                                te=0
                            #print("댓금오음 없고 내용이 있음")
                            elif len(parser)<=11 and parser[1].find('댓글모음')!=-1:
                            #print("댓글모음 있고 내용이 없음")
                                parser.insert(2, " ")
                                del parser[1]
                            elif len(parser)>11 and parser[1].find('댓글모음')!=-1:
                            #print("댓글모음 있고 내용이 있음")
                                del parser[1]
                            else:
                                print("아무것도 해당 안됨")
                            #print("parser = ", parser)
                        except:
                            print()
                        #print("ffddsfdfsdfs")
                        thisComment = ""
                        for j in parser:
                            thisComment = thisComment + j.strip() + "\n"
                        #temp = i.text.find('댓글모음\n')
                        indexNum = 0
                        #tempComment=""
                        #print("cBox = ", tempComment)
                        #cBoxParser = tempComment.split("\n")
                        cBoxParser = thisComment.split("\n")
                        #print(cBoxParser)
                        #print("second index = ", "@@" , cBoxParser[indexNum+1],"@@")
                        commentContent = cBoxParser[indexNum+1].strip()
                        commentParser = cBoxParser[indexNum+2].strip().split(" ")
                        cP1 = commentParser[0].split(".")
                        #print("cP1 = ", cP1)
                        cP2 = commentParser[1].split(":")
                        #print("cP2 = ", cP2)
                        commentDate = cP1[0].strip()+"-"+cP1[1].strip()+"-"+cP1[2].strip()+"T"+cP2[0].strip()+":"+cP2[1].strip()+":"+cP2[2].strip()+"+0900"
                        #print("error part's tempComment = ", tempComment)
                        commentGood = cBoxParser[indexNum+8].strip()
                        commentBad = cBoxParser[indexNum+10].strip()
                        comments.append([cs(str(commCnt)), cs(commentContent.replace("번역","")), cs(commentDate), cs(commentGood), cs(commentBad), cs(str(intCTC))])
                        print(comments[commCnt-1])
                        commCnt+=1
                except Exception as ex: # 에러 종류
                    print('cBox 에서 에러가 발생 했습니다', ex)
                    cBox = driver.find_elements_by_css_selector('div[class=u_cbox_comment_box]')
                    print("cBox_error_url = ", commentUrl)
                    return 
                    for i in cBox:
                        print("indexNum = ", i.text)
            elif isItAEntertain==1:
                print("isitaentertain = 0")
                print("entertain comments")

                try:
                    cBox = driver.find_elements_by_css_selector('div[class=u_cbox_comment_box]')
                #print("cBox's size = ", len(cBox))
                    commentDate = ""
                    commentContent = ""
                    commentGood = 0
                    commentBad = 0
                    commCnt = 1
                    for i in cBox:
                        parser = i.text.split("\n")
                        twit = parser[0].find('트위터')
                        face = parser[0].find('페이스북')
                        if twit==-1 and face==-1:
                            try:
                                fire = parser[1].find('댓글모음')
                                lens = len(parser) 
                                if lens<=9 and fire==-1:
                                #print("댓그모음 없고 내용 없음")
                                    parser.insert(1, "")
                                elif lens>9 and fire==-1:
                                    te=0
                                    #print("댓금오음 없고 내용 있음")
                                elif lens<=10 and fire!=-1:
                                    #print("댓글모음 있고 내용 없음")
                                    del parser[1]
                                    parser.insert(1, " ")
                                elif lens>10 and fire!=-1:
                                    #print("댓글모음 있고 내용 있음")
                                    del parser[1]
                                else:
                                    print("아무것도 해당 안됨")
                                #print("in if = ", parser)
                            except:
                                print()

                        else:
                            del parser[0]
                            lens = len(parser) 
                            fire = parser[1].find('댓글모음')
                            #parser.insert(1, "")
                            print("트위터 in comment error")
                            if lens<=9 and fire==-1:
                                #print("댓그모음 없고 내용 없음")
                                parser.insert(1, "")
                            elif lens>9 and fire==-1:
                                te=0
                                #print("댓금오음 없고 내용 있음")
                            elif lens<=10 and fire!=-1:
                                #print("댓글모음 있고 내용 없음")
                                parser.insert(2, " ")
                                del parser[1]
                            elif lens>10 and fire!=-1:
                                #print("댓글모음 있고 내용 있음")
                                del parser[1]
                            else:
                                print("아무것도 해당 안됨")
                            print("in else", parser)
                            print("twit''s size = ", lens)
                        #print("ffddsfdfsdfs")
                        #print("parser = ", parser)
                        thisComment = ""
                        for j in parser:
                            thisComment = thisComment + j.strip() + "\n"
                        #temp = i.text.find('댓글모음\n')
                        indexNum = 0
                        #print("cBox = ", tempComment)
                        #cBoxParser = tempComment.split("\n")
                        cBoxParser = thisComment.split("\n")
                        #print(cBoxParser)
                        if cBoxParser[2].find("전")!=-1:
                                intCTC-=1
                                continue
                        #print("second index = ", "@@" , cBoxParser[indexNum+1],"@@")
                        commentContent = cBoxParser[indexNum+1].strip()
                        commentParser = cBoxParser[indexNum+2].strip().split(" ")
                        cP1 = commentParser[0].split("-")
                        #print("cP1 = ", cP1)
                        cP2 = commentParser[1].split(":")
                        #print("cP2 = ", cP2)
                        commentDate = cP1[0].strip()+"-"+cP1[1].strip()+"-"+cP1[2].strip()+"T"+cP2[0].strip()+":"+cP2[1].strip()+":00"+"+0900"
                        #print("error part's tempComment = ", tempComment)
                        commentGood = cBoxParser[indexNum+7].strip()
                        commentBad = cBoxParser[indexNum+9].strip()
                        comments.append([cs(str(commCnt)), cs(commentContent.replace("번역","")), cs(commentDate), cs(commentGood), cs(commentBad), cs(str(intCTC))])
                        print(comments[commCnt-1])
                        commCnt+=1
                except Exception as ex: # 에러 종류
                    print('cBox 에서 에러가 발생 했습니다', ex)
                    cBox = driver.find_elements_by_css_selector('div[class=u_cbox_comment_box]')
                    print("cBox_error_url = ", commentUrl)
                    return
                    for i in cBox:
                        print("indexNum = ", i.text)
        lock = Lock()
        lock.acquire()
        print("UrlCnt = ", UrlCnt.value)
        UrlCnt.value+=1
        articleDict[int(UrlCnt.value)] = [cs(str(UrlCnt.value)), cs(articlePress), cs(articleDate), cs(articleTitle), cs(article), cs(currentUrl), cs(str(intCTC))]
        commentDict[int(UrlCnt.value)] = [cs(str(UrlCnt.value)), comments] 
        #UrlCnt.value+=1
        lock.release()
        driver.close()

def getCommentContents():
    print()

def cs(convertStr):
    return(convertStr.encode('euc-kr', "replace").decode('euc-kr', "replace"))


def writing(convertArticleDict, convertCommentDict, category):
    writer1 = open(args[2] + category+'_'+ 'article-long' +'.csv', 'w', encoding='euc-kr', newline='')
    writer2 = open(args[2] + category+'_'+ 'comment' +'.csv', 'w', encoding='euc-kr', newline='')
    writer3 = open(args[2] + category+'_'+ 'comment_cnt' +'.csv', 'w', encoding='euc-kr', newline='')

    writer1 = open(args[2] + category+'_'+ 'article-long' +'.csv', 'a', encoding='euc-kr', newline='')
    writer2 = open(args[2] + category+'_'+ 'comment' +'.csv', 'a', encoding='euc-kr', newline='')
    writer3 = open(args[2] + category+'_'+ 'comment_cnt' +'.csv', 'a', encoding='euc-kr', newline='')

    wr1 = csv.writer(writer1)
    wr2 = csv.writer(writer2)
    wr3 = csv.writer(writer3)

    wr1.writerow(["id","press","date","title","article","web.addr","comment.cnt"])
    wr2.writerow(["urlId","comments.contents","comments.regTimeGmt","comments.sympathyCount","comments.antipathyCount"])
    wr3.writerow(["urlId","cnt"])

    for i in range (0, len(convertArticleDict)):
        #print([str(convertArticleDict[i+1][0]), str(convertArticleDict[i+1][1]), str(convertArticleDict[i+1][2]), str(convertArticleDict[i+1][3]), str(convertArticleDict[i+1][4]), str(convertArticleDict[i+1][5]), str(convertArticleDict[i+1][6])])
        try:
            wr1.writerow([str(convertArticleDict[i+1][0]), str(convertArticleDict[i+1][1]), str(convertArticleDict[i+1][2]), str(convertArticleDict[i+1][3]), str(convertArticleDict[i+1][4]), str(convertArticleDict[i+1][5]), str(convertArticleDict[i+1][6])])
        except:
            print("wr1 error ")
        try:
            if str(convertArticleDict[i+1][6]) != '0':
                wr3.writerow([str(convertArticleDict[i+1][0]), str(convertArticleDict[i+1][6])])    
        except:
            print("wr3 error")

    for j in range (0, len(convertCommentDict)):
        try:
            comms = convertCommentDict[j+1][1]
        except:
            print("it must run continue")
            continue

        for c in comms:
            #print([convertCommentDict[j+1][0], c[1], c[2], c[3], c[4], c[5]])
            try:
                if c[5] != '0':
                    wr2.writerow([convertCommentDict[j+1][0], c[1], c[2], c[3], c[4], c[5]])
            except:
                print("wr2 error", "\nwr2 = ", wr2)

def getEndFunc(keyword, driverPath):
    url = "https://search.naver.com/search.naver?where=news&sm=tab_jum&nso=so%3Ar%2Cp%3Afrom20180901to20191031%2Ca%3Aa&query={}&start=5000000".format(keyword)
    print("firstUrl = ", url)
    driver = webdriver.Chrome(driverPath, chrome_options=options)
    driver.implicitly_wait(5)
    driver.get(url)
    
    #totalParser2 = driver.find_element_by_css_selector('div[class=title_desc.all_my]')
    totalCnt = 0
    try:
        #totalParser2 = driver.find_element_by_xpath("""//*[@id="main_pack"]/div[2]/div[1]/div[1]/span""").text
        try:
            totalCnt = int(driver.find_element_by_xpath("""//*[@id="main_pack"]/div[2]/div[1]/div[1]/span""").text.split('/')[1].strip().replace(",", "").replace("건", ""))
        except:
            totalCnt = int(driver.find_element_by_xpath("""//*[@id="main_pack"]/div/div[1]/div[1]/span""").text.split('/')[1].strip().replace(",", "").replace("건", ""))
        #totalParser2 = driver.find_element_by_xpath("""//*[@id="main_pack"]/div[2]/div[1]/div[1]/span""").text
        #totalParser = totalParser2.split("/")
        #totalCnt = totalParser[1].strip().replace(",", "").replace("건", "")
        lastTotalCnt = 0
        #print("totalCnt = ", totalCnt)
    
        if totalCnt>=4000:
            lastTotalCnt = 4000
        else:
            lastTotalCnt = totalCnt

        print("lastTotalCnt = ", lastTotalCnt)
        driver.close()
        return(lastTotalCnt)
    except Exception as ex: # 에러 종류
        print('에러가 발생 했습니_', ex)

if __name__ == '__main__':
    categories = {'결혼이민자': 'A', '귀화자': 'C', '영주자격자':'D', '외국인근로자':'E', '재외동포':'F', '외국국적동포':'G','전문인력 외국인':'M', '외국인유학생':'H', '난민':'I', '다문화자녀':'K', '중도입국자녀':'L'}
    coreNum = int(args[4])
    print("We will use ", coreNum, "cores.")
    print("keword = ", search_word)
    UrlCnt = manager.Value('i', 0)
    start_time = time.time()
    end = getEndFunc(search_word, args[3])
    #test
    #end = 3
    ###
    pool = Pool(processes=coreNum)
    pool.map(getNewsUrls, range(1, end, 10))
    tempLists = list(set(Urls_list))
    lists = []
    for i in range(0, len(tempLists)):
        url = tempLists[i]
        if "sports.news.naver.com" in url:
            print(url, " is sports")
            #lists.append(url)
            continue
        #if "sid1=106" in url:
        #    print(url," is entertain")
        #    lists.append(url)
        #    continue
        lists.append(url)
    print("Real Url's cnt = ", len(lists))
    #print("lists")
    #for i in lists:
    #    print(i)
    # for test
    #lists = ["https://news.naver.com/main/read.nhn?mode=LSD&mid=sec&oid=382&aid=0000756703", "https://news.naver.com/main/read.nhn?mode=LSD&mid=sec&sid1=101&oid=015&aid=0004033394"]
    #######
    func = partial(getNewsContents, UrlCnt)
    pool.map(func, lists)
    convertArticleDict = dict(articleDict)
    convertCommentDict = dict(commentDict)
    
    writing(convertArticleDict, convertCommentDict, categories[search_word])
    #print("articles :\n",convertArticleDict)
    #print("comments :\n",convertCommentDict)
