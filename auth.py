import pam
p = pam.pam()



user = input("username: ")
password = input("password: ")

if p.authenticate(user, password, print_failure_messages=True):
    print("pm auth success")
else:
    print("pam access failed")

print("END")