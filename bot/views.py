# -*- coding: utf-8 -*-

#from django.shortcuts import render
#
## Create your views here.
#
import os
import random
import datetime
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import (
    MessageEvent, FollowEvent, UnfollowEvent, TextSendMessage, TemplateSendMessage,
    PostbackTemplateAction, MessageTemplateAction, URITemplateAction,
    ButtonsTemplate, ConfirmTemplate, CarouselTemplate, CarouselColumn
)

line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')

        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()

        for event in events:
            if isinstance(event, MessageEvent):
                template_message=createMessage(event)
                if len(template_message) >= 5:
                    pass
                else:
                    line_bot_api.reply_message(
                        event.reply_token,
                        template_message
                    )
            elif isinstance(event, FollowEvent):
                userid = event.source.user_id
                #プロフィールの取得(名前のみ)
                username = 'default name'
                try:
                    profile = line_bot_api.get_profile(userid)
                    username = profile.display_name
                except LineBotApiError as e:
                    pass
                sqlExe("INSERT INTO userinfo(userid,username,available,recordtime) VALUES(%s,%s,%s,%s);",[userid,username,'t',datetime.datetime.now()], False)
            elif isinstance(event, UnfollowEvent):
                sqlExe("DELETE FROM userinfo WHERE userid = %s;", [event.source.user_id], False)
        return HttpResponse()
    else:
        return HttpResponseBadRequest()

@csrf_exempt
def teiki(request):
    if request.method == 'GET':
        #定期配信を利用しているユーザーの取得
        users = sqlExe("SELECT userid FROM userinfo WHERE available = %s", ['t'])
        userIdSets = [] #150件ずつのユーザIDを持つ2次元配列
        newUserIds = [] #最大150件
        count = 0
        for user in users:
            newUserIds.append(user[0])
            count+=1
            if count>=150:
                userIdSets.append(newUserIds)
                newUserIds = []
        if len(newUserIds) > 0:
            userIdSets.append(newUserIds)
        #メッセージの作成
        template_message = createRegulalyMessage()
        if template_message == 'bad':
            return HttpResponseBadRequest()
        if template_message == None:
            pass
        elif len(template_message) >= 5 or len(template_message) == 0:
            pass
        else:
            for user in userIdSets:
                line_bot_api.multicast(
                    user,
                    template_message
                )
        #予定データベースの更新
        regulalyUpdatePlan()
        return HttpResponse()
    else:
        return HttpResponseBadRequest()

