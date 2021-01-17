import requests
from xml.etree import ElementTree as ET
from io import BytesIO
from zipfile import ZipFile
from urllib.request import urlopen
import re
import io
import csv
import sys
import logging


def get_xml_string(file_url):
    """
    Accepts the file url and returns xml in form a string
    :param file_url: 
    :return: xml as a string
    """
    return str(requests.get(file_url).content, 'utf-8')


def get_file_download_link(resp):
    """
    Parses the xml string and extracts the first download link
    :param resp: 
    :return: returns the first download link
    """
    myroot = ET.fromstring(resp)
    # tags are nested at the level of 'doc'
    for doc in myroot.findall('.//doc'):
        temp_dict = {}
        # iterating over all elements under nested structure of 'doc' tag
        for elem in doc.iter():
            elem_dict = elem.attrib
            key_list = list(elem_dict.keys())
            if len(key_list) > 0 and (elem_dict[key_list[0]] in ["download_link", "file_type"]):
                # updating dict with keys as ["download_link", "file_type"] and their respective values
                temp_dict[elem_dict[key_list[0]]] = elem.text
        # check if file_type equals to "DLTINS"
        if temp_dict["file_type"] == "DLTINS":
            # exit the loop on first encounter of required file_type
            download_link = temp_dict["download_link"]
            break
    return download_link


def extract_zip_file_str(download_link):
    """
    From the download link in the arg extract the zipped xml and return  xml in form of string 
    :param download_link: 
    :return: xml in form of string
    """
    resp = urlopen(download_link)
    # reading zip file stream
    zipfile = ZipFile(BytesIO(resp.read()))
    # extracting zip file name
    file = zipfile.namelist()[0]
    # reading the content from the unzipped file
    xml_str_byte = zipfile.open(file).read()
    # convert from byte type str and return this string
    return str(xml_str_byte, "utf-8")


def cleaning_xml_string(xml_str_raw):
    """
    Remove the xmlns, xsi:schemaLocation and xmlns:xsi tags from the xml string so that they do not get attached to the tags and it is easier to parse the tree based on the name of the tag only.
    :param xml_str_raw: 
    :return: filtered xml string
    """
    # filtering the property columns so that the xml tree could be searched through tags directly
    xml_str_raw = re.sub(' xmlns="[^"]+"', '', xml_str_raw, flags=re.MULTILINE)
    xml_str_raw = re.sub(' xsi:schemaLocation="[^"]+"', '', xml_str_raw, flags=re.MULTILINE)
    xml_str = re.sub(' xmlns:xsi="[^"]+"', '', xml_str_raw, flags=re.MULTILINE)
    return xml_str


def create_sub_dict(elem, A):
    """
    keeps adding the extracted values to the ds [{},{},{}]
    :param elem: 
    :param A: 
    :return: 
    """
    if elem.tag == "Id":
        A["Id"] = elem.text
    elif elem.tag == "FullNm":
        A["FullNm"] = elem.text
    elif elem.tag == "ClssfctnTp":
        A["ClssfctnTp"] = elem.text
    elif elem.tag == "CmmdtyDerivInd":
        A["CmmdtyDerivInd"] = elem.text
    elif elem.tag == "NtnlCcy":
        A["NtnlCcy"] = elem.text

def extract_load(xml_str):
    """
    extracts the values from the xml string
    :param xml_str: 
    :return: List of dictionaries => [{},{},{}]
    """
    myroot1 = ET.fromstring(xml_str)
    final_list = []
    for tags in myroot1.findall(".//FinInstrmGnlAttrbts"):
        temp = {}
        for elem in tags.iter():
            create_sub_dict(elem, temp)

        final_list.append(temp)

    for i, tag_issr in enumerate(myroot1.findall(".//Issr")):
        final_list[i]["Issr"] = tag_issr.text

    return final_list


def write_to_aws_bucket(final_list, your_profile_name="default_profile_name", s3_bucket="some_default_bucket", s3_key="some_default_key"):
    """
    converts the DS to csv stream and writes the o/p to aws s3 bucket provided
    :param final_list: 
    :param your_profile_name: 
    :param s3_bucket: 
    :param s3_key: 
    :return: 
    """
    stream = io.StringIO()
    headers = list(final_list[0].keys())
    writer = csv.DictWriter(stream, fieldnames=headers)
    writer.writeheader()
    writer.writerows(final_list)
    csv_string_object = stream.getvalue()
    session = boto3.session.Session(profile_name=your_profile_name)
    resource = session.resource("s3")
    resource.Object(s3_bucket, s3_key).put(Body=csv_string_object)


if __name__ == "__main__":
    """
    The objective of this exercise is to perform the following tasks: 
    1) Download the xml
    2) From the xml, please parse through to the first download link whose file_type is DLTINS and           download the zip.
    3) Extract the xml from the zip.
    4) Convert the contents of the xml into a CSV.
    5) Store the csv from step 4) in an AWS S3 bucket
    """
    logger = logging.getLogger(__name__)
    logger.info("Data Extraction and Load Process for SteelEye")
    file_url = sys.argv[1]
    logger.info("Url used to extract file download link (file_type : DLTINS) {}".format(file_url))
    #file_url = "https://registers.esma.europa.eu/solr/esma_registers_firds_files/select?q=*&fq=publication_date:%5B2020-01-08T00:00:00Z+TO+2020-01-08T23:59:59Z%5D&wt=xml&indent=true&start=0&rows=100"
    try:
        resp = get_xml_string(file_url=file_url)
        logger.info("xml string extracted")
        download_link = get_file_download_link(resp)
        logger.info("Extracted download link of required file is : {}".format(download_link))
        xml_str_raw = extract_zip_file_str(download_link=download_link)
        logger.info("Data xml string extracted")
        xml_str = cleaning_xml_string(xml_str_raw=xml_str_raw)
        logger.info("Data xml string cleaned, few headers removed to maintain tag sanity")
        final_list = extract_load(xml_str=xml_str)
        logger.info("Data extracted and exists in DS [{},{},{}] named as final_list")
        write_to_aws_bucket(final_list=final_list, your_profile_name="some_profile", s3_bucket="bucket", s3_key="key")
        logger.info("Data written to S3 bucket successfully")
    except Exception as e :
        logger.info("Oops !! Error encountered : {}".format(e))


