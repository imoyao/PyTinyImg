#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by imoyao at 2020/1/15 23:15
import os

from tinify import tinify

import exceptions
import settings


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
        self.version = settings.VERSION
        self.support_img_type = settings.SUPPORT_IMG_TYPES
        tinify.key = self.api_key

    @staticmethod
    def get_counts():
        """
        get use counts after first connect to server
        """
        return tinify.compression_count

    @staticmethod
    def file_ext(fp):
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
        print(f'-from--{src_file_fp}--------to-----{dst_file_fp}-----compress_single_file--')
        assert os.path.isfile(src_file_fp)
        _, lower_from_ext = self.file_ext(src_file_fp)
        _, lower_to_ext = self.file_ext(dst_file_fp)
        if lower_to_ext:  # 保存路径有后缀，则保存在当前目录下
            assert lower_from_ext == lower_to_ext  # 类型相同
        else:  # 保存到指定目录下
            file_path, just_file_name = os.path.split(src_file_fp)
            dst_file_fp = os.path.join(file_path, just_file_name)

        ret = self.core_from_tinify(src_file_fp, dst_file_fp)
        return ret

    def compress_dir_action(self, parent, to_dir, current_fp, file_name_lists):
        file_list = []
        print(f'{parent, to_dir, current_fp, file_name_lists}------compress_dir_action------')
        for file in file_name_lists:
            _, ext = self.file_ext(file)
            if file and ext in self.support_img_type:
                from_fp = os.path.join(parent, file)
                to_file_name = os.path.basename(from_fp)
                if to_dir:
                    if os.path.exists(to_dir):
                        if os.path.isdir(to_dir):
                            dst_file_fp = os.path.join(current_fp, to_dir, to_file_name)
                        else:
                            raise exceptions.NotDirError(f'The path {to_dir} exist but not dir.')
                    else:
                        raise FileNotFoundError(f'The dir {to_dir} not exist.')
                else:
                    dst_file_fp = os.path.join(current_fp, settings.DEFUALT_TINY_SUFFIX, to_file_name)

                ret = self.compress_single_file(from_fp, dst_file_fp)
                print(f'ret is {ret}')
                file_list.append(from_fp)

    def compress_dir(self, from_dir='', to_dir='', recurse=True):
        print(f'From {from_dir} to {to_dir}------compress_dir--------')
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
                raise exceptions.NotDirError(f'The path {fp} exist but not dir.')

        return filelist
