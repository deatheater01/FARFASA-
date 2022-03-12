# May The Force Be With You

# Team FARFASA

# ----------------------------------------------------------------------------

from setuptools import setup

requirements = [
    'dlib==19.19.0',
    'Click==7.0',
    'numpy==1.18.1',
    'face_recognition_models==0.3.0',
    'opencv_python==4.2.0.32',
    'requests==2.23.0',
    'imutils==0.5.3',
    'Pillow==9.0.1'
]

setup(
    name='farfasa',
    version='1.0.1',
    description="FaceRecognition using dlib and face_recognition_models",
    author="Team farfasa",
    author_email='pitchappanprm.com',
    url='https://github.com/Pitch2342/Farfasa',
    packages=[
        'farfasa',
    ],
    package_dir={'farfasa': 'farfasa'},

    install_requires=requirements,
    license="GNU General Public License v3.0e",
    zip_safe=False,
    keywords='farfasa',
    classifiers=[
        'Development Status :: Beta',
        'Intended Audience :: Students',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
)
