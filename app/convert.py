import sys
import os
import csv
import logging
from pathlib import Path
from xml.etree.ElementTree import parse, Element

# ログの設定
logging.basicConfig(filename='xml_to_csv_conversion.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def setup_paths(input_path: str, output_path: str) -> tuple:
    """入力と出力のパスをPath objectsとして設定し、検証します。"""
    ipt_path = Path(input_path)
    opt_path = Path(output_path)

    if not ipt_path.exists():
        raise FileNotFoundError(f"入力パス '{input_path}' が見つかりません。")
    if not opt_path.exists():
        opt_path.mkdir(parents=True, exist_ok=True)
        logging.info(f"出力ディレクトリ '{output_path}' を作成しました。")

    return ipt_path, opt_path

def parse_xml(xml_file: Path) -> Element:
    """XMLファイルをパースしてルート要素を返します。"""
    try:
        return parse(xml_file).getroot()
    except Exception as e:
        logging.error(f"ファイル '{xml_file.name}' のXML解析エラー: {str(e)}")
        raise

def extract_data(elem: Element) -> list:
    """XML要素から必要なデータを抽出します。"""
    
    list_in = []
    namespaces = {'jp': 'http://www.jpo.go.jp'}

    # 格納
    list_in.append(str(elem.get('kind-of-jp'))) # 公開種別（jp）
    list_in.append(str(elem.get('kind-of-st16'))) # 公開種別（st16）
    list_in.append(str(elem.findtext('.//publication-reference/document-id/kind'))) # 公開種別（日本語）
    list_in.append(str(elem.findtext('.//publication-reference/document-id/doc-number'))) # 公開番号
    list_in.append(str(elem.findtext('.//publication-reference/document-id/date'))) # 公開日
    list_in.append(str(elem.findtext('.//application-reference/document-id/doc-number'))) # 出願番号
    list_in.append(str(elem.findtext('.//application-reference/document-id/date'))) # 出願日
    list_in.append(str(elem.findtext('.//invention-title'))) # 発明の名称
    list_in.append(str(elem.findtext('.//classification-ipc/main-clsf'))) # 国際特許分類(IPC)
    list_in.append(str(elem.findtext('.//number-of-claims'))) # 請求項の数
    list_in.append(str(elem.findtext('.//jp:total-pages', namespaces={'jp':'http://www.jpo.go.jp'}))) # 全頁数
    #FI ここはappendでスペース入れないとスペース入れてくれない
    list_in.append("      ".join((elem.find('.//classification-national')).itertext()).replace('JP', '').strip().replace('\n', '')) if elem.find('.//classification-national') != None else list_in.append('None')
    #テーマコード
    list_in.append("".join((elem.find('.//jp:theme-code-info', namespaces={'jp': 'http://www.jpo.go.jp'}).itertext())).replace('\n', '').strip()) if elem.find('.//jp:f-term-info', namespaces={'jp': 'http://www.jpo.go.jp'}) != None else list_in.append('None')
    # Fターム（一部Fタームの記載の無い公開特許公報（A) があるのでエラーを吐き出す. replaceメソッドで改行文字を削除している．よくわからないけどスペースが6つついている
    list_in.append("".join((elem.find('.//jp:f-term-info', namespaces={'jp': 'http://www.jpo.go.jp'}).itertext())).replace('\n', '').strip()) if elem.find('.//jp:f-term-info', namespaces={'jp': 'http://www.jpo.go.jp'}) != None else list_in.append('None')
    # 出願人情報
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/applicant[@sequence="1"]/addressbook[@lang="ja"]/registered-number', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/applicant[@sequence="1"]/addressbook[@lang="ja"]/name', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/applicant[@sequence="1"]/addressbook[@lang="ja"]/address/text', namespaces={'jp':'http://www.jpo.go.jp'})))
    
    # 2021/03/13 fixed applicant-agents sequence number to 1 (not 2, 3, ...5)
    # list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="2"]/applicant[@sequence="2"]/addressbook[@lang="ja"]/registered-number', namespaces={'jp':'http://www.jpo.go.jp'})))
    # list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="2"]/applicant[@sequence="2"]/addressbook[@lang="ja"]/name', namespaces={'jp':'http://www.jpo.go.jp'})))
    # list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="2"]/applicant[@sequence="2"]/addressbook[@lang="ja"]/address/text', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/applicant[@sequence="2"]/addressbook[@lang="ja"]/registered-number', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/applicant[@sequence="2"]/addressbook[@lang="ja"]/name', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/applicant[@sequence="2"]/addressbook[@lang="ja"]/address/text', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/applicant[@sequence="3"]/addressbook[@lang="ja"]/registered-number', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/applicant[@sequence="3"]/addressbook[@lang="ja"]/name', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/applicant[@sequence="3"]/addressbook[@lang="ja"]/address/text', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/applicant[@sequence="4"]/addressbook[@lang="ja"]/registered-number', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/applicant[@sequence="4"]/addressbook[@lang="ja"]/name', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/applicant[@sequence="4"]/addressbook[@lang="ja"]/address/text', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/applicant[@sequence="5"]/addressbook[@lang="ja"]/registered-number', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/applicant[@sequence="5"]/addressbook[@lang="ja"]/name', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/applicant[@sequence="5"]/addressbook[@lang="ja"]/address/text', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/applicant[@sequence="6"]/addressbook[@lang="ja"]/registered-number', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/applicant[@sequence="6"]/addressbook[@lang="ja"]/name', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/applicant[@sequence="6"]/addressbook[@lang="ja"]/address/text', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/applicant[@sequence="7"]/addressbook[@lang="ja"]/registered-number', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/applicant[@sequence="7"]/addressbook[@lang="ja"]/name', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/applicant[@sequence="7"]/addressbook[@lang="ja"]/registered-number', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/applicant[@sequence="8"]/addressbook[@lang="ja"]/name', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/applicant[@sequence="8"]/addressbook[@lang="ja"]/registered-number', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/applicant[@sequence="8"]/addressbook[@lang="ja"]/name', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/applicant[@sequence="9"]/addressbook[@lang="ja"]/registered-number', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/applicant[@sequence="9"]/addressbook[@lang="ja"]/name', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/applicant[@sequence="9"]/addressbook[@lang="ja"]/registered-number', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/applicant[@sequence="10"]/addressbook[@lang="ja"]/name', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/applicant[@sequence="10"]/addressbook[@lang="ja"]/registered-number', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/applicant[@sequence="10"]/addressbook[@lang="ja"]/name', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/applicant[@sequence="11"]/addressbook[@lang="ja"]/registered-number', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/applicant[@sequence="11"]/addressbook[@lang="ja"]/name', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/applicant[@sequence="11"]/addressbook[@lang="ja"]/registered-number', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/applicant[@sequence="12"]/addressbook[@lang="ja"]/name', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/applicant[@sequence="12"]/addressbook[@lang="ja"]/registered-number', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/applicant[@sequence="12"]/addressbook[@lang="ja"]/name', namespaces={'jp':'http://www.jpo.go.jp'})))
    # 代理人情報
    # 2021/03/13 fixed applicant-agents sequence number to 1 (not 2, 3, ...5)
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/agent[@sequence="1"][@jp:kind="representative"]/addressbook/registered-number', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/agent[@sequence="1"][@jp:kind="representative"]/addressbook/name', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/agent[@sequence="2"][@jp:kind="representative"]/addressbook/registered-number', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/agent[@sequence="2"][@jp:kind="representative"]/addressbook/name', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/agent[@sequence="3"][@jp:kind="representative"]/addressbook/registered-number', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/agent[@sequence="3"][@jp:kind="representative"]/addressbook/name', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/agent[@sequence="4"][@jp:kind="representative"]/addressbook/registered-number', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/agent[@sequence="4"][@jp:kind="representative"]/addressbook/name', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/agent[@sequence="5"][@jp:kind="representative"]/addressbook/registered-number', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/agent[@sequence="5"][@jp:kind="representative"]/addressbook/name', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/agent[@sequence="6"][@jp:kind="representative"]/addressbook/registered-number', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/agent[@sequence="6"][@jp:kind="representative"]/addressbook/name', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/agent[@sequence="7"][@jp:kind="representative"]/addressbook/registered-number', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/agent[@sequence="7"][@jp:kind="representative"]/addressbook/name', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/agent[@sequence="8"][@jp:kind="representative"]/addressbook/registered-number', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/agent[@sequence="8"][@jp:kind="representative"]/addressbook/name', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/agent[@sequence="9"][@jp:kind="representative"]/addressbook/registered-number', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/agent[@sequence="9"][@jp:kind="representative"]/addressbook/name', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/agent[@sequence="10"][@jp:kind="representative"]/addressbook/registered-number', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/agent[@sequence="10"][@jp:kind="representative"]/addressbook/name', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/agent[@sequence="11"][@jp:kind="representative"]/addressbook/registered-number', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/agent[@sequence="11"][@jp:kind="representative"]/addressbook/name', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/agent[@sequence="12"][@jp:kind="representative"]/addressbook/registered-number', namespaces={'jp':'http://www.jpo.go.jp'})))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/agent[@sequence="12"][@jp:kind="representative"]/addressbook/name', namespaces={'jp':'http://www.jpo.go.jp'})))
    # 発明者情報
    # 2021/03/13 fixed applicant-agents sequence number to 1 (not 2, 3, ...5)
    list_in.append(str(elem.findtext('.//parties/inventors/inventor[@sequence="1"]/addressbook/name')))
    list_in.append(str(elem.findtext('.//parties/inventors/inventor[@sequence="1"]/addressbook/address/text')))
    list_in.append(str(elem.findtext('.//parties/inventors/inventor[@sequence="2"]/addressbook/name')))
    list_in.append(str(elem.findtext('.//parties/inventors/inventor[@sequence="2"]/addressbook/address/text')))
    list_in.append(str(elem.findtext('.//parties/inventors/inventor[@sequence="3"]/addressbook/name')))
    list_in.append(str(elem.findtext('.//parties/inventors/inventor[@sequence="3"]/addressbook/address/text')))
    list_in.append(str(elem.findtext('.//parties/inventors/inventor[@sequence="4"]/addressbook/name')))
    list_in.append(str(elem.findtext('.//parties/inventors/inventor[@sequence="4"]/addressbook/address/text')))
    list_in.append(str(elem.findtext('.//parties/inventors/inventor[@sequence="5"]/addressbook/name')))
    list_in.append(str(elem.findtext('.//parties/inventors/inventor[@sequence="5"]/addressbook/address/text')))
    list_in.append(str(elem.findtext('.//parties/inventors/inventor[@sequence="6"]/addressbook/name')))
    list_in.append(str(elem.findtext('.//parties/inventors/inventor[@sequence="6"]/addressbook/address/text')))
    list_in.append(str(elem.findtext('.//parties/inventors/inventor[@sequence="7"]/addressbook/name')))
    list_in.append(str(elem.findtext('.//parties/inventors/inventor[@sequence="7"]/addressbook/address/text')))
    list_in.append(str(elem.findtext('.//parties/inventors/inventor[@sequence="8"]/addressbook/name')))
    list_in.append(str(elem.findtext('.//parties/inventors/inventor[@sequence="8"]/addressbook/address/text')))
    list_in.append(str(elem.findtext('.//parties/inventors/inventor[@sequence="9"]/addressbook/name')))
    list_in.append(str(elem.findtext('.//parties/inventors/inventor[@sequence="9"]/addressbook/address/text')))
    list_in.append(str(elem.findtext('.//parties/inventors/inventor[@sequence="10"]/addressbook/name')))
    list_in.append(str(elem.findtext('.//parties/inventors/inventor[@sequence="10"]/addressbook/address/text')))
    list_in.append(str(elem.findtext('.//parties/inventors/inventor[@sequence="11"]/addressbook/name')))
    list_in.append(str(elem.findtext('.//parties/inventors/inventor[@sequence="11"]/addressbook/address/text')))
    list_in.append(str(elem.findtext('.//parties/inventors/inventor[@sequence="12"]/addressbook/name')))
    list_in.append(str(elem.findtext('.//parties/inventors/inventor[@sequence="12"]/addressbook/address/text')))
    #要約【課題】＋【解決手段】＋【選択図】
    list_in.append("    ".join((elem.find('.//abstract/p').itertext())).replace('\n', '').strip())  if elem.find('.//abstract/p') != None else list_in.append('None')
    # 請求項（すべて）
    list_in.append("    ".join((elem.find('.//claims').itertext())).replace('\n', '').strip()) if elem.find('.//claims') != None else list_in.append('None')
    # 技術分野（すべて）
    list_in.append("    ".join((elem.find('.//technical-field').itertext())).replace('\n', '').strip()) if elem.find('.//technical-field') != None else list_in.append('None')
    # 背景技術（すべて）
    list_in.append("    ".join((elem.find('.//background-art').itertext())).replace('\n', '').strip()) if elem.find('.//background-art') != None else list_in.append('None')
    # 特許文献（すべて）
    list_in.append("    ".join((elem.find('.//patent-literature').itertext())).replace('\n', '').strip()) if elem.find('.//patent-literature') != None else list_in.append('None')
    # 非特許文献（すべて）
    list_in.append("    ".join((elem.find('.//non-patent-literature').itertext())).replace('\n', '').strip()) if elem.find('.//non-patent-literature') != None else list_in.append('None')
    # 発明が解決しようとする課題
    list_in.append("    ".join((elem.find('.//tech-problem').itertext())).replace('\n', '').strip()) if elem.find('.//tech-problem') != None else list_in.append('None')
    # 発明を解決するための手段
    list_in.append("    ".join((elem.find('.//tech-solution').itertext())).replace('\n', '').strip()) if elem.find('.//tech-solution') != None else list_in.append('None')
    # 発明の効果
    list_in.append("    ".join((elem.find('.//advantageous-effects').itertext())).replace('\n', '').strip()) if elem.find('.//advantageous-effects') != None else list_in.append('None')
    # 発明を実施するための形態
    list_in.append("    ".join((elem.find('.//description-of-embodiments').itertext())).replace('\n', '').strip().rstrip('\n')) if elem.find('.//description-of-embodiments') != None else list_in.append('None')
    # 産業利用上の可能性
    list_in.append("    ".join((elem.find('.//industrial-applicability').itertext())).replace('\n', '').strip()) if elem.find('.//industrial-applicability') != None else list_in.append('None')
    # 図面の簡単な説明
    list_in.append("    ".join((elem.find('.//description-of-drawings').itertext())).replace('\n', '').strip()) if elem.find('.//description-of-drawings') != None else list_in.append('None')
   
    return list_in

def write_to_csv(data: list, csv_file: Path):
    """抽出したデータをCSVファイルに書き込みます。"""
    try:
        with csv_file.open('a', newline='', encoding='cp932') as f:
            writer = csv.writer(f, lineterminator='\n')
            writer.writerow(data)
        logging.info(f"データをCSVファイル '{csv_file.name}' に追加しました。")
    except Exception as e:
        logging.error(f"CSVファイル '{csv_file.name}' への書き込み中にエラーが発生しました: {str(e)}")
        raise

def xml_to_csv(input_path: str, output_path: str):
    """指定されたディレクトリ内のすべてのXMLファイルを処理し、CSVに変換します。"""
    try:
        ipt_path, opt_path = setup_paths(input_path, output_path)
        xml_files = list(ipt_path.glob('**/*.xml'))

        if not xml_files:
            logging.warning(f"入力ディレクトリ '{input_path}' にXMLファイルが見つかりません。")
            return

        for xml_file in xml_files:
            try:
                root = parse_xml(xml_file)
                judge_status = root.findtext('.//publication-reference/document-id/kind')
                if judge_status in ["公開特許公報(A)", "公表特許公報(A)"]:
                    data = extract_data(root)
                    csv_file = opt_path / f"{data[3]}.csv"  # data[3] は公開日
                    write_to_csv(data, csv_file)
            except Exception as e:
                logging.error(f"ファイル '{xml_file.name}' の処理中にエラーが発生しました: {str(e)}")

        logging.info(f"すべてのXMLファイルの処理が完了しました。処理されたファイル数: {len(xml_files)}")
    except Exception as e:
        logging.error(f"処理中に予期しないエラーが発生しました: {str(e)}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("使用方法: python convert.py <入力ディレクトリ> <出力ディレクトリ>")
        sys.exit(1)

    input_dir, output_dir = sys.argv[1], sys.argv[2]
    xml_to_csv(input_dir, output_dir)