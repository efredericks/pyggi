import time
import pytest
from PIL import Image
from glitch_tool import *
import argparse
import uuid
import os

import cv2
import imagehash

# @pytest.fixture
# def shared_uuid(scope="session"):
#     return str(uuid.uuid1())

shared_uuid = str(uuid.uuid1())

test_img_path = "/home/erik/research-git/pyggi/sample/Image_glitcher/test-set/"

def check_validity(img_path):
    try:
        img = Image.open(img_path)
        assert img.verify() == None
    except:
        assert True, f"Corrupted image: {img_path}"

# average the hashed differences between all files?
def calc_hash_difference(comparator_path):
    global test_img_path
    global test_data

    try:
        i1 = Image.open(comparator_path)
        diff = 0.0

        i1_hash = imagehash.average_hash(i1)

        num_files = 0
        for dirpath, dirs, files in os.walk(test_img_path):
            for f in files:
                try:
                    i2 = Image.open(os.path.join(dirpath, f))
                    
                    num_files += 1

                    i2_hash = imagehash.average_hash(i2)

                    diff += abs(i1_hash - i2_hash)

                except:
                    pass # ignoring borked images

        assert num_files > 0, "Test set not found!"
        diff /= num_files

        print(f"Difference: {comparator_path} : {diff}")

        return diff
    except:
        return 0.0

def test_modes(starter):#shared_uuid):
    global shared_uuid

    parser = argparse.ArgumentParser(description="Do terrible things to data.")
    # Required arguments
    parser.add_argument("-i", "--infile", help="Input file")
    parser.add_argument("-m", "--mode", help="File change mode")
    # Optional arguments
    parser.add_argument("-o", "--outdir", default="./", help="Output folder")
    parser.add_argument("-s", "--seed", type=int, help="Seed to use for random")
    parser.add_argument("-a", "--amount", type=int, default=1, help="Amount of new files to create")
    parser.add_argument("-c", "--changes", help="Amount of random changes. Can be in a range, like '1-10'.")
    parser.add_argument("-b", "--bytes", help="Amount of bytes to change each change. Can be in a range, like '1-10'.")
    parser.add_argument("-r", "--repeat-width", help="Amount of bytes to repeat. Can be in a range, like '1-10'.")
    parser.add_argument("-q", "--quiet", default=False, action="store_true", help="Surpress logging")
    parser.add_argument("--output-iterations", type=int, default=0, help="How many iterations between outputs")

    modes = ["change", "reverse", "repeat", "remove", "zero", "insert", "replace", "move"]

    _uuid = shared_uuid
    out = f"/home/erik/research-git/pyggi/sample/Image_glitcher/out/{str(_uuid)}/"
    if not os.path.isdir(out):
        os.mkdir(out)
    print(out)


    args = parser.parse_args(args=[
        "--infile", "/home/erik/research-git/pyggi/sample/Image_glitcher/240124_PewCampusWinter_KSM-5143.jpg", 
        "--outdir", out,
        "--mode", random.choice(modes),
        "--amount", str(1), #str(random.randint(0,10)),
        "--changes", str(random.randint(0,100)),#str(1),
        "--bytes", str(random.randint(0,100)),#str(10),
        "--repeat-width", str(random.randint(0,100)),
    ])
    outPath = glitch_main(args, _uuid, out)
    check_validity(outPath)

@pytest.fixture(scope="session", autouse=True)
def starter(request):
    global shared_uuid
    global test_data

    start_time = time.time()

    _uuid = shared_uuid

    def finalizer(_uuid):
        # the calculate hash checks the individual differences
        # this checks for all generated outputs and averages the score
        out = f"/home/erik/research-git/pyggi/sample/Image_glitcher/out/{str(_uuid)}/"
        num_valid = 0
        num_invalid = 0
        total_diff = 0.0
        for dirpath, dirs, files in os.walk(out):
            for f in files:
                if f.endswith(".png") or f.endswith(".jpg"):
                    print(f"Trying {os.path.join(dirpath,f)}")
                    try:
                        img_path = os.path.join(dirpath, f)
                        img = Image.open(img_path)
                        if img.verify() == None:
                            num_valid += 1
                            diff = calc_hash_difference(img_path)
                            print(f"Comparing {img_path} : {diff}")
                            total_diff += diff
                    except:
                        num_invalid += 1

        total_diff = total_diff / (num_valid + num_invalid)

        print("uuid: {}, runtime: {}, invalid: {}, valid: {}, difference: {}".format(_uuid, str(time.time() - start_time), num_invalid, num_valid, total_diff))

    # request.addfinalizer(finalizer)
    request.addfinalizer(lambda: finalizer(_uuid))

# generate a suite of random images from known parameters, maximize difference between those and the GI ones?