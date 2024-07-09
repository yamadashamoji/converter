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
    list_in.append(str(elem.findtext('.//publication-reference/document-id/country')))
    list_in.append(str(elem.findtext('.//publication-reference/document-id/kind')))
    list_in.append(str(elem.findtext('.//publication-reference/document-id/date')))
    list_in.append(str(elem.findtext('.//application-reference/document-id/date')))
    list_in.append(str(elem.findtext('.//publication-reference/document-id/doc-number')))
    list_in.append(str(elem.findtext('.//application-reference/document-id/doc-number')))
    list_in.append(str(elem.findtext('.//invention-title')))
    list_in.append(str(elem.findtext('.//classification-ipc/main-clsf')))
    list_in.append(str(elem.findtext('.//number-of-claims')))
    list_in.append(str(elem.findtext('.//jp:total-pages', namespaces=namespaces)))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/applicant[@sequence="1"]/addressbook[@lang="ja"]/registered-number', namespaces=namespaces)))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/applicant[@sequence="1"]/addressbook[@lang="ja"]/name', namespaces=namespaces)))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/applicant[@sequence="1"]/addressbook[@lang="ja"]/address/text', namespaces=namespaces)))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="2"]/applicant[@sequence="2"]/addressbook[@lang="ja"]/registered-number', namespaces=namespaces)))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="2"]/applicant[@sequence="2"]/addressbook[@lang="ja"]/name', namespaces=namespaces)))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="2"]/applicant[@sequence="2"]/addressbook[@lang="ja"]/address/text', namespaces=namespaces)))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="3"]/applicant[@sequence="3"]/addressbook[@lang="ja"]/registered-number', namespaces=namespaces)))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="3"]/applicant[@sequence="3"]/addressbook[@lang="ja"]/name', namespaces=namespaces)))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="3"]/applicant[@sequence="3"]/addressbook[@lang="ja"]/address/text', namespaces=namespaces)))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="4"]/applicant[@sequence="4"]/addressbook[@lang="ja"]/registered-number', namespaces=namespaces)))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="4"]/applicant[@sequence="4"]/addressbook[@lang="ja"]/name', namespaces=namespaces)))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="4"]/applicant[@sequence="4"]/addressbook[@lang="ja"]/address/text', namespaces=namespaces)))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="5"]/applicant[@sequence="5"]/addressbook[@lang="ja"]/registered-number', namespaces=namespaces)))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="5"]/applicant[@sequence="5"]/addressbook[@lang="ja"]/name', namespaces=namespaces)))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="5"]/applicant[@sequence="5"]/addressbook[@lang="ja"]/address/text', namespaces=namespaces)))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="6"]/applicant[@sequence="6"]/addressbook[@lang="ja"]/registered-number', namespaces=namespaces)))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="6"]/applicant[@sequence="6"]/addressbook[@lang="ja"]/name', namespaces=namespaces)))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="6"]/applicant[@sequence="6"]/addressbook[@lang="ja"]/address/text', namespaces=namespaces)))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/agent[@sequence="1"][@jp:kind="representative"]/addressbook/registered-number', namespaces=namespaces)))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="1"]/agent[@sequence="1"][@jp:kind="representative"]/addressbook/name', namespaces=namespaces)))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="2"]/agent[@sequence="2"][@jp:kind="representative"]/addressbook/registered-number', namespaces=namespaces)))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="2"]/agent[@sequence="2"][@jp:kind="representative"]/addressbook/name', namespaces=namespaces)))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="3"]/agent[@sequence="3"][@jp:kind="representative"]/addressbook/registered-number', namespaces=namespaces)))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="3"]/agent[@sequence="3"][@jp:kind="representative"]/addressbook/name', namespaces=namespaces)))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="4"]/agent[@sequence="4"][@jp:kind="representative"]/addressbook/registered-number', namespaces=namespaces)))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="4"]/agent[@sequence="4"][@jp:kind="representative"]/addressbook/name', namespaces=namespaces)))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="5"]/agent[@sequence="5"][@jp:kind="representative"]/addressbook/registered-number', namespaces=namespaces)))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="5"]/agent[@sequence="5"][@jp:kind="representative"]/addressbook/name', namespaces=namespaces)))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="6"]/agent[@sequence="6"][@jp:kind="representative"]/addressbook/registered-number', namespaces=namespaces)))
    list_in.append(str(elem.findtext('.//parties/jp:applicants-agents-article/jp:applicants-agents[@sequence="6"]/agent[@sequence="6"][@jp:kind="representative"]/addressbook/name', namespaces=namespaces)))
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
                    csv_file = opt_path / f"{data[2]}.csv"  # data[2] は公開日
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