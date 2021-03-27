# -*- utf-8 -*-
import pandas as pd
import requests
from lxml import etree
from tqdm import tqdm
import urllib3
urllib3.disable_warnings()


def read_pc(pc_file):  # 读PC数据
    pcs = pd.read_excel(pc_file, sheet_name=0)
    pcs.drop([0], inplace=True)
    if 'Unnamed: 0' in pcs.columns.tolist():
        pcs.drop(['Unnamed: 0'], axis=1, inplace=True)
    pcs.reset_index(drop=True, inplace=True)
    return pcs


def process_name(string):  # 处理姓名字符串
    string = string.strip()
    string = ' '.join(string.split())  # 删去姓名之间的\xa0
    return string


def search_site(name):  # 检索
    add = "https://dblp.uni-trier.de/search?q=" + name
    root = requests.get(add, verify=False).content
    rootTree = etree.HTML(root)
    matches = rootTree.xpath(".//div[@id='completesearch-authors']//ul[@class='result-list']//a/@href")
    return ", ".join(matches).strip().strip(',')  # 以字符串形式返回一个或多个dblp-site


def fill_df(df, given_dict):
    for i in tqdm(range(0, len(df))):
        name = df.loc[i, 'name']
        if name in given_dict and str(given_dict[name]) != 'nan':  # 字典中有，则直接获取
            df.loc[i, 'dblp-site'] = given_dict[name]
        else:  # 字典中无，则检索
            site = search_site(name)
            df.loc[i, 'dblp-site'] = site
            given_dict.update({name: site})  # 检索完更新字典
    return df


if __name__ == '__main__':
    # 读入ALL表并处理
    raw = read_pc("nlp-PCs.xlsx")
    raw.iloc[:, 0] = raw.apply(lambda x: process_name(x['name']), axis=1)

    # # 读入已收集好的CCS表并处理
    # # 该步适用于已有人工处理好的数据，作为衔接
    # collected = pd.read_excel("C:\\Users\\DAIYQ\\Desktop\\作业\\大创\\作-pc\\ccs-pc_final.xlsx")
    # collected.iloc[:, 0] = collected.apply(lambda x: process_name(x['name']), axis=1)

    # 向原表中添加待填空列dblp-site
    raw.insert(1, 'dblp-site', '')

    # 已经收集的pc-site生成字典，根据姓名填入原表
    given = {}
    # given = collected.set_index('name')['dblp-site'].to_dict()  # 该步适用于已有人工处理好的数据，作为衔接
    output = fill_df(df=raw, given_dict=given)

    # 输出到csv
    output.to_csv("nlp_output.csv", sep=',', header=True, index=False)
