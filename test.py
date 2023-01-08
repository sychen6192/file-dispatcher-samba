import socket
from smb.SMBConnection import SMBConnection


ip = '192.168.1.103'

name = socket.gethostbyaddr(ip)
ipGet = socket.gethostbyname(name[0])
print(name, ipGet, sep='\n')

remote_name = name[0]
conn = SMBConnection('username', 'password', 'any_name', remote_name)
assert conn.connect(ip, timeout=3)

for s in conn.listShares():
    if s.isSpecial:
        continue
    print('------------------------------------')
    print('name', s.name)
    print('comments', s.comments)
    print('isSpecial', s.isSpecial)
    print('isTemporary', s.isTemporary)
    print('### FileList ###')
    try:
        for f in conn.listPath(s.name, '/'):
            print(f.filename)
    except:
        print('### can not access the resource')
    print('------------------------------------')
    print('')

filename = 'chaonima.txt'
with open(filename, 'rb') as f:
    try:
        conn.storeFile('MP', filename, f)
    except Exception as err:
        print(err)

conn.close()