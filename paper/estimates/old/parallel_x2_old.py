import autofit as af
import os

import matplotlib.pyplot as plt
from matplotlib.ticker import StrMethodFormatter

# Setup the path to the workspace, using a relative directory name.
workspace_path = "{}/../../../".format(os.path.dirname(os.path.realpath(__file__)))
plot_path = "{}/plotting/results/plots/".format(workspace_path)
output_path = path.join(workspace_path, "output_8_lin")

# Use this path to explicitly set the config path and output path.
af.conf.instance = af.conf.Config(
    config_path=workspace_path + "config", output_path=output_path
)

input_model_parameters = [0.13, 0.25, 1.25, 4.4, 1.0e-4, 0.58]
ylabels = [r"$\rho_{1}$", r"$\rho_{2}$", r"$\tau_{1}$", r"$\tau_{2}$", "d", r"$\beta$"]

pipeline = "pipeline_hyper__parallel_x2"
pipeline_meta = "pipeline_init__parallel_x2 + pipeline_hyper__parallel_x2"
phase = "phase_2_parallel_x2_noise_scaled"

sigma_limit = 2.0

epers = [517 * 6, 1034 * 6, 2068 * 6, 4136 * 6, 8272 * 6]


ci_images = [
    "ci_images_non_uniform_cosmic_rays",
    "ci_images_uniform",
    "ci_images_non_uniform",
    "ci_images_uniform_cosmic_rays",
    "ci_images_uniform",
]
ci_models = [
    "parallel_x2_poisson",
    "parallel_x2",
    "parallel_x2",
    "parallel_x2",
    "parallel_x2_poisson",
]
ci_settings = [
    "settings_par_front_mask_rows_(0,30)_cr_p10s10d3",
    "settings_par_front_mask_rows_(0,30)",
    "settings_par_front_mask_rows_(0,30)",
    "settings_par_front_mask_rows_(0,30)_cr_p10s10d3",
    "settings_par_front_mask_rows_(0,30)",
]

ci_resolutions = [
    "low_resolution",
    "mid_resolution",
    "high_resolution",
    "x2_high_resolution",
    "x4_high_resolution",
]

total_params = len(input_model_parameters)
total_images = len(ci_images)
total_resolutions = len(ci_resolutions)

most_probables_of_images = []
upper_errors_of_images = []
lower_errors_of_images = []
model_errors_of_images = []

for ci_image, ci_model, ci_setting in zip(ci_images, ci_models, ci_settings):

    optimizers = []

    for ci_resolution in ci_resolutions:

        result_path = path.join(
            output_path, ci_image, ci_model, ci_resolution, pipeline, phase, ci_setting
        )

        agg = af.Aggregator(directory=result_path)
        print(result_path)
        optimizers.append(agg.optimizers_with(pipeline=pipeline_meta, phase=phase)[0])

    most_probables_of_resolutions = list(
        map(lambda opt: opt.most_probable_model_parameters, optimizers)
    )
    upper_errors_of_resolutions = list(
        map(
            lambda opt: opt.model_errors_at_upper_sigma_limit(sigma_limit=sigma_limit),
            optimizers,
        )
    )
    lower_errors_of_resolutions = list(
        map(
            lambda opt: opt.model_errors_at_lower_sigma_limit(sigma_limit=sigma_limit),
            optimizers,
        )
    )
    model_errors_of_resolutions = list(
        map(
            lambda opt: opt.model_errors_at_sigma_limit(sigma_limit=sigma_limit),
            optimizers,
        )
    )

    most_probables_of_images.append(most_probables_of_resolutions)
    upper_errors_of_images.append(upper_errors_of_resolutions)
    lower_errors_of_images.append(lower_errors_of_resolutions)
    model_errors_of_images.append(model_errors_of_resolutions)

plt.figure(figsize=(19.0, 12.0), dpi=100)
# plt.suptitle("Accuracy of Parallel CTI Model", fontsize=20)

