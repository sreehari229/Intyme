from Intyme import intyme
from flask import render_template, request, redirect, session, flash
from Intyme.functions import *


@intyme.route("/add_student", methods=["POST","GET"])
def add_student():
    if "id" in session:
        id = session["id"]
        g_value = 'p'
        o_value = 'p'
        p_value = 'p'
        r_value = 'p'
        if request.method == "POST":
            try:
                gender = request.form["gender"]
                class_v = request.form["class"]
                section = request.form["section"]
            except:
                flash(" Choose the options", "warning")
                g_value = 'non'
            username = request.form["name"]
            regno = request.form["regno"]
            year = request.form["year"]
            course = request.form["course"]
            email = request.form["email"]
            mobile = request.form["mobile"]
            dob = request.form["dob"]
            address = request.form["address"]
            password = generatePassword()
            #print(username,regno,gender,class_v,section,year,course,email,mobile,dob,address,photo,password)

            check = [username, regno, year, course, email, mobile, dob, address, password]
            if check_if_empty(check):
                o_value = 'non'
                flash(" Fill in all the values","danger")
            if request.files:
                photo = request.files["photo"]
                print(photo)
                try:
                    photo.save(os.path.join(intyme.config["IMAGE_UPLOADS"],photo.filename))
                except:
                    flash(" No file uploaded","warning")
                    p_value = 'non'

            if regno_exists(regno):
                flash(" Register Number already exists","danger")
                r_value = 'non'

            if g_value == 'non' or o_value == 'non' or p_value == 'non' or r_value == 'non':
                print("Retry")
            else:
                data = [username, regno, gender, class_v, section, year, course, email, mobile, dob, address, password, photo.filename]
                print(data)
                store_student_db(data)
                send_notifications(email,"RegID:"+ str(regno) + " ,Password:" + str(password))
                flash(" Student Created, RegID:"+ str(regno) + " , Password:" + str(password),"success")


        return render_template("teacher_add_student.html", id=id)
    else:
        return redirect("/login")


@intyme.route("/send_mails", methods=["POST","GET"])
def send_mails():
    if "id" in session:
        id = session["id"]
        if request.method == "POST":
            students = request.form.getlist('students')
            msg = request.form["msg"]
            for i in students:
                send_notifications(i,msg)
            flash(" Email Sent...")
        data = get_data_for_email()
        return render_template("teacher_send_mail.html",id=id, data=data)
    else:
        return redirect("/login")


@intyme.route("/teacher_check_attendance")
def teacher_check_attendance():
    if "id" in session:
        id = session["id"]
        data = teacher_check_attendance_db(id)
        BCA6_A = data[0]
        BCA6_B = data[1]
        return render_template("teacher_check_attendance.html", id=id, data=data, BCA6_A=BCA6_A, BCA6_B=BCA6_B)
    else:
        return redirect("/login")

@intyme.route("/teacher_attendance_claim")
def teacher_attendance_claim():
    if "id" in session:
        id = session["id"]
        data = retrive_missed_form(id)
        x = 0
        for i in data:
            with open(os.path.join(intyme.config["IMAGE_UPLOADS"],str(x)+".jpg"), 'wb') as f:
                f.write(i[-1])
                x = x + 1
        d1 = list()
        for i in data:
            d1.append(list(i))
        x=0
        for i in d1:
            i.pop()
            i.append(str(x)+".jpg")
            x = x+1
        data = d1
        print(data)

        return render_template("teacher_attendance_claim.html", id=id, data=data)
    else:
        return redirect("/login")

@intyme.route("/medical_approval", methods=["GET","POST"])
def medical_approval():
    if "id" in session:
        id = session["id"]
        if request.method == "POST":
            d_id = request.form["id"]
            d_type = request.form["type"]
            d_reason = request.form["reason"]
            approve_attendance(d_id,d_type,d_reason)
            flash(" Attendance approved")
        return redirect("/teacher_attendance_claim")
    else:
        return redirect("/login")

@intyme.route("/document/<name>")
def document(name):
    if "id" in session:
        id = session["id"]
        return render_template("document.html",id=id, name=name)
    else:
        return redirect("/login")

@intyme.route("/teacher_absence")
def teacher_absence():
    if "id" in session:
        id = session["id"]
        sub_name = retrive_subject_name_from_teacherid(id)

        subject = ''
        if sub_name == 'daa':
            subject = 'DAA'
        elif sub_name == 'adbms':
            subject = 'ADBMS'
        data = retrive_teacher_absence(subject)
        det = list()
        for i in data:
            det.append(list(i))

        a_section = list()
        b_section = list()
        for i in det:
            info = retrive_personal(i[0])
            i.insert(1, info["username"])
            if info["section"] == "A":
                a_section.append(i)
            else:
                b_section.append(i)
        print(a_section,b_section)
        return render_template("teacher_absence.html",id=id, a_section=a_section, b_section=b_section)
    else:
        return redirect("/login")