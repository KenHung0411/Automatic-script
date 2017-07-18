
import cx_Oracle
import datetime
import csv

def FormatOutput(cursor, name, defaultType, size, precision,scale):
    if defaultType == cx_Oracle.DATETIME:
        return cursor.var(str, 100, cursor.arraysize,outconverter = round_date)

def round_date(dt):
    print dt
    print type(dt)
    return dt
    #return datetime.datetime.strftime(dt,'%Y-%m-%d')

   
def main():
    
    
    lrcs = ['lrc1vm4','lrc2vm4','lrc3vm4','lrc4vm4']
    #lrcs = ['lrc1vm4']
    
    lrc_port = '1521'
    lrc_sid = 'oss'
    db_user_name = 'rdr'
    db_user_password = 'rdr'
    csv_dir = '/opt/lte_admin/output/'
    
    for rc in lrcs:
	out_file_name = csv_dir+rc[0:4]+'_'+datetime.datetime.strftime(datetime.datetime.now(),"%Y%m%d_%H%M")+'.csv'
	ofile = open(out_file_name,'w')
        out_csv = csv.writer(ofile,delimiter=',', dialect='excel')
        dsn = cx_Oracle.makedsn(rc,lrc_port,lrc_sid)
        connection = cx_Oracle.connect(db_user_name,db_user_password, dsn)
	connection.outputtypehandler = FormatOutput
        cursor = cx_Oracle.Cursor(connection)
	cursor.execute("alter session set nls_date_format='YYYY/MM/DD HH24:mi:ss'")
        sel_qry = "select * from fx_alarm f where f.CANCELLED_BY='omc' and dn like 'PLMN-PLMN/MRBTS%'"\
            " and f.ACKED_BY='WITHCANCEL' and f.CANCEL_TIME >= (sysdate-1/24)"
	
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
        






if __name__ == '__main__':
    main()
