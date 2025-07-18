import os

class Config:
    SQLALCHEMY_DATABASE_URI = (
        "mysql+pymysql://edumusicadmin:Quique1395@/"
        "docentes?"
        "unix_socket=/cloudsql/cool-tree-464616-d1:southamerica-east1:edumusica-13"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False