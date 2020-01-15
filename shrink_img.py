#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Administrator at 2020/1/12 10:12
import os
from tinify import tinify
import click

TINY_KEY = ''
TINY_KEY_FILE = 'tiny.key'
DEFUALT_TINY_SUFFIX = 'tiny'  # 默认文件在当前目录时，保存的后缀名
DEFUALT_TINY_DIR = 'tiny'  # 如果
TINY_SAVE_IN_CURRENT_DIR_SUFFIX = '.'
SUPPORT_IMG_TYPE = ['.jpg', '.png', 'jpeg']
VERSION = '1.0.0'


class NotDirError(Exception):
    pass


class NotFileError(Exception):
    pass


class NoKeyError(Exception):
    pass


def check_key():
    """
    check TINY_KEY
    代码中查找；文件中查找，没有的话，click装饰器会去环境变量中查找，再没有的话，提示用户手动输入
    :return:bool False：不需要用户输入；True:用户输入key
    """
    _tiny_key = TINY_KEY
    if not _tiny_key:
        _tiny_key = os.environ.get('TINY_KEY')
        print(_tiny_key, '------------tiny_key')
        if _tiny_key is None:
            if os.path.exists(TINY_KEY_FILE):
                with open(TINY_KEY_FILE, 'r') as f:
                    _tiny_key = f.read()
    print(_tiny_key, '----check_key-----')
    ret = True if not _tiny_key else False
    print(ret, '-------------------')
    return ret, _tiny_key


class ShrinkImages:
    """
    1. 如果没有给出参数，则递归压缩当前目录下的文件，并保存到`tiny`目录；
    2. 如果给出参数并且是文件，则压缩单个文件
        1. 如果没有额外参数，则压缩该文件并保存到tiny目录；
        2. 如果给出的额外参数是 -d xxx，则保存到用户指定的目录（目录可以是相对，也可以是绝对路径）；
        3. 如果给出的参数是 -f  xxx，如果为空，则压缩成同名+'_tinified'；如果不为空且有后缀，则验证后缀相同再压缩，否则raise；覆盖压缩： -c flag:cover source file.
    3. 如果给出参数[源目录 目的目录]，则将文件保存到指定目录；
    """

    def __init__(self, api_key=''):
        self.api_key = api_key
        self.version = VERSION
        self.support_img_type = SUPPORT_IMG_TYPE
        tinify.key = self.api_key

    @staticmethod
    def get_counts():
        """
        socket 建立连接之后才可以获取到
        """
        return tinify.compression_count

    @staticmethod
    def _file_ext(fp):
        """
        返回给定的带路径的文件后缀名
        :param fp:
        :return:
        """
        root, ext = os.path.splitext(fp)
        return root, ext.lower()

    @staticmethod
    def core_from_tinify(src_file_fp, dst_file_fp):
        print(f'-from--{src_file_fp}--------to-----{dst_file_fp}-------')
        ret = tinify.from_file(src_file_fp).to_file(dst_file_fp)
        return ret

    @staticmethod
    def resize(options, width, height, src_file_fp, dst_file_fp):
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
        print(f'-from--{src_file_fp}--------to-----{dst_file_fp}-------')
        assert os.path.isfile(src_file_fp)
        _, lower_from_ext = self._file_ext(src_file_fp)
        _, lower_to_ext = self._file_ext(dst_file_fp)
        if lower_to_ext:  # 保存路径有后缀，则保存在当前目录下
            assert lower_from_ext == lower_to_ext  # 类型相同
        else:  # 保存到指定目录下
            file_path, just_file_name = os.path.split(src_file_fp)
            dst_file_fp = os.path.join(file_path, just_file_name)

        ret = self.core_from_tinify(src_file_fp, dst_file_fp)
        return ret

    def compress_dir_action(self, parent, to_dir, current_fp, file_name_lists):
        file_list = []
        for file in file_name_lists:
            _, ext = self._file_ext(file)
            if file and ext in self.support_img_type:
                from_fp = os.path.join(parent, file)
                to_file_name = os.path.basename(from_fp)
                if to_dir:
                    if not os.path.exists(to_dir):
                        if os.path.isdir(to_dir):
                            dst_file_fp = os.path.join(current_fp, to_dir, to_file_name)
                        else:
                            raise NotDirError(f'The path {to_dir} exist but not dir.')
                    else:
                        raise FileNotFoundError(f'The dir {to_dir} not exist.')
                else:
                    dst_file_fp = os.path.join(current_fp, DEFUALT_TINY_SUFFIX, to_file_name)

                ret = self.compress_single_file(from_fp, dst_file_fp)
                print(f'ret is {ret}')
                file_list.append(from_fp)

    def compress_dir(self, from_dir='', to_dir='', recurse=True):
        print(f'From {from_dir} to {to_dir}')
        if not os.path.exists(to_dir):  # 如果没有，则创建该目录，以存储压缩文件
            os.mkdir(to_dir)
        current_fp = os.path.join(os.getcwd(), os.path.dirname(__file__))
        filelist = []
        if not from_dir:
            fp = current_fp
        else:
            fp = from_dir
        print(fp, '==================')
        if recurse:
            for parent, dirnames, filenames in os.walk(fp):
                self.compress_dir_action(parent, to_dir, current_fp, filenames)

        else:
            dir_files = os.listdir(fp)
            if os.path.isdir(fp):
                parent = fp
                self.compress_dir_action(parent, to_dir, current_fp, dir_files)
            elif os.path.isfile(fp):
                raise NotDirError(f'The path {fp} exist but not dir.')

        return filelist


has_key, tiny_key = check_key()


