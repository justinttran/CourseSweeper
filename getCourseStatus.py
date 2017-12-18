import requests
from bs4 import BeautifulSoup, SoupStrainer

semesterString = "SP18"

def get_web_page_from_subjectcode(subjectcode):
    courses_url = 'https://classes.cornell.edu/browse/roster/' + semesterString + '/subject/' + subjectcode
    request_page = requests.get(courses_url)

    page_text = BeautifulSoup(request_page.text, 'html.parser')
    return page_text

def get_course_div_from_coursecode(coursecode, subjectpage):
    course_div = subjectpage.findAll("div", {"data-catalog-nbr" : coursecode})
    return course_div

def open_status_from_coursenum(coursenum, subjectpage):
    c_num = "c" + coursenum
    group_div = subjectpage.find("a", {"id" : c_num})
    li_obj = group_div.parent.find("li", {"class" : "open-status"})
    status_span = li_obj.find("span")
    return status_span["data-content"]

page = get_web_page_from_subjectcode("AEM")

# get_course_div_from_coursecode(1100, page)

print open_status_from_coursenum("15217", page)
