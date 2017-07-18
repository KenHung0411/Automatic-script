
import cx_Oracle
import datetime
import csv

def send_html_email(to_addr,subject,html_text,att_list):

    import smtplib,email,email.encoders,email.mime.text,email.mime.base

    smtpserver = '172.18.1.141'
    to = to_addr
    print to
    fromAddr = 'nsn_oss@nsnoss.com'
    emailMsg = email.MIMEMultipart.MIMEMultipart('alternative')
    emailMsg['Subject'] = subject
    emailMsg['From'] = fromAddr
    emailMsg['To'] = ', '.join(to)
    to = to_addr[0].split(',')
    emailMsg.attach(email.mime.text.MIMEText(html_text,'html'))
    server = smtplib.SMTP(smtpserver)
    print to
    if len(att_list)>0:
        for attach_file in att_list:
            print attach_file
            print 
            fileMsg = email.mime.base.MIMEBase('application','octet-stream')
            fileMsg.set_payload(file(attach_file).read())
            email.encoders.encode_base64(fileMsg)
            fileMsg.add_header('Content-Disposition','attachment;filename='+
                       attach_file.split('/')[-1])
            emailMsg.attach(fileMsg)
    try:
        server.sendmail(fromAddr,to,emailMsg.as_string())
        print 'Email Sent'
    except:
        print 'Error in sending email'
    server.quit() 

def make_blank_html():
    
    to_day = datetime.date.today()
    def_check_date = datetime.datetime.strftime(to_day,'%Y-%m-%d')
    
    html = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" '
    html +='"http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"><html xmlns="http://www.w3.org/1999/xhtml">'
    #html +='<body style="font-size:12px;font-family:Verdana"><p>...</p>'
    html +='<body style="font-size:12px;font-family:Verdana"><p>'
    html +='<br><B>Netact Internal alarms  check at  '+def_check_date+' 10:00 A.M  &nbsp &nbsp </B><br><br><br>'
    
     
    html +='<br><br>'
                
     
    html += '</p>'
    html += "</body></html>"
    return html



def FormatOutput(cursor, name, defaultType, size, precision,scale):
    if defaultType == cx_Oracle.DATETIME:
        return cursor.var(str, 100, cursor.arraysize,outconverter = round_date)

def round_date(dt):
    #print dt
    #print type(dt)
    return dt
    #return datetime.datetime.strftime(dt,'%Y-%m-%d')

   
def main():
    
    
    lrcs = ['lrc1vm4','lrc2vm4','lrc3vm4','lrc4vm4','lrc11vm4','lrc21vm4',
            'wrc1vm4','wrc2vm4','wrc3vm4','wrc4vm4','wrc11vm4','wrc21vm4','vlrc1vm4','wgcvm4']
    #lrcs = ['vlrc1vm4','wgcvm4','lgcldb']
    
    to_day = datetime.date.today()
    def_check_date = datetime.datetime.strftime(to_day,'%Y-%m-%d')
    lrc_port = '1521'
    lrc_sid = 'oss'
    db_user_name = 'rdr'
    db_user_password = 'rdr'
    csv_dir = '/opt/lte_admin/temp/'
    att_list=[]
    email_conf =  '/opt/lte_admin/conf/email_admin.conf'
    email_addr = open(email_conf).readlines()
    email_addr = [i.strip('\n') for i in email_addr]
    
    for rc in lrcs:
	if rc in ['vlrc1vm4','wgcvm4']:
	    db_user_password = 'Oss97531'
	if ('11' in rc)or ('21' in rc):
		out_file_name = csv_dir+rc[0:5]+'_internal_alarms.csv' 
	else:
		out_file_name = csv_dir+rc[0:4]+'_internal_alarms.csv'
	out_file_name = csv_dir+rc[:-3]+'_internal_alarms.csv'
	ofile = open(out_file_name,'w')
        out_csv = csv.writer(ofile,delimiter=',', dialect='excel')
        dsn = cx_Oracle.makedsn(rc,lrc_port,lrc_sid)
        connection = cx_Oracle.connect(db_user_name,db_user_password, dsn)
	connection.outputtypehandler = FormatOutput
        cursor = cx_Oracle.Cursor(connection)
	cursor.execute("alter session set nls_date_format='YYYY/MM/DD HH24:mi:ss'")
        sel_qry = " select f.ALARM_NUMBER,f.alarm_time,f.CANCEL_TIME,f.dn,f.text from fx_alarm f "\
	    " where 1=1 and dn like 'PLMN-PLMN/NETACT%' "\
	    " and f.ALARM_NUMBER not in (30000,30002,30001) "
	
        print sel_qry
	cursor.execute(sel_qry)
	rc_data=cursor.fetchall()
	#print cursor.description
	if len(rc_data) > 0:
	    cols = []
	    for col in cursor.description: cols.append(col[0])
	    out_csv.writerow(cols)
	    for i in rc_data: out_csv.writerow(i)
	else:
	    out_csv.writerow(['No alarms'])
	ofile.close()
	cursor.close()
	connection.close()
        att_list.append(out_file_name)
    print att_list
    
    email_sub = 'Netact internal alarms check'
    html_text = make_blank_html()
    email_sub = ' Netact internal alarms check '+def_check_date
    print email_sub
    send_html_email(email_addr,email_sub,html_text,att_list)




if __name__ == '__main__':
    main()
