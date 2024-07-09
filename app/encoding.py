import shutil
import os
import codecs
import logging
from pathlib import Path

# ログの設定
logging.basicConfig(filename='encoding_conversion.log', level=logging.INFO,
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

def copy_and_convert_encoding(input_file: Path, output_file: Path):
    """XMLファイルをコピーし、エンコーディングをEUC-JPからUTF-8に変換します。"""
    try:
        with open(input_file, 'r', encoding='euc_jp') as f_in, \
             open(output_file, 'w', encoding='utf_8') as f_out:
            content = f_in.read()
            converted_content = content.replace(
                '<?xml version="1.0" encoding="EUC-JP"?>',
                '<?xml version="1.0" encoding="UTF-8"?>'
            )
            f_out.write(converted_content)
        logging.info(f"ファイル '{input_file.name}' を変換しました。")
    except UnicodeDecodeError:
        logging.error(f"ファイル '{input_file.name}' のデコードに失敗しました。EUC-JPではない可能性があります。")
    except Exception as e:
        logging.error(f"ファイル '{input_file.name}' の処理中にエラーが発生しました: {str(e)}")

def copy_xml_and_chg_ipt_codec(input_path: str, output_path: str):
    """指定されたディレクトリ内のすべてのXMLファイルを処理します。"""
    try:
        ipt_path, opt_path = setup_paths(input_path, output_path)
        xml_files = list(ipt_path.glob('**/*.xml'))
        
        if not xml_files:
            logging.warning(f"入力ディレクトリ '{input_path}' にXMLファイルが見つかりません。")
            return

        for xml_file in xml_files:
            relative_path = xml_file.relative_to(ipt_path)
            output_file = opt_path / relative_path
            output_file.parent.mkdir(parents=True, exist_ok=True)
            copy_and_convert_encoding(xml_file, output_file)

        logging.info(f"すべてのXMLファイルの処理が完了しました。処理されたファイル数: {len(xml_files)}")
    except Exception as e:
        logging.error(f"処理中に予期しないエラーが発生しました: {str(e)}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("使用方法: python encoding.py <入力ディレクトリ> <出力ディレクトリ>")
        sys.exit(1)
    
    input_dir, output_dir = sys.argv[1], sys.argv[2]
    copy_xml_and_chg_ipt_codec(input_dir, output_dir)