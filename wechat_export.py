#!/usr/bin/env python3
import os
import iphone_backup_decrypt
import getpass
import argparse
import logging


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input-dir", help="iOS备份的目录路径", required=True)
    parser.add_argument("-o", "--output-dir", help="导出的目录", required=True)
    parser.add_argument("-v", "--verbose", help="显示更多的log", action="store_true")
    parser.add_argument("--password", help="直接在命令行指定密码", default=None)
    args = parser.parse_args()

    input_dir: str = args.input_dir
    output_dir: str = args.output_dir
    verbose: bool = args.verbose
    password: str = args.password or getpass.getpass("输入密码:")

    logging.basicConfig(level=logging.INFO if verbose else logging.WARNING)

    backup = iphone_backup_decrypt.EncryptedBackup(
        backup_directory=input_dir, passphrase=password
    )
    backup._decrypt_manifest_db_file()
    assert backup._temp_manifest_db_conn
    for file_id, relative_path, file_bplist in backup._temp_manifest_db_conn.execute(
        'select fileID, relativePath, file  from Files where flags = 1 and domain = "AppDomain-com.tencent.xin"'
    ):
        logging.info(
            "Decrypting and writing file ID %s with path %s", file_id, relative_path
        )
        data = backup._decrypt_inner_file(file_id=file_id, file_bplist=file_bplist)
        if data is None:
            logging.warning("No data for %r", relative_path)
        else:
            output_filename = os.path.join(output_dir, relative_path)
            os.makedirs(os.path.dirname(output_filename), exist_ok=True)
            with open(output_filename, "wb") as f:
                f.write(data)


if __name__ == "__main__":
    main()
