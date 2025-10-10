import argparse
import copy
import math
import os
import platform
import random
import re
import sys
from PIL import Image
import imagehash

class GlitchTool:
    def __init__(self, args, _uuid, out):
        self.args = args
        self.uuid = _uuid
        self.outDir = out
        self.outPath = ""

        # Constants
        self.transforms = {
            "change": self.changeBytes,
            "reverse": self.reverseBytes,
            "repeat": self.repeatBytes,
            "remove": self.removeBytes,
            "zero": self.zeroBytes,
            "insert": self.insertBytes,
            "replace": self.replaceBytes,
            "move": self.moveBytes
        }

    def writeFile(self, fileByteList, fileNum, iteration, bytesTochange, seed):
        filename, extension = os.path.splitext(self.args.infile)
        filename = filename.split("\\")[-1] if platform.system == "Windows" else filename.split("/")[-1]
        outPath = f"{self.args.outdir}{filename}_m={self.args.mode}_b={bytesTochange}_s={seed}_n={fileNum}_i={iteration}{extension}"
        if (not self.args.quiet):
            print("Writing file to " + outPath)
        open(outPath, "wb").write(bytes(fileByteList))
        self.outPath = outPath

    def messWithFile(self, originalByteList, iterations, bytesToChange, repeatWidth, fileNum):
        newByteList = copy.copy(originalByteList)
        iteration = 1
        seed = self.args.seed or random.randrange(sys.maxsize)
        random.seed(seed)
        for i in range(iterations):
            iteration = i+1
            if (self.args.mode == "repeat"):
                newByteList = self.repeatBytes(newByteList, bytesToChange, repeatWidth)
            else:
                newByteList = self.transforms[self.args.mode](newByteList, bytesToChange)
            if (self.args.output_iterations > 0 and iteration%self.args.output_iterations == 0):
                self.writeFile(newByteList, fileNum, iteration, bytesToChange, seed)
        self.writeFile(newByteList, fileNum, iteration, bytesToChange, seed)
            
    # Transforms

    def changeBytes(self, byteList, bytesToChange):
        pos = random.randint(0, len(byteList) - bytesToChange)
        chunk = [random.randint(0, 255) for i in range(bytesToChange)]
        byteList[pos:pos+bytesToChange] = chunk
        return byteList

    def reverseBytes(self, byteList, bytesToChange):
        pos = random.randint(0, len(byteList) - bytesToChange)
        chunk = byteList[pos:pos+bytesToChange][::-1]
        byteList[pos:pos+bytesToChange] = chunk
        return byteList

    def repeatBytes(self, byteList, bytesToChange, repeatWidth):
        pos = random.randint(0, len(byteList) - bytesToChange)
        chunk = []
        for i in range(math.ceil(bytesToChange/repeatWidth)):
            chunk.extend(byteList[pos:pos+repeatWidth])
        byteList[pos:pos+bytesToChange] = chunk[:bytesToChange]
        return byteList

    def removeBytes(self, byteList, bytesToChange):
        pos = random.randint(0, len(byteList) - bytesToChange)
        byteList[pos:pos+bytesToChange] = []
        return byteList

    def zeroBytes(self, byteList, bytesToChange):
        pos = random.randint(0, len(byteList) - bytesToChange)
        byteList[pos:pos+bytesToChange] = [0] * bytesToChange
        return byteList

    def insertBytes(self, byteList, bytesToChange):
        pos = random.randint(0, len(byteList))
        chunk = [random.randint(0, 255) for i in range(bytesToChange)]
        byteList[pos:pos] = chunk
        return byteList

    def replaceBytes(self, byteList, bytesToChange):
        pos = random.randint(0, len(byteList) - bytesToChange)
        chunk = byteList[pos:pos+bytesToChange]
        old = random.randint(0, 255)
        new = random.randint(0, 255)
        chunk = [new if b == old else b for b in chunk]
        byteList[pos:pos+bytesToChange] = chunk
        return byteList

    def moveBytes(self, byteList, bytesToChange):
        pos = random.randint(0, len(byteList) - bytesToChange)
        chunk = byteList[pos:pos+bytesToChange]
        byteList[pos:pos+bytesToChange] = []
        newPos = random.randint(0, len(byteList))
        byteList[newPos:newPos] = chunk
        return byteList

    def main(self):
        # Do stuff to arguments
        if (not self.args.infile):
            print("Error: No input file specified")
            return False
        if (not os.path.isfile(self.args.infile)):
            print("Error: Input file not found")
            return False
        if (not self.args.mode):
            print("Error: No mode specified")
            return False
        if (not (self.args.mode in self.transforms)):
            print("Error: Invalid mode")
            return False
        minChanges = 1
        maxChanges = 1
        if (self.args.changes and re.match(r"[0-9]+-[0-9]+", self.args.changes)):
            parts = self.args.changes.split("-")
            minChanges = int(parts[0])
            maxChanges = int(parts[1])
        elif (self.args.changes):
            minChanges = int(self.args.changes)
            maxChanges = int(self.args.changes)
        minBytes = 1
        maxBytes = 1
        if (self.args.bytes and re.match(r"[0-9]+-[0-9]+", self.args.bytes)):
            parts = self.args.bytes.split("-")
            minBytes = int(parts[0])
            maxBytes = int(parts[1])
        elif (self.args.bytes):
            minBytes = int(self.args.bytes)
            maxBytes = int(self.args.bytes)
        minRepeating = 1
        maxRepeating = 1
        if (self.args.repeat_width and re.match(r"[0-9]+-[0-9]+", self.args.repeat_width)):
            parts = self.args.repeat_width.split("-")
            minRepeating = int(parts[0])
            maxRepeating = int(parts[1])
        elif (self.args.repeat_width):
            minRepeating = int(self.args.repeat_width)
            maxRepeating = int(self.args.repeat_width)
        # Let the glitching commense!
        originalByteList = list(open(self.args.infile, "rb").read())
        for i in range(self.args.amount):
            iterations = random.randint(minChanges, maxChanges)
            bytesToChange = random.randint(minBytes, maxBytes)
            repeatWidth = random.randint(minRepeating, maxRepeating)
            self.messWithFile(originalByteList, iterations, bytesToChange, repeatWidth, i+1)
        if (not self.args.quiet):
            print("Finished writing files")



