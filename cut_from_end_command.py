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
        dest='seconds_to_cut_from_end', type=int,
        help='how much second to cut before the end'
    )
    my_input_parser.add_argument(
        '-o', '--out', dest='out_file_path',
        default=None,
        help='the file path to save the file after cutting it (get generate a random name without the argument)'
    )
    return my_input_parser.parse_args(argv)


def cut_video(video_path, end_time, target_name):
    with VideoFileClip(video_path) as source_clip:
        source_length = source_clip.duration
    return ffmpeg_extract_subclip(video_path, source_length - end_time, source_length, target_name)


def main(argv):
    cut_video(argv.video_file_path, argv.seconds_to_cut_from_end, argv.out_file_path)


if __name__ == '__main__':
    main(parse_input(sys.argv[1:]))
