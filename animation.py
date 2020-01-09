"""
:platform: Unix, Windows
:synopsis: This module contains the endpoint plot code. This code was adapted in part from K. Mulier's
    example on stackoverflow.
:moduleauthor: Michael Eller <mbe9a@virginia.edu>
"""

import numpy as np
from matplotlib.figure import Figure
from matplotlib.animation import TimedAnimation
from matplotlib.lines import Line2D
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from settings_interface import get_window_samples, get_sample_rate, get_x_axis_size, get_y_axis_max, get_y_axis_min, b1, m1, b2, m2


class CustomFigCanvas(FigureCanvas, TimedAnimation):
    """
    CustomFigCanvas is a class designed to allow integration of a matplotlib animation into a Qt backend.
    The animation will display the recorded voltage from the ADC and its corresponding differential derivative.
    The user can edit the axes limits and change the window filtering dynamically from the main menu.
    """

    def __init__(self):
        """
        Initializes the object and its parent objects. Creates the figure, axes, and artists to be displayed.
        """

        # buffer for the data send from the thread running plotGUI.dataSendLoop()
        self.addedData = []

        # get the x axis range from the settings file
        self.xlim = float(get_x_axis_size())
        # get the sample rate from the settings file
        samp_rate = get_sample_rate()

        # n contains the x values of the data points.
        # the plot is a rolling window so for a given x range, there are always the same
        # number of points shown on the plot.
        self.n = np.linspace(0, self.xlim - 1, int(self.xlim*samp_rate))

        # initialize the data (y array) with zeros
        self.y = (self.n * 0.0)
        # do the same for the differential derivative
        self.deriv = (self.n * 0.0)

        # all is used to save all recorded data.
        # when the window frame shifts and drops the oldest data points,
        # they are erased from self.y
        self.all = []
        # all_deriv is used to save all recorded derivative points
        self.all_deriv = []

        # get the number of samples to include in the moving average filter from the settings file
        self.window_samples = int(get_window_samples())
        # this will contain the moving average with which the filtered data point is calculated
        self.window = []
        # the derivative data can also be filtered
        self.deriv_window = []

        # separate arrays are used for the raw data and the filtered data.
        # these function like self.y and self.deriv.
        # Note:
        #       *   when filtering is active, i.e. windows samples > 1, the plot displays
        #           these instead.
        #
        #       *   if you change the filtering while the animation is running, previous values will not be filtered
        self.filtered_data = (self.n * 0.0)
        self.filtered_deriv = (self.n * 0.0)

        # we need these to store all the filtered points even after the plot has dropped them
        self.all_filtered_data = []
        self.all_filtered_deriv = []

        # get the y-axis limits from the settings file
        self.ymin = get_y_axis_min()
        self.ymax = get_y_axis_max()

        # create the figure with two axes that share the x-axis.
        # ax1 displays the received data
        # ax2 displays the derivative data
        self.fig = Figure(figsize=(10, 7), dpi=100)
        self.ax1 = self.fig.add_subplot(111)
        self.ax2 = self.ax1.twinx()

        # set labels and text
        self.ax1.set_xlabel('Time (s)')
        self.ax1.set_ylabel('Signal (V)')
        self.ax2.set_ylabel('Derivative (V)')
        self.ax1.set_title('Endpoint Signal vs. Time')

        # create the line artists, set colors
        # line1 is for the received data
        self.line1 = Line2D([], [], color='blue')
        self.line1_tail = Line2D([], [], color='red', linewidth=2)
        self.line1_head = Line2D([], [], color='red', marker='o', markeredgecolor='r')
        self.line1.set_label('Data')
        # line2 is for the derivative data
        self.line2 = Line2D([], [], color='purple')
        self.line2_tail = Line2D([], [], color='green', linewidth=2)
        self.line2_head = Line2D([], [], color='green', marker='o', markeredgecolor='g')
        self.line2.set_label('Deriv.')

        # add the lines to their corresponding axes
        self.ax1.add_line(self.line1)
        self.ax1.add_line(self.line1_tail)
        self.ax1.add_line(self.line1_head)
        self.ax2.add_line(self.line2)
        self.ax2.add_line(self.line2_tail)
        self.ax2.add_line(self.line2_head)

        # set axes limits based on the user's settings
        self.ax1.set_xlim(0, self.xlim - 1)
        self.ax1.set_ylim(self.ymin, self.ymax)
        self.ax2.set_xlim(0, self.xlim - 1)
        self.ax2.set_ylim(-self.ymax/2., self.ymax/2.)

        # add a legend
        self.fig.legend()

        # rename the x-axis labels to make the right most point at time 0
        self.generate_xticklabels()

        # initialize the parent matplotlib objects
        FigureCanvas.__init__(self, self.fig)
        # interval is time in ms between plot updates.
        # blitting is an optimization technique in computer graphics. It's important to disable it here
        # because we want to be able to update the plot axes dynamically, which is impossible with blitting active.
        TimedAnimation.__init__(self, self.fig, interval=100, blit=False)

    def get_windowed_value(self, window):
        """
        Helper function that simply calculates the average of all the samples in the window.

        :param window: the list containing the data to be averaged
        :return: the average
        """

        total = 0
        for num in window:
            total += num
        avg = float(total)/float(self.window_samples)
        return avg

    def new_frame_seq(self):
        """
        Return a new sequence of frame information.
        """
        return iter(range(self.n.size))

    def _init_draw(self):
        """
        Initial draw to clear the frame.
        """

        # clear the data in all the lines
        lines = [self.line1, self.line1_tail, self.line1_head, self.line2, self.line2_tail, self.line2_head]
        for l in lines:
            l.set_data([], [])

    def addData(self, value):
        """
        This function is called by the signal-slot mechanism within the plotGUI Dialog.
        It adds a value to the plots received data buffer, *addedData*.

        :param value: received value from the serial connection to the ADC
        """
        self.addedData.append(value)

    def close(self):
        """
        Soft close function. Closes the figure contained in the object.
        """
        plt.close(self.fig)

    def _step(self, *args):
        """
        Extends the _step() method for the TimedAnimation class.
        """
        try:
            TimedAnimation._step(self, *args)
        except Exception as e:
            self.abc += 1
            print(str(self.abc))
            TimedAnimation._stop(self)
            pass

    def update_xlim(self):
        """
        This function handles updating the x-axis range dynamically.
        """

        # save the old setting
        old_xlim = self.xlim
        # set the new xlim
        self.xlim = get_x_axis_size()
        # since all updating functions are called if any of the settings are changed,
        # we can check whether or not this setting actually changed and exit if not.
        if old_xlim == self.xlim:
            return

        # get the sample rate from the settings file
        samp_rate = get_sample_rate()

        # save the old y data
        y = self.y
        # save the old filtered data
        filtered_data = self.filtered_data
        # save the old derivative data
        deriv = self.deriv
        # save the old filtered derivative data
        filtered_deriv = self.filtered_deriv

        # generate the new list of x values based on the new limits and the sample rate
        n = np.linspace(0, self.xlim - 1, int(self.xlim*samp_rate))
        # set the axis limits
        self.ax1.set_xlim(0, self.xlim - 1)

        # add or remove data points from the lines depending on the x-axis range change.
        # this gets a little complicated.
        # if the range decreased
        if old_xlim > self.xlim:
            # calculate the difference in samples
            diff = int((old_xlim - self.xlim)*samp_rate)

            # drop oldest values from the data lists.
            # number of samples dropped = diff.
            self.y = y[diff:]
            self.deriv = deriv[diff:]
            self.filtered_data = filtered_data[diff:]
            self.filtered_deriv = filtered_deriv[diff:]

        # if the range increased
        else:
            # calculate the difference in samples
            diff = int((self.xlim - old_xlim) * samp_rate)

            # if the plot has been running long enough for self.all to have enough points to cover the new range,
            # prepend those data points to the data lists
            if (len(self.all) - len(self.n)) >= diff:
                # calculate the indices for the data points in self.all that we want to use
                index_1 = -len(self.n) - diff
                index_2 = -len(self.n)

                # add the old values to the front of the data lists
                self.y = np.concatenate((self.all[index_1:index_2], y))
                self.deriv = np.concatenate((self.all_deriv[index_1:index_2], deriv))
                self.filtered_data = np.concatenate((self.all_filtered_data[index_1:index_2],
                                                     filtered_data))
                self.filtered_deriv = np.concatenate((self.all_filtered_deriv[index_1:index_2],
                                                     filtered_deriv))

            # if self.all doesn't have enough to cover the whole difference,
            # but has more than the current shown data points -- prepend all available points in self.all and
            # then prepend zeros until the arrays have the correct length
            elif len(self.all) > len(self.n):
                # diff_diff is the difference between diff and the number of available points in
                # self.all (that aren't already in self.y etc.)
                diff_diff = diff - (len(self.all) - len(self.n))

                # diff2 = diff - diff_diff
                # used to calculate start and stop indices
                diff2 = len(self.all) - len(self.n)
                # calculate indices
                index_1 = -len(self.n) - diff2
                index_2 = -len(self.n)

                # prepend the data lists with zeros, old values, and original values
                self.y = np.concatenate(([0] * diff_diff, self.all[index_1:index_2], y))
                self.deriv = np.concatenate(([0] * diff_diff, self.all_deriv[index_1:index_2], deriv))
                self.filtered_deriv = np.concatenate(([0] * diff_diff, self.all_filtered_deriv[index_1:index_2],
                                                     filtered_deriv))

            # if self.all is the same size as self.y, i.e. the window hasn't had to drop any points yet
            else:
                # prepend zeros until the lists have the right size
                self.y = np.concatenate(([0] * diff, y))
                self.deriv = np.concatenate(([0] * diff, deriv))
                self.filtered_data = np.concatenate(([0] * diff, filtered_data))
                self.filtered_deriv = np.concatenate(([0] * diff, filtered_deriv))

        # set the new n list
        self.n = n

        # generate the labels again to ensure that the newest data point is at time=0
        self.generate_xticklabels()

    def generate_xticklabels(self):
        """
        Since the animation progresses from right to left, the left-most point is actually in the past,
        i.e. negative time. The simples way to do this is to keep the axis limits from 0 to xlim and alter the labels.
        """

        # get the x-axis ticks
        ticks = self.ax1.get_xticks()

        # generate the labels for each tick
        labels = []
        for num in reversed(ticks):
            labels.append(str(-num))
        if ticks[0] == 0:
            labels[-1] = "0"

        # set the labels
        self.ax1.set_xticklabels(labels)

    def update_ylim(self):
        """
        Update the data y-axis limits according to the input from the user.
        The derivative limits are hard-coded based on the ymax of the data axis.
        """

        # get the y-axis minimum from the settings file
        self.ymin = get_y_axis_min()
        # get the y-axis maximum from the settings file
        self.ymax = get_y_axis_max()

        # set the axis limits
        self.ax1.set_ylim(self.ymin, self.ymax)
        self.ax2.set_ylim(-self.ymax/2., self.ymax/2.)

    def update_window(self):
        """
        This function updates the *windows_samples* variable from the settings file.
        """
        self.window_samples = int(get_window_samples())

    def _draw_frame(self, framedata):
        """
        Overrides the *_draw_frame()* stub in the inherited animation class.
        This function updates the line data with the newest value from *self.addedData*.
        """

        # margin is a small space between the right side of the plot and the line head
        margin = 2

        # while a new value from the ADC is available
        while len(self.addedData) > 0:
            # get that value
            val = self.addedData[0]

            # back out the actual voltage using a two-part linear fit
            if val < 150:
                val = (val - b1) / m1
            else:
                val = (val - b2) / m2

            # calculate the newest derivative value
            deriv_val = val - self.y[-1]

            # append the values to the lists that save all values
            self.all.append(val)
            self.all_deriv.append(deriv_val)

            # if the window doesn't contain the right amount of samples
            if len(self.window) != self.window_samples:
                # fill the windows with the most recent value
                self.window = [val] * self.window_samples
                self.deriv_window = [deriv_val] * self.window_samples

            # shift the windows 1 to the left, replace last values with new value
            self.window = np.roll(self.window, -1)
            self.deriv_window = np.roll(self.deriv_window, -1)
            self.window[-1] = val
            self.deriv_window[-1] = deriv_val

            # shift the filtered data 1 to the left
            self.filtered_data = np.roll(self.filtered_data, -1)
            # calculate newest filtered value and append it
            self.filtered_data[-1] = self.get_windowed_value(self.window)
            # add the new filtered value to the permanent list
            self.all_filtered_data.append(self.get_windowed_value(self.window))

            # shift the filtered derivative 1 to the left
            self.filtered_deriv = np.roll(self.filtered_deriv, -1)
            # calculate new filtered derivative point
            self.filtered_deriv[-1] = self.get_windowed_value(self.deriv_window)
            # add the value to the permanent list
            self.all_filtered_deriv.append(self.get_windowed_value(self.deriv_window))

            # shift the main data list 1 to the left, set the last element to the new value
            self.y = np.roll(self.y, -1)
            self.y[-1] = val

            # perform the same operation for the derivative list
            self.deriv = np.roll(self.deriv, -1)
            self.deriv[-1] = deriv_val

            # del the value from the buffer
            del self.addedData[0]

        # if we need to display the filtered lists
        if self.window_samples > 1:
            # set the line1 data (voltage)
            self.line1.set_data(self.n[0: self.n.size - margin], self.filtered_data[0: self.n.size - margin])
            self.line1_tail.set_data(np.append(self.n[-10:-1 - margin], self.n[-1 - margin]),
                                     np.append(self.filtered_data[-10:-1 - margin], self.filtered_data[-1 - margin]))
            self.line1_head.set_data(self.n[-1 - margin], self.filtered_data[-1 - margin])

            # set the line2 data (derivative)
            self.line2.set_data(self.n[0: self.n.size - margin], self.filtered_deriv[0: self.n.size - margin])
            self.line2_tail.set_data(np.append(self.n[-10:-1 - margin], self.n[-1 - margin]),
                                     np.append(self.filtered_deriv[-10:-1 - margin], self.filtered_deriv[-1 - margin]))
            self.line2_head.set_data(self.n[-1 - margin], self.filtered_deriv[-1 - margin])

        # display y and deriv
        else:
            # set the line1 data (voltage)
            self.line1.set_data(self.n[0: self.n.size - margin], self.y[0: self.n.size - margin])
            self.line1_tail.set_data(np.append(self.n[-10:-1 - margin], self.n[-1 - margin]),
                                     np.append(self.y[-10:-1 - margin], self.y[-1 - margin]))
            self.line1_head.set_data(self.n[-1 - margin], self.y[-1 - margin])

            # set the line2 data (derivative)
            self.line2.set_data(self.n[0: self.n.size - margin], self.deriv[0: self.n.size - margin])
            self.line2_tail.set_data(np.append(self.n[-10:-1 - margin], self.n[-1 - margin]),
                                     np.append(self.deriv[-10:-1 - margin], self.deriv[-1 - margin]))
            self.line2_head.set_data(self.n[-1 - margin], self.deriv[-1 - margin])

        # set the artists that need to be drawn
        self._drawn_artists = [self.line1, self.line1_tail, self.line1_head,
                               self.line2, self.line2_tail, self.line2_head]
