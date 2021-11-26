import webbrowser, os
import json
import boto3
import io
from io import BytesIO
import sys
from pprint import pprint
import pandas as pd   
import html_to_json
from trp import Document
def get_rows_columns_map(table_result, blocks_map):
    rows = {}
    for relationship in table_result['Relationships']:
        if relationship['Type'] == 'CHILD':
            for child_id in relationship['Ids']:
                cell = blocks_map[child_id]
                if cell['BlockType'] == 'CELL':
                    row_index = cell['RowIndex']
                    col_index = cell['ColumnIndex']
                    if row_index not in rows:
                        # create new row
                        rows[row_index] = {}
                        
                    # get the text value
                    rows[row_index][col_index] = get_text(cell, blocks_map)
    return rows


def get_text(result, blocks_map):
    text = ''
    if 'Relationships' in result:
        for relationship in result['Relationships']:
            if relationship['Type'] == 'CHILD':
                for child_id in relationship['Ids']:
                    word = blocks_map[child_id]
                    if word['BlockType'] == 'WORD':
                        text += word['Text'] + ' '
                    if word['BlockType'] == 'SELECTION_ELEMENT':
                        if word['SelectionStatus'] =='SELECTED':
                            text +=  'X '    
    return text
def get_key_AWS():
    client = boto3.client("textract", aws_access_key_id="ASIARLUUWLP2B6V7S53U",
                              aws_secret_access_key="2sz7BDCjwEm5dszqrDZ9YJgoS8qZ+7PApXFD6mnW",
                              aws_session_token="FwoGZXIvYXdzEMr//////////wEaDF41F0zXD0jWE7zBoyLPAWFY6MZo8K9JW5P8gCXRegJTRhaEK21MsnfaEcb9/Vt183cWvc9zufxOtSS5rc6ED4iUWc5t9l5pdZW6pYJoK4cJlFGDTHsHNjQgRTccKysXoy2DzQBD8VJiZuEydxP8G4QV34A6d0pOyG1Yo26R8QL7T5IdhdgQgilL08zVsthazog4gnpW+6vaR2lRvyF9k0y4QI5Z9oSjdaMSAAOO4oqlHrfmLPIQlUFbiDSfEK77o9VdAx5gHMEFCxAfdoMAeFwjaFnFL3qrlajtTcpsYyjg0YCNBjItzMzGQW9iywkityvBBLQNJfAxq1fFoSbpiL8YVZPbuQk34ng2LhEmiifJn3zZ")
    return client

def get_table_csv_results(file_name):

    img_test = file_name.read()
    bytes_test = bytearray(img_test)
    print('Image loaded', file_name)

    # process using image bytes
    # get the results
    # client = boto3.client("textract", aws_access_key_id="ASIARLUUWLP2OCY5GP4T",
    #                           aws_secret_access_key="xMXhkCu/ycermwUHKqiF4nPa0Oc5hs/Om5E7ujoG",
    #                           aws_session_token="FwoGZXIvYXdzEMD//////////wEaDNqOWz525lhAqaEOziLPARh7odTmX6hgQ0XeoABYpGZhH1NI8MXmFnezpMUk31IBPEYDrPr9GClL0tKeNB6K2k3qnisSYr4CJJWD4gP4BtZ5CAJt3Zg7NaIA7cOMbhbZQAhZhDqnqB4h8OrQOhzrsJ85z0WzzbhWYUtkUELfIDBA2seoTIkxHmWRTEPCgiDuvA6PDMqVGTNfYniSS/mnOYaDk+nRH2hUhbmbsY8PWAxjBvL4xLfNSkbdV0UPxgeRLocqUL91PVaBsOjx+9G5L3HALSkL4wb32NuccVogxCiNvP6MBjIttBnOnanaqNLNdGXos+WctMTLEC3x0vLYROJ0QM59dU6UJUtYT2kU5iNH2+jF")
    client=get_key_AWS()

    response = client.analyze_document(Document={'Bytes': bytes_test}, FeatureTypes=['TABLES'])

    # Get the text blocks
    blocks=response['Blocks']
    #pprint(blocks)

    blocks_map = {}
    table_blocks = []
    for block in blocks:
        blocks_map[block['Id']] = block
        if block['BlockType'] == "TABLE":
            table_blocks.append(block)


    if len(table_blocks) <= 0:
        return "<b> NO Table FOUND </b>"

    csv = ''
    for index, table in enumerate(table_blocks):
        csv += generate_table_csv(table, blocks_map, index +1)
        csv += '\n\n'

    return csv

def generate_table_csv(table_result, blocks_map, table_index):
    rows = get_rows_columns_map(table_result, blocks_map)

    table_id = 'Table_' + str(table_index)
    
    # get cells.
    csv = 'Table: {0}\n\n'.format(table_id)

    for row_index, cols in rows.items():
        
        for col_index, text in cols.items():
            txt= '{}'.format(text)
            txt=txt.replace(",",".")
            csv += txt + ","
        csv += '\n'
        
    csv += '\n\n\n'
    return csv

def main(file_name):
    table_csv = get_table_csv_results(file_name)
    print(table_csv)

    output_file = 'output.csv'

    # replace content
    with open(output_file, "wt") as fout:
        fout.write(table_csv)

    # show the results
    table_html = pd.read_csv('output.csv')
    print(table_html)
def use(file_name):
    table_csv = get_table_csv_results(file_name)
    #print(table_csv)

    output_file = 'output.csv'

    # replace content
    with open(output_file, "wt") as fout:
        fout.write(table_csv)

    # show the results
    table = pd.read_csv('output.csv', encoding='latin-1',error_bad_lines=False)
    # table_html.dropna(subset=["text"], inplace=True)
    # table_html.apply(lambda x: pd.lib.infer_dtype(x.values))
    #print(table_html)
    output_json = html_to_json.convert(table.to_html())
    return table.to_html()
if __name__ == "__main__":
    file_name = sys.argv[1]
    main(file_name)
      
