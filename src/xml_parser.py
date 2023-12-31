from os import path
from typing import Optional

import requests
from chardet import UniversalDetector
from lxml import etree

from utils import VSMLManager
from vsml import VSML

CONFIG_FILE = "http://vsml.pigeons.house/config/vsml.xsd"
OFFLINE_CONFIG_FILE = "./config/vsml.xsd"


def get_text_encoding(
    filename: str,
) -> Optional[str]:
    with open(filename, "rb") as file:
        detector = UniversalDetector()
        for line in file:
            detector.feed(line)
            if detector.done:
                break
    detector.close()
    encoding = detector.result["encoding"]
    if encoding == "SHIFT_JIS":
        encoding = "CP932"
    return encoding


def formatting_xml(
    xml_text: str,
) -> str:
    """
    etreeで読み込むためにXMLのテキストから<?xmlから始まる行を削除する。

    Parameters
    ----------
    xml_text : str
        XMLテキスト

    Returns
    -------
    formatted_xml_text : str
        整形したXMLテキスト
    """

    formatted_text = xml_text
    (
        vsml_head,
        vsml_content,
    ) = xml_text.split("\n", 1)

    if "<?xml" in vsml_head:
        formatted_text = vsml_content

    return formatted_text


def get_parser_with_xsd(
    is_offline: bool,
) -> etree.XMLParser:
    """
    独自XSDファイルを読み込んだetreeのparserオブジェクトを返す

    Returns
    -------
    parser : XMLParser
        XSD情報を持った、XMLのparser
    """

    if is_offline:
        with open(OFFLINE_CONFIG_FILE, "r") as f:
            xsd_text = formatting_xml(f.read())
    else:
        xsd_text = formatting_xml(requests.get(CONFIG_FILE).text)
    schema_root = etree.XML(xsd_text, None)
    schema = etree.XMLSchema(schema_root)
    return etree.XMLParser(
        schema=schema,
        remove_comments=True,
        remove_blank_text=True,
    )


def get_vsml_text(
    filename: str,
) -> str:
    """
    受け取ったVSMLファイルのパスを開き、テキスト情報を返す。

    Parameters
    ----------
    filename : str
        VSMLファイルのパス

    Returns
    -------
    vsml_text : str
        VSMLファイルの整形されたテキスト情報
    """

    encoding = get_text_encoding(filename)
    with open(
        filename,
        "r",
        encoding=encoding,
    ) as f:
        vsml_text = f.read()
    return formatting_xml(vsml_text)


def parsing_vsml(filename: str, is_offline: bool) -> VSML:
    """
    受け取ったVSMLファイルのパスを開きVSMLクラスのオブジェクトにする。

    Parameters
    ----------
    filename : str
        VSMLファイルのパス

    Returns
    -------
    vsml_object : VSML
        読み込んだファイルから生成したVSMLオブジェクト
    """

    # 入力されたvsmlの読み込み(xsdでのバリデーション付き)
    parser = get_parser_with_xsd(is_offline)
    vsml_text = get_vsml_text(filename)
    vsml_element = etree.fromstring(vsml_text, parser)

    # vsmlファイルからの相対パスを想定するため、vsmlのルートパスを取得
    root_path = path.dirname(filename)
    if root_path != "":
        root_path = root_path + "/"
    VSMLManager.set_root_path(root_path)

    return VSML(vsml_element, is_offline)
