# May The Force Be With You

# Team FARFASA

# ----------------------------------------------------------------------------

import PIL.Image
import dlib
import numpy as np
from PIL import ImageFile
import face_recognition_models

ImageFile.LOAD_TRUNCATED_IMAGES = True

faceDetector = dlib.get_frontal_face_detector()

predictor68pt = face_recognition_models.pose_predictor_model_location()
predictorPose68pt = dlib.shape_predictor(predictor68pt)

predictor5pt = face_recognition_models.pose_predictor_five_point_model_location()
predictorPose5pt = dlib.shape_predictor(predictor5pt)

cnnFaceDetectModel = face_recognition_models.cnn_face_detector_model_location()
cnnFaceDetector = dlib.cnn_face_detection_model_v1(cnnFaceDetectModel)

faceRecogModel = face_recognition_models.face_recognition_model_location()
faceEncoder = dlib.face_recognition_model_v1(faceRecogModel)


def compareFaces(knownFaceEncodings, candidate, tolerance=0.6):
    # Compare a list of face encodings against a candidate

    # PARAMETERS
    # knownFaceEncodings: A list of known face encodings
    # candidate: A single face encoding to compare against the list
    # tolerance: How much distance between faces to consider it a match. Lower = Stricter

    # Return list of T/F values indicating which knownFaceEncodings match the face encoding to check

    return list(faceDist(knownFaceEncodings, candidate) <= tolerance)


def faceLandmarks(faceImg, faceLocations=None, model="large"):
    # Returns a dict of face feature locations for each face in the given image

    # PARAMETERS
    # faceImg           image to search
    # faceLocations     Optionally provide a list of face locations to check.
    # model             "large" (default) or "small" which only returns 5 points but is faster

    # Returns list of dicts of face feature locations

    landmarks = faceLandmarksRaw(faceImg, faceLocations, model)
    landmarksTuples = [[(p.x, p.y) for p in _.parts()] for _ in landmarks]

    # For a definition of each point index
    # https://cdn-images-1.medium.com/max/1600/1*AbEg31EgkbXSQehuNJBlWg.png

    if model == 'large':
        return [{
            "chin": points[0:17],
            "left_eyebrow": points[17:22],
            "right_eyebrow": points[22:27],
            "nose_bridge": points[27:31],
            "nose_tip": points[31:36],
            "left_eye": points[36:42],
            "right_eye": points[42:48],
            "top_lip": points[48:55] + [points[64]] + [points[63]] + [points[62]] + [points[61]] + [points[60]],
            "bottom_lip": points[54:60] + [points[48]] + [points[60]] + [points[67]] + [points[66]] + [points[65]] + [
                points[64]]
        } for points in landmarksTuples]

    elif model == 'small':
        return [{
            "nose_tip": [points[4]],
            "left_eye": points[2:4],
            "right_eye": points[0:2],
        } for points in landmarksTuples]

    else:
        raise ValueError("Invalid landmarks model type. Supported models are ['small', 'large'].")


def faceEncodings(faceImg, knownFaceLocations=None, numberOfJitters=1, model="small"):
    # Return the 128-dimension face encoding for each face in given image.

    # PARAMETERS
    # faceImg: input image
    # knownFaceLocations: known bounding boxes of faces
    # numberOfJitters: How many times to re-sample the face when calculating encoding
    # model: "large" (default) or "small" which only returns 5 points but is faster.

    # Returns list of 128-dimensional face encodings (one for each face in the image)

    raw_landmarks = faceLandmarksRaw(faceImg, knownFaceLocations, model)
    return [np.array(faceEncoder.compute_face_descriptor(faceImg, _, numberOfJitters)) for _ in raw_landmarks]


def faceLandmarksRaw(faceImg, faceLocations=None, model="large"):
    # Uses pose_predictor of dlib and face_recognition_models to identify face landmarks

    # PARAMETERS
    # faceImg           image containing face
    # faceLocations     locations of face
    # model             small/large

    # Returns list of pose_predictors

    if faceLocations is None:
        faceLocations = rawFaceLocations(faceImg)
    else:
        faceLocations = [css2Rect(_) for _ in faceLocations]

    pose_predictor = predictorPose68pt

    if model == "small":
        pose_predictor = predictorPose5pt

    return [pose_predictor(faceImg, _) for _ in faceLocations]


