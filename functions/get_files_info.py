import os


def get_files_info(working_directory, directory="."):
    working_dir_abs = os.path.abspath(working_directory)
    target_dir = os.path.normpath(os.path.join(working_dir_abs, directory))
    print('Result for current directory:')
    try:
        # Will be True or False
        valid_target_dir = (
            os.path.commonpath([working_dir_abs, target_dir]) == working_dir_abs
        )
        if not valid_target_dir:
            raise Exception(f'Error: Cannot list "{directory}" as it is outside the permitted working directory')
        if (not os.path.isdir(target_dir)):
            raise Exception(f'Error: "{directory}" is not a directory')
        for item in os.listdir(target_dir):
            path = os.path.join(target_dir, item)
            size = os.path.getsize(path)
            is_dir = os.path.isdir(path)
            print(f' - {item}: file_size={size} bytes, is_dir={is_dir}')
    except Exception as e:
        print(f'  Error: {e}')
