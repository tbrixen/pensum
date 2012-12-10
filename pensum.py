# -*- coding: ISO-8859-1 -*-
import urllib, urllib2, cookielib, re, sys
from time import gmtime, strftime

#######################
####### Config ########
#######################

#Change into your credentials
user = '';
passw = '';

#Do you want a log file?
log = 0;
def correctLogin(html):
    #check if the heading Login appears.
    #If it does, the user is not succesfully logged in.
    errorStringRegex = re.compile("<h1>Login</h1>")
    result = errorStringRegex.search(html)
    if result:
        sys.exit('Wrong username or password')

def refreshBooks(username, password):

    ########################
    ###### Get cookie ######
    ########################

    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    login_data = urllib.urlencode({'username' : username, 'userpw' : password})
    opener.open('http://www.pensum.dk/login.php', login_data)
    resp = opener.open('http://www.pensum.dk/brugtliste.php')
    brugtlisteHTML = resp.read()

    correctLogin(brugtlisteHTML)
    ########################
    ###### Get books #######
    ########################

    #Getting html for book-ID's on the form:
    #<input type="checkbox" name="userbookid[]" value="1234567">
    bookIdHTMLRegex = re.compile("<input type=\"checkbox\" name=\"userbookid\[\]\" value=\"[0-9]{,}\"")
    bookHTML = bookIdHTMLRegex.findall(brugtlisteHTML)

    #Getting the ID's
    bookIDs = []
    bookIDRegex = re.compile("[0-9]{7}")
    for x in bookHTML:
    	bookIDs.extend(bookIDRegex.findall(x))

    ########################
    ## Sending the update ##
    ########################

    #Creating the HTTP request
    extendBooksData = urllib.urlencode({'fldAction' : '10', 'updateMany' : 'Opdater', 'submitted' : 'true'})
    #for each book, add to the request:
    for x in bookIDs:
    	extendBooksData += "&" + urllib.urlencode({'userbookid[]' : x})

    #Send request
    extendedRespHTML = opener.open('http://www.pensum.dk/brugtliste.php', extendBooksData)

    ########################
    ### Printing to promt ##
    ########################

    #Print the response from pensum
    promtRespRegEx = re.compile("[0-9]{,} blev opdateret")
    promtResp = promtRespRegEx.findall(extendedRespHTML.read())
    print promtResp[0] + ":"

    #Print the names of the books:
    #Getting the names
    #Patteren: title="Se annoncen"><h3 style="padding: 0px;">C++ for Dummies</h3></a>
    bookNameHTMLRegex = re.compile("title=\"Se annoncen\"><h3 style=\"padding: 0px;\">.*</h3></a>")
    bookNameHTML = bookNameHTMLRegex.findall(brugtlisteHTML)

    #Getting and printing the names
    bookNameRegex = re.compile("0px;\">.{1,}</h3>")
    for x in bookNameHTML:
    	s = bookNameRegex.findall(x)
    	name = s[0]
    	print "\t" + name[6:-5]


    ########################
    ######## Logfile #######
    ########################
    if(log == 1):
        s = strftime("%Y-%m-%d %H:%M:%S", gmtime()) + ": " + promtResp[0] + "\n"
        f = open('pensum.log', 'a')
        f.writelines(s)
        f.close()


if __name__ == '__main__':
    if(len(sys.argv) != 1 and len(sys.argv) != 3):
        sys.exit('Usage: pensum.py [username password]');

    #Get user and password from commandline if provided
    if(len(sys.argv) == 3):
        user = sys.argv[1]
        passw = sys.argv[2]

    if(user == '' or passw == ''):
        sys.exit('You need to configure the script')
    #Call the def
    refreshBooks(user, passw)
