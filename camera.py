import threading

from pygrabber.PyGrabber import *
from pygrabber.image_process import *
from pygrabber.dshow_graph import FilterGraph


class Camera:
    def __init__(self):
        self.graph = FilterGraph()
        self.callback = self.on_frame
        self.image_grabbed = None
        self.image_done = threading.Event()
        self.width = 720
        self.height = 400
        self.bpp = 1

    def get_devices(self):
        return self.graph.get_input_devices()

    def get_formats(self):
        return self.graph.get_formats()

    def set_device(self, input_device_index):
        self.graph.add_input_device(input_device_index)

    def display_format_dialog(self):
        self.graph.display_format_dialog()

    def start(self):
        self.graph.add_sample_grabber(self.callback)
        self.graph.add_null_render()
        self.graph.prepare()
        #self.graph.configure_render(handle)
        self.graph.run()

    def stop(self):
        self.graph.stop()

    def update_window(self, width, height):
        self.graph.update_window(width, height)

    def set_device_properties(self):
        self.graph.set_properties(self.graph.get_input_device())

    def grab_frame(self):
        self.graph.grab_frame()        
        
    def wait_image(self):        
        self.image_done.wait(1000)
        return self.image_grabbed         
        
    def on_frame(self, image):
        self.width = image.shape[1]
        self.height = image.shape[0]
        self.bpp = image.shape[2]
        self.image_grabbed = np.flip(image, axis=2)
        self.image_done.set()
        