ebs = []

jitters = [-40.0 * 6, -20.0 * 6, 0.0, 20.0 * 6, 40.0 * 6]

for param_index in range(total_params):

    subplot_index = [1, 3, 2, 4, 5, 6]

    plt.subplot(4, 3, subplot_index[param_index])

    epers_plot = [min(epers) + min(jitters), 1034 * 6, 2068 * 6, 4136 * 6, 8272 * 6]
    jitter_factors = [1.0, 2.0, 4.0, 9.0, 15.0]

    plt.plot(
        epers_plot,
        [input_model_parameters[param_index] for j in range(len(epers))],
        linestyle="--",
        linewidth=2,
        color="k",
    )

    for image_index in range(total_images):

        epers_plot = list(
            map(
                lambda eper, jitter_factor: eper + jitter_factor * jitters[image_index],
                epers,
                jitter_factors,
            )
        )

        eb = plt.errorbar(
            x=epers_plot,
            y=[
                most_probables_of_image[param_index]
                for most_probables_of_image in most_probables_of_images[image_index]
            ],
            yerr=[
                [
                    lower_errors_of_image[param_index]
                    for lower_errors_of_image in lower_errors_of_images[image_index]
                ],
                [
                    upper_errors_of_image[param_index]
                    for upper_errors_of_image in upper_errors_of_images[image_index]
                ],
            ],
            capsize=5,
            elinewidth=1,
            markeredgewidth=3,
            linestyle="--",
        )
        eb[-1][0].set_linestyle("-")
        eb[-1][0].set_linewidth(1)

    plt.xscale("log")
    plt.tick_params(
        axis="x",  # changes apply to the x-axis
        which="minor",  # both major and minor ticks are affected
        bottom=False,  # ticks along the bottom edge are off
        top=False,  # ticks along the top edge are off
        labelbottom=False,
    )  # labels along the bottom edge are off
    plt.xticks(ticks=epers, labels=epers, fontsize=8)
    plt.yticks(fontsize=8)
    plt.ylabel(ylabels[param_index], fontsize=12)
    plt.gca().yaxis.set_major_formatter(StrMethodFormatter("{x:,.4f}"))

ylabels = [
    r"$\delta \rho_{1}$",
    r"$\delta \rho_{2}$",
    r"$\delta \tau_{1}$",
    r"$\delta \tau_{2}$",
    r"$\delta $d",
    r"$\delta \beta$",
]

for param_index in range(6):

    subplot_index = [7, 9, 8, 10, 11, 12]

    plt.subplot(4, 3, subplot_index[param_index])

    plt.xscale("log")

    for image_index in range(total_images):

        plt.plot(
            epers,
            [
                model_errors_of_image[param_index]
                for model_errors_of_image in model_errors_of_images[image_index]
            ],
        )

    plt.tick_params(
        axis="x",  # changes apply to the x-axis
        which="minor",  # both major and minor ticks are affected
        bottom=False,  # ticks along the bottom edge are off
        top=False,  # ticks along the top edge are off
        labelbottom=False,
    )  # labels along the bottom edge are off
    plt.xticks(ticks=epers, labels=epers, fontsize=8)
    plt.yticks(fontsize=8)
    plt.ylabel(ylabels[param_index], fontsize=12)
    plt.gca().yaxis.set_major_formatter(StrMethodFormatter("{x:,.4f}"))
    if subplot_index[param_index] >= 10:
        plt.xlabel("$EPER_{\mathrm{8}}$", usetex=True, fontsize=12)

plt.figlegend(
    labels=["Input Value", "All", "Uniform", "Non-uniform", "Cosmic Rays", "Poisson"],
    bbox_to_anchor=(0.84, 0.935),
    ncol=6,
    fontsize=17,
    frameon=False,
)

plt.subplots_adjust(top=0.87, bottom=0.06, left=0.05, right=0.95)
plt.savefig(plot_path + "/parallel_x2_results.png")
plt.show()
