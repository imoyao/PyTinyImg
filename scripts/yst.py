#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created by imoyao at 2020/1/12 10:12
import os
import click

import exceptions
import settings
from tiny_core import ShrinkImages


def check_key():
    """
    check TINY_KEY
    代码中查找；文件中查找，没有的话，click装饰器会去环境变量中查找，再没有的话，提示用户手动输入
    :return:bool False：不需要用户输入；True:用户输入key
    """
    _tiny_key = settings.TINY_KEY
    if not _tiny_key:
        _tiny_key = os.environ.get('TINY_KEY')

        if _tiny_key is None:
            if os.path.exists(settings.TINY_KEY_FILE):  # TODO conf
                with open(settings.TINY_KEY_FILE, 'r') as f:
                    _tiny_key = f.read()

    ret = True if not _tiny_key else False
    return ret, _tiny_key


has_key, tiny_key = check_key()


def show_version(ctx, param, value):
    """
    show the version
    :param ctx:
    :param param: del this will get: Warning: Invoked legacy parameter callback……
    :param value:
    :return:
    """
    if not value or ctx.resilient_parsing:
        return
    click.echo(settings.VERSION)
    ctx.exit()


@click.command()
@click.option('-d', "--dir", type=click.Path(exists=True), default=settings.TINY_SAVE_IN_CURRENT_DIR_SUFFIX,
              help="被压缩的文件夹")
@click.option('-f', "--file", type=click.Path(exists=True), help="单个文件压缩")
@click.option('-s', "--save", type=click.Path(exists=False), default=settings.DEFUALT_TINY_SUFFIX,
              help="选择文件夹时，指定保存的目录")
@click.option('-o/-no', "--overwrite/-write", help="覆盖压缩，即直接压缩并保存到当前目录")
@click.option('-r/-nr', "--recurse/--not_recurse", default=True, help="递归压缩整个给定的目录")
@click.option("--scale", type=str, help="以scale方式调整图片大小")
@click.option('-w', "--width", type=int, help="以 scale 方式（仅该方式需要此参数）调整图片时指定宽度")
@click.option("--height", type=int, help="以 scale 方式（仅该方式需要此参数）调整图片时指定高度")
@click.option("--fit", type=click.Tuple([str, int, int]), default=[None] * 3, help="以fit方式调整图片大小")
@click.option("--cover", nargs=3, type=click.Tuple([str, int, int]), default=[None] * 3, help="以cover方式调整图片大小")
@click.option("--thumb", nargs=3, type=(str, int, int), default=[None] * 3, help="以thumb方式调整图片大小")
@click.option('-k', '--key', prompt=has_key, envvar='TINY_KEY', help="官网申请的key")
@click.option('-v', '--version', is_flag=True, callback=show_version,
              expose_value=False, is_eager=True)
def cli(file, dir, save, overwrite, fit, thumb, cover, scale, width, height, recurse, key=None):
    # print(fit)
    print(f'resize file {scale, fit, cover, thumb}')
    print(f'I get args: {file, dir, save, overwrite, fit, thumb, cover, scale, width, height, key, recurse}')
    ret = None
    if key is None:
        key = tiny_key
        if not key:
            raise exceptions.NoKeyError("I can't make bricks without straw.Give me TINY_KEY Please?")
    print(f' Using key-------{key}------------.')  # TODO: 检查key超过次数之后，应该重新设置key
    if key is not '':
        with open(settings.TINY_KEY_FILE, 'w') as f:  # TODO: configuration
            f.write(key)
    # ======== handle key finished ============
    tiny_img = ShrinkImages(api_key=key)

    if dir is not None and not all([scale, fit, cover, thumb]) and not file:
        print(dir, '---------------------------dddddd')
        if not recurse:
            tiny_img.compress_dir(recurse=False)
            print(f'not recurse compress {dir} to {save}')
        else:
            if overwrite:
                if click.confirm(f'The files of dir: {dir} will be overwrite,Do you want to continue?', abort=True):
                    fp = os.path.abspath(dir)
                    tiny_img.compress_dir(from_dir=fp, to_dir=fp)
            else:
                # 不输入任何参数：递归保存dir目录下文件到tiny目录
                print(f'压缩目录 {dir} to {save}')
                tiny_img.compress_dir(from_dir=dir, to_dir=save)

    elif file is not None:  # 压缩文件 TODO:此处需要考虑只给定目录的情况
        print(f'file {file}---{dir}----')
        if dir is settings.TINY_SAVE_IN_CURRENT_DIR_SUFFIX:  # 指定目录
            if overwrite:
                print('覆盖压缩到文件所在目录')
                tiny_img.compress_single_file(src_file_fp=file, dst_file_fp=file)
            else:
                if os.path.isfile(file):
                    print('文件名加后缀名之后保存到当前目录下')
                    fp, fn_with_ext = os.path.split(file)
                    fn, ext = tiny_img.file_ext(fn_with_ext)
                    dst_file_fp = f'{settings.TINY_SAVE_IN_CURRENT_DIR_SUFFIX}/{fn}_{settings.DEFUALT_TINY_SUFFIX}{ext}'

                    if os.path.exists(dst_file_fp):
                        if click.confirm(f'The file {dst_file_fp} already exists,Do you want to continue?', abort=True):
                            click.echo('Well done!')
                    tiny_img.compress_single_file(src_file_fp=file, dst_file_fp=dst_file_fp)

        else:
            # fp, ext = tiny_img.file_ext(file) # TODO: save to user specific path
            # dst_file_fp = f'{fp}_{DEFUALT_TINY_SUFFIX}{ext}'
            dst_file_fp = dir or save
            print('保存到指定目录')
            tiny_img.compress_single_file(src_file_fp=file, dst_file_fp=dst_file_fp)

    elif any([scale, fit, cover, thumb]):  # TODO: resize file only 是否支持-f参数？
        print(f'resize file {scale, fit, cover, thumb}')  # TODO: 传参 conflict
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

        if dir is None:  # 指定目录
            if overwrite:
                print('覆盖压缩到当前目录')
                tiny_img.resize(method, width, height, src_file_fp=file, dst_file_fp=file)
            else:
                if os.path.isfile(file):
                    print('文件名加后缀之后保存到当前目录下')

                    tiny_img.resize(method, width, height, src_file_fp=file,
                                    dst_file_fp=settings.TINY_SAVE_IN_CURRENT_DIR_SUFFIX)

        else:
            dst_file_fp = dir or save
            print('保存到指定目录，相当于覆盖保存')
            # tiny_img.compress_single_file(src_file_fp=file, dst_file_fp=dst_file_fp)

            tiny_img.resize(method, width, height, src_file_fp=file, dst_file_fp=dst_file_fp)

    else:
        pass
    count = tiny_img.get_counts()
    print(f'The key has used for {count} times.')
    return ret


# tiny_img = ShrinkImages()


# @click.command()
# @click.option('--pos', nargs=2, type=float)
# def cli(pos):
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
    # see also: https://www.osgeo.cn/click/options.html#values-from-environment-variables
    result = cli(auto_envvar_prefix='TINY')
    print(result)
