from flask import Flask, request, render_template,send_file
import json
import boto3
from trp import Document
import textract_python_table_parser
textractclient = textract_python_table_parser.get_key_AWS()

app = Flask(__name__)


@app.route("/", methods=["GET"])
def main():
    return render_template("index.html", jsonData=json.dumps({}))


@app.route("/extract", methods=["POST"])
def extractImage():

    option =request.form['format']
    if option =='text':
        file = request.files.get("filename")
        binaryFile = file.read()
        response = textractclient.detect_document_text(
            Document={
                'Bytes': binaryFile
            }
        )
        extractedText = ""
        for block in response['Blocks']:
            if block["BlockType"] == "LINE":
                # print('\033[94m' + item["Text"] + '\033[0m')
                extractedText = extractedText+block["Text"]+" "
    elif option =='table':
        file = request.files.get("filename")
        extractedText =textract_python_table_parser.use(file)
        # binaryFile = file.read()
        # response = textractclient.analyze_document(
        #     Document={
        #         'Bytes': binaryFile
        #     },
        # FeatureTypes=["TABLES"])
        # extractedText = ""
        # doc = Document(response)
        # for page in doc.pages:
        #     for table in page.tables:
        #         for r, row in enumerate(table.rows):
        #             itemName = ""
        #             for c, cell in enumerate(row.cells):
        #                 extractedText = extractedText+ "Table[{}][{}] = {}".format(r, c, cell.text)
        #             extractedText = extractedText+ "<br>"

    responseJson = {

        "text": extractedText
    }
    print(responseJson)
    return render_template("index.html", jsonData=json.dumps(responseJson))
@app.route('/download')
def download_file():
    file ="output.csv"
    return send_file(file,as_attachment=True)
app.run("0.0.0.0", port=5000, debug=True)
