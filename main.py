import csv
from pyg2plot import Plot
import urllib.request
import urllib.parse
import json
import os

tarCity = [["010", "Beijing"]]
APIKEY = "44cdd042045af4570f95e47e4484b01a"
KEYWORD = "自行车专卖店"
KEYDEC = urllib.parse.quote(KEYWORD)
CSVHEADERS = ["id", "pname", "cityname", "adname", "address", "category", "location"]
BRANDNAME = [
    ["捷安特", "GIANT"],
    ["美利达", "MEREIDA"],
    ["闪电", "SPECIALIZED", "specialized", "Specialized"],
    ["崔克", "TREK"],
    ["UUC", "uuc"],
    ["大行"],
    ["彩虹衫"],
    ["永久"],
    ["飞鸽"]
]

adname_counter = dict()
brand_counter = {"其他": 0}


def counter_opt(dat: list):
    if dat["adname"] in adname_counter.keys():
        adname_counter[dat["adname"]] += 1
    else:
        adname_counter[dat["adname"]] = 1
    flag = False
    for brandname in BRANDNAME:
        for name in brandname:
            if dat["name"].find(name) != -1:
                flag = True
                if brandname[0] in brand_counter.keys():
                    brand_counter[brandname[0]] += 1
                else:
                    brand_counter[brandname[0]] = 1
                break
    if flag == False:
        brand_counter["其他"] += 1


def url_open(url):
    req = urllib.request.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/38.0.2125.122 Safari/537.36')
    response = urllib.request.urlopen(req)
    html = response.read().decode('utf-8', 'ignore')
    return html


def get_urlList():
    urlList = []
    for city in tarCity:
        url = "http://restapi.amap.com/v3/place/text?key=" + APIKEY + "&keywords=" + KEYDEC + "&types=" + KEYDEC + "&city=" + \
              city[0] + "&children=1&extensions=all"
        urlList.append(url)
    return urlList


def total_gasStation():
    urlList = get_urlList()
    i = 0
    totalNum = 0
    cityListNo = []
    for url in urlList:
        html = url_open(url)
        target = json.loads(html)
        gsNo = int(target['count'])
        pageNo = divmod(gsNo, 20)[0] + 1 if divmod(gsNo, 20)[1] > 0 else divmod(gsNo, 20)[0]
        cityListNo.append([tarCity[i][0], tarCity[i][1], gsNo, pageNo])
        totalNum = totalNum + gsNo
        i = i + 1
    return cityListNo


def get_GSByCity():
    cityListNo = total_gasStation()
    cityUrlList = []
    for city in cityListNo:
        urlList = []
        for i in range(city[3]):
            url = "http://restapi.amap.com/v3/place/text?key=" + APIKEY + "&keywords=" + KEYDEC + "&types=" + KEYDEC + "&city=" + \
                  city[0] + "&children=1&offset=20&page=" + str(i + 1) + "&extensions=all"
            urlList.append(url)
        cityUrlList.append(urlList)
    return cityUrlList


def get_result():
    cityUrlList = get_GSByCity()
    allList = []
    for cityUrl in cityUrlList:
        cityPoisList = []
        for url in cityUrl:
            html = url_open(url)
            target = json.loads(html)
            pagePoisList = target['pois']
            cityPoisList.append(pagePoisList)
        cityPoisList = sum(cityPoisList, [])
        allList.append(cityPoisList)
    allList = sum(allList, [])
    ffff = []
    fffe = []
    i = 0
    for aList in allList:
        if aList['name'].find("电动车") == -1:
            try:
                dddd = aList['id'] + '\t' + aList['name'] + '\t' + aList['pname'] + '\t' + aList['cityname'] + '\t' + aList[
                    'adname'] + '\t' + aList['address'] + '\t' + aList['type'] + '\t' + aList['location'] + '\n'
                temp = [aList['id'], aList['name'], aList['pname'], aList['cityname'], aList['adname'], aList['address'], aList['type'], aList['location']]
                i = i + 1
                counter_opt(aList)
            except Exception as e:
                continue
            else:
                ffff.append(dddd)
                fffe.append(temp)

    os.getcwd()
    file_name = 'result.txt'
    f = open(file_name, 'w')
    f.writelines(ffff)
    f.close()
    print("beforesort")
    print(sorted(adname_counter.items(), key=lambda kv: (kv[1], kv[0])))
    print(sorted(brand_counter.items(), key=lambda kv: (kv[1], kv[0])))
    with open("result.csv", "w", newline='') as f:
        f_csv = csv.writer(f)
        f_csv.writerow(CSVHEADERS)
        f_csv.writerows(fffe)


def generate_pie():
    adnameList = sorted(adname_counter.items(), key=lambda kv: (kv[1], kv[0]))
    brandList = sorted(brand_counter.items(), key=lambda kv: (kv[1], kv[0]))

    adnameData = list()
    brandData = list()

    # for key in adname_counter.keys():
    #     adnameData.append({"type": key, "value": adname_counter[key]})
    # for key in brand_counter.keys():
    #     brandData.append({"type": key, "value": brand_counter[key]})

    for dat in adnameList:
        adnameData.append({"type": dat[0], "value": dat[1]})
    for dat in brandList:
        brandData.append({"type": dat[0], "value": dat[1]})

    adnamePie = Plot("Pie")
    brandPie = Plot("Pie")
    adnamePie.set_options({
        "appendPadding": 10,
        "data": adnameData,
        "angleField": "value",
        "colorField": "type",
        "radius": 0.75,
        "label": {
            "type": "spider",
            "labelHeight": 28,
            "content": '{name}\n{percentage}',
        },
        "interactions": [{"type": "element-active"}],
    })
    brandPie.set_options({
        "appendPadding": 10,
        "data": brandData,
        "angleField": "value",
        "colorField": "type",
        "radius": 0.75,
        "label": {
            "type": "spider",
            "labelHeight": 28,
            "content": '{name}\n{percentage}',
        },
        "interactions": [{"type": "element-active"}],
    })

    adnamePie.render("adnamePie.html")
    brandPie.render("brandPie.html")


if __name__ == '__main__':
    get_result()
    generate_pie()
