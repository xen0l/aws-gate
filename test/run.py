#!/usr/bin/env python

import os
import sys
import multiprocessing
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('-L', '--no-lint', action='store_false', default=True,
                    dest='lint', help="Skip file linting")
parser.add_argument('-C', '--no-coverage', action='store_false', default=True,
                    dest='coverage', help="Skip coverage report")
args, rest = parser.parse_known_args()

root_dir = os.path.split(os.path.dirname(sys.argv[0]))[0]
report_dir = os.path.join(root_dir, 'reports')

if not os.path.exists(report_dir):
    os.mkdir(report_dir, mode=0o755)

if 'PLACEBO_MODE' not in os.environ:
    os.environ['PLACEBO_MODE'] = 'playback'


os.environ['PLACEBO_DIR'] = os.path.join(root_dir, 'test', 'unit', 'placebo')

cmd = [
    'pytest',
    '--verbose'
]

if args.lint:
    lint_args = [
        '--flake8',
        '--pylint',
        '--pylint-jobs={}'.format(multiprocessing.cpu_count()),
        '--pylint-rcfile={}'.format(os.path.join(root_dir, '.pylintrc')),
    ]
    cmd.extend(lint_args)

if args.coverage:
    coverage_args = [
        '--cov=aws_gate',
        '--cov-report=term-missing',
        '--cov-report=xml:reports/coverage.xml',
        '--cov-report=html:reports/coverage/aws-gate',
        '--junitxml=reports/test.xml',
    ]
    cmd.extend(coverage_args)
else:
    cmd.append('--no-cov')

cmd.extend(rest)

os.execvp(cmd[0], cmd)
