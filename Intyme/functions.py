from Intyme import intyme
import sqlite3
import os
import cv2
import matplotlib.pyplot as plt
import face_recognition
import time
import json
import requests
import datetime
import smtplib
import random
import string
import secrets

#Returns type(student or teacher) from login_details table using id
def retrive_type(id):
    connection = sqlite3.connect("intyme.db")
    cursor = connection.cursor()
    sql_query = "SELECT type FROM login_details where id=" + str(id) + ";"
    cursor.execute(sql_query)
    data = cursor.fetchone()
    cursor.close()
    connection.close()
    return data


#Returns binary data of piicture from pictures table using id
def retrive_picture(id):
    connection = sqlite3.connect("intyme.db")
    cursor = connection.cursor()
    sql_query = "SELECT pic FROM pictures where id=" + str(id) + ";"
    cursor.execute(sql_query)
    data = cursor.fetchone()
    cursor.close()
    connection.close()
    return data[0]


#Converts the binary data to picture using binary data passed as parameter
def write_picture(data):
    with open("person.jpg", "wb") as f:
        f.write(data)


#Returns a dictionary of personal data of student using id
def retrive_personal(id):
    connection = sqlite3.connect("intyme.db")
    cursor = connection.cursor()
    sql_query = "SELECT * FROM student_details where id=" + str(id) + ";"
    cursor.execute(sql_query)
    field_names = [i[0] for i in cursor.description]
    data = cursor.fetchone()
    cursor.close()
    connection.close()
    result = dict(zip(field_names,data))
    return result


#Captures an image using OpenCV
def capture_image():
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        ret, frame = cap.read()
    else:
        ret = False
    image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    plt.imshow(image)
    plt.xticks([])
    plt.yticks([])
    plt.savefig('test_image.jpg')
    cap.release()


#Face Recognition part which returns either True/False or Something when index out of range
def faceRecognition():
    try:
        location = os.getcwd().replace("\\", "/") + "/Intyme/static/profile/images/"
        test_image = face_recognition.load_image_file(location+"test_image.jpg")
        test_image_encoded = face_recognition.face_encodings(test_image)[0]
        profile_picture = face_recognition.load_image_file(location+"person.jpg")
        profile_picture_encoded = face_recognition.face_encodings(profile_picture)[0]
        result = face_recognition.compare_faces([profile_picture_encoded], test_image_encoded)
    except:
        result = ["Something"]
    return result


#Returns timetable data using table_name as parameter
def db_timetable(table_name):
    connection = sqlite3.connect("intyme.db")
    cursor = connection.cursor()
    sql_query = "SELECT * FROM " + table_name + ";"
    cursor.execute(sql_query)
    data = cursor.fetchall()
    cursor.close()
    connection.close()
    return data


#Returns table name for timetable based on the personal id (Section only)
def student_ttable(id):
    personal = retrive_personal(id)
    if personal['section'] == 'B':
        table_name = "bca6_B_timetable"
    elif personal['section'] == 'A':
        table_name = "bca6_A_timetable"
    data = db_timetable(table_name)
    return data

#Returns table name for timetable based on the personal id (Section only)
def student_ttable2(id):
    personal = retrive_personal(id)
    if personal['section'] == 'B':
        table_name = "bca6_B_timetable"
    elif personal['section'] == 'A':
        table_name = "bca6_A_timetable"
    return table_name

#Returns the time function
def time_fn():
    return time.asctime()


#Returns a list consisting of the latitude and longitude using the ipstack api
def location():
    #ipstack website username and password is christ email and password
    Access_Key = " "
    send_url = "http://api.ipstack.com/check?access_key=" + Access_Key
    geo_req = requests.get(send_url)
    geo_json = json.loads(geo_req.text)
    latitude = geo_json['latitude']
    longitude = geo_json['longitude']
    city = geo_json['city']
    return latitude,longitude


