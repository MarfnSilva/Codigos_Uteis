# -*- coding: utf-8 -*-
#
#
# Color examples: http://www.htmlcodes.ws/color/html-color-code-generator.cfm?colorName=SeaGreen

from datetime import *
import traceback, threading, os, time

htmlPageHeader = """<!DOCTYPE html>
<meta content="text/html;charset=utf-8" http-equiv="Content-Type">
<script>
var original_html = null;
var filter = '';
function filter_log()
{
    document.body.style.cursor = 'wait';
    if (original_html == null) {
        original_html = document.body.innerHTML;
    }
    if (filter == '') {
        document.body.innerHTML = original_html;
    } else {
        l = original_html.split("<br>");
        var pattern = new RegExp(".*" + filter.replace('"', '\\"') + ".*", "i");
        final_html = '';
        for(var i=0; i<l.length; i++){
            if (pattern.test(l[i]))
                final_html += l[i] + '<br>';
        }
        document.body.innerHTML = final_html;
    }
    document.body.style.cursor = 'default';
}

document.onkeydown = function(event) {
    if (event.keyCode == 76) {
        var ret = prompt("Enter the filter regular expression. Examples:\\n\\n\\
CheckFirmwareUpdate'\\n\\n'ID=1 |ID=2 \\n\\nID=2 .*Got message\\n\\n2012-08-31 16:.*(ID=1 |ID=2 )\\n\\n", filter);
        if (ret != null) {
            filter = ret;
            filter_log();
        }
        return false;
    }
}
</script>
<STYLE TYPE="text/css">
<!--
BODY
{
  color:white;
  background-color:black;
  font-family:monospace, sans-serif;
}
-->
</STYLE>
<body bgcolor="black" text="white">
<font color="white">"""


def trace(Message, userID='', color='white'):
    
    #'''
    #@param userID:
    #@param Message:
    #@return:
    #'''

    print(f"{userID} - {Message}")
    executableName = 'Integra'
    folderName = 'Trace ' + executableName 

    # ---------------------------------- create trace if file below exists ------------------ 
    #enabled_trace = os.path.isfile('Trace' + executableName + 'Enable.txt')
    enabled_trace = os.path.isfile('Trace' + executableName + 'Enable.txt')
    #files = os.listdir()
    #print(files)
    if not enabled_trace:
        return

    #------------------------------------Check if folder exists. If dont >> Create --------------

    os.makedirs(folderName, exist_ok=True)


    f = os.path.isfile(folderName + '/trace.html')
    if f:
        
        #------------------------ Remove oldest file in path ------------
        list_of_files = os.listdir(folderName + '/')
        #print(len(list_of_files))
        if len(list_of_files) > 30:
            try:
                oldest_file = sorted([ folderName + '/' + f for f in os.listdir(folderName)], key=os.path.getctime)[0]
                #print (oldest_file)
                os.remove(oldest_file)
        
            except Exception as ex:
                report_exception(ex)     

        #------------------------- 
        fileMaxSize = 5000000
        size = os.path.getsize(folderName + '/trace.html')
        #print(size)

        if size > fileMaxSize:
            Current_Date = datetime.now().strftime ('%Y-%m-%d_%H_%M_%S')
            os.rename(folderName + '/trace.html', folderName + '/'+ str(Current_Date) + ' - trace.html')
            with open(folderName + "/trace.html", "a", encoding="utf-8") as newfile:
                #with open (folderName + '/trace.html', 'a', encoding="utf-8") as newfile:
                newfile.write(htmlPageHeader)

        with open(folderName + "/trace.html", "a", encoding="utf-8") as myfile:
            myfile.write('\n<br></font><font color="' + str(color) + '">' + str(datetime.now().strftime ('%Y-%m-%d %H:%M:%S.%f'))[:-3] + ' - ' + str(userID) + ' - ' + str(Message))
            myfile.close()

    else:
        with open (folderName + '/trace.html', 'a', encoding="utf-8") as newfile:
            newfile.write(htmlPageHeader)
            newfile.write('\n<br></font><font color="' + str(color) + '">' + str(datetime.now().strftime ('%Y-%m-%d %H:%M:%S.%f'))[:-3] + ' - ' + str(userID) + ' - ' + str(Message))
            newfile.close()


def report_exception(e):
    try:
        t = "{}".format(type(threading.currentThread())).split("'")[1].split('.')[1]
    except IndexError:
        t = 'UNKNOWN'

    trace("", "Bypassing exception at %s (%s)" % (t, e), color="red")
    trace("", "**** Exception: <code>%s</code>" % (traceback.format_exc(),), color="red")


#Message = 'Novo teste'
#writeTrace('', Message) 


