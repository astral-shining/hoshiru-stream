import os
import argparse
import subprocess

parser = argparse.ArgumentParser(description="Stream video script")
parser.add_argument("-j", "--join", default=0, metavar="<host>", type=str, help="Join to stream rtsp")
parser.add_argument("-s", "--stream", action="store_true", default=False, help="Stream rtsp")
parser.add_argument("-b", "--stream-bitrate", default=1000, type=int, help="Stream bitrate KB (default 1000)")
parser.add_argument("-c", "--stream-crf", type=int, help="Stream crf")
parser.add_argument("-t", "--stream-threads", default=2, metavar="<threads>", type=int, help="Number of threads streaming (default 2)")
parser.add_argument("-f", "--stream-fps", default=24, metavar="<fps>", type=int, help="Fps video rate")
parser.add_argument("--stream-preset", default="fast", metavar="<preset>", type=str, help="Preset ffmpeg (default fast)")
parser.add_argument("--stream-no-audio", action='store_true', help="Disable audio")

args = parser.parse_args()
if args.join:
    subprocess.run("ffplay -probesize 32 -analyzeduration 0 -sync ext -rtsp_transport tcp rtsp://{}:8554/stream".format(args.join), shell=True)
    exit()


if args.stream:
    rtsp_process = subprocess.Popen("rtsp-simple-server", shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
    ffmpeg_process = subprocess.Popen("ffmpeg {audio} -video_size 1920x1080 -probesize 32 -f x11grab -i :0.0+0,0 -c:v libx264 -maxrate {maxrate}k -preset {preset} -tune zerolatency -x264-params \"intra-refresh=1\" -bufsize {bufsize}k -g 120 -refs 1 -f_strict experimental -syncpoints none -threads {threads} -f rtsp 'rtsp://localhost:8554/stream'".format(
        audio="-fragment_size 256 -f pulse -i 0 -framerate 24 " if not args.stream_no_audio else "",
        maxrate=args.stream_bitrate,
        bufsize=args.stream_bitrate*2,
        threads=args.stream_threads,
        preset=args.stream_preset

    ), shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    rtsp_process.communicate()

