from pypylon import pylon
from pypylon import genicam
import time


class BaslerCamera:
    def __init__(self, config_file_dir=None):
        """
        connects to the first available camera and reads in a configuration
        file. Create a configuration file using the pylon viewer, the most
        painless way to deal with camera configurations.

        Arguments:
        config_file_dir :   Path to the saved config file

        Returns:
        A Basler camera object
        """
        # conecting to the first available camera
        self.camera = pylon.InstantCamera(
            pylon.TlFactory.GetInstance().CreateFirstDevice())
        print("Using device ", self.camera.GetDeviceInfo().GetModelName())
        self.camera.Open()
        if config_file_dir:
            # Read a camera cofiguration file into the camera
            # refer to https://github.com/basler/pypylon/issues/131
            print("Reading file back to camera's node map...")
            pylon.FeaturePersistence.Load(
                config_file_dir, self.camera.GetNodeMap(), True)
        return

    def change_feature_map(self, config_file_dir):
        pylon.FeaturePersistence.Load(
            config_file_dir, self.camera.GetNodeMap(), True)

        return

    def start_imaging(self):
        """
        starts grabbing images with the camera, must run this before actually
        taking images

        Arguments:
        None
        Returns:
        None
        """
        # Latest Image strategy, none of the others seems suitable
        self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

        return

    def stop_imaging(self):
        """
        Stops grabbing images.

        Arguments:
        None

        Returns:
        None
        """
        # Releasing the resource
        self.camera.StopGrabbing()

        return

    def close_camera(self):
        """
        Switch off the camera and release all resources. Run create to restart.
        Arguments:
        None
        Returns:
        None
        """
        self.camera.Close()

        return

    def opencv_converter(self):
        """
        Creates an image format converter for getting opencv BGR images.
        Arguments:
        None
        Returns:
        Converter object
        """
        converter = pylon.ImageFormatConverter()
        # converting to opencv bgr format
        converter.OutputPixelFormat = pylon.PixelType_BGR8packed
        converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned

        return converter

    def take_one_opencv_image(self, converter):
        """
        Obtains a single opencv RGB image from the camera. Camera object
        should be created and imaging should have been started. Converter must
        be an opencv converter.

        Arguments:
        converter : opencv converter object, can be obtained using opencv_converter()

        returns:
        BGR opencv image array
        """
        try:
            grabResult = self.camera.RetrieveResult(
                5000, pylon.TimeoutHandling_ThrowException)
            # Image grabbed successfully?
            if grabResult.GrabSucceeded():
                # convert the image
                image = converter.Convert(grabResult)
                # Access the image data
                img = image.GetArray()
            else:
                print("Error: ", grabResult.ErrorCode,
                      grabResult.ErrorDescription)
            grabResult.Release()
        except genicam.GenericException as e:
            # Error handling.
            print("An exception occurred.")
            print(e.GetDescription())
            return

        return img

    def change_ROI(self, dimensions, offsets):
        """
        Change the camera ROI to capture only those pixels from the sensor.

        Arguments:
        dimensions : tuple of (width, height) of ROI in pixels
        offsets : tuple of (x-offset, y-offset) from the left top corner in pixels

        Returns:
        None
        """
        try:
            # Maximize the Image AOI.
            self.camera.Width = dimensions[0]
            self.camera.Height = dimensions[1]
            if genicam.IsWritable(self.camera.OffsetX):
                self.camera.OffsetX = offsets[0]
            if genicam.IsWritable(self.camera.OffsetY):
                self.camera.OffsetY = offsets[1]

        except genicam.GenericException as e:
            print(e.GetDescription())
            raise genicam.RuntimeException(
                "Could not apply configuration. GenICam::GenericException \
                                            caught in OnOpened method")
        return

    def max_ROI(self):
        """
        Set capture area to maximum available on the sensor.

        Arguments:
        None

        Returns:
        None
        """
        try:
            # Maximize the Image AOI.
            if genicam.IsWritable(self.camera.OffsetX):
                self.camera.OffsetX = self.camera.OffsetX.Min
            if genicam.IsWritable(self.camera.OffsetY):
                self.camera.OffsetY = self.camera.OffsetY.Min
            self.camera.Width = self.camera.Width.Max
            self.camera.Height = self.camera.Height.Max

        except genicam.GenericException as e:
            raise genicam.RuntimeException(
                "Could not apply configuration. GenICam::GenericException \
                                            caught in OnOpened method msg=%s" %
                e.what())
        return

    def capture_and_save_png(self, filename):
        """
        Captures an image to save it as a png in the given path. Can also use
        opencv to saved any converted images.

        Arguments:
        filename :  Path to the image

        Returns:
        None
        """
        img = pylon.PylonImage()
        with self.camera.RetrieveResult(5000) as result:
            # Calling AttachGrabResultBuffer creates another reference to the
            # grab result buffer. This prevents the buffer's reuse for
            # grabbing.
            img.AttachGrabResultBuffer(result)
            img.Save(pylon.ImageFileFormat_Png, filename)

            # In order to make it possible to reuse the grab result for grabbing
            # again, we have to release the image (effectively emptying the
            # image object)
            img.Release()

        return

    def capture_and_save_tiff(self, filename):
        """
        Captures an image to save it as a png in the given path. Can also use
        opencv to saved any converted images.

        Arguments:
        filename :  Path to the image

        Returns:
        None
        """
        img = pylon.PylonImage()
        with self.camera.RetrieveResult(5000) as result:
            # Calling AttachGrabResultBuffer creates another reference to the
            # grab result buffer. This prevents the buffer's reuse for
            # grabbing.
            img.AttachGrabResultBuffer(result)
            img.Save(pylon.ImageFileFormat_Tiff, filename)

            # In order to make it possible to reuse the grab result for grabbing
            # again, we have to release the image (effectively emptying the
            # image object)
            img.Release()

        return

    def set_exposure_time(self, exp_time):
        """
        Set exposure time for the sensor, switches auto exposure to "off".

        Arguments:
        exp_time   :    exposure time

        Returns:
        None
        """
        if self.camera.ExposureAuto() != "Off":
            self.camera.ExposureAuto.SetValue("Off")

        self.camera.ExposureTime.SetValue(exp_time)

        return

    def get_exposure_time(self):
        """
        Get current exposure time for the sensor.

        Arguments:
        None

        Returns:
        Current Exposure Time
        """
        return self.camera.ExposureTime()

    def set_pixel_format(self, mode):
        """
        Set pixel format of the camera. Look up docs for available formats.

        Arguments:
        mode   :    desired format as a string

        Returns:
        None
        """
        self.camera.PixelFormat.SetValue(mode)

        return

    def get_pixel_format(self):
        """
        Get current pixel format for the sensor.

        Arguments:
        None

        Returns:
        Current Exposure Time
        """
        return self.camera.PixelFormat()

    def show_preview_window(self):
        """Displays a preview window for the feed from the camera."""
        try:
            imageWindow = pylon.PylonImageWindow()
            imageWindow.Create(1)

            # Start the grabbing of c_countOfImagesToGrab images.
            # The camera device is parameterized with a default configuration which
            # sets up free-running continuous acquisition.
            self.camera.StartGrabbingMax(
                10000, pylon.GrabStrategy_LatestImageOnly)

            while self.camera.IsGrabbing():
                # Wait for an image and then retrieve it. A timeout of 5000 ms
                # is used.
                grabResult = self.camera.RetrieveResult(
                    5000, pylon.TimeoutHandling_ThrowException)

                # Image grabbed successfully?
                if grabResult.GrabSucceeded():
                    imageWindow.SetImage(grabResult)
                    imageWindow.Show()
                else:
                    print("Error: ", grabResult.ErrorCode)
                    # grabResult.ErrorDescription does not work properly in python
                    # could throw UnicodeDecodeError
                grabResult.Release()
                time.sleep(0.05)

                if not imageWindow.IsVisible():
                    self.camera.StopGrabbing()

            # imageWindow has to be closed manually
            imageWindow.Close()

        except genicam.GenericException as e:
            # Error handling.
            print("An exception occurred.")
            print(e.GetDescription())
