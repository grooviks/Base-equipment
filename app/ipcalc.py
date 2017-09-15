def network(subnet):
        network = []
        addrlist = subnet.net.split(".")
        for i in range(4):
            network.append(int(addrlist[i]) & mask(subnet)[i])
        return network

def mask(subnet):
    msk = [0,0,0,0]
    for i in range(int(subnet.cidr)):
        msk[i//8] = msk[i//8] + (1 << (7 - i % 8))
    return msk

def reverse(subnet):
    rev = mask(subnet)
    for i in range(4):
        rev[i] = ~ rev[i] & 0xFF
    return rev

def broadcast(subnet):
    broadcast = []
    net = network(subnet)
    rev = reverse(subnet)
    for i in range(4):
        broadcast.append(int(net[i])  | int(rev[i]))
    return broadcast

def first_addr(subnet):
    b = broadcast(subnet)
    net = network(subnet)
    f = []
    for i in range(4):
        if net[i] == b[i]:
            f.append(net[i])
        else:
            b[i] = ~ b[i] & 0xFF
            if i == 3 :
                f.append(net[i]+1)
            else:
                f.append(net[i])
    return f

def last_addr(subnet):
    last_from_broadcast = broadcast(subnet)
    last_from_broadcast[-1] = last_from_broadcast[-1] & 0xFE
    return last_from_broadcast

def hosts(subnet):
    binmask = ''.join([bin(octet)[2:].zfill(8) for octet in mask(subnet)])
    count = 0
    for i in binmask: 
        if i == '0':
            count+=1
    return 2**count-2 

def check_ip(subnet):
    try:
        valid = subnet.split(".")
    except:
        print ("Invalid address!")
        return False
    if len(valid) != 4:
        print ("Invalid address! Count octet != 4")
        return False
    for octet in valid: 
        if 0 > int(octet) > 255: 
            print ("Bad octet", octet)
            return False
    return True


#def undotIPv4 (dotted):
#    return sum (int (octet) << ( (3 - i) << 3) for i, octet in enumerate (dotted.split ('.') ) )

#def dotIPv4 (addr):
#    return '.'.join (str (addr >> off & 0xff) for off in (24, 16, 8, 0) )

#def rangeIPv4 (start, stop):
#    for addr in range (undotIPv4 (start), undotIPv4 (stop) ):
#        print (addr)
#        yield dotIPv4 (addr)

def range_ip(subnet): 
    start_addr =  network(subnet)
    end_addr = last_addr(subnet)
    #cur_addr = ".".join([str(octet) for octet in first_addr(subnet)])
    #stop_addr = ".".join([str(octet) for octet in last_addr(subnet)])
    #print(type(stop_addr))
    #print (int(cur_addr), int(stop_addr))
    #   for x in rangeIPv4 (cur_addr, stop_addr):
    start = list(map(int,start_addr))
    end = list(map(int,end_addr))
    while start!=end:
        for i in range(len(start)-1,-1,-1):
            if start[i]<255:
                start[i]+=1
                break
            else:
                start[i]=1
        yield '.'.join(map(str,start))