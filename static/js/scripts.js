function buttonPressed(){
  var officialCourseId = document.getElementById("idInput").value;
  var email = document.getElementById("emailInput").value;
  email = email.replace("@", "%40");
  if (email == ""){
    alert("Invalid email.  Please try again.")
    return;
  }
  if (officialCourseId == ""){
    officialCourseId = pass_to_get_courseNum();
  }

  if (courseid_exists(officialCourseId).length == 0 || email == ""){
    alert("Invalid course id or email.  Please try again.");
    return;
  }
  else{
    store_email_with_coursenum(email, officialCourseId);
    document.getElementById("subjectInput").value = "";
    document.getElementById("coursenumInput").value = "";
    document.getElementById("ssrInput").value = "";
    document.getElementById("sectionInput").value = "";
    document.getElementById("idInput").value = "";
    document.getElementById("emailInput").value = "";

    alert("Successfully submitted!");
    return;
  }
}

function pass_to_get_courseNum(){
  subject = document.getElementById("subjectInput").value;
  coursecode = document.getElementById("coursenumInput").value;
  ssrC = document.getElementById("ssrInput").value;
  sectionNum = document.getElementById("sectionInput").value;
  if (subject == "" || coursecode == "" || ssrC == "" || sectionNum == ""){
    num = get_courseNum("blank", "blank", "blank", "blank");
  }
  else{
    num = get_courseNum(subject, coursecode, ssrC, sectionNum);
  }

  //num[0] is either undefined (aka course doesn't exist)
  //or has length of 1, where num[0][0] is the coursenum itself
  if (num[0] == 'undefined'){
    return null;
  }
  else{
    return num[0];
  }
}


//******************************************************************
function get_courseNum(subject, courseCode, ssr, sectionNum) {
    var xhr = new XMLHttpRequest();
    xhr.open("GET", 'https://coursesweeper.herokuapp.com/getNum/' + subject + '/' + courseCode + '/' + ssr + '/' + sectionNum, false);
    xhr.setRequestHeader("Content-Type", "application/json");
    xhr.send(null);
    return JSON.parse(xhr.responseText);
}

function store_email_with_coursenum(email, coursenum){
    var obj = {"email" : email, "coursenum" : coursenum};
    var xhr = new XMLHttpRequest();
    xhr.open("POST", 'https://coursesweeper.herokuapp.com/store/' + email + '/' + coursenum, true);
    xhr.setRequestHeader("Content-Type", "application/json")
    console.log(JSON.stringify(obj));
    xhr.send(JSON.stringify(obj));
}

function courseid_exists(courseid){
  var xhr = new XMLHttpRequest();
  xhr.open("GET", 'https://coursesweeper.herokuapp.com/exists/' + courseid, false);
  xhr.setRequestHeader("Content-Type", "application/json");
  xhr.send(null);
  return JSON.parse(xhr.responseText);
}
