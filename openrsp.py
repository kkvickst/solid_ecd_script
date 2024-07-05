icounter=0
with open('v536r12ver1_Rn_belgianblocks_new_comforttrack_10to30kph_acc.rsp',mode='rb') as f:
    for x in f:
        line = f.readline()
        #print(line)
        icounter+=1
        if icounter>10:
            new = line.decode('utf-64')
            print(new)
    
