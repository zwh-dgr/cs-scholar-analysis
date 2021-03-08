# -*- coding: utf-8 -*-
import requests
from lxml import etree
import json
import time
import urllib3
urllib3.disable_warnings()
import ssl


def main_crawler(add, path):  # returning a list of metadata dicts expected
    f = open(path, 'a', encoding='utf-8')
    metas = []

    root = requests.get(add, verify=False).content  # index页
    rootTree = etree.HTML(root)

    publ_index = rootTree.xpath(".//ul[@class='publ-list']")
    proceedingsls = []
    for publ in publ_index:
        each_pro_ls = publ.xpath("./li[@class='entry editor toc']")
        proceedingsls.append(each_pro_ls[0])  # 只采集long papers

    for proceedings in proceedingsls:  # 外层循环获取conf和proceedings信息
        proceedingsTitle = proceedings.xpath(".//span[@class='title' and @itemprop='name']/text()")
        proceedingsTitle = ''.join(proceedingsTitle)

        publisher = proceedings.xpath(".//span[@itemprop='publisher']/text()")
        publisher = ''.join(publisher)

        publYear = proceedings.xpath(".//span[@itemprop='datePublished']/text()")
        publYear = ''.join(publYear)

        isbn = proceedings.xpath(".//span[@itemprop='isbn']/text()")
        isbn = ''.join(isbn)

        # chairs = proceedings.xpath(".//span[@itemprop='author']")
        # chairsInfo = []
        # for chair in chairs:
        #     chairInfo = {}
        #     chairName = chair.xpath(".//span[@itemprop='name']/text()")
        #     chairName = ''.join(chairName)
        #
        #     chairTitle = chair.xpath(".//span[@itemprop='name']/@title")
        #     chairTitle = ''.join(chairTitle)
        #
        #     chairSite = chair.xpath(".//a[@itemprop='url']/@href")
        #     chairSite = ''.join(chairSite)
        #
        #     chairPage = author_page_crawler(chairSite)
        #
        #     res = affiliation_crawler(chairSite)
        #     chairAffiliation = res[0]
        #     chairOrcid = res[1]
        #
        #     chairInfo.update({'name': chairName, 'title': chairTitle, 'site': chairSite, 'page': chairPage,
        #                        'affiliation': chairAffiliation, 'orcid': chairOrcid})
        #     chairsInfo.append(chairInfo)

        contentsls = proceedings.xpath(".//a[@class='toc-link']/@href")
        for contents in contentsls:  # 中层循环获取每个volume的页面
            bunch = requests.get(contents, verify=False).content
            bunchTree = etree.HTML(bunch)

            # session
            headers = bunchTree.xpath(".//header[not(@id)]")
            publ_ls = bunchTree.xpath(".//ul[@class='publ-list']")
            sessions = []
            for header in headers:
                sessions.append(header.xpath("./h2/text()"))
            for i in range(0, len(publ_ls)):
                leafNode = publ_ls[i].xpath(".//li[@class='entry inproceedings']")

                if len(leafNode) == 0:  # 是proceedings的publ-list，跳过
                    continue

                if len(headers) == 0:  # 没有区分session
                    session = ''
                else:  # 有区分session
                    session = sessions[i - (len(publ_ls) - len(sessions))]
                    session = ''.join(session)

                for leaf in leafNode:  # 内层循环获取每篇文章
                    meta = {}

                    # Author
                    authors = leaf.xpath(".//cite/span[@itemprop='author']")
                    authorsInfo = []
                    for author in authors:
                        authorInfo = {}

                        name = author.xpath(".//span[@itemprop='name']/text()")  # 作者姓名
                        name = ''.join(name)

                        title = author.xpath(".//span[@itemprop='name']/@title")  # 作者标识名
                        title = ''.join(title)

                        site = author.xpath(".//a[@itemprop='url']/@href")  # 作者对应的dblp页面地址
                        site = ''.join(site)

                        authorPage = author_page_crawler(site)  # 作者个人主页

                        res = affiliation_crawler(site)
                        affiliation = res[0]  # 作者单位

                        orcid = res[1]  # 作者orcid

                        authorInfo.update({'name': name, 'title': title, 'site': site, 'page': authorPage,
                                           'affiliation': affiliation, 'orcid': orcid})
                        authorsInfo.append(authorInfo)

                    # Paper
                    paperTitle = leaf.xpath(".//span[@class='title']/text()")
                    paperTitle = ''.join(paperTitle)  # 论文标题

                    paperDate = leaf.xpath(".//meta[@itemprop='datePublished']/@content")
                    paperDate = ''.join(paperDate)  # 发表年

                    paperPagination = leaf.xpath(".//span[@itemprop='pagination']/text()")
                    paperPagination = ''.join(paperPagination)  # 所在页数范围

                    # paperGenre = leaf.xpath(".//meta[@property='genre']/@content")
                    # paperGenre = ''.join(paperGenre)  # 学科

                    meta.update({
                        'title': paperTitle,
                        'datePublished': paperDate,
                        'pagination': paperPagination,
                        'authorsInfo': authorsInfo,
                        'session': session,
                        'proceedingsTitle': proceedingsTitle,
                        'publisher': publisher,
                        'publYear': publYear,
                        'isbn': isbn})
                    # meta.update({
                    #             'title': paperTitle,
                    #             'datePublished': paperDate,
                    #             'pagination': paperPagination,
                    #             'genre': paperGenre,
                    #             'authorsInfo': authorsInfo,
                    #             'session': session,
                    #             'proceedingsTitle': proceedingsTitle,
                    #             'publisher': publisher,
                    #             'publYear': publYear,
                    #             'isbn': isbn,
                    #             'chairsInfo': chairsInfo})
                    print(meta)
                    write2json(meta, f)
    f.close()
    return metas


