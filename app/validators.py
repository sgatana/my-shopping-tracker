import re


def isValidEmail(email):
    exp = '^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,})$'
    return re.match(exp, email)


def validate_username(username):
   exp = "^[A-Za-z0-9]*$"
   return re.match(exp, username)


def password_validator(password):
    reg_pass = '^(?=\S{6,}$)(?=.*?\d)(?=.*?[a-z])(?=.*?[A-Z])(?=.*?[^A-Za-z\s0-9])'
    return re.match(reg_pass, password)


def validate_names(name):
    exp = "^[A-Za-z][\sA-Za-z]*$"
    return re.match(exp, name)