import hpilo

EPC_hosts = [
             ['SAEW03TNES', '172.18.12.146', '79523881'], ['SAEW04TNES', '172.18.12.148', '61035135'],
             ['SAEW05TNES', '172.18.12.150', '07903983'], ['SAEW06TNES', '172.18.12.152', '61942510'], ['SAEW07TNES', '172.18.12.54', '07564893'],
             ['SAEW08TNES', '172.18.12.52', '42391985'], ['SAEW09TNES', '172.18.15.143', '83070550'], ['SAEW10TNES', '172.18.15.145', '21324316'],
             ['SAEW11TNES', '172.18.15.147', '34710780'], ['SAEW12TNES', '172.18.15.169', '47592265'], ['SAEW13TNES', '172.18.15.202', '37813198'] ]

VoLte_hosts = [['VOLTETS', '172.18.30.19', '73772785'],
               ['TASA01TNES', '172.18.55.49', '15986786'],
               ['CSCFA01TNES', '172.18.55.50', '54264822'],
               ['TASW01TNES', '172.18.15.94', '40219399'],
               ['CSCFW01TNES', '172.18.15.95', '14968328']]

def get_host_and_password(host, ip, password):
    print('------------------------------------')
    print('Checking the host: {}'.format(host))
    ilo = hpilo.Ilo(ip,'Administrator', password)
    status = ilo.get_embedded_health()
    result = status['health_at_a_glance']
    return result
    

def Volte_hardware_check():
    
    print('Checking Volte Traffica.....')
    alert = False
    alert_server = list()
    for i in VoLte_hosts:
        result_Volte = get_host_and_password(i[0],i[1],i[2])
        for i in result_Volte:
            print('{} : {}!!!'.format(i, result_Volte[i]['status']))
            if  result_Volte[i]['status'] != 'OK':
                print('Something Wrong in {}, Please login to ckeck and report to HP !!!!!!'.format(i[0]))
                alert_server.append(i[0])
                  
    print('There are {} servers need to be check!!'.format(str(len(alert_server))))
    for k in alert_server:
        print(k) 


def EPC_hardware_check():
    
    print('Checking Volte Traffica.....')
    alert = False
    alert_server = list()
    for i in EPC_hosts:
        result_Volte = get_host_and_password(i[0],i[1],i[2])
        for i in result_Volte:
            print('{} : {}!!!'.format(i, result_Volte[i]['status']))
            if  result_Volte[i]['status'] != 'OK':
                print('Something Wrong in {}, Please login to ckeck and report to HP !!!!!!'.format(i[0]))
                alert_server.append(i[0])
                  
    print('There are {} servers need to be check!!'.format(str(len(alert_server))))
    for k in alert_server:
        print(k) 

##def EPC_hardware_check():
##    
##    print('Checking Volte Traffica.....')
##    alert = False
##    alert_server = list()
##    
##    for i in EPC_hosts:
##        result_EPC = get_host_and_password(i[0],i[1],i[2])
##        for x in result_EPC:
##            for y in  result_EPC[x]:
##                print(x, ' ', y, ':', result_EPC[x][y])
##                if  result_EPC[x]['status'] != 'OK':
##                    print('Something Wrong in {}, Please login to ckeck and report to HP !!!!!!'.format(i[0]))
##                    alert_server.append(i[0])
##                  
##    print('There are {} servers need to be check!!'.format(str(len(alert_server))))
##    for k in alert_server:
##        print(k)
##    return alert_server

        
def main():
    try:
        try:
            status = EPC_hardware_check()
        except hpilo.IloError: 
            print('have wrong password please check....')
            pass
    except hpilo.IloCommunicationError:
        print('have wrong config please check....')
        pass

##    try:
##        try:
##            status = Volte_hardware_check()
##        except hpilo.IloError: 
##            print('have wrong password please check....')
##            pass
##    except hpilo.IloCommunicationError:
##        print('have wrong config please check....')
##        pass
if __name__ == '__main__':
    main()
    
     
