# May The Force Be With You

# Team FARFASA

# ----------------------------------------------------------------------------

from __future__ import print_function
import click
import os
import re
import farfasa.FarfasaCore as FarfasaCore
import multiprocessing
import itertools
import sys
import PIL.Image
import numpy as np


@click.command()
@click.argument('folder')
@click.argument('img2Check')
@click.option('--numCPU', default=1, help='number of CPU cores to use . -1 = max')
@click.option('--tolerance', default=0.6, help='Tolerance for face comparisons. lower = stricter')
@click.option('--showDist', default=False, type=bool, help='Output face distance')
def main(folder, img2Check, numCPU, tolerance, showDist):
    # Main driver function

    # PARAMETERS
    # folder            folder containing known faces and names
    # img2Check         image to compare known list with
    # numCPU            number of CPUs to use. -1 = max
    # tolerance         tolerance . lower = stricter
    # showDist          boolean option to show distance

    # run face recoginition on given images and quit

    known_names, known_face_encodings = scanKnownPpl(folder)

    # Multi-core processing only supported on Python 3.4 or greater
    if (sys.version_info < (3, 4)) and numCPU != 1:
        numCPU = 1

    if os.path.isdir(img2Check):
        if numCPU == 1:
            [testImg(image_file, known_names, known_face_encodings, tolerance, showDist) for image_file in
             folderImages(img2Check)]
        else:
            processPoolProcessImgs(folderImages(img2Check), known_names, known_face_encodings, numCPU, tolerance,
                                   showDist)
    else:
        testImg(img2Check, known_names, known_face_encodings, tolerance, showDist)


def folderImages(folder):
    # stream all jpeg , jpg , png images from a folder

    # PARAMETERS
    # folder        path of folder to Scan

    # returns list of all images in folder with extensions jpeg, jpg, png

    return [os.path.join(folder, f) for f in os.listdir(folder) if re.match(r'.*\.(jpg|jpeg|png)', f, flags=re.I)]


def processPoolProcessImgs(images2Check, knownNames, knownFaces, numCPU, tolerance, showDist):
    # To multiprocess images for efficiency based on number of CPUs

    # PARAMETERS
    # images2Check      images to check for faces
    # knownNames        list of known names
    # knownFaces        list of known face encodings
    # numCPU            number of CPUs to use . -1 = max
    # tolerance         tolerance . lower = stricter
    # showDist          boolean option to show distance

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
        itertools.repeat(knownNames),
        itertools.repeat(knownFaces),
        itertools.repeat(tolerance),
        itertools.repeat(showDist)
    )

    pool.starmap(testImg, function_parameters)


def scanKnownPpl(folder):
    # Scan known people from given folder

    # PARAMETERS
    # folder        path to folder where faces are there

    # returns known faces and their names

    knownNames = []
    knownFaces = []

    for file in folderImages(folder):
        basename = os.path.splitext(os.path.basename(file))[0]
        img = FarfasaCore.imgLoad(file)
        encodings = FarfasaCore.faceEncodings(img)

        if len(encodings) > 1:
            click.echo("WARNING: More than one face found in {}. Considering first face.".format(file))

        if len(encodings) == 0:
            click.echo("WARNING: No faces found in {}. Ignoring file.".format(file))
        else:
            knownNames.append(basename)
            knownFaces.append(encodings[0])

    return knownNames, knownFaces


def printing(file, name, distance, showDist=False):
    # Print the names of recognized people

    # PARAMETERS
    # file          file where person was recognized
    # name          name of recognized guy
    # distance      distance of recognized person
    # showDist      option to show distance ( boolean )

    # prints and then exits function

    if showDist:
        print("{},{},{}".format(file, name, distance))
    else:
        print("{},{}".format(file, name))


def testImg(img2Check, knownNames, knownFaces, tolerance=0.6, showDist=False):
    # Test the image for people by finding faces and comparing them to known faces.

    # PARAMETERS
    # img2Check         image as numpy array to scan
    # knownNames        list of known names
    # knownFaces        list of known face encodings
    # tolerance         tolerance level. lower = stricter
    # showDist          boolean variable to show distance

    # Test image for known people and print then, print unknown if a person found but name unknown

    unknownImg = FarfasaCore.imgLoad(img2Check)

    # Scale down image for efficiency
    if max(unknownImg.shape) > 1600:
        pil_img = PIL.Image.fromarray(unknownImg)
        pil_img.thumbnail((1600, 1600), PIL.Image.LANCZOS)
        unknownImg = np.array(pil_img)

    unknownEnc = FarfasaCore.faceEncodings(unknownImg)

    for unknown in unknownEnc:
        distances = FarfasaCore.faceDist(knownFaces, unknown)
        result = list(distances <= tolerance)

        if True in result:
            [printing(img2Check, name, dist, showDist) for isMatch, name, dist in zip(result, knownNames, distances) if isMatch]
        else:
            printing(img2Check, "unknown_person", None, showDist)

    if not unknownEnc:
        printing(img2Check, "no_persons_found", None, showDist)


if __name__ == "__main__":
    main()

