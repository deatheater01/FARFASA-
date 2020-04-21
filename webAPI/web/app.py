from flask import Flask, jsonify, request
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt

# defining the constructors
app = Flask(__name__)
api = Api(app)

#connection to database
client = MongoClient("mongodb://" + "admin" + ":" + "qazwsxedc" + "@localhost:" + str(27017))

#define database
db = client.attendanceApi

#define collection
#our collection format will be
"""
{
    "Date-Period (dd-mm-yy-P)": "07-03-20-2",
    "17Z301": p,
    "17Z309": p,
    "17Z336": p,
    "17Z351": a,
    "17Z353": a
  }
"""
attendance = db['attendanceCollection1']
users = db['users']

#check if user exists
def UserExist(username):
    if users.find({"Username":username}).count()==0:
        return False
    else:
        return True

#register users to access api
#post format

#username:username
#password:password
#RollNo:RollNo
class Register(Resource):

    def post(self):
        postedData = request.get_json()

        username = postedData["username"]
        password = postedData["password"]

        if UserExist(username):
            retJson = {
                "status": "301",
                "msg": "One of you is more than enough!"
            }
            return jsonify(retJson)
        
        hashed_pwd = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt())

        users.insert({
            "Username" : username,
            "Password": hashed_pwd,
            "RollNo": postedData["RollNo"]
        })

        retJson = {
            "status":200,
            "msg":"Succesfully registerd!!!"
        }

        return jsonify(retJson)

# to validate username and passwd
def verifyPw(username, password):
    if not UserExist(username):
        return False
    
    hashed_pw = users.find({
        "Username":username
    })[0]["Password"]

    if bcrypt.hashpw(password.encode('utf8'),hashed_pw)==hashed_pw:
        return True
    else:
        return False

#to generate return dictionary
def generateReturnDictionary(status, msg):
    retJson = {
        "status": status,
        "msg":msg
    }
    return retJson


#to verify entered credentials
def verifyCrendtials(username, password):
    if not UserExist(username):
        return generateReturnDictionary(301, "Invalid Username"), True

    correct_pw = verifyPw(username, password)

    if not correct_pw:
        return generateReturnDictionary(302,"Incorrect Password"), True

    return None, False

#let's mark attendance

#now anyone can post attendance but token based auth will be introduced

class MarkAttendance(Resource):
    def post(self):
        postedData = request.get_json
        specField = postedData["SpecialField"]
        
        if attendance.find({"SpecialField":specField}).count()==0:
            attendance.insert(postedData)
        else:
            retJson = generateReturnDictionary(303,"invalid class")
            return jsonify(retJson)


#to allow teachers to modify the attendance entered
""" 
post format
{
    "username":username,
    "password":passwd,
    "specialField":specField,
    "RollNo":rollNo,
    "newData":newdata
    "Remark":reasonToModify"
}
"""
#special token must also need to introduced to teachers to modify attendance
class ModifyAttendance(Resource):
    def post(self):
        postedData = request.get_json

        username = postedData["username"]
        password = postedData["password"]
        specField = postedData["specialField"]
        rollNo = postedData["RollNo"]
        newData = postedData["newData"]
        Reason = postedData["Remark"]

        retJson, error = verifyCrendtials(username,password)

        if error:
            return jsonify(retJson)

        attendance.update(
            {
            "SpecialField":specField
            },
            {
                "$set" :
                {
                    rollNo:newData,
                    "Remarks":Reason
                }
            }

        )

#to add attendance stats and individual attendance
 
#student attendance
# here we assume that a student is trying to view his/her attendance
""" 
{
    username:username
    password:password
    rollNo:rollNo
}
"""
#for our main ui we need to convert specField to human readable form
class PersonalAttendance(Resource):
    def post(self):
        postedData = request.get_json

        username = postedData["username"]
        password = postedData["password"]
        rollNo = postedData["RollNo"]

        retJson, error = verifyCrendtials(username, password)

        if error:
            return jsonify(retJson)
        #there is a chance that other rollNo will also come
        retJson = attendance.find({
            "RollNo":rollNo
        },{
            "_id":0,
            "Remarks":0
        }
        )

        return jsonify(retJson)
#check the parameters properly
api.add_resource(Register, '/register')
api.add_resource(MarkAttendance, '/markAttendance')
api.add_resource(ModifyAttendance, '/modifyAttendance')
api.add_resource(PersonalAttendance, '/personalAttendance')

if __name__=="__main__":
    app.run(host='0.0.0.0')


 




              






        





 












