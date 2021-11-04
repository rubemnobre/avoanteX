# Programmed for a modified version of AVL. The source code can be found in https://github.com/rubemnobre/avl-mod

import re
import subprocess

pi = 3.14159265358

def avl_results(avl_text, command): # CM0, CL0, CLa, CMa, Xnp
    process = subprocess.Popen(['./avl.exe'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
    if command[0] == 'solo':
        out = process.communicate(bytes('load\n%s\noper\na a %.3f\nx\nst\n\nquit\n' % (avl_text, command[1]), 'utf-8'))[0]
    if command[0] == 'alpha':
        out = process.communicate(bytes('load\n%s\noper\na a %.3f\nx\nst\n\nquit\n' % (avl_text, command[1]), 'utf-8'))[0]
    if command[0] == 'trim':
        out = process.communicate(bytes('load\n%s\noper\na pm %.3f\nx\nst\n\nquit\n' % (avl_text, 0), 'utf-8'))[0]
        
    process.terminate()
    output = out.decode('utf-8')
    results = dict()
    
    match = re.search(r'Execute flow calculation first!', output)
    if match:
        return None
    else:
        match = re.search(r'Alpha =..........', output)
        if match == None:
            print(output)
        results['Alpha'] = float(output[match.start() + 7:match.start() + 17])

    match = re.search(r'(Cmtot =..........)', output)
    results['CM'] = float(output[match.start() + 7:match.start() + 17])

    match = re.search(r'(CLtot =..........)', output)
    results['CL'] = float(output[match.start() + 7:match.start() + 17])

    match = re.search(r'(CLa =...........)', output)
    results['CLa'] = float(output[match.start() + 7:match.start() + 17]) * pi/180

    match = re.search(r'(Cma =...........)', output)
    results['CMa'] = float(output[match.start() + 7:match.start() + 17]) * pi/180

    match = re.search(r'(Cmq =...........)', output)
    results['CMq'] = float(output[match.start() + 7:match.start() + 17]) * pi/180

    match = re.search(r'(Cnb =...........)', output)
    results['Cnb'] = float(output[match.start() + 7:match.start() + 17]) * pi/180

    match = re.search(r'(Cnr =...........)', output)
    results['Cnr'] = float(output[match.start() + 7:match.start() + 17]) * pi/180

    match = re.search(r'(Xnp =...........)', output)
    results['Xnp'] = float(output[match.start() + 7:match.start() + 17])

    match = re.search(r'(CDtot =...........)', output)
    results['CD'] = float(output[match.start() + 7:match.start() + 17])

    return results