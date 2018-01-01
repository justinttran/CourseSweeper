# Course Sweeper

Inspired by Course Sniper at Rutgers University.

Checks the Cornell Course Roster every 15 minutes and sends an email if a course that you are tracking is open (will only send the email once).

Can only update as fast as the Cornell Course Roster does (its fastest update speed is 10 minutes from 6am to 5pm, according to the Roster FAQ).  However, in order to decrease the number of database checks that the system does (so as to not exceed the Free Tier of AWS Database services), I had to increase the amount of time between calls from 10 minutes to 15 minutes.

There may be discrepancies between Student Center and the Course Roster.
