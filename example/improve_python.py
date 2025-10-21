"""
Improving non-functional properties ::
"""
import sys
import random
import argparse
from pyggi.base import Patch, AbstractProgram
from pyggi.line import LineProgram
from pyggi.line import LineReplacement, LineInsertion, LineDeletion
from pyggi.tree import TreeProgram
from pyggi.tree import StmtReplacement, StmtInsertion, StmtDeletion
from pyggi.algorithms import LocalSearch

import subprocess, os
import ast

class MyProgram(AbstractProgram):
    def compute_fitness(self, result, return_code, stdout, stderr, elapsed_time):
        import re
        m = re.findall("difference: ([0-9.]+)", stdout)
        # with open("./output", "a") as f:
        #     f.write(stdout)
        if len(m) > 0:
            runtime = m[0]
            failed = re.findall("([0-9]+) failed", stdout)
            pass_all = len(failed) == 0
            if pass_all:

                cmd = f"diff -U 0 /home/erik/research-git/pyggi/sample/Image_glitcher/glitch_tool.py {self.tmp_path}/glitch_tool.py | grep ^@ | wc -l"
                ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
                output = int(ps.communicate()[0])
                with open('test-contents', 'a') as f:
                    f.write(str(self.tmp_path)+'\n')

                    f.write(f"diffs: {str(int(output))}\n")

                rt = round(float(runtime), 3)
                result.fitness = rt +output
                with open("./parse-success", "a") as f:
                    f.write(f"{result.fitness} {output} {rt} {stdout}")
            else:
                result.status = 'PARSE_ERROR'
                with open("./parse-error-output-1", "a") as f:
                    f.write(stdout)
        else:
            result.status = 'PARSE_ERROR'
            with open("./parse-error-output-2", "a") as f:
                f.write(stdout)

        # m = re.findall("runtime: ([0-9.]+)", stdout)
        # if len(m) > 0:
        #     runtime = m[0]
        #     failed = re.findall("([0-9]+) failed", stdout)
        #     pass_all = len(failed) == 0
        #     if pass_all:
        #         result.fitness = round(float(runtime), 3)
        #     else:
        #         result.status = 'PARSE_ERROR'
        # else:
        #     result.status = 'PARSE_ERROR'

class MyLineProgram(LineProgram, MyProgram):
    pass

class MyTreeProgram(TreeProgram, MyProgram):
    pass

class MyTabuSearch(LocalSearch):
    def setup(self):
        self.tabu = []

    def get_neighbour(self, patch):
        while True:
            temp_patch = patch.clone()
            if len(temp_patch) > 0 and random.random() < 0.5:
                temp_patch.remove(random.randrange(0, len(temp_patch)))
            else:
                edit_operator = random.choice(self.operators)
                temp_patch.add(edit_operator.create(self.program, method="weighted"))
            if not any(item == temp_patch for item in self.tabu):
                self.tabu.append(temp_patch)
                break
        return temp_patch

    def is_better_than_the_best(self, fitness, best_fitness):
        return fitness > best_fitness

    def stopping_criterion(self, iter, fitness):
        return fitness > 100000

class MyLocalSearch(LocalSearch):
    def get_neighbour(self, patch):
        if len(patch) > 0 and random.random() < 0.5:
            patch.remove(random.randrange(0, len(patch)))
        else:
            edit_operator = random.choice(self.operators)
            patch.add(edit_operator.create(self.program))
        return patch

    def stopping_criterion(self, iter, fitness):
        return fitness > 50#< 0.05

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='PYGGI Improvement Example')
    parser.add_argument('--project_path', type=str, default='../sample/Triangle_fast_python')
    parser.add_argument('--mode', type=str, default='line')
    parser.add_argument('--epoch', type=int, default=30,
        help='total epoch(default: 30)')
    parser.add_argument('--iter', type=int, default=100,
        help='total iterations per epoch(default: 100)')
    args = parser.parse_args()
    assert args.mode in ['line', 'tree']

    if args.mode == 'line':
        program = MyLineProgram(args.project_path)
        local_search = MyTabuSearch(program)#MyLocalSearch(program)
        local_search.operators = [LineReplacement, LineInsertion, LineDeletion]
    elif args.mode == 'tree':
        program = MyTreeProgram(args.project_path)
        local_search = MyTabuSearch(program)#MyLocalSearch(program)
        local_search.operators = [StmtReplacement, StmtInsertion, StmtDeletion]

    result = local_search.run(warmup_reps=5, epoch=args.epoch, max_iter=args.iter, timeout=50)#15)
    print("======================RESULT======================")
    for epoch in range(len(result)):
        print("Epoch {}".format(epoch))
        print(result[epoch])
        print(result[epoch]['diff'])
    program.remove_tmp_variant()
