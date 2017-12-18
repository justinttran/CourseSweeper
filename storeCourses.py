import os
import urllib
import json
import requests
from bs4 import BeautifulSoup, SoupStrainer
import mysql.connector

semesterString = "SP18"

db_username = os.environ['POCKET_USERNAME']
db_password = os.environ['POCKET_PASSWORD']
db_host = os.environ['POCKET_HOST']

connection = mysql.connector.connect(user=db_username, password=db_password, port=1425, host=db_host)

print ("finished connection")


def get_subject_list(semester):
    api_url = 'https://classes.cornell.edu/api/2.0/config/subjects.json?roster=' + semester

    response = urllib.urlopen(api_url)
    data = json.loads(response.read())

    subject_dict = data['data']['subjects']
    subject_list = []
    for subject_index in range(0, len(subject_dict)):
        subject = subject_dict[subject_index]['value']
        subject_list.append(subject)

    return subject_list

def store_subject_classes(subject):
    api_url = 'https://classes.cornell.edu/api/2.0/search/classes.json?roster=' + semesterString + '&subject=' + subject

    response = urllib.urlopen(api_url)
    data = json.loads(response.read())

    class_list = data["data"]["classes"]

    # print class_list[0]["enrollGroups"]["classSections"][0]

    for eachClass in class_list:
        for enrollGroup in eachClass["enrollGroups"]:
            for section in enrollGroup["classSections"]:
                try:
                    cursor = connection.cursor()
                    query = 'insert into cornellcoursesniper.Courses(subjectCode, courseCode, ssrComponent, sectionNum, courseNum) values(\"%s\", \"%s\", \"%s\", \"%s\", \"%s\");' % (subject, eachClass["catalogNbr"], section["ssrComponent"], section["section"], section["classNbr"])
                    cursor.execute(query)
                    connection.commit()
                finally:
                    print ("Inserted %s %s" % (subject, eachClass["catalogNbr"]))

subjects_list = get_subject_list(semesterString)
for subject in subjects_list:
    store_subject_classes(subject)
print "FINISHED"
