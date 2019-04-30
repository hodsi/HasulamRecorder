import sys
from argparse import ArgumentParser

from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip


def parse_input(argv):
    my_input_parser = ArgumentParser()
    my_input_parser.add_argument(
        dest='video_file_path',
        help='the video path to cut'
    )
    my_input_parser.add_argument(
        dest='start_time', type=int,
        help='how many second from the start to cut from'
    )
    my_input_parser.add_argument(
        dest='end_time', type=int, nargs='?', default=None,
        help='how many seconds from the start to cut to'
    )
    my_input_parser.add_argument(
        '-o', '--out', dest='out_file_path',
        default=None,
        help='the file path to save the file after cutting it (get generate a random name without the argument)'
    )
    return my_input_parser.parse_args(argv)


def get_video_length(video_path):
    with VideoFileClip(video_path) as source_clip:
        source_length = source_clip.duration
    return source_length


def get_absolute_time(relative_time, video_length):
    if relative_time >= 0:
        return relative_time
    return video_length + relative_time


def main(argv):
    video_length = get_video_length(argv.video_file_path)
    start_time = get_absolute_time(argv.start_time, video_length)
    end_time = get_absolute_time(argv.end_time or video_length, video_length)
    ffmpeg_extract_subclip(
        argv.video_file_path,
        start_time,
        end_time,
        argv.out_file_path
    )


if __name__ == '__main__':
    main(parse_input(sys.argv[1:]))
