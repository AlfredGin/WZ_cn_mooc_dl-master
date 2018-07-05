# -*- coding: utf-8 -*-

from __future__ import print_function

import re
import os
import sys
import requests
import time

from utils import mkdir_p, parse_args, clean_filename, DownloadProgress, download_file

def parse_syllabus_study163(session, page):
    lesson_url = ''
    lessonName = ''
    data = page.splitlines(True)
    
    multi_resolution_flag = ['videoSHDUrl',
                            'mp4HdUrl',
                            'mp4SdUrl',
                            'flvShdUrl',
                            'videoHDUrl',
                            'flvHdUrl',
                            'videoUrl',
                            'flvSdUrl']
    course = []
    lessons = []
    course_id = ''
    cur_chapter = ''

    get_videoid_url = 'http://study.163.com/dwr/call/plaincall/LessonLearnBean.getVideoLearnInfo.dwr'

    headers = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'zh-CN,zh;q=0.9',
            'Connection':'keep-alive',
            'Host':'study.163.com',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
            }

    #正则匹配courseId、cur_chapter(章名)的表达式
    for line in data:
        lesson_info = dict(re.findall(r"s\d+\.(?P<name>.*?)=(?P<value>.*?);",line))
        if lesson_info:
            if ('courseId' in lesson_info) and ('name' in lesson_info):
                course_id = lesson_info['courseId']
                if lessons:
                    course.append((cur_chapter, lessons))
                    lessons = []
                cur_chapter = lesson_info['name'].decode('raw_unicode_escape')
                print('*************************')
                print('     '+cur_chapter+'     ')
                print('*************************')

            elif 'lessonName' in lesson_info:
            	print('====')
                params =  {
                        'callCount':'1',
                        'scriptSessionId':'${scriptSessionId}190', #* , but arbitrarily
                        'httpSessionId':'686777b732444cd2b43020d3fcddd0d1',
                        'c0-scriptName':'LessonLearnBean',
                        'c0-methodName':'getVideoLearnInfo',
                        'c0-id':'0',
                        'c0-param0':'string:' + lesson_info['id'],
                        'c0-param1':'string:' + course_id,
                        'batchId':'969403', #* , but arbitrarily
                        }
                r = session.post(get_videoid_url, headers = headers, data = params, cookies = {'Cookie':'videoResolutionType=3;'})

                if r.status_code is not 200:
                    print("Failed to get video ID.")
                    sys.exit(0)

                #正则匹配lesson_url的表达式
                info = dict(re.findall(r".(?P<name>.*?)=(?P<value>.*?);", r.content))

                #根据爬取来的网页信息，需要规范化键值对，因为根据post来的数据中，mp4HdUrl等视频标识符前面还有个s1.,即视频标识符为s1.mp4HdUrl=“url”
                infofixed = {}
                for i in info:
                	new_name=i.split('.')
                	if len(new_name)>1 :
               			n_name = new_name[1]
               			infofixed[n_name]=info[i]


                #添加lesson_url
                for res in multi_resolution_flag:
                	if (res in infofixed) and (infofixed[res] != 'null'):
                		lesson_url = infofixed[res].strip('\"')
                		break

                #向lessons列表中添加lesson_url和lessonName
                lessonName = lesson_info['lessonName'].strip('\"')
                lessons.append((lesson_url,lessonName))
                print(len(lessons), end="")
                print(lessonName.decode('raw_unicode_escape'))
                

    course.append((cur_chapter, lessons))
    
    return (course_id, course)