#Returns True/False depending on the time
def time_check():
    start_min = 0
    end_min = 10
    start_hour = 9
    end_hour = 17
    minutes = datetime.datetime.now().time().minute
    hour = datetime.datetime.now().time().hour
    if minutes in range(start_min,end_min) and hour in range(start_hour,end_hour):
        return True
    else:
        return False


#Returns subject from the timetable based on the section and id
def retrive_subject(id):
    day = datetime.datetime.now().strftime("%A")
    hour = datetime.datetime.now().time().hour

    table_name = student_ttable2(id)

    connection = sqlite3.connect("intyme.db")
    cursor = connection.cursor()
    sql_query = "SELECT period_number FROM subject_timings WHERE start_time=" + str(hour)
    cursor.execute(sql_query)
    data = cursor.fetchone()



    print(table_name)
    sql_query = "SELECT " + data[0] + " FROM " + table_name + " WHERE day='" + day + "';"
    cursor.execute(sql_query)
    subject = cursor.fetchone()

    cursor.close()
    connection.close()
    return subject[0]


#Returns the subject info table name using subject name from retrive_subject table
def retrive_subjectTable_db(id):
    subject_name = retrive_subject(id)
    connection = sqlite3.connect("intyme.db")
    cursor = connection.cursor()
    sql_query = "SELECT table_name FROM subject_table WHERE subject='" + subject_name.lower() + "';"
    cursor.execute(sql_query)
    data = cursor.fetchone()
    cursor.close()
    connection.close()
    return data[0]


#Updates the main attendance sheet with subject, id, location
def attendance_sheet_update(id):
    subject = retrive_subject(id)
    ti = time.asctime()
    loc = str(location())
    status = "present"

    connection = sqlite3.connect("intyme.db")
    cursor = connection.cursor()
    cursor.execute("INSERT INTO attendance_sheet(id,subject,time,location,status) VALUES (?,?,?,?,?)",(id,subject,ti,loc,status))
    connection.commit()
    cursor.close()
    connection.close()
    return ' '


#Returns a list of subject info data based on the student id
def check_attendance_from_db(id):
    tables = ['daa_info','cyber_law_info','cloud_computing_info','major_project_info','adbms_info']
    subjects = ['Design and Analysis of Algorithms', 'Cyber Law', 'Cloud Computing', 'Major Project', 'Advanced Database Management System']
    data = []
    for i in range(len(tables)):
        connection = sqlite3.connect("intyme.db")
        cursor = connection.cursor()
        sql_query = "SELECT * FROM " + tables[i] + " WHERE id=" + str(id)
        cursor.execute(sql_query)
        result = cursor.fetchone()
        result = list(result)
        result.insert(0,subjects[i])
        result.pop(1)
        result.pop(1)
        data.append(result)
        cursor.close()
        connection.close()
    return data


#Checks if a list has empty string in it and returns True/False accordingly
def check_if_empty(data):
    for d in data:
        if d == "":
            return True
    return False


#Checks if a register number exists in the login_details and returns True/False accordingly
def regno_exists(reg):
    connection = sqlite3.connect("intyme.db")
    cursor = connection.cursor()
    sql_query = "SELECT id FROM login_details"
    cursor.execute(sql_query)
    data = cursor.fetchall()
    cursor.close()
    connection.close()
    for tup in data:
        for id in tup:
            if reg == str(id):
                return True
    return False


