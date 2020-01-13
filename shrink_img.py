#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Administrator at 2020/1/12 10:12
import os
from tinify import tinify
import click


class NotDirError(Exception):
    pass


class NotFileError(Exception):
    pass


class ShrinkImages:
    """

1. 如果没有给出参数，则递归压缩当前目录下的文件，并保存到`tiny`目录；
2. 如果给出参数并且是文件，则压缩单个文件
    1. 如果没有额外参数，则压缩该文件并保存到tiny目录；
    2. 如果给出的额外参数是 -d xxx，则保存到用户指定的目录（目录可以是相对，也可以是绝对路径）；
    3. 如果给出的参数是 -f  xxx，如果为空，则压缩成同名+'_tinified'；如果不为空且有后缀，则验证后缀相同再压缩，否则raise；覆盖压缩： -c flag:cover source file.
3. 如果给出参数[源目录 目的目录]，则将文件保存到指定目录；
    """

    def __init__(self, api_key='', back_up_folder=''):
        self.api_key = api_key
        self.version = '1.0.0'
        self.back_up_folder = back_up_folder or 'tiny'
        self.support_img_type = ['.jpg', '.png', 'jpeg']
        tinify.key = self.api_key

    def check_key(self):
        if not self.api_key:
            os.environ.get('TINY_KEY')
        else:
            # 压缩之后才能获取到
            compression_counts = tinify.compression_count
        print(compression_counts)

    def file_ext(self, fp):
        """
        返回给定的带路径的文件后缀名
        :param fp:
        :return:
        """
        root, ext = os.path.splitext(fp)
        return root, ext.lower()

    def core_from_tinify(self, src_file_fp, dst_file_fp):
        print(src_file_fp, '-----------core_from_tinify------------', dst_file_fp)
        ret = tinify.from_file(src_file_fp).to_file(dst_file_fp)
        return ret

    def resize(self, options, width, height, src_file_fp, dst_file_fp):
        """
        调整大小也算是一种压缩
        """
        assert options in ['scale', 'fit', 'cover', 'thumb']
        source = tinify.from_file(src_file_fp)
        resized = source.resize(
            method=options,
            width=width,
            height=height
        )
        ret = resized.to_file(dst_file_fp)
        return ret

    def compress_single_file(self, src_file_fp='', dst_file_fp=''):
        """
        全路径，直接保存文件： from >> to
        """
        print(src_file_fp, '-----------tototo------------', dst_file_fp)
        assert os.path.isfile(src_file_fp)
        _, lower_from_ext = self.file_ext(src_file_fp)
        _, lower_to_ext = self.file_ext(dst_file_fp)
        print(lower_from_ext, '-----------bf lower_to_ext------------', lower_to_ext)
        if lower_to_ext:  # 保存路径有后缀，则保存在当前目录下
            assert lower_from_ext == lower_to_ext  # 类型相同
        else:  # 保存到指定目录下
            file_path, just_file_name = os.path.split(src_file_fp)
            dst_file_fp = os.path.join(file_path, just_file_name)

        ret = self.core_from_tinify(src_file_fp, dst_file_fp)
        return ret

    def compress_dir(self, from_dir='', to_dir=''):
        print(f'From {from_dir} to {to_dir}')
        current_fp = os.path.join(os.getcwd(), os.path.dirname(__file__))
        filelist = []
        if not from_dir:
            fp = current_fp
        else:
            fp = from_dir
        print(fp, '==================')
        for parent, dirnames, filenames in os.walk(fp):
            for file in filenames:
                _, ext = self.file_ext(file)
                if file and ext in self.support_img_type:
                    from_fp = os.path.join(parent, file)
                    to_file_name = os.path.basename(from_fp)
                    if to_dir:
                        if os.path.exists(to_dir):
                            if os.path.isdir(to_dir):
                                dst_file_fp = os.path.join(current_fp, to_dir, to_file_name)
                            else:
                                raise NotDirError(f'The path {to_dir} exist but not dir.')
                        else:
                            raise FileNotFoundError(f'The dir {to_dir} not exist.')
                    else:
                        dst_file_fp = os.path.join(current_fp, self.back_up_folder, to_file_name)
                    print(dst_file_fp, '---------11111-----')
                    dirname = os.path.dirname(dst_file_fp)
                    if not os.path.exists(dirname):  # 如果没有，则创建该目录，以存储压缩文件
                        os.mkdir(dirname)
                    ret = self.compress_single_file(from_fp, dst_file_fp)
                    print(f'ret is {ret}')
                    filelist.append(from_fp)
        return filelist


tiny_img = ShrinkImages(api_key='GT5qbfVhYvp9X5gfXBPdsvG8hRtmKCMz')


@click.command()
@click.option('-f', "--file", type=str, default=None, help="单个文件压缩")
@click.option('-d', "--dir", type=str, default=None, help="被压缩的文件夹")
@click.option('-s', "--save", type=str, default=None, help="选择文件夹时，指定保存的目录")
# @click.option('-d', "--dir", 'dir name', flag_value=None,
#               default=True, help="如果没有文件，则是被压缩的文件夹/如果有文件，则是被压缩的文件保存的目录")
# @click.option('-w', "--width", type=int, default=-1, help="图片宽度，默认不变")
@click.option('-c', "--fcover", type=str, default='', help="覆盖压缩，即直接压缩并保存到当前目录")
@click.option('-r', "--recurse/--not-recurse", default=True, help="递归压缩整个给定的目录")
@click.option("--scale", type=int, help="以scale方式调整图片大小")
@click.option("--width", type=int, help="以 scale 方式（仅该方式需要此参数）调整图片时指定宽度")
@click.option("--height", type=int, help="以 scale 方式（仅该方式需要此参数）调整图片时指定高度")
@click.option("--fit", type=(int, int), help="以fit方式调整图片大小")
@click.option("--cover", type=(int, int), help="以cover方式调整图片大小")
@click.option("--thumb", type=(int, int), help="以thumb方式调整图片大小")
@click.option('-k', '--key', prompt=True, default=lambda: os.environ.get('TINY_KEY', ''), help="官网申请的key")
def run(file, dir, save, fcover, fit, thumb, cover, scale,width,height, key='', recurse=False,):
    ret = None
    if key is not '':
        """
        在执行前直接配置：程序自动获取（环境变量、文件、代码中），没有则提示配置
        如果设置key>>>保存到文件中，下一次执行，直接读取;
        如果不设置，在环境变量和文件中去读取，读取到，则判断key是否可用，可以继续执行
        """
        print(key)
    if any([scale, fit, cover, thumb]):
        if scale:
            assert (width or height) and not all([width, height])
            if width:
                print(f'width for scale is {width}.')
            else:
                print(f'height for scale is {height}.')

    if file is not None:  # 压缩文件
        if dir is None:
            if fcover:
                print('覆盖压缩到当前目录')

            else:
                print('改名保存到当前目录')
        else:
            print('保存到指定目录')
    if any([scale, fit, cover, thumb]):
        print('resize file')
        if os.path.isfile(file):
            print(f'resieze file: {file}')
        else:
            raise NotFileError(f'The args you give file {file} is not a file.')
        print('压缩文件，直接覆盖压缩！')
        # ret = tiny_img.compress_single_file(file)  # 仅压缩一个文件
    else:
        print('压缩目录!')
        if save is not None:
            print(f'the file will save in folder {save}.')
        else:
            print(f'the file will save in default folder.')

        # ret = tiny_img.compress_dir(dir)  # 压缩指定目录下的文件

    return ret


if __name__ == '__main__':
    ret = run()
    print(ret)
