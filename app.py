import os
import datetime
import sqlite3, csv

from io import StringIO
from tempfile import NamedTemporaryFile

import pandas as pd
import numpy as np
from pandas.api.types import is_numeric_dtype
import matplotlib.pyplot as plt

from flask import Flask, render_template, request, redirect, url_for, make_response, jsonify, send_file, g
from werkzeug.utils import secure_filename


DATABASE = "db/dataframes.db"


class DatabaseManager:
    def get_db(self):
        db = getattr(g, '_database', None)
        if db is None:
            db = g._database = sqlite3.connect(DATABASE)
            db.row_factory = sqlite3.Row
        return db
    
    def gather_df(self, df, name):
        db = self.get_db()
        df.to_sql(name, db, index=False)
        db.commit()
    
    def retrieve_df(self, name):
        db = self.get_db()

        query = "SELECT * from  {}".format(name)
        content = db.execute(query).fetchall()
        content = [dict(row) for row in content]
        return content
    
    def gather_df_names(self, name):
        db = self.get_db()
        query = "CREATE table if not exists df_names (name STR)"
        db.execute(query)
        query2 = "INSERT into df_names (name) VALUES('{}')".format(name)
        db.execute(query2)
        db.commit()
    
    def retrieve_df_names(self):
        db = self.get_db()
        query = "SELECT name from df_names"
        names = db.execute(query).fetchall()
        names = [dict(row) for row in names]
        return names


app = Flask(__name__)

class DataframeReader:
    FILE_EXTENSIONS = [".csv", ".tsv"]
    TARGET_NAME = "my_data"

    def check_extension(self, filename):
        extension = os.path.splitext(filename)[1]
        if not extension:
            return True, extension
        if extension not in self.FILE_EXTENSIONS:
            return False, extension
        return True, extension
    
    def _check_if_column(self, df, column_name):
        if column_name not in df.columns:
            return False
        return True
    
    def process_file(self, file_read, column_name):
        s = str(file_read,'utf-8')
        # Might be needed in flat files/tsv files
        s = s.replace("\t", ",")
        data = StringIO(s)
        df = pd.read_csv(data)
        col_exists = self._check_if_column(df, column_name)
        if col_exists:
            df = df.rename(columns={column_name : self.TARGET_NAME})
            return df
        return None 

    def validate_target_column(self, df):
        target_column = df[self.TARGET_NAME]
        return is_numeric_dtype(target_column)


class BenfordValidator:
    BENFORD = [30.1, 17.6, 12.5, 9.7, 7.9, 6.7, 5.8, 5.1, 4.6]
    TARGET_NAME = "my_data"
    def count_first_digit(self, data_str, df):
        mask=df[data_str]>1      
        data=list(df[mask][data_str])
        data = [str(item) for item in data]
        data = [item[0] for item in data]
        first_digits=sorted([int(x) for x in data])
        unique=(set(first_digits))
        data_count = [first_digits.count(i) for i in unique]
        total_count=sum(data_count)
        data_percentage=[(i/total_count)*100 for i in data_count]
        return total_count, data_count, data_percentage

    def get_expected_counts(self, total_count):
        """Return list of expected Benford's Law counts for total sample count."""
        return [round(p * total_count / 100) for p in self.BENFORD]

    def chi_square_test(self, data_count, expected_counts):
        """Return boolean on chi-square test (8 degrees of freedom & P-val=0.05)."""
        chi_square_stat = 0  # chi square test statistic
        for data, expected in zip(data_count, expected_counts):

            chi_square = (data - expected)**2
            chi_square_stat += chi_square / expected

        print("chi square stat", chi_square_stat)
        return chi_square_stat < 15.51
    
    def _format_chart_header(self, result):
        if result:
            return "Data passed the Benford test"
        return "Anomaly detected - did not pass Benford test"

    def build_chart(self, data, expected, result, table_name):


        """Create a bar chart representing our data adherence to Bendford's law"""
        labels = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
        result = self._format_chart_header(result)
        x = np.arange(len(labels))  # the label locations
        width = 0.55  # the width of the bars

        fig, ax = plt.subplots(figsize=(12,5))
        rects1 = ax.bar(x - width/2, data, width, label='data')
        rects2 = ax.bar(x + width/2, expected, width, label='expected')

        # Add some text for labels, title and custom x-axis tick labels, etc.
        ax.set_ylabel('Result')
        ax.set_title('DATA vs.expected \n {}'.format(result))
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.legend()
        self._autolabel(rects1, ax)
        self._autolabel(rects2, ax)
        datestamp = datetime.datetime.utcnow().strftime("%m%d%Y%H%M%S")
        url_to_chart = 'static/{}.png'.format(table_name)
        plt.savefig(url_to_chart)
        final_url = "/" + url_to_chart
        return final_url
    
    def _autolabel(self, rects, ax):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{}'.format(height),
                        xy=(rect.get_x() + rect.get_width() / 4, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='baseline')

