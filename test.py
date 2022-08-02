CREDENTIALS_FILE = "credentials.txt"
f = open(CREDENTIALS_FILE, "r")
credentials = f.read().split()
#print(credentials.index('hans'))
if 'hans' in credentials:
    if credentials.index('hans') % 2 == 0:
        print("hans is in")
    else:
        print("hans is not in")
        
f.close()