import re 
from rupa.models import * 

print('Now creating the Admin user:')
print('username: admin')
while True:
    email = input('input email:')
    if re.compile(r'^[\w]+@[\w]+\.[\w]+$').match(email):
        break

while True:
    password = input('input password:')
    if re.compile(r'^[\w,<>;:\-_=&%#@!~`\*\.\?\+\$\^\[\]\(\)\{\}\|\\\/]{8,16}$').match(password):
        break 
    else:
        print('should be 8~16 characters, includes numbers, letters and symbols')

# 创建 admin
admin = User(username='admin',
                nickname='admin',
                email=email,
                password=password,
                role=User.ROLE_ADMIN,
                )

db.session.add(admin)
db.session.commit()


