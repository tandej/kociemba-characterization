import argparse
import time
import math
from typing import Tuple, List

import matplotlib.pyplot as plt
import matplotlib.patches as mplpatches
import numpy as np
from tqdm import tqdm


def entryPoint(
    iterations: int,
    timeSecondsPerMove: float,
    minGoalDepth: int,
    maxGoalDepth: int,
    noPlot: bool,
    toFile: bool,
    fullCsv: str,
    summaryCsv: str,
):

    print()
    print("loading/generating solver table cache...")

    # pylint: disable=C0415

    import twophase.solver as sv  # type: ignore
    import twophase.cubie as cb  # type: ignore

    # pylint: enable=C0415
    # need lots of comments that YES I DO want to do this

    print("solver table cache loaded/generated!")
    print()

    timeoutSeconds = 1

    floatRoundPrecision = 3

    def getSolveStats(cubestring: str, goal: int, timeout: float) -> Tuple[int, float]:
        startTime = time.time()

        sol = sv.solve(cubestring, goal, timeout)

        return (len(sol.split(" ")), time.time() - startTime)

    cube = cb.CubieCube()

    meanTime = []
    maxTime = []
    meanDepth = []
    maxDepth = []
    goalDepths = []

    # returns min, max, median, mean, stddev
    def getSequenceStats(
        sequence: List[float],
    ) -> Tuple[float, float, float, float, float]:
        meanSum: float = 0
        for i in sequence:
            meanSum += i

        squaredDeviationSum: float = 0

        for i in sequence:
            squaredDeviationSum += (i - (meanSum / len(sequence))) ** 2

        sortedSequence = sorted(sequence)

        median: float = 0
        if len(sequence) % 2 == 0:
            upper: float = sortedSequence[math.floor((len(sequence) / 2))]
            lower: float = sortedSequence[math.floor((len(sequence) / 2) - 1)]

            median = (upper + lower) / 2
            # ex: midpoints for n=2 are 0/1, n=4 are 1/2, n=6 are 2/3
        else:
            median = sortedSequence[int(math.floor(float(len(sequence))) / 2)]
            # ex: midpoint for n=1 is 0, n=3 is 1, n=5 is 2

        return (
            sortedSequence[0],
            sortedSequence[-1],
            median,
            meanSum / len(sequence),
            math.sqrt(squaredDeviationSum / len(sequence)),
        )

    def getStatsSummaryString(
        stats: Tuple[float, float, float, float, float], unit: str
    ) -> str:
        return (
            "min="
            + str(round(stats[0], floatRoundPrecision))
            + unit
            + ", max="
            + str(round(stats[1], floatRoundPrecision))
            + unit
            + ", median="
            + str(round(stats[2], floatRoundPrecision))
            + unit
            + ", mean="
            + str(round(stats[3], floatRoundPrecision))
            + unit
            + ", stddev="
            + str(round(stats[4], floatRoundPrecision))
            + unit
        )

    def characterizeDepth(depth: int):
        solveTimeSequence = []
        solveMovesSequence: List[float] = []

        runningTimeSum: float = 0
        runningDepthSum: int = 0

        numberGoalHits: int = 0

        numberSamples: int = 0

        with tqdm(range(iterations)) as progressBar:
            for i in progressBar:
                cube.randomize()

                stats = getSolveStats(
                    cube.to_facelet_cube().to_string(), depth, timeoutSeconds
                )

                runningTimeSum += stats[1]
                solveTimeSequence.append(stats[1] * 1000)
                runningDepthSum += stats[0]
                solveMovesSequence.append(stats[0])

                if stats[0] <= depth:
                    numberGoalHits += 1

                numberSamples += 1

                progressBar.set_postfix(
                    meanTime=str(
                        round(
                            (runningTimeSum / numberSamples) * 1000, floatRoundPrecision
                        )
                    )
                    + "ms",
                    meanDepth=float(runningDepthSum) / numberSamples,
                    goalHitPct=(float(numberGoalHits) / numberSamples) * 100,
                )

        timeStats = getSequenceStats(solveTimeSequence)
        moveStats = getSequenceStats(solveMovesSequence)

        print("solve time: " + getStatsSummaryString(timeStats, "ms"))
        print("solve moves: " + getStatsSummaryString(moveStats, ""))

        meanTime.append(timeStats[3])
        maxTime.append(timeStats[1])
        meanDepth.append(moveStats[3])
        maxDepth.append(moveStats[1])
        goalDepths.append(depth)

    characterizeStartTime = time.time()

    for i in range(minGoalDepth, maxGoalDepth + 1):
        print("characterizing goal depth: " + str(i))
        characterizeDepth(i)

    characterizeEndTime = time.time()

    combinedTimes = []
    combinedMaxTimes = []

    for i in range(0, len(goalDepths)):
        combinedTimes.append((meanDepth[i] * (timeSecondsPerMove * 1000)) + meanTime[i])
        combinedMaxTimes.append(
            (maxDepth[i] * (timeSecondsPerMove * 1000)) + maxTime[i]
        )

    fig, axes = plt.subplots(1, 3, sharex=True)

    axes[0].scatter(x=goalDepths, y=meanDepth, c="blue")
    axes[0].scatter(x=goalDepths, y=maxDepth, c="red")

    axes[1].scatter(x=goalDepths, y=meanTime, c="blue")
    axes[1].scatter(x=goalDepths, y=maxTime, c="red")

    humanRecord = 3130  # ms

    axes[2].scatter(x=goalDepths, y=combinedTimes, c="blue")
    axes[2].scatter(x=goalDepths, y=combinedMaxTimes, c="red")
    axes[2].plot(
        np.linspace(minGoalDepth - 1, maxGoalDepth + 1),
        np.linspace(humanRecord, humanRecord),
        color="green",
    )

    axes[0].set_ylabel("solution moves")
    axes[1].set_ylabel("solution time (ms)")
    axes[2].set_ylabel(
        "combined solve time (ms) using t/move = "
        + str(1000 * timeSecondsPerMove)
        + "ms"
    )

    axes[0].set_xlabel("goal solution depth")
    axes[1].set_xlabel("goal solution depth")
    axes[2].set_xlabel("goal solution depth")

    axes[2].set_xlim(minGoalDepth - 0.5, maxGoalDepth + 0.5)

    axes[2].set_ylim(0, humanRecord * 1.1)

    fig.legend(
        handles=[
            mplpatches.Patch(color="red", label="worst-case"),
            mplpatches.Patch(color="blue", label="mean"),
            mplpatches.Patch(color="green", label="human-record"),
        ]
    )

    fig.set_size_inches(18, 9)

    plt.figtext(
        0.5,
        0.01,
        "finished characterization (n="
        + str(iterations)
        + ") in "
        + str(round(characterizeEndTime - characterizeStartTime, 1))
        + "s",
        horizontalalignment="center",
    )

    if toFile:
        plt.savefig("output.png")
    if not noPlot:
        plt.show()