@click.command()
@click.option('-d', "--dir", type=click.Path(exists=True), default=TINY_SAVE_IN_CURRENT_DIR_SUFFIX, help="被压缩的文件夹")
@click.option('-f', "--file", type=click.Path(exists=True), help="单个文件压缩")
@click.option('-s', "--save", type=click.Path(exists=False), default=DEFUALT_TINY_SUFFIX,
              help="选择文件夹时，指定保存的目录")
# @click.option('-d', "--dir", 'dir_name', flag_value=None, default=True, help="如果没有文件，则是被压缩的文件夹/如果有文件，则是被压缩的文件保存的目录")
@click.option('-o', "--overwirte", type=bool, default=True, help="仅支持指定文件时，覆盖压缩，即直接压缩并保存到当前目录")
@click.option('-r/-nr', "--recurse/--not_recurse", default=True, help="递归压缩整个给定的目录")
@click.option("--scale", type=str, help="以scale方式调整图片大小")
@click.option('-w', "--width", type=int, help="以 scale 方式（仅该方式需要此参数）调整图片时指定宽度")
@click.option('-h', "--height", type=int, help="以 scale 方式（仅该方式需要此参数）调整图片时指定高度")
@click.option("--fit", type=click.Tuple([str, int, int]), default=[None] * 3, help="以fit方式调整图片大小")
@click.option("--cover", nargs=3, type=click.Tuple([str, int, int]), default=[None] * 3, help="以cover方式调整图片大小")
@click.option("--thumb", nargs=3, type=(str, int, int), default=[None] * 3, help="以thumb方式调整图片大小")
@click.option('-k', '--key', prompt=has_key, envvar='TINY_KEY', help="官网申请的key")
def run(file, dir, save, overwirte, fit, thumb, cover, scale, width, height, recurse, key=None):
    # print(fit)
    print(f'resize file {scale, fit, cover, thumb}')
    print(f'I get args: {file, dir, save, overwirte, fit, thumb, cover, scale, width, height, key, recurse}')
    ret = None
    if key is None:
        key = tiny_key
        if not key:
            raise NoKeyError("I can't make bricks without straw.Give me TINY_KEY Please?")
    print(f' Using key-------{key}------------.')  # TODO: 检查key超过次数之后，应该重新设置key
    if key is not '':
        with open(TINY_KEY_FILE, 'w') as f:  # TODO: configuration
            f.write(key)
    # ======== handle key finished ============
    tiny_img = ShrinkImages(api_key=key)
    if dir is not None and not any([scale, fit, cover, thumb]):
        print(dir, '---------------------------dddddd')
        if not recurse:
            tiny_img.compress_dir(recurse=False)
            print(f'not recurse compress {dir} to {save}')
        else:
            # 不输入任何参数：递归保存dir目录下文件到tiny目录
            print(f'压缩目录 {dir} to {save}')
            return
            tiny_img.compress_dir(from_dir=dir, to_dir=save)

    elif file is not None:  # 压缩文件 TODO:此处需要考虑只给定目录的情况
        print(f'file {file}-------')
        if dir is None:  # 指定目录
            if overwirte:
                print('覆盖压缩到当前目录')
                tiny_img.compress_single_file(src_file_fp=file, dst_file_fp=file)
            else:
                if os.path.isfile(file):
                    print('文件名加后缀之后保存到当前目录下')

                    tiny_img.compress_single_file(src_file_fp=file, dst_file_fp=TINY_SAVE_IN_CURRENT_DIR_SUFFIX)

        else:
            dst_file_fp = dir or save
            print('保存到指定目录，相当于覆盖保存')
            tiny_img.compress_single_file(src_file_fp=file, dst_file_fp=dst_file_fp)

    elif any([scale, fit, cover, thumb]):  # TODO: resize file only 是否支持-f参数？
        print(f'resize file {scale, fit, cover, thumb}')  # TODO: 传参 conflict
        method = ''
        if scale:
            method = 'scale'
            assert (width or height) and not all([width, height])
            if width:
                print(f'width for scale is {width}.')
            else:
                print(f'height for scale is {height}.')
        else:
            print(f'args is {fit, cover, thumb}')
            if fit:
                method = 'fit'
            elif cover:
                method = 'cover'
            else:
                method = 'thumb'

            file, width, height = fit or cover or thumb
            
        if dir is None:  # 指定目录     #TODO partical  偏函数
            if overwirte:
                print('覆盖压缩到当前目录')
                tiny_img.resize(method, width, height,src_file_fp=file, dst_file_fp=file)
            else:
                if os.path.isfile(file):
                    print('文件名加后缀之后保存到当前目录下')

                    tiny_img.resize(method, width, height,src_file_fp=file, dst_file_fp=TINY_SAVE_IN_CURRENT_DIR_SUFFIX)

        else:
            dst_file_fp = dir or save
            print('保存到指定目录，相当于覆盖保存')
            # tiny_img.compress_single_file(src_file_fp=file, dst_file_fp=dst_file_fp)

            tiny_img.resize(method, width, height,src_file_fp=file, dst_file_fp=dst_file_fp)

    else:
        pass
    count = tiny_img.get_counts()
    print(f'the key used for {count} times.')
    return ret


# tiny_img = ShrinkImages()


# @click.command()
# @click.option('--pos', nargs=2, type=float)
# def run(pos):
#     click.echo('%s / %s' % pos)

# def conditional_decorator(dec, condition):
#     def decorator(func):
#         if not condition:
#             # Return the function unchanged, not decorated.
#             return func
#         return dec(func)
#
#     return decorator


if __name__ == '__main__':
    # 来自环境变量的值 https://www.osgeo.cn/click/options.html#values-from-environment-variables
    result = run(auto_envvar_prefix='TINY')
    print(result)
