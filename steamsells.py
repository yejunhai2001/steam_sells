# 获取steam热销游戏信息
import re
import urllib.request
import urllib.error
import xlwt

# 规则
findgamename = re.compile(r'<span class=\\"title\\">(.*?)<\\/span>', re.S)
findreleasetime = re.compile(r'class=\\"col search_released responsive_secondrow\\">(.*?)<\\/div>')
findprice1 = re.compile(r'class=\\"col search_price_discount_combined responsive_secondrow(.*?)style=\\"clear: left;',
                        re.S)
findprice2 = re.compile(r'<strike>¥ (.*?)<\\/strike>', re.S)  # 有折扣时的原价
findprice3 = re.compile(r'responsive_secondrow\\">\\r\\n                        ¥ (.*?)                    <',
                        re.S)  # 无折扣时的原价
findprice4 = re.compile(r'<br>¥ (.*?)                    <', re.S)  # 折扣价格
findprice5 = re.compile(r'<span>-(.*?)<', re.S)  # 找折扣
findcomments = re.compile(r'"col search_reviewscore responsive_secondrow\\"(.*?)<div class=', re.S)
findcomments2 = re.compile(r'data-tooltip-html=\\"(.*?)。')
findgamelink = re.compile(r'href=\\"(.*?)\\"\\r\\n\\t\\t\\t')


def main():
    URl1 = "https://store.steampowered.com/search/results/?query&start="
    URl2 = "&count=50&dynamic_data=&sort_by=_ASC&snr=1_7_7_7000_7&filter=topsellers&os=win&infinite=1"
    # 爬取网页
    datalist = getData(URl1, URl2)
    savepath = "Steam热销游戏.xls"
    saveData(datalist, savepath)


def askURL(url):
    head = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36 Edg/90.0.818.56",
        "Accept-Language": "zh-CN,zh;q=0.9"
    }  # 用户代理
    request = urllib.request.Request(url, headers=head)
    html = ""
    try:
        response = urllib.request.urlopen(request)
        html = response.read().decode("utf-8")
        # print(html)
    except urllib.error.URLError as e:
        if hasattr(e, "code"):
            print(e.code)
        if hasattr(e, "reason"):
            print(e.reason)
    return html


def getData(URl1, URl2):
    dataList = []
    price_now = []  # 存折扣价格
    price_old = []  # 存原价
    price_rate = []  # 存降价的幅度
    comments = []

    html = ""
    for page in range(0, 6):
        html = html + askURL(URl1+str(page*50)+URl2)  # 获取网页源码
        html = str(html)

    # 对游戏信息处理
    gamename = re.findall(findgamename, html)  # 游戏名称
    time = re.findall(findreleasetime, html)  # 发售时间
    prices = re.findall(findprice1, html)  # 游戏价格
    for items in range(0, 300):  # 对价格处理
        a = re.findall(findprice2, prices[items])
        a = str(a).strip('\'\'[] ')
        b = re.findall(findprice3, prices[items])
        b = str(b).strip('\'\'[] ')
        if a != "":  # 无折扣，则运行
            price_old.append(a)
            price_now.append(str(re.findall(findprice4, prices[items])).strip('\'\'[]'))
        else:
            price_old.append(b)
            price_now.append(b)
        price_rate.append(str(re.findall(findprice5, prices[items])).strip('\'\'[]'))  ##

    comment = re.findall(findcomments, html)  # 评论
    for i in range(0, 300):
        comment[i] = str(re.findall(findcomments2, comment[i])).strip("''[]").replace("&lt;br&gt", "").replace(" ", "")
        comments.append(comment[i])

    links = re.findall(findgamelink, html)  # 游戏详情链接
    for i in range(0, 300):
        links[i] = str(links[i]).replace('\\', '')

    dataList.append(gamename)
    dataList.append(time)
    dataList.append(price_old)
    dataList.append(price_now)
    dataList.append(price_rate)
    dataList.append(comments)
    dataList.append(links)
    return dataList


def saveData(datalist, savepath):
    print("save....")
    book = xlwt.Workbook(encoding="utf-8")  # 创建workbook对象
    sheet = book.add_sheet('Steam热销游戏', 'w')  # 创建工作表
    col = ("游戏名称", "发布时间", "原价", "现价", "降价幅度", "评论", "游戏详情链接")
    for i in range(0, 7):
        sheet.write(0, i, col[i])  # 列名

    for i in range(0, 7):
        data = datalist[i]
        for j in range(0, 300):
            sheet.write(j + 1, i, data[j])  # 数据

    book.save(savepath)  # 保存


if __name__ == "__main__":  # 当程序执行时
    # 调用函数
    main()
    print("爬取完毕！")
