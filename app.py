from flask import Flask, render_template, g, jsonify, request
import os
import mysql.connector
import requests
from bs4 import BeautifulSoup, SoupStrainer
import atexit
from apscheduler.scheduler import Scheduler
from flask import Flask
import logging
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
import smtplib

logging.basicConfig()

app = Flask(__name__)

scheduler = Scheduler()

@scheduler.interval_schedule(hours=0.25)
def some_job():
    with app.app_context():
        with app.test_request_context():
            emails_and_codes = get_emails_and_codes()
            for userRow in emails_and_codes:
                subject = get_subject_from_courseid(userRow["coursenum"])

                subjectpage = get_web_page_from_subjectcode(subject)
                state = open_status_from_coursenum(userRow["coursenum"], subjectpage)

                if (state == "Open"):
                    send_email(userRow["email"], userRow["coursenum"])
                    remove_email_and_id(userRow["email"], userRow["coursenum"])
                    print('Email sent to ' + userRow["email"] + " about " + userRow["coursenum"])


def send_email(emailee, courseNum):
    fromAddr = os.environ['POCKET_EMAIL']
    toAddr = emailee
    msg = MIMEMultipart()
    msg['From'] = fromAddr
    msg['To'] = toAddr
    msg['Subject'] = "Course " + courseNum + " is open!"

    body = "Your course is open!"
    msg.attach(MIMEText(body, 'plain'))

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(os.environ['POCKET_EMAIL'], os.environ['POCKET_EMAIL_PASSWORD'])
    text = msg.as_string()
    server.sendmail(fromAddr, toAddr, text)

scheduler.start()


db_username = os.environ['POCKET_USERNAME']
db_password = os.environ['POCKET_PASSWORD']
db_host = os.environ['POCKET_HOST']
db_port = os.environ['POCKET_PORT']

semesterString = "SP18"

#Taken from Flask's tutorial on database connections
def get_db():
    if not hasattr(g, 'db'):
        g.db = mysql.connector.connect(user = db_username, password = db_password, port = db_port, host = db_host)
    return g.db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        g.db.close()

@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('index.html')

@app.route('/store/<email>/<coursenum>', methods=['GET', 'POST'])
def store_email_with_coursenum(email, coursenum):
    data = request.get_json(force=True)
    email = data['email']
    email = email.replace("%40", "@")
    coursenum = data['coursenum']

    connection = get_db()
    cursor = connection.cursor()
    query = 'insert ignore into cornellcoursesniper.Users(email, coursenum) values (\"' + email + '\", \"' + coursenum + '\")'
    cursor.execute(query)
    connection.commit()
    return jsonify({'success' : 'true'})

@app.route('/getNum/<sub>/<course>/<ssr>/<sec>')
def get_courseNum_from_details(sub, course, ssr, sec):
    connection = get_db()
    cursor = connection.cursor()
    query = 'select courseNum from cornellcoursesniper.Courses where subjectCode = \"' + sub + '\" and courseCode = \"' + course + '\" and ssrComponent = \"' + ssr + '\" and sectionNum = \"' + sec + '\"'
    cursor.execute(query);
    result = cursor.fetchone()
    if (result == None):
        return ""
    final_result = str(list(result)[0])
    return final_result

@app.route('/exists/<courseid>')
def courseid_exists(courseid):
    connection = get_db()
    cursor = connection.cursor()
    query = 'select * from cornellcoursesniper.Courses where courseNum = \"' + courseid + '\"'
    cursor.execute(query);
    result = cursor.fetchall()
    return jsonify(result)

def get_subject_from_courseid(courseid):
    connection = get_db()
    cursor = connection.cursor()
    query = 'select subjectCode from cornellcoursesniper.Courses where courseNum = \"' + courseid + '\"'
    cursor.execute(query);
    result = cursor.fetchone()
    if (result == None):
        return ""
    final_result = str(list(result)[0])
    return final_result

def remove_email_and_id(email, courseid):
    connection = get_db()
    cursor = connection.cursor()
    query = 'delete from cornellcoursesniper.Users where email = \"' + email + '\"' + ' and coursenum = \"' + courseid + '\"'
    cursor.execute(query);
    connection.commit()
    return "Deleted!"

def get_emails_and_codes():
    connection = get_db()
    cursor = connection.cursor()
    cursor.execute('select * from cornellcoursesniper.Users')
    result = []
    mysql_result = cursor.fetchall()
    for user_set in mysql_result:
        result.append({'email' : user_set[0], 'coursenum' : user_set[1]})
    return result


def get_web_page_from_subjectcode(subjectcode):
    courses_url = 'https://classes.cornell.edu/browse/roster/' + semesterString + '/subject/' + subjectcode
    request_page = requests.get(courses_url)

    page_text = BeautifulSoup(request_page.text, 'html.parser')
    return page_text

# def get_course_div_from_coursecode(coursecode, subjectpage):
#     course_div = subjectpage.findAll("div", {"data-catalog-nbr" : coursecode})
#     return course_div

def open_status_from_coursenum(coursenum, subjectpage):
    c_num = "c" + coursenum
    # group_div = subjectpage.find("a", {"id" : c_num})
    strong_obj = subjectpage.find("strong", {"data-content" : coursenum})
    ul_obj = strong_obj.parent.parent.parent

    status_span = ul_obj.find("li", {"class" : "open-status"}).find("span")
    return status_span["data-content"]

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port, use_reloader=False)
    # app.run(debug=True, use_reloader=False)
