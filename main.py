# 这是一个示例 Python 脚本。

# 按 ⌃R 执行或将其替换为您的代码。
# 按 双击 ⇧ 在所有地方搜索类、文件、工具窗口、操作和设置。
import os
import sys
import requests
import time
import json
from lxml.html import document_fromstring
import hashlib
from bs4 import BeautifulSoup

path = './data/'
with open(path + '2023sp.json', 'r', encoding='utf-8') as fp:
    data = json.load(fp)


def get_validatecode(session: requests.Session) -> str:
    import re
    import pytesseract
    from PIL import Image
    from io import BytesIO

    for attempts in range(20):
        response = session.get(
            "https://passport.ustc.edu.cn/validatecode.jsp?type=login"
        )
        stream = BytesIO(response.content)
        image = Image.open(stream)
        text = pytesseract.image_to_string(image)
        codes = re.findall(r"\d{4}", text)
        if len(codes) == 1:
            break
    return codes[0]


def login(session: requests.Session, username, passwd):
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
    session.cookies.set("lang", "zh")
    response = session.get(
        "https://passport.ustc.edu.cn/login?service=https%3A%2F%2Fjw.ustc.edu.cn%2Fucas-sso%2Flogin",
        headers={"Referer": "https://jw.ustc.edu.cn/"},
    )
    root = document_fromstring(response.text)
    input = root.cssselect("input[name=CAS_LT]")
    cas_lt = input[0].value

    response = session.post(
        "https://passport.ustc.edu.cn/login",
        data={
            "model": "uplogin.jsp",
            "service": "https://jw.ustc.edu.cn/ucas-sso/login",
            "CAS_LT": cas_lt,
            "warn": "",
            "showCode": "1",
            "username": username,
            "password": passwd,
            "button": "",
            "LT": get_validatecode(session),
        },
        headers={
            "Referer": "https://passport.ustc.edu.cn/login?service=https%3A%2F%2Fjw.ustc.edu.cn%2Fucas-sso%2Flogin",
        },
        allow_redirects=True,
    )
    return session


""""
def login_fine(session: requests.Session):
    finereportTargetUrl = "https://jw.ustc.edu.cn/webroot/decision"
    username = '' 
    fineReportPw = ''
    password = hashlib.md5(fineReportPw.encode()).hexdigest()
    validity = "-1"
    url = finereportTargetUrl + "/login/cross/domain" + "?fine_username=" + username + "&fine_password=" + password + "&validity=" + validity
    r = session.get(
        url,
        headers={
            "Referer": "https://jw.ustc.edu.cn/home",
        },
    )
    return session


def fetch(session: requests.Session):
    payload = {"turnId": "", "studentId": ""}
    url = "https://jw.ustc.edu.cn/ws/for-std/course-select/addable-lessons?turnId=721&studentId="
    response = session.post(
        url,
        #data=payload,
    )
    print(response.text)
    return response, session
"""


def get_std_count(session: requests.Session, courseID):
    payload = {"lessonIds[]": courseID}
    url = "https://jw.ustc.edu.cn/ws/for-std/course-select/std-count"
    response = session.post(
        url,
        data=payload,
        headers={
            "Referer": "https://jw.ustc.edu.cn/for-std/course-select/353951/turn/721/select",
        },
    )
    return response.text[13:15], session


def check_course(session: requests.Session, code):
    std_limit = 0
    for course in data:
        if (course['code'] == code):
            std_limit = course['limitCount']
            course_name = course['course']['nameZh']
            course_id = course['id']
            break
    while(1):
        os.system('cls' if os.name == 'nt' else 'clear')
        std_count, session = get_std_count(session, course_id)
        print(f'Frequency: 5 SEC per query')
        print(f'{course_name}: {std_count} / {std_limit}')
        time.sleep(5)
    return session


if __name__ == '__main__':
    username = sys.argv[1]
    passwd = sys.argv[2]
    code = sys.argv[3]
    session = requests.Session()
    session = login(session, username, passwd)
    # print(r.text)
    # session = login_fine(session)
    # print(session.cookies)
    session = check_course(session, code)
