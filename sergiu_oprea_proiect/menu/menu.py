import subprocess
executed = []
pyt = '/home/osboxes/.virtualenvs/NetworkAutomation3/bin/python'
while True:
    print('---MENU---')
    print('0.Press q to quit')
    print('1.Routers preconfig')
    print('2.NetAuto config')
    print('3.FTD preconfig')
    print('4.Routers config')
    print('5.FTD config')
    print('6.Ping test')
    print('7.Check what was done so far')
    option = input('Choose your option: ')
    match option:
        case '0': break
        case '1':
            if 'routers preconfig' not in executed:
                executed.append('routers preconfig')
            prog1 = '/tmp/pycharm_project_13/sergiu_oprea_proiect/telnet_config/router_config.py'
            subprocess.run([f'{pyt}', f'{prog1}'])
        case '2':
            prog2 = '/tmp/pycharm_project_13/sergiu_oprea_proiect/telnet_config/netauto_config.py'
            subprocess.run([f'{pyt}', f'{prog2}'])
            if 'netauto config' not in executed:
                executed.append('netauto config')
        case '3':
            prog3 = '/tmp/pycharm_project_13/sergiu_oprea_proiect/telnet_config/ftd_preconfig.py'
            subprocess.run([f'{pyt}', f'{prog3}'])
            if 'ftd preconfig' not in executed:
                executed.append('ftd preconfig')
        case '4':
            prog4 = '/tmp/pycharm_project_13/sergiu_oprea_proiect/ssh_config/routers_config.py'
            subprocess.run([f'{pyt}', f'{prog4}'])
            if 'routers config' not in executed:
                executed.append('routers config')
        case '5':
            prog5 = '/tmp/pycharm_project_13/sergiu_oprea_proiect/swagger_config/ftd_config.py'
            subprocess.run([f'{pyt}', f'{prog5}'])
            if 'ftd config' not in executed:
                executed.append('ftd config')
        case '6':
            prog6 = '/tmp/pycharm_project_13/sergiu_oprea_proiect/test/inside_ping.py'
            subprocess.run([f'{pyt}', f'{prog6}'])
            if 'test inside_ping' not in executed:
                executed.append('test inside_ping')
        case '7':
            for i in executed:
                print(i)
        case _: continue