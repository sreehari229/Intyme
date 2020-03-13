from Intyme import intyme
from flask import render_template, request, redirect,session, flash
from Intyme.functions import *
import os
import shutil

@intyme.route("/mark_attendance")
def mark_attendance():
    if "id" in session:
        id = session["id"]
        capture_image()
        source = os.getcwd().replace("\\", "/") + '/test_image.jpg'
        destination = os.getcwd().replace("\\", "/") + "/Intyme/static/profile/images"
        des = destination + "/test_image.jpg"
        if os.path.exists(des):
            os.remove(des)
        if os.path.exists(source):
            dest = shutil.move(source, destination)
        timetable_data = student_ttable(id)
        type = retrive_type(id)
        type = type[0]
        dt = time_fn()
        loc = location()
        return render_template("student_mark_attendance.html", id=id, timetable_data=timetable_data, type=type, dt=dt, loc=loc)
    else:
        return redirect("/login")

@intyme.route("/report")
def report():
    if "id" in session:
        id = session["id"]
        result = faceRecognition()
        time = time_fn()
        loc = location()
        timetable_data = student_ttable(id)
        type = retrive_type(id)
        type = str(type[0])
        return render_template("student_report.html",
                               id=id, result=result, update_value_attendance_present=update_value_attendance_present,
                               time=time, loc=loc, time_check=time_check, retrive_subject=retrive_subject,
                               attendance_sheet_update=attendance_sheet_update, timetable_data=timetable_data,
                               type=type)
    else:
        return redirect("/login")


@intyme.route("/missed_form", methods=["POST","GET"])
def missed_form():
    if "id" in session:
        id = session["id"]
        o_value = 's'
        d_value = 's'
        timetable_data = student_ttable(id)
        type = retrive_type(id)
        type = type[0]
        if request.method == "POST":
            try:
                subject = request.form["subject"]
                from_date = request.form["from"]
                to_date = request.form["to"]
                r_type = request.form["r_type"]
                reason = request.form["reason"]
            except:
                o_value = 'n'
                flash(" Enter all the values.","warning")
            if request.files:
                docsf = request.files["docsf"]
                try:
                    docsf.save(os.path.join(intyme.config["IMAGE_UPLOADS"],docsf.filename))
                except:
                    d_value = 'n'
                    flash(" No supporting documents uploaded", "danger")

            if o_value == 'n' or d_value == 'n':
                print("Error")
            else:
                store_missed_form_db(id,subject,from_date,to_date,r_type,reason,docsf.filename)
                flash(" Form submitted", "success")
                print(from_date,to_date)
                print(docsf.filename)


        return render_template("student_missed_form.html", id=id, timetable_data=timetable_data, type=type)
    else:
        return redirect("/login")


@intyme.route("/check_attendance")
def check_attendance():
    if "id" in session:
        id = session["id"]
        result = check_attendance_from_db(id)
        timetable_data = student_ttable(id)
        type = retrive_type(id)
        type = type[0]
        subject = list()
        conducted = list()
        present = list()
        for i in result:
            subject.append(i[0])
            conducted.append(i[1])
            present.append(i[2])
        total_c = sum(conducted)
        total_p = sum(present)
        per = (total_p/total_c) * 100
        print(per)
        return render_template("student_check_attendance.html", id=id, result=result, timetable_data=timetable_data, type=type,
                               total_p=total_p, total_c=total_c, per=per)
    else:
        return redirect("/login")

@intyme.route("/graphs_charts")
def graphs_charts():
    if "id" in session:
        id = session["id"]
        timetable_data = student_ttable(id)
        data = check_attendance_from_db(id)
        type = retrive_type(id)
        type = type[0]
        print(data)
        subject = list()
        conducted = list()
        present = list()
        colours = list()
        for i in data:
            subject.append(i[0])
            conducted.append(i[1])
            present.append(i[2])
        print(subject,conducted,present)
        for i in range(len(subject)):
            colours.append(random_color())
        return render_template("student_graphs.html",id=id, subject=subject, conducted=conducted, present=present,
                               colours=colours, timetable_data=timetable_data,type=type)
    else:
        return redirect("/login")

@intyme.route("/student_absence")
def student_absence():
    if "id" in session:
        id = session["id"]
        type = retrive_type(id)
        timetable_data = student_ttable(id)
        type = type[0]
        data = retrive_student_absence(id)
        return render_template("student_absence.html",id=id, data=data, type=type, timetable_data=timetable_data)
    else:
        return redirect("/login")