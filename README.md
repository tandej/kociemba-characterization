# kociemba-characterization

Proof-of-concept / requirement-setting code for a future project (*not hard to guess what it is*)

Primarily an aid in selecting what goals the solver should have set (on specific compute hardware), to optimize for total (solve + move) time.

Install requirements with `pip3 install -r requirements.txt`

On first run, the underlying solver library needs to populate some quite large lookup tables. This may take half an hour or more.

## Usage
usage: `characterize.py [-h] [-n] [-f FULLCSV] [-s SUMMARYCSV] [--minDepth MINDEPTH] [--maxDepth MAXDEPTH] iterations timeSecondsPerMove`

positional arguments:

  `iterations`         | number of cubes to solve per goal depth

  `timeSecondsPerMove` | time of a 180deg turn in seconds, used for plotting time estimates

options:

  `-h`, `--help`            | shows help message and exits

  `-n`, `--noPlot`          | disables output graph

  `-f` FULLCSV, `--fullCsv` FULLCSV |
                        outputs a csv file of every simulated solve to a given filepath

  `-s` SUMMARYCSV, `--summaryCsv` SUMMARYCSV |
                        outputs a summary csv (same data as displayed during iterative solving phase) to a given filepath

  `--minDepth` MINDEPTH  | minimum goal depth to sample, defaults to 19
  
  `--maxDepth` MAXDEPTH  | maximum goal depth to sample, defaults to 25

## TODO: CSV dumping not implemented

## Licensed under the MIT license