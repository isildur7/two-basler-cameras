from threading import Thread
from time import sleep
from pypylon import pylon
import imageio as iio
from FFMPEGwriter import FFMPEGVideoWriter


def videos_from_two_cameras(filename1, filename2, recordTime, pixFormatCam,
                            camExposure, fps, pixFormatVideo, writer):
    """Shoot and save simultaneous video from two Basler cameras.

    Creates and opens a two camera array, sets imaging parameters on both
    cameras, opens two threads and runs the video capture function for one
    camera on each thread. Closes the camera array after capture is done. A
    fixed number of images are captured given by <frame rate> times <time> and
    written to video. There are two choices of video writers, selected via the
    'writer' argument - 'imageio' is the writer from python imageio library and
    'FFMPEG' is the writer from issue #113 on pypylon GitHub repository.

    :param filename1: string filename of the first video file
    :param filename2: string filename of the second video file
    :param recordTime: float time of recording in seconds
    :param pixFormatCam: string pixel format string for the Basler cameras
    :param camExposure: int exposure time of Basler cameras in microseconds
    :param fps: float frame rate in frames per second
    :param pixFormatVideo: string to choose pixel format for the video writer
    :param: writer: string either 'imageio' or 'FFMPEG' to choose video writer

    :returns: None
    """
    cams = create_n_cameras(2)
    numImages = fps * recordTime

    cams.Open()

    set_camera_properties(cams[0], fps, pixFormatCam, camExposure)
    set_camera_properties(cams[1], fps, pixFormatCam, camExposure)

    # start recording on two threads
    t1 = Thread(target=camera_video, args=(cams[0], filename1, numImages, fps,
                                           pixFormatVideo, writer))
    t2 = Thread(target=camera_video, args=(cams[1], filename2, numImages, fps,
                                           pixFormatVideo, writer))
    t1.start()
    t2.start()

    cams.Close()

    return


def set_camera_properties(cam, fps, pixFormatCam, camExposure):
    cam.PixelFormat = pixFormatCam
    cam.AcquisitionFrameRateEnable.SetValue(True)
    cam.AcquisitionFrameRate.SetValue(fps)
    cam.ExposureTime.SetValue(camExposure)


def camera_video(cam, fname, numImages, fps, pixFormatVideo, writer):
    # sleep for a bit
    sleep(1)

    # grab images for the video and store them in a buffer
    cam.StartGrabbingMax(numImages, pylon.GrabStrategy_LatestImageOnly)
    buffer = []  # TODO find a better way
    while cam.IsGrabbing():
        res = cam.RetrieveResult(1000)
        buffer.append(res.Array)
        res.Release()

    if writer == "imageio":
        with iio.get_writer(
            fname,  # mkv players often support H.264
            fps=fps,  # FPS is in units Hz; should be real-time.
            codec='libx264',  # When used properly, this is basically
                              # "PNG for video" (i.e. lossless)
            quality=None,  # disables variable compression
            pixelformat=pixFormatVideo,  # keep it as RGB colours
            ffmpeg_params=[  # compatibility with older library versions
                '-preset',  # set to faster, veryfast, superfast, ultrafast
                'medium',     # for higher speed but worse compression
                '-crf',  # quality; set to 0 for lossless, but keep in mind
                '11'     # that the camera probably adds static anyway
                        ]) as writer:
            for image in buffer:
                writer.append_data(image)
    else:
        with FFMPEGVideoWriter(fname, (cam.Height(), cam.Width()), fps=20,
                               pixfmt=pixFormatVideo) as writer:
            for image in buffer:
                writer.write_frame(image)

    return


def create_n_cameras(n):
    tlf = pylon.TlFactory.GetInstance()

    # See all the available devices
    di = pylon.DeviceInfo()

    devs = tlf.EnumerateDevices([di, ])
    print(devs)

    # Create a camera array object and attach the cameras to it
    cam_arr = pylon.InstantCameraArray(n)
    for idx, cam in enumerate(cam_arr):
        cam.Attach(tlf.CreateDevice(devs[idx]))

    return


if __name__ == "__main__":
    FPS = 20
    RECORDING_TIME = 10  # in seconds
    FILE1 = "./samplevid1.avi"  # extension can be changed
    FILE2 = "./samplevid2.avi"  # extension can be changed
    CAMPIXFMT = "Mono8"  # can change to anything available on the camera
    VIDPIXFMT = "gray"  # since camera is in Mono mode
    CAMEXPTIME = 40000
    WRITER = "imageio"  # use either "imageio" or "FFMPEG"

    # shoot video
    videos_from_two_cameras(FILE1, FILE2, RECORDING_TIME, CAMPIXFMT,
                            CAMEXPTIME, FPS, VIDPIXFMT, WRITER)