# Setup argparser
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
parser.add_argument("--generate_test_set", action="store_true", help="Generate random test data for comparison with PyGGI")

if __name__ == "__main__":
    args = parser.parse_args()

    if args.generate_test_set:
        out = "/home/erik/research-git/pyggi/sample/Image_glitcher/test-set/"
        modes = ["change", "reverse", "repeat", "remove", "zero", "insert", "replace", "move"]

        csv_out = f"{out}hash_data.csv"

        with open(csv_out, "w") as f:
            f.write(f"UUID,Average Hash\n")

        for i in range(5000):
            uuid = f"test_{i}"
            args = parser.parse_args(args=[
                # "--infile", "/home/erik/research-git/pyggi/sample/Image_glitcher/fredericks-headshot-sm.jpg", 
                "--infile", "/home/erik/research-git/pyggi/sample/Image_glitcher/240124_PewCampusWinter_KSM-5143.jpg", 
                "--outdir", out,
                "--mode", random.choice(modes),
                "--amount", str(1),#str(random.randint(0,10)),
                "--changes", str(random.randint(0,100)),#str(1),
                "--bytes", str(random.randint(0,100)),#str(10),
                "--repeat-width", str(random.randint(1,100)),
            ])
            glitch_tool = GlitchTool(args, uuid, out)
            glitch_tool.main()

        # remove broken ones
        for dirpath, dirs, files in os.walk(out):
            for f in files:
                if f.endswith(".png") or f.endswith(".jpg"):
                    try:
                        img = Image.open(os.path.join(dirpath,f))
                        # if img.verify() == None:

                            # write out image hash to file for loading in the test set
                        img_hash = imagehash.average_hash(img)
                        with open(csv_out, "a") as ihf:
                            fn = f.split(".")
                            ihf.write(f"{fn[0]},{img_hash}\n")


                    except:
                        print(f"Deleting {f}")
                        os.remove(os.path.join(dirpath, f))


    else:
        glitch_tool = GlitchTool(args, "manual", ".")
        glitch_tool.main()
