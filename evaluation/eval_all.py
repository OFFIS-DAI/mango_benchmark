from pathlib import Path

import pandas
import plotly.graph_objects as go
import os
import numpy as np


def create_multilevel_grouped_bar_chart(
    y_array_list,
    x_array_list,
    color_list,
    name_list,
    group_labels,
    group_size,
    x_axis_labels,
    yaxis_title,
    title=None,
    multi_level_distance=-0.18,
):
    fig = go.Figure()
    sum_length = sum([len(l) for l in y_array_list])
    common_x = np.array(range(sum_length)) + np.array(
        [i // group_size for i in range(sum_length)]
    )

    for i, color in enumerate(color_list):
        fig.add_bar(
            x=x_array_list[i],
            y=y_array_list[i],
            name=name_list[i],
            marker_color=color,
        )
    for i, group_label in enumerate(group_labels):
        fig.add_annotation(
            text=group_label,
            xref="paper",
            yref="paper",
            x=(common_x[i * group_size]) * 1.5 / (max(common_x)),
            y=multi_level_distance,
            showarrow=False,
            font_size=20,
        )

    # Layout
    fig.update_layout(
        showlegend=True,
        template="plotly_white",
        height=800,
        width=1600,
        legend=dict(
            title="",
            orientation="h",
            traceorder="normal",
            x=0.46,
            y=1.05,
            bgcolor="rgba(0,0,0,0)",
            bordercolor="rgba(0,0,0,1)",
            borderwidth=0,
            font_size=20,
        ),
        title=title,
    )

    fig.update_yaxes(
        showline=True,
        showgrid=False,
        linewidth=0.5,
        linecolor="black",
        title=yaxis_title,
        titlefont=dict(size=24),
        title_standoff=40,
        ticks="outside",
        dtick=2,
        ticklen=10,
        tickfont=dict(size=20),
        range=[
            0,
            max(
                [
                    sum([y_array_list[i][j] for i in range(len(y_array_list))])
                    for j in range(len(y_array_list[0]))
                ]
            )
            + 0.5,
        ],
    )

    fig.update_xaxes(
        title="",
        tickvals=common_x,
        ticktext=x_axis_labels,
        ticks="",
        tickfont_size=20,
        linecolor="black",
        linewidth=1,
    )
    return fig


def load_df(folder_name):
    dfs = []
    csv_path = Path("results/" + folder_name)
    for file in [f.path for f in os.scandir(csv_path) if f.is_file()]:
        dfs.append(pandas.read_csv(file))
    return pandas.concat(dfs)


def bar(df):
    df_means = (
        df.groupby(["scenario", "version"])
        .mean()
        .reset_index()
        .sort_values(by=["scenario", "version"])
    )
    unique_version = pandas.unique(df_means["version"])
    unique_scenario = pandas.unique(df_means["scenario"])
    bar_fig = create_multilevel_grouped_bar_chart(
        [
            list(
                df_means[df_means["version"].apply(lambda v: version in v)][
                    "performance"
                ]
            )
            for version in ["julia", "python"]
        ],
        [
            np.array(
                list(
                    range(
                        len(unique_scenario)
                        * sum([version in s for s in unique_version])
                    )
                )
            )
            + np.array(
                [
                    j // sum([version in s for s in unique_version]) * (5)
                    + i * (sum([version in s for s in unique_version]))
                    for j in range(
                        len(unique_scenario)
                        * sum([version in s for s in unique_version])
                    )
                ]
            )
            for i, version in enumerate(["julia", "python"])
        ],
        ["#ffa000", "#d32f2f"],
        ["julia", "python"],
        [f"<b>{scenario}</b>" for scenario in pandas.unique(df_means["scenario"])],
        len(unique_version),
        list(unique_version) * len(unique_scenario),
        yaxis_title="<b>performance in s</b>",
        multi_level_distance=-0.4,
    )
    bar_fig.write_html(file="bar_julia_python_benchmark.html")


def eval_all(folder_name):
    df = load_df(folder_name)
    bar(df)


if __name__ == "__main__":
    eval_all("set_one")