@app.route('/')
def index():
    return render_template('file_ingest.html')

@app.route('/', methods=['POST'])
def upload_file():
    uploaded_file = request.files['file']
    column_name = request.form.get("column")
    if not column_name:
        err = {"error": "column name was not provided"}
        return make_response(err, 400)
    filename = secure_filename(uploaded_file.filename)
    df_reader = DataframeReader()

    file_ext_validity, file_ext  = df_reader.check_extension(filename)
    filename_to_write = filename.replace(file_ext, "")
    if not file_ext_validity:
        err = {"error": "wrong extension"}
        return make_response(err, 400)
    file_read = uploaded_file.read()
    if not file_read:
        err = {"error": "no file provided"}
        return make_response(err, 400)
    
    df = df_reader.process_file(file_read, column_name)

    if df is None:
        msg = "column {} does not exist".format(column_name)
        err = {"error": msg}
        return make_response(err, 400)
        # persist dataframe in DB
    name_of_table = "table_" + filename_to_write + datetime.datetime.utcnow().strftime("%m%d%Y%H%M%S")
    dbm = DatabaseManager()
    dbm.gather_df(df, name_of_table)
    dbm.gather_df_names(name_of_table)
    target_column_numeric = df_reader.validate_target_column(df)
    if not target_column_numeric:
        err = {"error": "wrong type of column"}
        return make_response(err, 400)
    benford_validator = BenfordValidator()
    results = benford_validator.count_first_digit(benford_validator.TARGET_NAME, df)
    total_count, data_count, total_percentage = results
    expected_counts = benford_validator.get_expected_counts(total_count)
    chi_test = benford_validator.chi_square_test(data_count, expected_counts)
    src = benford_validator.build_chart(data_count, expected_counts, chi_test, name_of_table)
    uploaded_file.save(uploaded_file.filename)
    return render_template("charts.html", src=src, name=name_of_table)

@app.route("/analyze_dataset/<name>")
def analyze_dataset(name=None):
    "Dataset with particular name is retrieved and can be validated"
    dbm = DatabaseManager()
    try:
        results = dbm.retrieve_df(name)
        dataframe = pd.DataFrame(results)
        # HERE we can check if this particular dataset follows Benford's Law
        benford_validator = BenfordValidator()
        bv_res = benford_validator.count_first_digit(benford_validator.TARGET_NAME, dataframe)
        total_count, data_count, total_percentage = bv_res
        expected_counts = benford_validator.get_expected_counts(total_count)
        chi_test = benford_validator.chi_square_test(data_count, expected_counts)
        benford_results = {"benford_validation": chi_test}
        src = benford_validator.build_chart(data_count, expected_counts, chi_test, name)

        return render_template("charts.html", src=src, result=chi_test, name=name)
    except Exception as e:
        err = {"error": "no such dataframe"}
        return make_response(err, 400)

@app.route("/dataset/<name>", methods=["POST", "GET"])
def retrieve_dataset(name=None):
    """Download datasets from those that are available in database
       Dataset can be analysed then to see if they follow Benford's Law
    """
    dbm = DatabaseManager()
    results = dbm.retrieve_df(name)
    dataframe = pd.DataFrame(results)
    with NamedTemporaryFile(delete=False) as tempfile:
        dataframe.to_csv(tempfile.name, index=False)
        return send_file(tempfile.name, as_attachment=True, attachment_filename=name)

@app.route("/names")
def get_dataset_names():
    dbm = DatabaseManager()
    try:
        names = dbm.retrieve_df_names()
        return render_template("list_of_names.html", names=names)
    except Exception as e:
        err = {"error": str(e)}
        return make_response(err, 400)

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")