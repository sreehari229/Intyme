from Intyme import intyme
from Intyme.functions import *
from flask import render_template, request, redirect, session, flash
import sqlite3
import os
import shutil

@intyme.route("/", methods=["GET","POST"])
def home():
    #Contact Form
    if request.method == "POST":
        connection = sqlite3.connect("intyme.db")
        cursor = connection.cursor()
        cursor.execute("INSERT INTO contact_form(first_name, last_name, email, subject, message) VALUES (?,?,?,?,?)",( request.form["fname"] , request.form["lname"] , request.form["email"] , request.form["subject"] , request.form["message"] ))
        connection.commit()
        cursor.close()
        connection.close()
    return render_template("home.html")


@intyme.route("/login", methods=["POST","GET"])
def login():
    if request.method == "POST":
        id = request.form["id"]
        password = request.form["pass"]
        connection = sqlite3.connect('intyme.db')
        cursor = connection.cursor()
        try:
            sql_query = "SELECT id,password,type FROM login_details where id=" + str(id) + ";"
            cursor.execute(sql_query)
            data = cursor.fetchone()

            if data == None:
                print("\nResult: No Student found with register number", id)
                flash(" Register number not found")
                return redirect(request.url)
            else:
                if data[1] != password:
                    print("\nResult: Invalid Password")
                    flash(" Invalid Password")
                    return redirect(request.url)
                else:
                    print("\nResult: Welcome", data[0])
                    session["id"] = id
                    print(id)
                    return redirect("/user")
        except:
            print("Login Error")
            flash(" Enter a valid ID")
            return redirect("/login")

        cursor.close()
        connection.close()
    else:
        if "id" in session:
            return redirect("/user")
        return render_template("login.html")


@intyme.route("/user")
def user():
    if "id" in session:
        id = session["id"]
        type = retrive_type(id)
        write_picture(retrive_picture(id))
        source = os.getcwd().replace("\\", "/") + '/person.jpg'
        destination = os.getcwd().replace("\\", "/") + "/Intyme/static/profile/images"
        des = destination + "/person.jpg"
        if os.path.exists(des):
            os.remove(des)
        if os.path.exists(source):
            dest = shutil.move(source, destination)
        if 'student' in type:
            print(type)
            p_data = retrive_personal(id)
            timetable_data = student_ttable(id)
            type = type[0]
            print(type)
            return render_template("student_home.html", id=id, p_data=p_data, timetable_data=timetable_data, type=type)
        else:
            t_data = retrive_teacher_details(id)
            return render_template("teacher_home.html",id=id, t_data=t_data)
    else:
        return redirect("/login")


@intyme.route("/logout")
def logout():
    file = os.getcwd().replace("\\","/") + "/Intyme/static/profile/images/"
    if os.path.exists(file+"person.jpg"):
        os.remove(file+"person.jpg")
    if os.path.exists(file+"test_image.jpg"):
        os.remove(file+"test_image.jpg")
    session.pop("id", None)
    return redirect("/")