def affiliation_crawler(dblp_site):
    page = requests.get(dblp_site, verify=False).content
    pageTree = etree.HTML(page)
    affTag = pageTree.xpath(".//li[@itemprop='affiliation']")
    orcidTag = pageTree.xpath(".//li[@class='orcid drop-down']")
    affiliation = ''
    orcid = ''
    if len(affTag) == 1:  # dblp页面直接给出
        affiliation = affTag[0].xpath(".//span[@itemprop='name']/text()")
        affiliation = ''.join(affiliation)  # return a string
    elif len(affTag) > 1:
        affiliation = []
        for aff in affTag:
            affelem = aff.xpath(".//span[@itemprop='name']/text()")
            affelem = ''.join(affelem)
            affiliation.append(affelem)  # return a list
    elif len(orcidTag) != 0:
        if len(orcidTag[0].xpath(".//em[@class='warning']")) != 0:  # disambiguation不采集
            affiliation = ''
        else:
            orcid = orcidTag[0].xpath(".//ul/li/a/text()")[0].strip('"')
            # orcidUrl = orcidTag[0].xpath(".//ul/li/a/@href")
            # orcidUrl = ''.join(orcidUrl)
            # orcidPage = requests.get(orcidUrl, verify=False).content
            # orcidTree = etree.HTML(orcidPage)
            # affPath = orcidTree.xpath(".//affiliation-ng2//ul[@id='body-employment-list']//h3")
            # for path in affPath:
            #     affiliation = path.xpath("string(.)")
            #     if len(affiliation) <= 1:
            #         affiliation = ''.join(affiliation)
    return affiliation, orcid


def author_page_crawler(dblp_site):
    page = requests.get(dblp_site, verify=False).content
    pageTree = etree.HTML(page)
    visitTag = pageTree.xpath(".//li[@class='visit drop-down']")
    author_page = ''
    if len(visitTag) != 0:
        author_page = visitTag[0].xpath(".//a[contains(text(), \"author's page\")]/@href")
        author_page = ''.join(author_page)
    return author_page


def write2json(meta, path):
    meta_json = json.dumps(meta, ensure_ascii=False)
    path.write(meta_json+'\n')


if __name__ == '__main__':
    start = time.time()
    ssl._create_default_https_context = ssl._create_unverified_context
    addls = ['https://dblp.uni-trier.de/db/conf/acl/', 'https://dblp.uni-trier.de/db/conf/naacl/',
             'https://dblp.uni-trier.de/db/conf/emnlp/', 'https://dblp.uni-trier.de/db/conf/coling/']  # 要爬取的DBLP会议页面
    conf_name = ['acl', 'naacl', 'emnlp', 'coling']  # 要爬取的会议名称
    # addls = ['https://dblp.uni-trier.de/db/conf/uss/']
    # conf_name = ['uss']
    for i in range(0, len(addls)):
        file_name = './' + conf_name[i] + '.json'
        main_crawler(addls[i], file_name)
        time.sleep(5)
    end = time.time()
    print("执行完成，共用时{0}s".format(end - start))