# 返信用メッセージを作り，返す．
# 次の予定を返す:selectNextPlan()
# 指定された日の予定を返す:selectDatePlan(date):
# 今日の予定を返す:selectToDayPlan()
# 明日の予定を返す:selectTomorrowPlan()
# 明後日の予定を返す:selectDayAfterTomorrowPlan()
# 2つの日付間の予定を返す:selectBetweenDatePlan(startD, endD)
# 指定された日から1週間の予定を返す:selectWeekPlan(date)
# 今日から一週間の予定を返す:selectThisWeekPlan()
# 指定された月の予定を返す:selectMonthPlan(month)
# 今月の予定を返す:selectThisMonthPlan()
# 来月の予定を返す:selectNextMonthPlan()
def createMessage(event):
    text = event.message.text
    userid = event.source.user_id
    if text == 'こんにちは':
        return [TextSendMessage(text='こんにちは～')]
    elif text == '予定':
        return [TextSendMessage(text='予定を確認したい場合は，下のパネルをタップしてください．')]
    elif text == '陸上':
        return [TextSendMessage(text='我ら陸上競技部！')]
    elif ('次' in text) and ('予定' in text):
        template_message = createPlan(selectNextPlan())
        if template_message != None:
            return template_message
        else:
            return [TextSendMessage(text='次の予定はありません')]
    elif ('今月' in text) and ('予定' in text):
        template_message = createPlan(selectThisMonthPlan())
        if template_message != None:
            return template_message
        else:
            return [TextSendMessage(text='今月の予定はありません')]
    elif ('今週' in text) and ('予定' in text):
        template_message = createPlan(selectThisWeekPlan())
        if template_message != None:
            return template_message
        else:
            return [TextSendMessage(text='今週の予定はありません')]
    elif ('今日' in text) and ('予定' in text):
        template_message = createPlan(selectToDayPlan())
        if template_message != None:
            return template_message
        else:
            return [TextSendMessage(text='今日の予定はありません')]
    elif ('管理' in text) or (('設定' in text) and ('変' in text)):
        return [TextSendMessage(text='https://rktabot.herokuapp.com/\nにアクセスしてください．')]
    elif text == 'testCarousel':
        return [createCarouselMessage()]
    elif text == 'testCarousel2':
        return [createCarouselMessage2(),createCarouselMessage2()]
    elif text == 'testConfirm':
        return [createConfirmMessage()]
    elif text == 'てすと' or text == 'テスト':
        return [createButtonsMessage()]
    elif '定期配信' in text and ('中止' in text or '停止' in text or '止め' in text or 'とめる' in text or 'やめる' in text):
        sqlExe("UPDATE userinfo SET available = %s WHERE userid = %s", ['f',userid], False)
        return [TextSendMessage(text='定期予定配信の利用を中止しました．')]
    elif '定期配信' in text and ('開始' in text or '始め' in text or 'はじめ' in text):
        sqlExe("UPDATE userinfo SET available = %s WHERE userid = %s", ['t',userid], False)
        return [TextSendMessage(text='定期予定配信の利用を開始しました．')]
    elif 'ヘルプ' in text:
        return [
            TextSendMessage(text='【基本的な機能】\n下のパネルから，次の予定，今日の予定，今週の予定，今月の予定を確認することができます．'),
            TextSendMessage(text='【定期予定配信について】\n予定が近づいてきた場合，3日前の朝からお知らせします．\n朝の予定配信を中止したい場合は「定期配信停止」，\nまた，開始したい場合は「定期配信開始」と送信してください．'),
        ]
    else:
        return [TextSendMessage(text=text)]

#月：その週の予定を送信
#土日：予定を送信しない
#その他：3日前から予定を送信
def createRegulalyMessage():
    returnMessage = []
    #曜日判定
    today = datetime.date.today()
    week = today.strftime('%a')
    nowHour = datetime.datetime.now().hour
    if 7 != nowHour:
        return 'bad'
    elif week == 'Mon':
        #月曜日の処理
        returnMessage.append(TextSendMessage(text='【予定の定期配信】\nおはようございます。\n今週の予定をお知らせします。'))
        template_message = createPlan(selectThisWeekPlan())
        if template_message != None:
            for tm in template_message:
                returnMessage.append(tm)
        else:
            returnMessage.append(TextSendMessage(text='今週の予定はありません。\n今週も1週間，頑張ってください。'))
    else:
        #その他の処理
        returnMessage.append(TextSendMessage(text='【予定の定期配信】\nおはようございます。\n予定が近づいています。'))
        startD = today
        endD = today + datetime.timedelta(days=2)
        template_message = createPlan(selectBetweenDatePlan(startD, endD))
        if template_message != None:
            for tm in template_message:
                returnMessage.append(tm)
        else:
            return None
    return returnMessage

#データベースの定期的な更新
def regulalyUpdatePlan():
    today = datetime.date.today()
    yesterday = today - datetime.timedelta(1)
    #前日の予定の無効化
    sqlExe("UPDATE manager_post SET available=%s WHERE sdate=%s;", ['f', yesterday.strftime('%Y-%m-%d')], False)
    #1月1日に実行
    if today.month == 1 and today.day == 1:
        sqlExe("UPDATE manager_post SET sdate=make_date(CAST(EXTRACT(YEAR FROM current_date) AS INTEGER), CAST(EXTRACT(MONTH FROM sdate) AS INTEGER), CAST(EXTRACT(DAY FROM sdate) AS INTEGER));", ret=False)

# planを引数に，カルーセル（複数の場合もある）に変換して返す．
def createPlan(plan):
    return createCarouselPlanMessage(stringFormat(plan))

