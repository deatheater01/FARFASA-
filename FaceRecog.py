# May The Force Be With You

# Team FARFASA

# ----------------------------------------------------------------------------

import cv2
import numpy as np
import farfasa as farfasa
import argparse
import imutils
import pickle
import time as t
from datetime import datetime,time,timedelta
import requests
import json

#ap = argparse.ArgumentParser()
#ap.add_argument("-e", "--encodings", required=True, help="path to serialized db of facial encodings")
#args = vars(ap.parse_args())
#input()

def Attendance(args):
    timer = t.perf_counter_ns()
    key1 = []
    val1 = []
    video_capture = cv2.VideoCapture(0)
    print("loading encodings")
    data = pickle.loads(open(args["encodings"], "rb").read())
    for key in data:
        key1.append(key)
        val1.append(data[key])

    known_face_encodings = val1[0]
    known_face_names = val1[1]

    # Initialize variables
    face_locations = []
    face_names = []
    process_this_frame = True
    #AttDictList = []
    XXX = []
    Attendees = []
    Times = []

    while True:
        # change val to change timer
        if(t.perf_counter_ns()-timer > .25*(60*(10**9))):
            break

        TempDict = []
        # Grab a single frame of video
        ret, frame = video_capture.read()

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Only process every other frame of video to save time
        if process_this_frame:
            # Find all the faces and face encodings in the current frame of video
            face_locations = farfasa.faceLocations(rgb_small_frame)
            face_encodings = farfasa.faceEncodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = farfasa.compareFaces(known_face_encodings, face_encoding)
                name = "Unknown"

                # # If a match was found in known_face_encodings, just use the first one.
                # if True in matches:
                #     first_match_index = matches.index(True)
                #     name = known_face_names[first_match_index]

                # Or instead, use the known face with the smallest distance to the new face
                face_distances = farfasa.faceDist(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]

                face_names.append(name)

        process_this_frame = not process_this_frame


        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_ITALIC
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
            Attendees.append(name)
            Times.append(datetime.now().strftime("%H:%M:%S"))
            X = json.dumps({"Roll": name, "Time": datetime.now().strftime("%H:%M:%S"), "Date": datetime.now().strftime("%d-%m-%Y"), "ID" : "PitchWebCam01", "UTC": (datetime.utcnow()-datetime(1970,1,1)).total_seconds()})
            #AttDictList.append(X)
            if int(round(t.time()*1000))%5 == 0:
                XXX.append(X)
                SendToServer(X)
            #print(X)
        # Display the resulting image
        cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release handle to the webcam
    video_capture.release()
    cv2.destroyAllWindows()

    def convertList(a):
        dict1 = {a[i]:'a' for i in range(0,len(lst))}
        return dict1

    lst = known_face_names

    AttendanceDict = convertList(lst)

    for i in lst:
        if i in Attendees:
            AttendanceDict[i] = 'p'
    a = args["encodings"]
    a = a.replace(".pickle", "")

    def getPeriod(S=None):
        if(8*60+0 <= S < 9*60+20):
            return 1
        elif(9*60+20 <= S < 10*60+10):
            return 2
        elif (10*60+30 <= S < 11*60+20):
            return 3
        elif (11*60+20 <= S < 12*60+10):
            return 4
        elif (13*60+40 <= S < 14*60+30):
            return 5
        elif (14*60+30 <= S < 15*60+20):
            return 6
        elif (15*60+30 <= S < 16*60+20):
            return 7
        elif (16*60+20 <= S < 17*60+10):
            return 8
        else:
            return 99



    times = Times
    T = str(timedelta(seconds=sum(map(lambda f: int(f[0])*3600 + int(f[1])*60 + int(f[2]), map(lambda f: f.split(':'), times)))/len(times)))
    T1 = T.split(".")
    T = T1[0]

    def getTimeSec(T):
        h,m,s = T.split(":")
        return int(h)*60 + int(m)

    S = getTimeSec(T)

    P = getPeriod(S)
    #print(P)

    AttendanceDict["Class"] = str(P)+"-"+a
    AttendanceDict["Date"] = datetime.now().strftime("%d-%m-%Y")
    AttendanceDict["ID"] = "PitchWebCam01"
    #print(AttendanceDict)
    #print(AttDictList)
    SendToServer(AttendanceDict)
    #print(XXX)

def SendToServer(Dict1):
    print(Dict1)
    # API_ENDPOINT = "111.111.111.111"
    # API_KEY = "XXXXXXXXXXXXXXXXXXXXX"
    # User = "Cam1"
    # r = requests.post(url = API_ENDPOINT, json = Dict1, auth =(User,API_KEY))

if __name__ == "__main__":
    args = {"encodings":"0"}
    #E = input()
    E = "encodings.pickle"
    args["encodings"] = E
    Attendance(args)
