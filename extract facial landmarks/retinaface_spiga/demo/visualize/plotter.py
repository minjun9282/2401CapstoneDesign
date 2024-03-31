# Demo libs
import demo.visualize.layouts.plot_basics as pl_basic
import demo.visualize.layouts.plot_bbox as pl_bbox
import demo.visualize.layouts.plot_landmarks as pl_lnd
import demo.visualize.layouts.plot_headpose as pl_hpose


class Plotter:

    def __init__(self):
        self.basic = pl_basic.BasicLayout()
        self.bbox = pl_bbox.BboxLayout()
        self.landmarks = pl_lnd.LandmarkLayout()
        self.hpose = pl_hpose.HeadposeLayout()
