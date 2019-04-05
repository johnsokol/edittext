#!/bin/bash 

BASEDIR="/htdocs/edittext"
WORKDIR="/edittext"
THISCGI="/cgi/edittext.cgi"

#echo "<html><body>"

if [ "$REQUEST_METHOD" == "POST" ] ; then
#echo "Content-type: text/plain"
echo "Content-type: text/html"
echo

QS=`cat`
FORMINPUT=`echo $QS |tr '&' '\n' | sed -e 's/+/ /g' -e 's/%2C/,/g' -e 's/%40/@/g' > /tmp/$$.tmp`

#cat /tmp/$$.tmp

#FORMINPUT=`sed -e 's/\&/--\n--/g'`

#CDOWN=`awk -F'=' '/countdown/ { print $2 }'  /tmp/$$.tmp`

TEXT=`awk -F'=' '/limitedtextarea/ { print $2 }' /tmp/$$.tmp | sed -e 's/%0D/NEWLINE/g' -e 's/%0A//g'`
CNT=`awk -F'=' '/filename/ { print $2 }'  /tmp/$$.tmp`
SUBJECT=`awk -F'=' '/subject/ { print $2 }'  /tmp/$$.tmp`

if [ -s /tmp/$$.tmp ] ; then
  rm /tmp/$$.tmp
fi

#echo "$QS"
FNAME="FILE$CNT.html"


sed -e 's/INITIALTEXT/'"$TEXT"'/'  $BASEDIR/edit1.tmpl |\
sed -e 's/SUBJECT/'"$SUBJECT"'/' |\
sed -e 's/FILENAME/'"$CNT"'/' |\
sed -e 's!VIEWPAGE!'"$WORKDIR/$FNAME"'!' |\
sed -e 's/NEWLINE/\n/g'  




QSS=`echo "$QS" | sed -e 's/\&/\\\\&/g'`
sed -e 's/^INITIALTEXT.*/'"$TEXT"'/'  $BASEDIR/text1.tmpl |\
sed -e 's/^DATALINE.*/DATALINE '$QSS'/' |\
sed -e 's/SUBJECT/'"$SUBJECT"'/' |\
sed -e 's!^LISTINGDATA.*!LISTINGDATA <a href="'$WORKDIR/$FNAME'">'"$SUBJECT"'</a>, \&nbsp; \&nbsp; <a href="/cgi/edittext.cgi?name='$CNT'">edit</a>!' |\
sed -e 's/NEWLINE/\n/g'   > $BASEDIR/$FNAME

$BASEDIR/makeindex

else
###################################################
#################  GET  ###########################
###################################################

echo "Content-type: text/html"
#echo "Content-type: text/plain"
echo

echo $QUERY_STRING | grep "name="  > /dev/null
if [ "$?" -eq 0 ] ; then
#echo "with data posted"

   CNT=`echo $QUERY_STRING | sed -e 's/.*=//'`
   FNAME="FILE$CNT.html"

   grep "^DATALINE" $BASEDIR/$FNAME | sed -e 's/^DATALINE //' |tr '&' '\n' | sed -e 's/+/ /g' -e 's/%2C/,/' -e 's/%40/@/g'  > /tmp/$FNAME
 
   TEXT=`awk -F'=' '/limitedtextarea/ { print $2 }' /tmp/$FNAME| sed -e 's/+/ /g'`
   CNTx=`awk -F'=' '/filename/ { print $2 }'  /tmp/$FNAME`
   SUBJECT=`awk -F'=' '/subject/ { print $2 }'  /tmp/$FNAME`

#echo "<br>"
#cat  /tmp/$FNAME
#echo "<br>"
#echo "sss $TEXT, $CNTx  , $SUBJECT"

else
#echo "without data posted"

CNT=`cat $BASEDIR/count`
CNT=$[$CNT+1]
echo $CNT > $BASEDIR/count
#echo $CNT

#FORMINPUT=`tr '&' '\n' > /tmp/$FNAME`

fi

FNAME="FILE$CNT.html"

#echo "past parse $FNAME"

sed -e 's/INITIALTEXT/'"$TEXT"'/'  $BASEDIR/edit1.tmpl |\
sed -e 's/SUBJECT/'"$SUBJECT"'/' |\
sed -e 's!VIEWPAGE!'"$WORKDIR/$FNAME"'!' |\
sed -e 's/FILENAME/'"$CNT"'/' |\
sed -e 's/%0D/\n/g' -e 's/%0A//g' 


echo $FNAME

if [ -s /tmp/$FNAME ] ; then
  rm /tmp/$FNAME
fi



#echo ----------------------
#echo REQUEST_METHOD = $REQUEST_METHOD
#echo -----------SET-----------
#set
#echo -----------SET-ENV----------
#setenv

fi



# echo SERVER_SOFTWARE = $SERVER_SOFTWARE
# echo SERVER_NAME = $SERVER_NAME
# echo GATEWAY_INTERFACE = $GATEWAY_INTERFACE
# echo SERVER_PROTOCOL = $SERVER_PROTOCOL
# echo SERVER_PORT = $SERVER_PORT
# echo REQUEST_METHOD = $REQUEST_METHOD
# echo HTTP_ACCEPT = "$HTTP_ACCEPT"
# echo PATH_INFO = "$PATH_INFO"
# echo PATH_TRANSLATED = "$PATH_TRANSLATED"
# echo SCRIPT_NAME = "$SCRIPT_NAME"
# echo QUERY_STRING = "$QUERY_STRING"
# echo REMOTE_HOST = $REMOTE_HOST
# echo REMOTE_ADDR = $REMOTE_ADDR
# echo REMOTE_USER = $REMOTE_USER
# echo AUTH_TYPE = $AUTH_TYPE
# echo CONTENT_TYPE = $CONTENT_TYPE
# echo CONTENT_LENGTH = $CONTENT_LENGTH
# echo
# echo HTTP_REFERER = $HTTP_REFERER
# echo -----------SET-----------
# set
# echo -----------SET-ENV----------
# setenv
# echo ------------------
# echo REQUEST_URI = $REQUEST_URI
# echo HTTP_HOST = $HTTP_HOST
# echo ---------stdin---------
# cat
# 