def download_syllabus_study163(session, syllabus, path = '', overwrite = False):

    headers = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'zh-CN,zh;q=0.9',
            'Connection':'keep-alive',
            'Host':'study.163.com',
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
            }
    get_token_url = 'http://study.163.com/video/getVideoAuthorityToken.htm'

    session.headers.update(headers);

    course_id = syllabus[0]
    print('-----')
    print(course_id)
    course = syllabus[1]
    retry_list = []

    for (chapter_num,(chapter, lessons)) in enumerate(course):
        chapter_name = clean_filename(chapter)
        dir = os.path.join(path, ('%02d %s'% (chapter_num+1, chapter_name)))
        print(dir)
        if not os.path.exists(dir):
            mkdir_p(dir)
        for (lesson_num,(lesson_url, lesson_name)) in enumerate(lessons):

            print('lesson_num:   ', end="")
            print(lesson_num)
            print('lesson_name:   '+lesson_name.decode('raw_unicode_escape'))

            lesson_name = clean_filename(lesson_name.decode('raw_unicode_escape'))
            filename = os.path.join(dir, '%02d_%s.mp4' %(lesson_num+1, lesson_name))
            print(filename)


            if overwrite or not os.path.exists(filename):
                try:
                    r = session.get(get_token_url)
                    video_url = lesson_url
                    download_file(video_url, filename )

                except Exception as e:
                    print(e)
                    print('1Error, add it to retry list')
                    retry_list.append((lesson_url, filename))
            else:
                print ('Already downloaded')

    retry_times = 0
    while len(retry_list) != 0 and retry_times < 3:
        print('%d items should be retried, retrying...' % len(retry_list))
        tmp_list = [item for item in retry_list]
        retry_times += 1
        for (url, filename) in tmp_list:
            try:
                print(url)
                print(filename)
                r = session.get(get_token_url)
                video_url = lesson_url
                download_file(video_url, filename )

            except Exception as e:
                print(e)
                print('2Error, add it to retry list')
                print('lesson_url:'+lesson_url)
                continue

            retry_list.remove((url, filename))

    if len(retry_list) != 0:
        print('%d items failed, please check it' % len(retry_list))
    else:
        print('All done.')


def main():

    args = parse_args()
    course_link = args.course_url[0]
    path = args.path
    overwrite = args.overwrite

    regexs = [r'(?:https?://)study.163.com/course/introduction/(?P<courseid>\d+)\.htm',
              r'(?:https?://)study.163.com/course/courseMain.htm\?courseId=(?P<courseid>\d+)',
              r'(?:https?://)study.163.com/course/introduction.htm\?courseId=(?P<courseid>\d+)'
              ]

    for regex in regexs:
        m = re.match(regex, course_link)
        if m is not None:
            break

    if m is None:
        print ('The URL provided is not valid for study.163.com')
        sys.exit(0)

    path = os.path.join(path, m.group('courseid'))
    headers = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
            'Accept-Encoding':'gzip, deflate',
            'Accept-Language':'zh-CN,zh;q=0.9',
            'Connection':'keep-alive',
            'Referer': 'http://study.163.com/course/introduction.htm?courseId=334013&from=study',
            'Host': 'study.163.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
              }

    post_data = {
                'callCount':1,
                'scriptSessionId':'${scriptSessionId}190',
                'c0-scriptName':'PlanNewBean',
                'c0-methodName':'getPlanCourseDetail',
                'c0-id': 0,
                'c0-param0':'string:' + m.group('courseid'),
                'c0-param1':'number:0',
                'c0-param2':'null:null',
                'batchId':434820, #arbitrarily
                }
    course_detail_dwr_url = 'http://study.163.com/dwr/call/plaincall/PlanNewBean.getPlanCourseDetail.dwr'

    session = requests.Session()
    session.headers.update(headers)
    r = session.post(course_detail_dwr_url, data = post_data)
    if r.status_code is not 200:
        print('Failed to get .dwr file.')
        sys.exit(0)
    print ('Parsing...')

    #解析课程网页信息，syllabus数据类型为tuple(course_id, course),其中course = [(cur_chapter, lessons)]列表，lessons = [(lesson_url,lessonName)]列表。
    syllabus = parse_syllabus_study163(session, r.content)
    if syllabus:
        print ('Done.')
    else:
        print ('Failed. No course content on the page.')
        sys.exit(0)
        
    #根据解析的信息进行批量自动化下载,注意一点，在utils.py的函数download_file()里有个变量chunk_sz用于限定下载文件的size,初始设置为1MB左右，可根据自己下载视频的实际大小进行调整
    download_syllabus_study163(session, syllabus, path, overwrite)

if __name__ == '__main__':
    main()