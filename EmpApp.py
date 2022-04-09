from flask import Flask, render_template, request
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)

bucket = custombucket
region = customregion

db_conn = connections.Connection(
    host=customhost,
    port=3306,
    user=customuser,
    password=custompass,
    db=customdb

)
output = {}
table = 'employee'


@app.route("/", methods=['GET', 'POST'])
def home():
    return render_template('HomePage.html')


@app.route("/about", methods=['POST'])
def about():
    return render_template('www.intellipaat.com')


@app.route("/addstaff", methods=['POST'])
def AddEmp():
    emp_id = request.form['emp_id']
   # first_name = request.form['first_name']
  #  last_name = request.form['last_name']
   # pri_skill = request.form['pri_skill']
    emp_name = request.form['emp_name']
    phone = request.form['emp_phone']
    email = request.form['emp_email']
    position = request.form['emp_posi']
    department = request.form['emp_dept'] 
    joindate = request.form['emp_date']
    salary = request.form['emp_salary']
    location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:
        val = (emp_id, emp_name, phone, email, position, department, joindate, salary)
        cursor.execute(insert_sql, val)
        db_conn.commit()
        #emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
        s3 = boto3.resource('s3')

        try:
            print("Data inserted in MySQL RDS... uploading image to S3...")
            s3.Bucket(custombucket).put_object(Key=emp_image_file_name_in_s3, Body=emp_image_file)
            bucket_location = boto3.client('s3').get_bucket_location(Bucket=custombucket)
            s3_location = (bucket_location['LocationConstraint'])

            if s3_location is None:
                s3_location = ''
            else:
                s3_location = '-' + s3_location

            object_url = "https://s3{0}.amazonaws.com/{1}/{2}".format(
                s3_location,
                custombucket,
                emp_image_file_name_in_s3)

        except Exception as e:
            return str(e)

    finally:
        cursor.close()

    print("all modification done...")

    return render_template('AddStaffOutput.html', name=emp_name)



@app.route("/staffpage", methods=['GET', 'POST'])
def staffpage():
    return render_template('AddStaff.html')

@app.route("/searchstaffpage", methods=['GET', 'POST'])
def searchstaffpage():
    return render_template('SearchStaff.html')



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
