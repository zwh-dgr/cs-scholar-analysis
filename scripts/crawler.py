import requests
# from bs4 import BeautifulSoup
from lxml import etree  # BeautifulSoup和lxml都既可以解析HTML也可以解析XML
import pandas as pd
import time


def crawler(add):  # returning a list of metadata lists expected
    # gc_pc = []  # General and Program Chairs
    # tc = []  # Tutorial Chairs
    # srwc = []  # Student Research Workshop Chairs
    # dc = []  # Demonstration Chairs

    scholarMetas = []
    paperMetas = []
    conferenceMetas = []

    root = requests.get(add).content  # index页
    # res.encoding = 'utf-8'
    rootTree = etree.HTML(root)
    confls = rootTree.xpath("//a[@class='toc-link']/@href")  # 获取每次会议的url

    # papers和scholar信息
    for conf in confls:  # 每个论文集合（volume）
        bunch = requests.get(conf).content
        bunchTree = etree.HTML(bunch)
        leafNode = bunchTree.xpath("//li[@class='entry inproceedings']")

        for leaf in leafNode:  # 每篇文章
            # Author
            authors = leaf.xpath(".//cite/span[@itemprop='author']")
            authorName_string = ""
            for author in authors:
                authorMeta = {}

                authorTitle = author.xpath(".//span[@itemprop='name']/@title")
                authorTitle = ''.join(authorTitle)

                authorSite = author.xpath(".//a[@itemprop='url']/@href")  # 作者对应的DBLP页面地址
                authorSite = ''.join(authorSite)

                authorName = author.xpath(".//span[@itemprop='name']/text()")  # 作者姓名
                authorName = ''.join(authorName)

                authorName_string = authorName_string + authorName + ";"  # 拼接成字符串

                authorMeta.update({'name': authorName, 'title': authorTitle, 'site': authorSite})
                scholarMetas.append(authorMeta)  # 添加到scholar信息中

            # Paper
            paperMeta = {}

            paperTitle = leaf.xpath(".//span[@class='title']/text()")
            paperTitle = ''.join(paperTitle)  # 论文标题

            paperDate = leaf.xpath(".//meta[@itemprop='datePublished']/@content")
            paperDate = ''.join(paperDate).strip()  # 发表年

            paperPagination = leaf.xpath(".//span[@itemprop='pagination']/text()")
            paperPagination = ''.join(paperPagination)  # 所在页数范围

            paperGenre = leaf.xpath(".//meta[@property='genre']/@content")
            paperGenre = ''.join(paperGenre)  # 学科

            paperAuthor = authorName_string.strip(';')  # 论文作者

            paperMeta.update({'title': paperTitle, 'datePublished': paperDate, 'pagination': paperPagination,
                              'genre': paperGenre, 'author': paperAuthor})
            paperMetas.append(paperMeta)

    # Conference信息
    confNode = rootTree.xpath("//div[@id='main']//h2")
    # Chairs
    confIndexls = rootTree.xpath(".//ul[@class='publ-list']")
    conf_chairs = []
    for confIndex in confIndexls:
        editorls = confIndex.xpath(".//li[@class='entry editor toc']")
        chairName_string = ""
        publYear = ""
        for entry_editor in editorls:
            chairs = entry_editor.xpath(".//span[@itemprop='author']")
            publYear = entry_editor.xpath(".//span[@itemprop='datePublished']/text()")[0]
            publYear = ''.join(publYear)  # 出版年作为标识
            for chair in chairs:
                chairName = chair.xpath(".//span[@itemprop='name']/text()")
                chairName = ''.join(chairName)  # Chairs姓名
                chairName_string = chairName_string + chairName + ";"  # 拼接成字符串
        conf_chairs.append([chairName_string.strip(';'), publYear])  # 每个子列表含有Chairs姓名和作为标识的publYear

    # Conference
    for j in range(0, len(confNode)):
        confMeta = {}
        confInfo = confNode[j].xpath("./text()")

        confYear = confNode[j].xpath("./@id")
        confYear = ''.join(confYear)  # 会议年份

        confInfols = ''.join(confInfo).split(':')  # 切割h2标题栏的会议信息
        confName = confInfols[0].strip()  # 会议名称
        if (len(confInfols) == 1):
            confLoc = ''
        else:
            confLoc = confInfols[1].strip()
        confLoc = confLoc.split(', ')
        confLoc = ' - '.join(confLoc).strip()  # 会议地址

        confChairsFound = find_index(conf_chairs, 1, confYear)  # 匹配每个子列表中的publYear，其索引为1
        if confChairsFound is not None:
            confMeta.update({'name': confName, 'location': confLoc, 'year': confYear,
                             'chairs': conf_chairs[confChairsFound][0]})
        else:
            confMeta.update({'name': confName, 'location': confLoc, 'year': confYear, 'chairs': ''})
        conferenceMetas.append(confMeta)  # 添加到conference信息中
    return [scholarMetas, paperMetas, conferenceMetas]


def find_index(nestedls, bottom_index, target):  # 以出版年作为标识找到对应的Chairs
    for subls in nestedls:
        if subls[bottom_index] == target:
            return nestedls.index(subls)
        else:
            continue
    return None


def write2csv(meta, file_name):  # 输出到csv文件
    meta_df = pd.DataFrame(meta)
    meta_df.to_csv(file_name)


if __name__ == '__main__':
    addls = ['https://dblp.uni-trier.de/db/conf/acl/', 'https://dblp.uni-trier.de/db/conf/naacl/',
            'https://dblp.uni-trier.de/db/conf/emnlp/', 'https://dblp.uni-trier.de/db/conf/coling/']  # 要爬取的DBLP会议页面
    conf_name = ['acl', 'naacl', 'emnlp', 'coling']  # 要爬取的会议名称
    info_name = ['scholar', 'paper', 'conference']  # 输出到三张表

    for i in range(0, len(addls)):
        metas = crawler(addls[i])
        file_name = ""
        for j in range(0, len(metas)):
            file_name = conf_name[i] + '-' + info_name[j] + '.csv'
            write2csv(metas[j], file_name)
        time.sleep(5)
