# encoding: utf-8

from copy import deepcopy
import datetime
import json
import os
import sys
import urllib.parse

def file2list(filepath):
    ret = []
    with open(filepath, encoding='utf8', mode='r') as f:
        ret = [line.rstrip('\n') for line in f.readlines()]
    return ret

def list2file(filepath, ls):
    with open(filepath, encoding='utf8', mode='w') as f:
        f.writelines(['{:}\n'.format(line) for line in ls] )

def str2file(filepath, s):
    with open(filepath, encoding='utf8', mode='w') as f:
        f.write(s)

def split_to_name_and_value(line):
    if line.find(':')==-1:
        return [None, None]
    # value は url など ':' を含むことがあるので split 回数は 1 回で.
    name, value = [x.strip() for x in line.split(':', 1)]
    return [name, value]

def basename2datetimeobj(basename):
    # 2019/01/17/070200
    year, month, day, timestr = basename.split('/')
    year = int(year)
    month = int(month)
    day = int(day)
    h, m, s = [int(timestr[i*2:i*2+2]) for i in range(3)]

    dt = datetime.datetime(year, month, day, h, m, s)
    return dt

def datetimeobj2datetimestr(dt):
    datestr = dt.strftime("%Y/%m/%d")
    timestr = dt.strftime("%H:%M:%S")

    weekdays = ['月','火','水','木','金','土','日']
    idx = dt.weekday()
    wdstr = weekdays[idx]

    return '{:}({:}) {:}'.format(datestr, wdstr, timestr)

def parse_arguments():
    import argparse

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description='',
    )
    parser.add_argument('-i', '--input-filename', required=True)
    parser.add_argument('-o', '--output-filename', required=True)
    parser.add_argument('-u', '--url', required=True)

    parsed_args = parser.parse_args()
    return parsed_args
args = parse_arguments()

MYFULLPATH = os.path.abspath(sys.argv[0])
MYDIR = os.path.dirname(MYFULLPATH)

target_filename = args.input_filename
save_filename   = args.output_filename
base_url        = args.url 

#   ...hatenablog.com
#   ...hatenablog.com/
# 末尾の / 有無を吸収する
if base_url[-1] == '/':
    base_url = base_url[0:-1]

lines = file2list(target_filename)

conf = {
    'url' : {
        'root'      : '{:}'.format(base_url),
        'entry'     : '{:}/entry/'.format(base_url),
        'category'  : '{:}/archive/category/'.format(base_url),
    },
}
data = {
    'title'    : None,
    'basename' : None,
    'categories' : [],
    'custom'   : {
        'full_url' : None,
        'full_category_urls' : [],
        'readable_datetime' : None,
    }
}

alldata = []

current_data = None

flag_do_skip_because_not_published = False

for i,line in enumerate(lines):
    stripped_line = line.strip()
    if len(stripped_line) == 0:
        continue
    firstchar = stripped_line[0]
    if firstchar == '-' or firstchar == '<':
        continue

    name, value = split_to_name_and_value(line)
    if name==None:
        continue
    if value==None:
        continue

    name = name.lower()
    if name=='title':
        flag_do_skip_because_not_published = False
        current_data = deepcopy(data)
        current_data['title'] = value
        continue
    # 次の記事が表れるまでスキップする.
    if flag_do_skip_because_not_published:
        continue

    if name=='basename':
        current_data['basename'] = value
        continue

    if name=='status' and value!='Publish':
        flag_do_skip_because_not_published = True
        continue

    if name=='category':
        current_data['categories'].append(value)
        continue

    if name=='image':
        # value は image full url だけど, 表示したらどうせ重たいから無視.
        continue

    if name=='body':
        # 特に絶対的な理由はないけど, 全体的な見通しの良さから
        # この辺で残りのデータを組み立てることにする.

        current_data['custom']['full_url'] = '{:}{:}'.format(
            conf['url']['entry'],
            current_data['basename']
        )

        if(len(current_data['categories']) == 0):
            # カテゴリー未設定時は
            # urllib.parse.quote で TypeError: quote() doesn't support 'encoding' for bytes
            # が出るので, カテゴリ未設定の旨を適当に設定しておく.
            current_data['categories'].append('__CATEGORY_NOT_SET__')
        for i,categoryname in enumerate(current_data['categories']):
            full_category_url = '{:}{:}'.format(
                conf['url']['category'],
                urllib.parse.quote(categoryname, encoding='utf-8')
            )
            current_data['custom']['full_category_urls'].append(full_category_url)

        basename = current_data['basename']
        dt = basename2datetimeobj(basename)
        dtstr = datetimeobj2datetimestr(dt)
        current_data['custom']['readable_datetime'] = dtstr

        alldata.append(current_data)

# 中間生成物
option_jsondump = {
    'ensure_ascii' : False,
    'indent' : 2,
}
outstr = json.dumps(alldata, **option_jsondump)
str2file('data.json', outstr)

# 仕分け
alldata_with_yyyymmkeys = {}
for i,data in enumerate(alldata):
    dtstr = data['custom']['readable_datetime']
    # 2019/01/
    # ^^^^^^^
    yyyymm = dtstr[0:7]
    
    if not yyyymm in alldata_with_yyyymmkeys:
        alldata_with_yyyymmkeys[yyyymm] = []

    alldata_with_yyyymmkeys[yyyymm].append(data)

outlines = []
for yyyymm_key in alldata_with_yyyymmkeys:
    alldata_with_onekey = alldata_with_yyyymmkeys[yyyymm_key]

    element_count = len(alldata_with_onekey)
    outlines.append('## {:} ({:}記事)'.format(
        yyyymm_key,
        element_count
    ))

    for data in alldata_with_onekey:
        # 一行に datetime と linktext を並べると
        # linktext が改行されて不格好なので, もう少し工夫する.
        outlines.append('- {:}'.format(
            data['custom']['readable_datetime'],
        ))
        for i,url in enumerate(data['custom']['full_category_urls']):
            text = data['categories'][i]
            outlines.append('  - カテゴリ: [{:}]({:})'.format(
                text,
                url,
            ))
        outlines.append('  - [{:}]({:})'.format(
            data['title'],
            data['custom']['full_url'],
        ))

    outlines.append('')
list2file(save_filename, outlines)
