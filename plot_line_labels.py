# Plot from dataframe with the end of each line labeled
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import tol_colors

import math

from itertools import cycle

def plot_df(df, ax=None, cols=None, col_labels=None, title='',
            x_title='', y_title=None,
            label_edit={}, x_lim=None,
            add_text=None, xticks=None, yticks=None):
    '''
    Plot line chart with labels at end of each line

        * df:           dataframe to plot; x-axis should be index
        * ax:           axes to plot
        * cols:         list of columns of dataframe to plot
        * col_labels:   column labels as a dictionary
        * title:        title of plot
        * x_title:      x-axis label
        * y_title:      y-axis label
        * label_edit:   manually edit position of label using dict
        * x_lim:        manually set the x-axis limit
        * add_text:     text to add as a dictionary
        * xticks:       list of xticks
        * yticks:       list of yticks

    Details:

    add_text: text to add as a dictionary. Added text should take the form:
    add_text = {'add_loc': (1, 0.95), 'add_str': 'N simulations'}
    '''

    # List of colors used
    color_list = list(tol_colors.tol_cset('bright'))
    # remove black
    # color_list.remove('#000000')

    # Some useful numbers
    first_idx = df.index.array.min()
    last_idx = df.index.array.max()
    step_size = (last_idx - first_idx) / (df.index.size - 1)

    # Columns of the dataframe to plot and their labels
    if cols is None:
        cols = list(df.columns)
    if col_labels is None:
        col_labels = {num: str(num) for num in cols}

    # Initialize figure
    if ax is None:
        fig, ax = plt.subplots()
    # fig.patch.set_facecolor('None')

    for col, hex_color in zip(cols, cycle(color_list)):
        # Plot the rate
        df.plot(y=col, ax=ax, color=hex_color, linewidth=1.5)
        # Find text defaults
        last_col_idx = df[col].last_valid_index()
        y_pos = df.loc[last_col_idx, col]
        # Can add some manual adjustments to the text
        if len(label_edit) > 0:
            for col_edit, adjustment in label_edit.items():
                if col == col_edit:
                    y_pos = y_pos + adjustment
        # Plot text for each line
        ax.text(x=last_col_idx + step_size / 2, y=y_pos, s=col_labels[col],
                color=hex_color, fontsize=20)
    ax.get_legend().remove()

    # Set the x_lim of the graph
    # If not specified, this needs to account for length of column labels
    if x_lim is not None:
        max_x = x_lim
    else:
        # Find the length of the longest label
        len_labels = max(len(value) for key, value in col_labels.items())
        max_x = last_idx + max(0.25 * (last_idx - first_idx),
                               math.floor(len_labels * .5))
    # Set limit to accommodate labels
    min_x, _ = ax.get_xlim()
    ax.set_xlim((min_x, max_x))
    # ax.set_ylim((0, 1))

    # Tick values
    # Better to manually feed tick labels to tikzplotlib as strings
    # get default x tick values, if necessary
    if xticks is None:
        xticks = ax.get_xticks().tolist()
    # Get default y tick values
    if yticks is None:
        yticks = ax.get_yticks().tolist()

    # remove ticks that are beyond the indexed area
    new_xticks = [tick for tick in xticks if
                  ((tick >= min_x) & (tick <= last_idx))]
    ax.set_xticks(new_xticks)
    if yticks is not None:
        min_ytick = min(yticks)
        max_ytick = max(yticks)
        new_yticks = [tick for tick in yticks if
                      ((tick >= min_ytick) & (tick <= max_ytick))]
        ax.set_yticks(new_yticks)

    def tick_str_labels(ticks, round_num=2):
        ticks_str = [
            r'$' + '{0:n}'.format(tick) + '$' for tick in ticks]
        return ticks_str

    ax.set_xticklabels(tick_str_labels(new_xticks))
    ax.set_yticklabels(tick_str_labels(new_yticks))

    # Labels and title; default x to no title
    ax.set_xlabel(x_title)
    if y_title is not None:
        ax.set_ylabel(y_title)

    # There is an error that sometimes arises with minor xticks in group plots
    # To avoid that, set the minor ticks to []
    ax.set_xticks([], minor=True)
    ax.set_yticks([], minor=True)

    # Add any additional text
    if add_text is not None:
        # Added text should take the form:
        # add_text = {'add_loc': (1, 0.95), 'add_str': 'N simulations'}
        ax.text(x=add_text['add_loc'][0], y=add_text['add_loc'][1],
                s=add_text['add_str'], fontsize=20)

    ax.set_title(title)

    # Create grid
    ax.grid(axis='y', color='#000000', linewidth=.3, linestyle=':')

    # Remove axes
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)


if __name__ == '__main__':
    df = sns.load_dataset('flights')
    # df['month'].cat.as_ordered(inplace=True)
    df['month'] = df['month'].cat.codes
    df = df.pivot(index='month', columns='year', values='passengers')

    cols = list(df.columns)
    col_labels = {yr: str(yr)[-2:] for yr in cols}

    plot_df(df=df,
            cols=cols,
            col_labels=col_labels,
            label_edit={1960: 100},
            x_lim=15,
            yticks=[150, 700]
            )

    # import tikzplotlib

    # tikzplotlib.clean_figure()
    # tikzplotlib.save('testfig.tex')
    # # tikzplotlib.save('testfig.tex', standalone=True)
    # fig = plt.gca()
    plt.show()
