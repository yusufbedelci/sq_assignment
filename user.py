class User:
    def __init__(self, id,role_id,username, email, password, mobile, fullname, age, gender, weight):
        self.id = id
        self.fullname = fullname
        self.role_id= role_id
        self.email=email
        self.username = username
        self.password=password
        self.mobile=mobile
        self.age = age
        self.gender = gender
        self.weight =weight
    
    