defaultMinDepth = 19
defaultMaxDepth = 25

parser = argparse.ArgumentParser()
parser.add_argument(
    "iterations", help="number of cubes to solve per goal depth", type=int
)
parser.add_argument(
    "timeSecondsPerMove",
    help="time of a 180deg turn in seconds, used for plotting time estimates",
    type=float,
)
parser.add_argument(
    "-n", "--noPlot", action="store_true", help="disables output graph", default=False
)
parser.add_argument(
    "-r",
    "--toFile",
    action="store_true",
    help="stores output graph to 'output.png' file in project root",
    default=False,
)
parser.add_argument(
    "-f",
    "--fullCsv",
    type=str,
    help="outputs a csv file of every simulated solve to a given filepath",
    default=None,
)
parser.add_argument(
    "-s",
    "--summaryCsv",
    type=str,
    help="outputs a summary csv (same data as displayed during iterative solving phase) to a given filepath",
    default=None,
)
parser.add_argument(
    "--minDepth",
    type=int,
    help="minimum goal depth to sample, defaults to " + str(defaultMinDepth),
    default=defaultMinDepth,
)
parser.add_argument(
    "--maxDepth",
    type=int,
    help="maximum goal depth to sample, defaults to " + str(defaultMaxDepth),
    default=defaultMaxDepth,
)
args = parser.parse_args()

try:
    entryPoint(
        args.iterations,
        args.timeSecondsPerMove,
        args.minDepth,
        args.maxDepth,
        args.noPlot,
        args.toFile,
        args.fullCsv,
        args.summaryCsv,
    )
except KeyboardInterrupt:
    print()
    print("program terminated by user keyboard interrupt!")
