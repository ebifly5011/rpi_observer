# Raspberry Pi Observer

<!-- @import "[TOC]" {cmd="toc" depthFrom=2 depthTo=2 orderedList=false} -->

<!-- code_chunk_output -->

- [概要](#概要)
- [開発環境](#開発環境)
- [RaspberryPi のセットアップ](#raspberrypi-のセットアップ)
- [rpid の利用](#rpid-の利用)
- [Issue](#issue)

<!-- /code_chunk_output -->

## 概要

RaspberryPiを用いて環境制御を行うシステム．
小規模農業ハウス模型への実装を予定．

### システム概要図

![figures-俯瞰図-2](https://user-images.githubusercontent.com/62172470/127176647-f7cdefb7-3c4b-42f0-b95d-ee81f550cb64.png)

### 回路図

![figures-回路図](https://user-images.githubusercontent.com/62172470/127176549-fb8077ac-c0f8-4b65-9539-f5b0a9aca886.png)

### 内容物（rpid/以下）

- hardware/*：各種センサとの通信用
- setup/*：RaspberryPiの環境構築用
- software/db/*：各種DBとのデータ送受信
- software/html/*：操作用Webページに用いるhtml，css（Bootstrap5使用）
- software/*.py：後述
- main.py：実行用

#### software/*.pyについて

- controller.py：環境情報をもとにGPIOの出力変更．操作用ページのUI設計．
- database.py：software/db/*.pyに対して，各DBとのアクセス方法を統一する役割．（現在はDBを全てPrometheusで賄っているのでほぼ未使用）
- discord.py：Discord（チャットツール）にメッセージを送信する．
- flask_.py：素のFlaskは扱いづらかったため，threadingと併用したものを再定義．
- logger.py：各センサから読み取った値をdatabase.pyを通じてロギングする．
- reporter.py：loggerで読み取った値，controllerの制御値をdiscordにて報告する．
- types.py：型定義など．入力補完を充実させる目的にも使用．

### 今後の展望

- 電磁弁を用いたCO2濃度の自動制御
- 養液のpH管理
- 水量不足の検知

## 開発環境

|    使用機器等     |                     詳細                      |
| :---------------: | :-------------------------------------------: |
|        PC         |          MacBook Pro (15-inch, 2016)          |
|     PC の OS      |              macOS Big Sur 11.4               |
|   Raspberry Pi    |          Raspberry Pi 3 Model B V1.2          |
| RaspberryPi の OS | Raspberry Pi OS (32-bit) Released: 2021-05-07 |
| 温湿度センサ | Aosong Guangzhou Electronics Co., Ltd. AM2302 (DHT22) |
| CO2濃度センサ | Senseair K30 |
| リレーモジュール | 秋月電子通商 AE-SH-SSR-8A-KIT |

## RaspberryPi のセットアップ

### OS の書き込み

[Raspberry Pi Imager](https://www.raspberrypi.org/software/)を用いて Raspberry Pi OS を microSD カードに書き込む．

### SSH の有効化

下記のコマンドを実行し，microSD カード内にファイル`ssh`を作成する．
`/Volumes/boot/`の部分は環境に応じて書き換えること．

```Mac:zsh
rpi_observer % touch /Volumes/boot/ssh
```

### Wi-Fi 設定

`wpa_supplicant.conf.sample`を参考に，ファイル`wpa_supplicant.conf`を作成する．
`priority`の数値が大きいほど優先して接続される．
下記のコマンドを実行し，作成した`wpa_supplicant.conf`を microSD にコピーする．

```Mac:zsh
rpi_observer % cp wpa_supplicant.conf /Volumes/boot/wpa_supplicant.conf
```

### RaspberryPi の起動・SSH 接続

microSD カードを Mac から取り出し，RaspberryPi に挿入し，起動する．
PC は`wpa_supplicant.conf`に記入したネットワークに接続しておく．
下記のコマンドを実行し，`pi`ユーザーとして RaspberryPi に SSH 接続する．
デフォルトのパスワードは`raspberry`．

```Mac:zsh
rpi_observer % ssh pi@raspberrypi.local
```

下記のコマンドを実行し，`pi`ユーザーのパスワードを変更する．

```Raspberry Pi:bash
~ $ passwd pi
Changing password for pi.
Current password: raspberry
New password: <新しいパスワード>
Retype new password: <パスワード確認>
```

ホスト名を`rpiobserver`に変更し，再起動する．
`1 System Options` -> `S4 Hostname`

```Raspberry Pi:bash
~ $ sudo raspi-config
```

### 公開鍵認証（RSA 暗号による認証）

下記のコマンドを実行し，公開鍵と秘密鍵を生成する．

```Mac:zsh
rpi_observer % ssh-keygen
Generating public/private rsa key pair.
Enter file in which to save the key (/Users/hogeuser/.ssh/id_rsa): rpi_observer_rsa
Enter passphrase (empty for no passphrase): <パスワード(入力せずEnter)>
Enter same passphrase again: <パスワード確認(入力せずEnter)>
```

下記のコマンドを実行し，RaspberryPi に公開鍵を送付する．

```Mac:zsh
rpi_observer % ssh-copy-id -i rpi_observer_rsa.pub pi@rpiobserver.local
```

下記のコマンドを実行し，公開鍵認証によって RaspberryPi にログインする．

```Mac:zsh
rpi_observer % ssh -i rpi_observer_rsa pi@rpiobserver.local
```

### 各種アップデート

下記のコマンドを実行し，アップデートを行う．
`upgrade`は非常に時間がかかる場合があるので注意．

```Raspberry Pi:bash
~ $ sudo apt -y update
~ $ sudo apt -y upgrade
```

### タイムゾーンと言語の変更

下記のコマンドを実行し，日本仕様にする．

```Raspberry Pi:bash
~ $ sudo raspi-config nonint do_change_locale ja_JP.UTF-8
~ $ sudo raspi-config nonint do_change_timezone Asia/Tokyo
```

## rpid の利用

### 導入

ラズパイにディレクトリ`rpid`をコピーする．

```Mac:zsh
rpi_observer % scp -ri rpi_observer_rsa rpid pi@rpiobserver.local
```

Python環境のセットアップを実施する．

```Raspberry Pi:bash
~ $ source /home/pi/rpid/setup/setup_python.sh
```

### 実行

回路図通りに結線する．

![figures-回路図](https://user-images.githubusercontent.com/62172470/127176549-fb8077ac-c0f8-4b65-9539-f5b0a9aca886.png)

`main.py`を実行する．

```Raspberry Pi:bash
(.venv)rpid $ nohup python software/main.py &
```

## Issue

Ambient へのアクセス間隔が 5 秒程度必要．
読み出し優先，書き込みデータ破棄等の処理を要追加．

学内 LAN への外部からのアクセスが不可能．
学外 DB へのデータ書き出し等必要．

カメラ利用時のデータ圧迫．
適切な撮影間隔の検討，データ破棄等の処理を要追加．

水位検知用の端子が破損．
端子には青い物質が付着．原因不明．

データ欠損等のエラー処理．
