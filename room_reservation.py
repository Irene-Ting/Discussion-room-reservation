from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import NoSuchElementException
from dotenv import load_dotenv
from argparse import ArgumentParser
from datetime import date
from datetime import datetime as dt
import time
import os 
import sys
import datetime
import calendar

priority = [
    [4, 'deviceRadio0'], #401
    [5, 'deviceRadio0'], #501
    [6, 'deviceRadio0'], #601
    [2, 'deviceRadio0'], #201
    [2, 'deviceRadio1'], #202
    [2, 'deviceRadio2'], #203
    [2, 'deviceRadio3'], #204
    [2, 'deviceRadio4'], #205
    [3, 'deviceRadio0'], #301
    [3, 'deviceRadio1'], #302
    [3, 'deviceRadio2'], #303
    [5, 'deviceRadio1'], #502
    [6, 'deviceRadio1']  #602
]

room_num = {
    '4deviceRadio0': "401",
    '5deviceRadio0': "501",
    '6deviceRadio0': "601",
    '2deviceRadio0': "201",
    '2deviceRadio1': "202",
    '2deviceRadio2': "203",
    '2deviceRadio3': "204",
    '2deviceRadio4': "205",
    '3deviceRadio0': "301",
    '3deviceRadio1': "302",
    '3deviceRadio2': "303",
    '5deviceRadio1': "502",
    '6deviceRadio1': "602",
}

def get_args():
    cur = date.today()
    today = cur.weekday()

    parser = ArgumentParser()
    parser.add_argument(
        "-s",
        help='student ID',
        default=["021060611430", "021080311300"],
        type=str,
        nargs=2
    )
    parser.add_argument(
        "-d", 
        help='The day you want to reserve. 1 for next Monday, 2 for next Tuesday ...', 
        dest="reserve_date",
        default=f'{today+1}',
        type=int
    )
    parser.add_argument(
        "-t", 
        help='Start time of your reservation. ex. 15:00', 
        dest="start_time",
        default='15:00', 
    )
    return parser.parse_args()


def get_span(start):
    span = []
    start = [start[0:2], start[3:5]]

    for i in range(4):
        end = ['15', '00']
        if(start[1] == '00'):
            end[0] = start[0]
            end[1] = '29'
        else:
            end[0] = start[0]
            end[1] = '59'

        span.append(f'{start[0]}:{start[1]}~{end[0]}:{end[1]}')

        if(end[1] == '59'):
            start[0] = str(int(end[0])+1).zfill(2)
            start[1] = '00'
        else:
            start[0] = end[0]
            start[1] = '30'
    return span


def main():
    print("Loading...")
    load_dotenv()
    ACCOUNT = os.getenv("ACCOUNT")
    PW = os.getenv("PW")

    args = get_args()

    setting = {
        "student1": args.s[0],
        "student2": args.s[1],
        "start_time": args.start_time,
        "reserve_date": args.reserve_date,
    }

    span = get_span(setting['start_time'])

    # open browser
    print("Open browser...\t", end="")
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome('./chromedriver', options=options)
    driver.get("https://libsms.lib.nthu.edu.tw/build/")
    print("Succeed")

    # login
    print("Login...\t", end="")
    driver.find_element_by_id("login_account").send_keys(ACCOUNT)
    driver.find_element_by_id("login_password").send_keys(PW)
    driver.find_element_by_class_name("btn").click()
    driver.implicitly_wait(1) 
    print("Succeed")

    today = date.today()
    cur_hour, cur_min = dt.now().strftime("%H"), dt.now().strftime("%M")
    if(setting['reserve_date']==today.weekday()+1 and (int(setting['start_time'][0:2])>int(cur_hour) or (int(setting['start_time'][0:2])==int(cur_hour) and int(setting['start_time'][3:5])>int(cur_min)))):	
        d2 = today.strftime("%B %-d, %Y")
        d1 = calendar.day_name[today.weekday()]
        reserve_date = f'Selected. {d1}, {d2}'
    else:
        find_date = today + datetime.timedelta(1)
        while find_date.weekday() != setting['reserve_date']-1:
            find_date += datetime.timedelta(1)
        d2 = find_date.strftime("%B %-d, %Y")
        d1 = calendar.day_name[setting['reserve_date']-1]
        reserve_date = f'{d1}, {d2}'
    print(f"Reserving for {d1}, {d2} {span[0][0:5]}~{span[3][6:11]}")

    for room in priority:
        print(f'Trying room{room_num[str(room[0])+room[1]]}')

        # add discussion room
        time.sleep(1)
        driver.find_element_by_class_name("appointment").click()
        driver.find_element_by_class_name("room_spacetype_2").click()

        # choose date
        driver.find_element_by_id("startDate").click()
        driver.implicitly_wait(1) 
        driver.find_element_by_xpath(f"//td[@aria-label='{reserve_date}']").click()

        # reserve
        floor = room[0]
        driver.find_element_by_xpath(f"//*[@zonename='{floor}F-討論室']").click()
        driver.implicitly_wait(1)

        driver.find_element_by_id("confirm_policy").click()
        driver.find_element_by_xpath("//*[text()='下一步']").click()
        driver.implicitly_wait(1) 

        print("Enter ID...\t", end="")
        blanks = driver.find_elements_by_class_name('form-control')
        blanks[0].send_keys(setting['student1'])
        blanks[1].send_keys(setting['student2'])
        driver.find_element_by_xpath("//*[text()='預約讀者查詢']").click()
        driver.implicitly_wait(1) 
        
        try:
            driver.find_element_by_xpath("//*[text()='查詢當日所有空間']").click()
            print("Verified")
            time.sleep(1)
        except NoSuchElementException:
            print("Fail")
            return

        try:
            driver.find_element_by_id(room[1]).click()
            driver.find_element_by_xpath(f"//*[@viewvalue='{span[0]}']").click()
            driver.find_element_by_xpath(f"//*[@viewvalue='{span[1]}']").click()
            driver.find_element_by_xpath(f"//*[@viewvalue='{span[2]}']").click()
            driver.find_element_by_xpath(f"//*[@viewvalue='{span[3]}']").click()
            
            print("Done")
            time.sleep(30)
            break
            #driver.find_element_by_xpath("//*[text()='確認預約資訊']").click()
            #driver.close()
        except ElementClickInterceptedException:
            print("Fail to reserve")
            driver.back()

    print("There is no room available QAQ")


if __name__ == "__main__":
    main()
    