#Registers a new student to the database and Initializes all the table
def store_student_db(data):

    connection = sqlite3.connect("intyme.db")
    cursor = connection.cursor()

    cursor.execute("INSERT INTO login_details(id, username, type, password) VALUES(?,?,?,?)",
                   (data[1],data[0],'student',data[11]))
    connection.commit()

    with open(os.path.join(intyme.config["IMAGE_UPLOADS"],data[12]),'rb') as f:
        pictu = f.read()
    cursor.execute("INSERT INTO pictures (id,pic) VALUES (?,?)", (data[1], pictu))
    connection.commit()

    cursor.execute("INSERT INTO student_details(id,username,class,section,year,course,mobile,email,dob,father,mother,address) VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                   (data[1],data[0],data[3],data[4],data[5],data[6],data[8],data[7],data[9],'Father','Mother',data[10]))
    connection.commit()

    cursor.execute("INSERT INTO adbms_info(id,username,conducted,present,absent,cocurricular,extra_curricular,medical) VALUES(?,?,?,?,?,?,?,?)",
                   (data[1],data[0],0,0,0,0,0,0))
    connection.commit()

    cursor.execute(
        "INSERT INTO cloud_computing_info(id,username,conducted,present,absent,cocurricular,extra_curricular,medical) VALUES(?,?,?,?,?,?,?,?)",
        (data[1], data[0], 0, 0, 0, 0, 0, 0))
    connection.commit()

    cursor.execute(
        "INSERT INTO cyber_law_info(id,username,conducted,present,absent,cocurricular,extra_curricular,medical) VALUES(?,?,?,?,?,?,?,?)",
        (data[1], data[0], 0, 0, 0, 0, 0, 0))
    connection.commit()

    cursor.execute(
        "INSERT INTO daa_info(id,username,conducted,present,absent,cocurricular,extra_curricular,medical) VALUES(?,?,?,?,?,?,?,?)",
        (data[1], data[0], 0, 0, 0, 0, 0, 0))
    connection.commit()

    cursor.execute(
        "INSERT INTO major_project_info(id,username,conducted,present,absent,cocurricular,extra_curricular,medical) VALUES(?,?,?,?,?,?,?,?)",
        (data[1], data[0], 0, 0, 0, 0, 0, 0))
    connection.commit()

    cursor.execute(
        "INSERT INTO french_info(id,username,conducted,present,absent,cocurricular,extra_curricular,medical) VALUES(?,?,?,?,?,?,?,?)",
        (data[1], data[0], 0, 0, 0, 0, 0, 0))
    connection.commit()

    cursor.execute(
        "INSERT INTO german_info(id,username,conducted,present,absent,cocurricular,extra_curricular,medical) VALUES(?,?,?,?,?,?,?,?)",
        (data[1], data[0], 0, 0, 0, 0, 0, 0))
    connection.commit()

    cursor.close()
    connection.close()


#Sends email notifications to Students
def send_notifications(email,messg):
    from_email_address = ''
    from_email_password = ''
    to_email_address = email

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(from_email_address, from_email_password)
        subject = 'Intyme Notification'
        body = messg
        msg = "Subject: " + subject + "\n\n " + body
        smtp.sendmail(from_email_address, to_email_address, msg)


#Returns a list of id, username and email
def get_data_for_email():
    con = sqlite3.connect("intyme.db")
    cursor = con.cursor()
    cursor.execute("SELECT id,username,email,class FROM student_details")
    data = cursor.fetchall()
    cursor.close()
    con.close()
    return data


#Updates the subject info table by increasing th conducted and present by 1
def update_value_attendance_present(id):
    sub_table = retrive_subjectTable_db(id)
    connection = sqlite3.connect("intyme.db")
    cursor = connection.cursor()
    sql_query = "SELECT conducted,present FROM " + sub_table + " WHERE id=" + str(id)
    cursor.execute(sql_query)
    data = cursor.fetchone()
    conducted = data[0] + 1
    present = data[1] + 1

    sql_query = "UPDATE " + sub_table + " SET conducted=" + str(conducted) + " ,present=" + str(present) + " WHERE id=" + str(id)
    cursor.execute(sql_query)
    connection.commit()
    cursor.close()
    connection.close()
    return 'Attendance Updated'


#Returns the info from the subject info table
def teacher_check_attendance_db(id):
    connection = sqlite3.connect("intyme.db")
    cursor = connection.cursor()

    sql_query = "SELECT subject FROM subject_teacher WHERE teacher_id='" + str(id) + "';"
    cursor.execute(sql_query)
    subject_name = cursor.fetchone()
    subject_name = subject_name[0]

    sql_query = "SELECT table_name FROM subject_table WHERE subject='" + subject_name + "';"
    cursor.execute(sql_query)
    table_name = cursor.fetchone()
    table_name = table_name[0]

    sql_query = "SELECT * FROM " + table_name
    cursor.execute(sql_query)
    data = cursor.fetchall()

    BCA6_A = []
    BCA6_B = []
    for i in data:
        received = retrive_personal(i[0])
        if received["class"] == "6 BCA A":
            BCA6_A.append(i)
        elif received["class"] == "6 BCA B":
            BCA6_B.append(i)
        else:
            print("Other Class")
    data = [BCA6_A,BCA6_B]

    cursor.close()
    connection.close()
    return data


#Generate random colors
def random_color():
    color = "#" + ''.join([random.choice('0123456789ABCDEF') for j in range(6)])
    return color


#Stores missed class form to the missed_class_form table
def store_missed_form_db(id,subject,from_date,to_date,r_type,reason,filename):
    connection = sqlite3.connect("intyme.db")
    cursor = connection.cursor()
    with open(os.path.join(intyme.config["IMAGE_UPLOADS"], filename), 'rb') as f:
        doc = f.read()
    sql_query = "INSERT INTO missed_form_details(id,subject,documents,date,end_date,reason,type) VALUES(?,?,?,?,?,?,?)"
    cursor.execute(sql_query,(id,subject,doc,from_date,to_date,reason,r_type))
    connection.commit()
    cursor.close()
    connection.close()

#Retrives person info of teachers
def retrive_teacher_details(id):
    connection = sqlite3.connect("intyme.db")
    cursor = connection.cursor()
    sql_query = "SELECT * FROM teacher_details where id=" + str(id) + ";"
    cursor.execute(sql_query)
    field_names = [i[0] for i in cursor.description]
    data = cursor.fetchone()
    cursor.close()
    connection.close()
    result = dict(zip(field_names, data))
    return result

def retrive_missed_form(id):
    connection = sqlite3.connect("intyme.db")
    cursor = connection.cursor()
    sql_query = "SELECT subject FROM subject_teacher WHERE teacher_id='" + str(id) + "';"
    cursor.execute(sql_query)
    data = cursor.fetchone()

    sql_query = "SELECT id,date,end_date,type,reason,documents FROM missed_form_details WHERE subject='" + data[0] + "' and status='pending';"
    cursor.execute(sql_query)
    data = cursor.fetchall()

    cursor.close()
    connection.close()
    return data

def approve_attendance(d_id,d_type,d_reason):
    connection = sqlite3.connect("intyme.db")
    cursor = connection.cursor()
    sql_query = "UPDATE missed_form_details SET status='approved' WHERE id='" + str(d_id) + "' and type='" + str(d_type) + "' and reason='" + str(d_reason) + "';"
    cursor.execute(sql_query)
    connection.commit()
    cursor.close()
    connection.close()
    data = retrive_personal(d_id)
    send_notifications(data["email"],"Your claim for "+ str(d_type) + " has been approved. Please meet the subject teacher with the original documents for further proceedings. Thank You")

def generatePassword():
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(6))
    return password


def retrive_student_absence(id):
    connection = sqlite3.connect("intyme.db")
    cursor = connection.cursor()
    sql_query = "SELECT subject,time FROM attendance_sheet WHERE id='" + str(id) + "' and status='absent';"
    cursor.execute(sql_query)
    data = cursor.fetchall()
    cursor.close()
    connection.close()
    return data

def retrive_teacher_absence(subject):
    connection = sqlite3.connect("intyme.db")
    cursor = connection.cursor()
    sql_query = "SELECT id,time FROM attendance_sheet WHERE subject='" + subject + "' and status='absent';"
    cursor.execute(sql_query)
    data = cursor.fetchall()
    cursor.close()
    connection.close()
    return data

def retrive_subject_name_from_teacherid(id):
    connection = sqlite3.connect("intyme.db")
    cursor = connection.cursor()
    sql_query = "SELECT subject FROM subject_teacher WHERE teacher_id='" + str(id) + "';"
    cursor.execute(sql_query)
    data = cursor.fetchone()
    cursor.close()
    connection.close()
    return data[0]
