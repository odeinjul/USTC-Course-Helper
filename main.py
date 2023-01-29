import os
import sys
import time
import re
import requests
import time
import json
from lxml.html import document_fromstring
import argparse
import hashlib
from bs4 import BeautifulSoup

def mass(session: requests.Session):
    path = './data/'
    with open(path + '2023sp.json', 'r', encoding='utf-8') as fp:
        data = json.load(fp)
    session.headers.update(
        {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36",
            "Origin": "https://passport.ustc.edu.cn",
            "Accept-Language": "en,zh-CN;q=0.9,zh;q=0.8",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Sec-Ch-Ua-Mobile": "?0",
            "Sec-Ch-Ua-Platform": "macOS",
            "Cache-Control": "max-age=0",
            "Upgrade-Insecure-Requests": "1",
        }
    )
    with open(path + 'cookies.txt', 'r', encoding='utf-8') as file:
        cookies = file.readlines()
    for cookie in cookies:
        key = cookie.split(':')[0]
        value = cookie.split(':')[1][:-1]
        session.cookies.set(key, value)
    url = "https://jw.ustc.edu.cn/for-std/course-select/"
    r = session.get(url)
    stu_assoc = r.url.split('/')[-1]
    url = "https://jw.ustc.edu.cn/ws/for-std/course-select/open-turns"
    payload = {'bizTypeId': '2', 'studentId': stu_assoc}
    r = session.post(url, data=payload)
    turn_id = BeautifulSoup(r.text, 'lxml').id.string
    return stu_assoc, turn_id, data, session

def fetch(session: requests.Session, stu_assoc, turn_id):
    payload = {"turnId": turn_id, "studentId":  stu_assoc}
    url = "https://jw.ustc.edu.cn/ws/for-std/course-select/addable-lessons"
    response = session.post(
        url,
        data=payload,
    )
    #print(response.text)
    return session

def get_std_count(session: requests.Session, course_assoc):
    payload = {"lessonIds[]": course_assoc}
    url = "https://jw.ustc.edu.cn/ws/for-std/course-select/std-count"
    response = session.post(
        url,
        data=payload,
    )
    rule_ = '>\d+<'
    std_count = re.findall(rule_, response.text)
    return std_count[0][1:-1], session

def check_course(session: requests.Session, args):
    if args.watch:
        code = args.watch
    elif args.select:
        code = args.select
    else:
        raise ValueError("Please specify a course.")

    std_limit = -1
    course_assoc = 0
    course_name = ''
    for course in data:
        if (course['code'] == code):
            std_limit = course['limitCount']
            course_name = course['course']['nameZh']
            course_assoc = course['id']
            break
    assert std_limit != -1, "Can not find such course: " + code

    if args.watch:
        while (1):
            os.system('cls' if os.name == 'nt' else 'clear')
            std_count, session = get_std_count(session, course_assoc)
            print(f'[WATCH]- Frequency: 5 SEC per query')
            print(f'{course_name}: {std_count} / {std_limit}')
            time.sleep(5)
    elif args.select:
        while (1):
            os.system('cls' if os.name == 'nt' else 'clear')
            std_count, session = get_std_count(session, course_assoc)
            print(f'[SELECT] - Frequency: 5 SEC per query')
            print(f'{course_name}: {std_count} / {std_limit}')
            if int(std_count) < std_limit:
                print(f'Available! - Sending request')
                session, msg = apply_course(session, course_assoc, stu_assoc)
                if msg == "时间冲突":
                    break
                elif msg == "教学班人数已满":
                    continue

            time.sleep(5)

    return session


def apply_course(session: requests.Session, course_assoc):
    payload = {"studentAssoc": stu_assoc, "lessonAssoc": course_assoc, "courseSelectTurnAssoc": turn_id,
               "scheduleGroupAssoc": "", "virtualCost": "0"}
    url = "https://jw.ustc.edu.cn/ws/for-std/course-select/add-request"
    response = session.post(
        url,
        data=payload,
    )
    print(f'requestID - {response.text}')
    url = "https://jw.ustc.edu.cn/ws/for-std/course-select/add-drop-response"
    payload = {"studentId": stu_assoc, "requestId": response.text}
    response = session.post(
        url,
        data=payload,
    )
    text_ = BeautifulSoup(response.text, 'lxml')
    msg = str(text_.textzh)[8:-9]
    print(f'{msg}！')
    return session, msg


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="USTC course helper")
    parser.add_argument('-w', '--watch', metavar='[courseID]', type=str, help='the courseID you want to watch')
    parser.add_argument('-s', '--select', metavar='[courseID]', type=str, help='the courseID you want to select, the '
                                                                               'program will send application when '
                                                                               'available')
    parser.add_argument('-i', '--frequency', metavar='[sec]', type=int, default=5, help='how many (sec) to refresh '
                                                                                        'the result')
    args = parser.parse_args()

    session = requests.Session()
    stu_assoc, turn_id, data, session = mass(session)
    # session = fetch(session, stu_assoc, turn_id)
    session = check_course(session, args)
