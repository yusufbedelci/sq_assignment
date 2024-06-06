class User:
    def __init__(self, id, fullname,role_id,email, username, password):
        self.id = id
        self.fullname = fullname
        self.role_id= role_id
        self.email=email
        self.username = username
        self.password=password
        
    
class Profile(User):
    def __init__(self, id, fullname,role_id,email, username, password, mobile, age, gender,weight):
        super().__init__(id, fullname, role_id, email,username, password)
        self.mobile=mobile
        self.age = age
        self.gender = gender
        self.weight =weight
    def __str__(self) -> str:
        return f"Name: {self.fullname} Role: {self.role_id}, Email: {self.email} username:{self.username}"