def rawFaceLocationsBatched(imageList, numberOfScans=1, batchSize=128):
    # Returns an 2d array of dlib rects of human faces in a image using the cnn face detector

    # PARAMETERS
    # imageList         A list of numpy array images
    # numberOfScans     How many times to scan the image looking for faces

    # Returns list of dlib 'rect' objects of face locations

    return cnnFaceDetector(imageList, numberOfScans, batch_size=batchSize)


def faceLocationsBatched(imageList, numberOfScans=1, batchSize=128):
    # Uses the cnn face detector to return a 2d array of bounding boxes of human faces in an image

    # PARAMETERS
    # imageList         A list of imageList (each as a numpy array)
    # numberOfScans     How many times to scan the image looking for faces
    # batchSize         How many imageList to include in each GPU processing batch.

    # Returns list of tuples of found face locations in css

    def cnn2Css(detections):
        return [trimCss(rect2Css(_.rect), imageList[0].shape) for _ in detections]

    rawDetectionsBatched = rawFaceLocationsBatched(imageList, numberOfScans, batchSize)

    return list(map(cnn2Css, rawDetectionsBatched))


def faceLocations(img, numberOfScans=1, model="hog"):
    # Returns an array of bounding boxes of human faces in a image

    # PARAMETERS
    # img               Image as numpy array
    # numberOfScans     How many times to scan the image for faces
    # model             hog or cnn

    # Returns list of tuples of found face locations in css

    if model == "cnn":
        return [trimCss(rect2Css(_.rect), img.shape) for _ in rawFaceLocations(img, numberOfScans, "cnn")]
    else:
        return [trimCss(rect2Css(_), img.shape) for _ in rawFaceLocations(img, numberOfScans, model)]


def imgLoad(file, mode='RGB'):
    # Loads an image file (.jpg / .png / .jpeg) into a numpy array

    # PARAMETERS
    # file      image file name or file object to load
    # mode      format to convert the image to.

    # Returns image as numpy array

    im = PIL.Image.open(file)
    if mode:
        im = im.convert(mode)
    return np.array(im)


def rawFaceLocations(img, numberOfScans=1, model="hog"):
    # Returns an array of bounding boxes of human faces in a image

    # PARAMETERS
    # img               Image as numpy array
    # numberOfScans     How many times to scan the image for faces
    # model             hog or cnn

    # Returns list of dlib 'rect' objects of found face locations

    if model == "cnn":
        return cnnFaceDetector(img, numberOfScans)
    else:
        return faceDetector(img, numberOfScans)


def faceDist(faceEncodings, comparisionFace):
    # Compare Face to list of known faces and get a euclidean distance for each comparision
    # The distance tells you how similar the faces are.

    # PARAMETERS
    # faceEncodings             List of face encodings to compare
    # comparisionFace           A face encoding to compare against

    # Returns numpy ndarray with the distance for each face comparision in the same order as the 'faces' array

    if len(faceEncodings) == 0:
        return np.empty((0))

    return np.linalg.norm(faceEncodings - comparisionFace, axis=1)


def rect2Css(rect):
    # Convert a dlib 'rect' object to a plain tuple in (top, right, bottom, left) order

    # PARAMETERS
    # rect      dlib rect object

    # Returns a tuple of (top, right, bottom, left)

    return rect.top(), rect.right(), rect.bottom(), rect.left()


def css2Rect(css):
    # Convert a tuple in (top, right, bottom, left) order to a dlib `rect` object

    # PARAMETERS
    # css       a tuple of (top, right, bottom, left)

    # Returns a dlib `rect` object

    return dlib.rectangle(css[3], css[0], css[1], css[2])


def trimCss(css, imgShape):
    # Check if tuple is within the bounds of the image.

    # PARAMETERS
    # css               plain tuple representation of the rect
    # image_shape       numpy shape of the image array

    # Returns a trimmed plain tuple representation of the rect in (top, right, bottom, left) order

    return max(css[0], 0), min(css[1], imgShape[1]), min(css[2], imgShape[0]), max(css[3], 0)