# リスト型plansを5件ずつに分けて処理し，複数のカルーセルをリストで返す．
def createCarouselPlanMessage(plans, plannum = 5):
    pl = len(plans)
    if pl==0:
        return None
    new_plans = []
    temp_plans = []
    for plan in plans:
        temp_plans.append(plan)
        if len(temp_plans) == 5:
            new_plans.append(createCarousel(temp_plans))
            temp_plans = []
            if len(new_plans) >= plannum-1:
                new_plans.append(TextSendMessage(text="表示しきれなかったので最新の"+str((plannum-1)*5)+"件を表示しました．"))
                break
    if len(temp_plans) != 0:
        new_plans.append(createCarousel(temp_plans))
    return new_plans

# タプル型plansからカルーセルを生成してテンプレート化して返す．最大5件
def createCarousel(plans):
    if len(plans) > 5:
        return None
    columns = []
    for plan in plans:
        columns.append(createColumn(plan))
    carousel_template = CarouselTemplate(columns)
    return TemplateSendMessage(
        alt_text = 'RKTAが予定を送信しました．',
        template = carousel_template
    )

# 辞書型planから，コラムを生成して返す．
def createColumn(plan):
    column = CarouselColumn(
        text=plan['text'],
        title=plan['title'],
        thumbnail_image_url = imageURL(),
        actions=[
            URITemplateAction(
                label='詳細を見る',
                uri='https://rktabot.herokuapp.com/stop/?id='+str(plan['id'])
            )
        ]
    )
    return column

# 適当な画像のURLを返す．
def imageURL():
    images = (
        'https://c.o16.co/1/gift/image/sc1-3145-300-2.jpg',
        'https://dnavi.drwallet.jp/wp-content/uploads/2015/10/401428927e7866f2a637820429da114d.jpg'
    )
    return random.choice(images)

# sqlselect.py
#import datetime
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
def sqlExe(exestr, elements = [], ret = True):
    conn = connect()
    cur = conn.cursor()
    if len(elements)==0:
        cur.execute(exestr)
    else:
        cur.execute(exestr, elements)
    if(ret):
        result = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    if(ret):
        return result

'''
                                    テーブル "public.manager_post"
       列       |            型            |                          修飾語
----------------+--------------------------+-----------------------------------------------------------
 id             | integer                  | not null default nextval('manager_post_id_seq'::regclass)
 title          | character varying(40)    | not null
 sdate          | date                     | not null
 starttime      | time without time zone   | not null
 endtime        | time without time zone   | not null
 content        | character varying(60)    | not null
 available      | boolean                  | not null
 created_date   | timestamp with time zone | not null
 published_date | timestamp with time zone |
インデックス:
    "manager_post_pkey" PRIMARY KEY, btree (id)
'''
# 次の予定を1次元配列で返す．
def selectNextPlan():
    nextPlan = sqlExe("SELECT * FROM manager_post WHERE available ORDER BY sdate ASC;")
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
    return []

# 指定された日の予定を2次元配列で返す．
def selectDatePlan(date):
    datePlan = sqlExe("SELECT * FROM manager_post WHERE sdate = %s AND available ORDER BY starttime ASC;", [date.strftime('%Y-%m-%d')])
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
    weekPlan = sqlExe("SELECT * FROM manager_post WHERE sdate >= %s AND sdate <= %s AND available ORDER BY sdate ASC;", [startD.strftime('%Y-%m-%d'),endD.strftime('%Y-%m-%d')])
    return weekPlan

# 指定された日から1週間の予定を2次元配列で返す．
def selectWeekPlan(date):
    startD = date
    endD = date + datetime.timedelta(7)
    return selectBetweenDatePlan(startD, endD)

# 今日から一週間の予定を2次元配列で返す．
def selectThisWeekPlan():
    return selectWeekPlan(datetime.date.today())

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

# ２次元リストの1次元を文字列の辞書型(カルーセルコラムに合う形)に変換し，2次元をリストにして返す．
# [{'title':'Y年M月D日\nタイトル', 'text':'H時M分～H時M分\n予定に関するメッセージ'}]
def stringFormat(plans):
    if plans == None:
        return None
    new_plans=[]
    for plan in plans:
        new_plan = {
            'id':plan[0],
            'title':plan[2].strftime('%Y{0}%m{1}%d{2}').format('年','月','日') +'\n'+ plan[1].strip(),
            'text' :plan[3].strftime('%H{0}%M{1}').format('時','分')+'～'
                    +plan[4].strftime('%H{0}%M{1}').format('時','分')+'\n'
                    +plan[5].strip()
        }
        new_plans.append(new_plan)
    return new_plans

