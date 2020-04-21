# May The Force Be With You

# Team FARFASA

# ----------------------------------------------------------------------------

from __future__ import print_function
import click
import os
import re
import farfasa.FarfasaCore as FarfasaCore
import multiprocessing
import sys
import itertools


@click.command()
@click.argument('img2Check')
@click.option('--numCPU', default=1, help='number of CPU cores to use. -1 = max')
@click.option('--model', default="hog", help='face detection model hog / cnn.')

def main(img2Check, numCPU, model):
    # Main driver function

    # PARAMETERS
    # img2Check         image to check for faces
    # numCPU            number of CPUs to use. -1 = max
    # model             hog / cnn

    # run face detection on given images and quit

    # Multi-core processing only supported on Python 3.4 or greater
    if (sys.version_info < (3, 4)) and numCPU != 1:
        numCPU = 1

    if os.path.isdir(img2Check):
        if numCPU == 1:
            [testImg(image_file, model) for image_file in folderImages(img2Check)]
        else:
            processPoolProcessImgs(folderImages(img2Check), numCPU, model)
    else:
        testImg(img2Check, model)


def processPoolProcessImgs(images2Check, numCPU, model):
    # To multiprocess images for efficiency based on number of CPUs

    # PARAMETERS
    # images2Check      images to check for face locations
    # numCPU            number of CPUs to use . -1 = max
    # model             cnn / hog

    # uses multiprocessing module to stream all images to check to testImg function

    if numCPU == -1:
        processes = None
    else:
        processes = numCPU

    context = multiprocessing
    if "forkserver" in multiprocessing.get_all_start_methods():
        context = multiprocessing.get_context("forkserver")

    pool = context.Pool(processes=processes)

    function_parameters = zip(
        images2Check,
        itertools.repeat(model),
    )

    pool.starmap(testImg, function_parameters)


def folderImages(folder):
    # stream all jpeg , jpg , png images from a folder

    # PARAMETERS
    # folder        path of folder to Scan

    # returns list of all images in folder with extensions jpeg, jpg, png

    return [os.path.join(folder, f) for f in os.listdir(folder) if re.match(r'.*\.(jpg|jpeg|png)', f, flags=re.I)]


def printing(file, location):
    # Print the locations of detected faces

    # PARAMETERS
    # file          file where person was recognized
    # location      location of detected face

    # prints and then exits function

    top, right, bottom, left = location
    print("{},{},{},{},{}".format(file, top, right, bottom, left))


def testImg(img2Check, model):
    # Test given image for face locations

    # PARAMETERS
    # img2Check     image to scan and detect face locations
    # model         cnn / hog

    # prints locations of any faces in the given image image_file

    unknownImg = FarfasaCore.imgLoad(img2Check)
    faceLocations = FarfasaCore.faceLocations(unknownImg, numberOfScans=0, model=model)

    for Location in faceLocations:
        printing(img2Check, Location)


if __name__ == "__main__":
    main()
