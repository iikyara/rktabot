# coding: utf-8

import os
import datetime
import dj_database_url
import psycopg2

def connect():
    if os.getenv("DATABASE_URL")!=None:
        p = dj_database_url.config()
    else:
        print('config:DATABASE_URL is NOT found.')
        exit(1)

    return psycopg2.connect(
        dbname = p['NAME'],
        user = p['USER'],
        password = p['PASSWORD'],
        host = p['HOST'],
        port = p['PORT'],
        )

#
# 引数
#   exestr   文字列　省略不可
#   elements リスト　省略可能
#
# 戻り値
#   exestrを実行し，結果を返す．
#
def sqlExe(exestr, elements = []):
    conn = connect()
    cur = conn.cursor()
    if len(elements)==0:
        cur.execute(exestr)
        result = cur.fetchall()
    else:
        cur.execute(exestr, elements)
        result = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    return result

'''
            テーブル "public.setting"
     列     |            型            |  修飾語
------------+--------------------------+----------
 id         | integer                  | not null
 title      | character(10)            |
 sdate      | date                     |
 starttime  | time without time zone   |
 endtime    | time without time zone   |
 content    | character(30)            |
 updatetime | timestamp with time zone |
インデックス:
    "setting_pkey" PRIMARY KEY, btree (id)
参照元：
    TABLE "settingdetail" CONSTRAINT "settingdetail_id_fkey" FOREIGN KEY (id) REFERENCES setting(id) ON DELETE CASCADE
'''
# 次の予定を1次元配列で返す．
def selectNextPlan():
    nextPlan = sqlExe("SELECT * FROM setting ORDER BY sdate ASC;")
    today = datetime.date.today()
    now = datetime.datetime.now().time()
    if len(nextPlan)!=0:
        for plan in nextPlan:
            if len(plan)<3:
                break
            startdate = plan[2]
            endtime = plan[4]
            if startdate == today and endtime < now:
                continue
            elif startdate < today:
                continue
            else:
                return [plan]
    return None

# 指定された日の予定を2次元配列で返す．
def selectDatePlan(date):
    datePlan = sqlExe("SELECT * FROM setting WHERE sdate = %s ORDER BY starttime ASC;", [date.strftime('%Y-%m-%d')])
    return datePlan

# 今日の予定を2次元配列で返す．
def selectToDayPlan():
    return selectDatePlan(datetime.date.today())

# 明日の予定を2次元配列で返す．
def selectTomorrowPlan():
    return selectDatePlan(datetime.date.today()+datetime.timedelta(1))

# 明後日の予定を2次元配列で返す．
def selectDayAfterTomorrowPlan():
    return selectDatePlan(datetime.date.today()+datetime.timedelta(2))

# 2つの日付間の予定を2次元配列で返す．
def selectBetweenDatePlan(startD, endD):
    weekPlan = sqlExe("SELECT * FROM setting WHERE sdate >= %s AND sdate <= %s ORDER BY sdate ASC;", [startD.strftime('%Y-%m-%d'),endD.strftime('%Y-%m-%d')])
    return weekPlan

# 指定された日から1週間の予定を2次元配列で返す．
def selectWeekPlan(date):
    startD = date
    endD = date + datetime.timedelta(7)
    return selectBetweenDatePlan(startD, endD)

# 指定された月の予定を2次元配列で返す．
def selectMonthPlan(month):
    startD = datetime.date(month.year,month.month,1)
    tempD = datetime.date(month.year,month.month%12+1,1)
    endD = datetime.date(month.year,month.month,(tempD-datetime.timedelta(days=1)).day)
    return selectBetweenDatePlan(startD, endD)

# 今月の予定を2次元配列で返す．
def selectThisMonthPlan():
    return selectMonthPlan(datetime.date.today())

# 来月の予定を2次元配列で返す．
def selectNextMonthPlan():
    today = datetime.date.today()
    nextMonth = datetime.date(today.year,today.month%12+1,1)
    return selectMonthPlan(nextMonth)

os.environ['DATABASE_URL'] = 'postgres://znbsgmzmumcwna:ea509f79b04c4ebc12f441f31389728f1d9985da0ead6cf76bc1f0d2be7486ce@ec2-54-243-38-139.compute-1.amazonaws.com:5432/d4cqsd3c2mss6m'
'''
print(selectNextPlan())
print(selectDatePlan(datetime.date(2017,1,29)))
print(selectDatePlan(datetime.date(2018,1,1)))
print(selectToDayPlan())
print(selectTomorrowPlan())
print(selectWeekPlan(datetime.date(2017,1,28)))
print(selectMonthPlan(datetime.date(2017,2,2)))
print(selectThisMonthPlan())
print(selectNextMonthPlan())
'''
print(selectThisMonthPlan())
print(selectToDayPlan())
print(selectNextPlan())