# tests.py
def createCarouselMessage():
    carousel_template = CarouselTemplate(
        columns = [
            CarouselColumn(
                text='予定１',
                title='予定１に関するメッセージです',
                #thumbnail_image_url = 'https://c.o16.co/1/gift/image/sc1-3145-300-2.jpg',
                actions=[
                    PostbackTemplateAction(
                        label='postback1',
                        text='postback text1',
                        data='text1'
                    ),
                    MessageTemplateAction(
                        label='message1',
                        text='message text1'
                    ),
                    URITemplateAction(
                        label='Go to Google',
                        uri='http://www.google.co.jp'
                    )
                ]
            ),
            CarouselColumn(
                text='予定２',
                title='予定２に関するメッセージです',
                #thumbnail_image_url = 'https://c.o16.co/1/gift/image/sc1-3145-300-2.jpg',
                actions=[
                    PostbackTemplateAction(
                        label='postback2',
                        text='postback text2',
                        data='text2'
                    ),
                    MessageTemplateAction(
                        label='message2',
                        text='message text2'
                    ),
                    URITemplateAction(
                        label='Go to Yahoo',
                        uri='http://www.yahoo.co.jp'
                    )
                ]
            )
        ]
    )
    template_message = TemplateSendMessage(
        alt_text = 'これはテストカルーセルです．',
        template = carousel_template
    )
    return template_message

def createCarouselMessage2():
    carousel_template = CarouselTemplate(
        columns = [
            CarouselColumn(
                text='予定1に関するメッセージです．',
                title='予定１',
                thumbnail_image_url = 'https://dnavi.drwallet.jp/wp-content/uploads/2015/10/401428927e7866f2a637820429da114d.jpg',
                actions=[
                    PostbackTemplateAction(
                        label='postback1',
                        text='postback text1',
                        data='text1'
                    ),
                    MessageTemplateAction(
                        label='message1',
                        text='message text1'
                    ),
                    URITemplateAction(
                        label='Go to Google',
                        uri='http://www.google.co.jp'
                    )
                ]
            ),
            CarouselColumn(
                text='予定２に関するメッセージです．',
                title='予定２',
                thumbnail_image_url = 'https://c.o16.co/1/gift/image/sc1-3145-300-2.jpg',
                actions=[
                    PostbackTemplateAction(
                        label='postback2',
                        text='postback text2',
                        data='text2'
                    ),
                    MessageTemplateAction(
                        label='message2',
                        text='message text2'
                    ),
                    URITemplateAction(
                        label='Go to Yahoo',
                        uri='http://www.yahoo.co.jp'
                    )
                ]
            )
        ]
    )
    template_message = TemplateSendMessage(
        alt_text = 'これはテストカルーセルです．',
        template = carousel_template
    )
    return template_message

def createConfirmMessage():
    confirm_template = ConfirmTemplate(
        text='あなたはこの質問にYesと答える．．．',
        actions=[
            MessageTemplateAction(label='Yes', text='Yes...ハッ!?'),
            MessageTemplateAction(label='Yes!!', text='Yes!!...ハッ!?')
        ]
    )
    template_message = TemplateSendMessage(
        alt_text='これはテストコンファームです',
        template=confirm_template
    )
    return template_message

def createButtonsMessage():
    buttons_template = ButtonsTemplate(
        title='簡易テストフォーム',
        text='ボタンを押すことでテストを実施できますパァンッ!!',
        thumbnail_image_url = 'https://c.o16.co/1/gift/image/sc1-3145-300-2.jpg',
        actions=[
            MessageTemplateAction(
                label='テストカルーセル１',
                text='testCarousel'
            ),
            MessageTemplateAction(
                label='テストカルーセル２',
                text='testCarousel2'
            ),
            MessageTemplateAction(
                label='テストコンファーム',
                text='testConfirm'
            )
        ]
    )
    template_message = TemplateSendMessage(
        alt_text='これはテスト用カールセルです．',
        template=buttons_template
    )
    return template_message

