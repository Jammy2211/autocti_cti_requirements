import math
import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter
import os
from os import path
import pickle
import warnings

from autoconf import conf
from autofit.non_linear.samples.pdf import quantile
import autofit as af
import autocti as ac

warnings.filterwarnings("ignore")

workspace_path = os.getcwd()

config_path = path.join(workspace_path, "config")
conf.instance.push(new_path=config_path)

plot_path = path.join(workspace_path, "paper", "images", "require")
pickle_path = path.join(workspace_path, "paper", "pickles", "require")

# database_name = "uniform"
# database_name = "poisson"
# database_name = "cosmic_rays"
database_name = "non_uniform"

if database_name == "poisson":

    name_list = ["parallel[x2]", "parallel[x3]"]

else:

    name_list = ["parallel[x2]", "parallel[x3]", "serial[x2]", "serial[x3]"]

eb_list = []

plt.figure(figsize=(13.0, 13.0))

for name in name_list:

    out_path = path.join(pickle_path, database_name, name)

    with open(path.join(out_path, "error_list.pickle"), "rb") as f:
        error_list = pickle.load(f)

    parallel_epers = [517 * 6, 1034 * 6, 2068 * 6, 4136 * 6, 8272 * 6]
    serial_epers = [517, 1034, 2068, 4136, 8272]

    jitters = [-30.0, -10.0, 10.0, 30.0]

    parallel_epers_plot = list(
        map(lambda parallel_eper: parallel_eper + jitters[0], parallel_epers)
    )

    if name == "parallel[x2]":

        parallel_epers_plot = list(
            map(lambda parallel_eper: parallel_eper + jitters[0], parallel_epers)
        )

        pl0 = plt.plot(parallel_epers_plot, error_list, linewidth=2)

    elif name == "parallel[x3]":

        parallel_epers_plot = list(
            map(lambda parallel_eper: parallel_eper + jitters[1], parallel_epers)
        )

        pl1 = plt.plot(parallel_epers_plot, error_list, linewidth=2)

    elif name == "serial[x2]":

        serial_epers_plot = list(
            map(lambda serial_eper: serial_eper + jitters[2], serial_epers)
        )

        pl2 = plt.plot(serial_epers_plot, error_list, linewidth=2)

    elif name == "serial[x3]":

        serial_epers = [517, 1034, 2068, 4136, 8272]

        serial_epers_plot = list(
            map(lambda serial_eper: serial_eper + jitters[3], serial_epers)
        )

        pl3 = plt.plot(serial_epers_plot, error_list, linewidth=2)


eper_limits = [517 - 30, 1034 * 6, 2068 * 6, 4136 * 6, 8272 * 6 + 30]

if not path.exists(plot_path):
    os.makedirs(plot_path)

plt.legend(
    # handles=[pl0, pl1, pl2, pl3],
    labels=["Parallel x2", "Parallel x3", "Serial x2", "Serial x3"],
    loc="best",
    fontsize=22,
    frameon=False,
)
plt.plot(eper_limits, len(eper_limits) * [1.1e-4], linestyle="--", color="b")

plt.tick_params(labelsize=16)
plt.xscale("log")
plt.xlim([517 - 100, 8272 * 6 + 100])
eper_ticks = [517, 1034, 2068, 517 * 6, 1034 * 6, 2068 * 6, 4136 * 6, 8272 * 6]
plt.yticks(fontsize=20)
plt.xticks(ticks=eper_ticks, labels=eper_ticks, fontsize=20)
plt.gca().yaxis.set_major_formatter(StrMethodFormatter("{x:,.5f}"))
plt.xlabel("$N_{\mathrm{EPER}}$", fontsize=24)
plt.ylabel(r"$\Delta e_{\rm 2\sigma}$", fontsize=24)
plt.savefig(path.join(plot_path, f"precision_{database_name}.png"))
plt.show()
