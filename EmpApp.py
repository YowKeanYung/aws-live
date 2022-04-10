from flask import Flask, render_template, request, session
from flask_session import Session
from flask.wrappers import Response
from pymysql import connections
import os
import boto3
from config import *

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
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

   # location = request.form['location']
    emp_image_file = request.files['emp_image_file']

    insert_sql = "INSERT INTO employee VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
    cursor = db_conn.cursor()

    if emp_image_file.filename == "":
        return "Please select a file"

    try:
        val = (emp_id, emp_name, phone, email, position, department, joindate, salary)
        cursor.execute(insert_sql, val)
        db_conn.commit()
        #emp_name = "" + first_name + " " + last_name
        # Uplaod image file in S3 #
        emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file.jpg"
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

    return render_template('AddStaffOutput.html', name=emp_name, id=emp_id)



@app.route("/staffpage", methods=['GET', 'POST'])
def staffpage():
    return render_template('AddStaff.html')

@app.route("/searchstaffpage", methods=['GET', 'POST'])
def searchstaffpage():
    return render_template('SearchStaff.html')

@app.route("/searchpay", methods=['GET', 'POST'])
def searchpay():
    return render_template('SearchPay.html')



@app.route("/searchstaffdetails", methods=['POST'])
def searchstaffdetails():
     emp_id = request.form['emp_id']
   
     selectsql = "SELECT * FROM employee WHERE emp_id = %s"
     cursor = db_conn.cursor()
     adr = (emp_id)

     try:
      cursor.execute(selectsql, adr) 

        # if SELECT:
      myresult = cursor.fetchone()

      emp_id = myresult[0]
      emp_name = myresult[1]
      phone = myresult[2]
      email = myresult[3]
      position = myresult[4]
      department = myresult[5] 
      joindate = myresult[6]
      salary = myresult[7]

      emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file.jpg"
      s3 = boto3.resource('s3')
    # # obj = s3.Object(Bucket=custombucket, Key=emp_image_file_name_in_s3)
      s3_client = boto3.client('s3')
    # ## response = s3_client.get_object(Bucket=custombucket, Key=emp_image_file_name_in_s3)
    # ## data = response['Body'].read().decode('utf-8')
    #  response = s3.Bucket(custombucket).download_file(Key=emp_image_file_name_in_s3, 'my_localimage.jpg')
    ##  datas=obj.get()['Body'].read().decode('utf-8')
      #url = s3_client.generate_presigned_url('get_object',
      #                          Params={
      #                              'Bucket': 'custombucket',
      #                              'Key': 'emp_image_file_name_in_s3',
      #                          },                                  
      #                          ExpiresIn=3600)
      #print (url)
     

      object_url = "https://yowkeanyung-employee.s3.amazonaws.com/{1}".format(
      custombucket,
      emp_image_file_name_in_s3)
     finally:
      cursor.close()

     return render_template('ViewStaff.html', id=emp_id, name=emp_name,
                           phone=phone, email=email, position=position, department=department, joinDate=joindate, salary=salary, image_url=object_url)
    


@app.route("/getemp", methods=['POST'])
def getemp():
     emp_id = request.form['emp_id']
   
     selectsql = "SELECT * FROM employee"
     cursor = db_conn.cursor()
     #adr = (emp_id)

     
     cursor.execute(selectsql) 

        
     result = cursor.fetchall()

     #p = []

     #tbl = "<tr><td>ID</td><td>Name</td><td>Email</td><td>Phone</td></tr>"
     #p.append(tbl)

     #for row in result:
     # a = "<tr><td>%s</td>"%row[0]
     # p.append(a)
     # b = "<td>%s</td>"%row[1]
     # p.append(b)
     # c = "<td>%s</td>"%row[2]
     # p.append(c)
     # d = "<td>%s</td></tr>"%row[3]
     # p.append(d)

     return render_template('Allemp.html', value=result)

@app.route("/getattendance", methods=['GET', 'POST'])
def getattendance():
    # emp_id = request.form['emp_id']
   
     selectsql = "SELECT * FROM attendance"
     cursor = db_conn.cursor()
     #adr = (emp_id)

     
     cursor.execute(selectsql) 

        
     result = cursor.fetchall()
     session["result"]=result
     
     return render_template('Attendance.html', value=result)

@app.route("/getattendanceoutput", methods=['GET', 'POST'])
def getattendanceoutput():
    # emp_id = request.form['emp_id']
   
     selectsql = "SELECT * FROM attendance"
     cursor = db_conn.cursor()
     #adr = (emp_id)

     
     cursor.execute(selectsql) 

        
     result = cursor.fetchall()
     session["result"]=result
     
     return render_template('AttendanceOutput.html', value=result)

@app.route("/payroll", methods=['POST'])
def payroll():
     emp_id = request.form['emp_id']
   
     selectsql = "SELECT * FROM employee WHERE emp_id = %s"
     cursor = db_conn.cursor()
     adr = (emp_id)
     session["adr"]=adr
     try:
      cursor.execute(selectsql, adr) 

        # if SELECT:
      myresult = cursor.fetchone()

      emp_id = myresult[0]
      emp_name = myresult[1]
      position = myresult[4]
      department = myresult[5] 
      salary = myresult[7]

      session["name"]=emp_name
      
      #emp_image_file_name_in_s3 = "emp-id-" + str(emp_id) + "_image_file"
      #s3_client = boto3.client('s3')
      #response = s3_client.get_object(Bucket=custombucket, Key=emp_image_file_name_in_s3)
      #data = response['Body'].read()

     finally:
      cursor.close()

     return render_template('Payroll.html', idd=emp_id, name=emp_name,
                           position=position, department=department, salary=salary)




@app.route("/updatesalary", methods=['GET', 'POST'])
def updatesalary():
     
     salaryy = request.form['emp_salary']
     
     update_sql = "UPDATE employee SET salary = %s WHERE emp_id = %s"
     val = (salaryy, session.get("adr"))
     cursor = db_conn.cursor()
     cursor.execute(update_sql, val)
     db_conn.commit()
     cursor.close()
     return render_template('PayrollOutput.html', salary=salaryy, id=session.get("adr"), name=session.get("name"))


@app.route("/saveattendance", methods=['GET', 'POST'])
def saveattendance():
    return render_template('AttendanceOutput.html')




if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
