# hatenablog_pagelist
はてなブログの全記事一覧をつくるスクリプト(Markdown 記法限定)。

## 概要
はてなブログの全記事一覧をつくる。

- エクスポートしたブログデータを解析して全記事一覧の本文を生成し、
- これを固定ページの編集画面で貼り付ける

というアプローチで行う。

## デモ
以下は筆者ブログ stamemo の全記事一覧ページ。

- [記事一覧 - stamemo](http://stakiran.hatenablog.com/pagelist)

**作業時間は初回 5 分、以後の更新は 1 分で済む**。少なくとも手作業で苦労して書く手間からは解放される。

## システム要件
- Windows 7+
- Python 3.6+

## インストール
- 1: [Python](https://www.python.org/) を入手してインストール
- 2: 本リポジトリのファイル一式を入手

※Python や GitHub 自体の解説は割愛します

## 使い方
- 1: ブログ記事をエクスポートする
  - 例: `stakiran.hatenablog.com.export.txt`
- 2: generate.py と 1 を同じディレクトリ内に配置する
- 3: convert_sample.bat を適当な名前でコピーして、以下 3 箇所を編集する

```
set url=http://stakiran.hatenablog.com/
set inputfilename=stakiran.hatenablog.com.export.txt
set outputfilename=archive_stamemo.md
```

- 4: 3 を実行する

すると、outputfilename で指定したファイルが出力されているはず。

- 5: 4 で出力された本文を、はてなブログの固定ページ編集ボックスにコピペする

## 出力フォーマットをカスタマイズしたい
すみませんが generate.py を適当にいじってください……。

## License
[MIT License](LICENSE)

## Author
[stakiran](https://github.com/stakiran)
