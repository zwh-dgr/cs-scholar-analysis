# cs-scholar-analysis
大创项目-杰出学者评价

## data

### papers

包含五个文件夹：

- ai：人工智能领域
- hci：人机交互领域
- ir：信息检索领域
- nlp：自然语言处理领域
- security：安全领域

分别放置以上五个领域的json格式会议论文数据。

数据字段如下：

|    **字段名**    | **数据含义** |
| :--------------: | :----------: |
|      title       |   论文标题   |
|  datePublished   |  论文出版年  |
|   authorsInfo    |   作者信息   |
|     session      |   分卷主题   |
| proceedingsTitle | 会议记录标题 |
|    publisher     |   出版机构   |
|     publYear     | 论文集出版年 |
|       isbn       | 论文集ISBN号 |

其中`authorsInfo`是一个嵌套json列表，数据字段如下：

| **字段名**  |  **数据含义**   |
| :---------: | :-------------: |
|    name     |    作者姓名     |
|    title    | DBLP作者标识名  |
|    site     |   DBLP作者页    |
|    page     |  作者个人主页   |
| affiliation |    作者单位     |
|    orcid    | 作者ORCID标识ID |

### security-PC

安全领域的PC数据，包含两个xlsx文件：

|       **文件名**       |                         **数据**                         |
| :--------------------: | :------------------------------------------------------: |
|   security-PCs.xlsx    |              从各届会议官网中采集到的PC名单              |
| security-pc-final.xlsx | 补充PC的DBLP页链接字段后的数据（未进行机构与国别的清洗） |

### nlp-PC

自然语言处理领域的PC，包含三个xlsx文件：

|      文件名       |                        数据                        |
| :---------------: | :------------------------------------------------: |
|      pc.xlsx      |    从各届会议官网中采集到的PC名单，包含四个会议    |
|   nlp-PCs.xlsx    | 从pc.xlsx中选择ACL和EMNLP两个会议2011-2020年的数据 |
| nlp-pc-final.xlsx |      补充PC的DBLP页链接字段后的数据（进行中）      |

其中，`nlp-pc-final.xlsx`的`dblp-site`字段已经通过脚本填充检索结果，到第480行之前已经人工筛选、更改为正确的DBLP页，第480行之后仍只是自动检索结果。大量数据的`affiliation`（机构）与`location`（国别）字段没有补充。

## scripts

- crawler.py与crawler-new.py：爬取DBLP会议论文数据的脚本
- crawler-site.py：根据PC姓名，实现自动搜索DBLP作者页并将粗结果写入文件的脚本