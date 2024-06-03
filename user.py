class User:
    def __init__(self, id,role_id,name, email, password, mobile):
        self.id = id
        self.name=name
        self.email=email
        self.password=password
        self.mobile=mobile
        self.role_id= role_id
    
    