import unittest
import tempfile
import os
import sys
from dataclasses import dataclass
from string import Template


@dataclass
class PackageScanItem:
    full_path: str
    package: str
    has_package_info: bool

    def __eq__(self, other: object) -> bool:
        if type(other) is not PackageScanItem:
            return False
        if not os.path.samefile(other.full_path, self.full_path):
            return False
        if not other.package == self.package:
            return False
        return True


def scan_packages(root: str) -> list[PackageScanItem]:
    """
    List packages full paths

    :param str root: where to start scanning for packages, would be **src/main/java** or **src/test/java** for a typical maven project
    """
    q = [PackageScanItem(root, "", False)]
    res: list[PackageScanItem] = []
    while len(q) > 0:
        parent = q[0]
        del q[0]
        for sub in os.listdir(parent.full_path):
            sub_full = os.path.join(parent.full_path, sub)
            if os.path.isdir(sub_full):
                package = sub if parent.package == "" else f"{parent.package}.{sub}"
                next = PackageScanItem(
                    sub_full,
                    package,
                    os.path.isfile(os.path.join(sub_full, "package-info.java")),
                )
                res.append(next)
                q.append(next)
    return res


def write_all_missing(scan: list[PackageScanItem], template_lines: list[str]) -> int:
    """
    Write each missing package-info from template and return the number of missing package-info
    """
    return write_all([i for i in scan if not i.has_package_info], template_lines)


def write_all(scan: list[PackageScanItem], template_lines: list[str]) -> int:
    """
    Write a package-info from template and return the number of written package-info
    """
    count = 0
    for item in scan:
        with open(os.path.join(item.full_path, "package-info.java"), "w") as f:
            f.writelines(
                [Template(l).substitute(package=item.package) for l in template_lines]
            )
            count += 1
    return count


def error_all_missing(scan: list[PackageScanItem]) -> int:
    """
    Print an error message for each missing package-info and return the number of missing package-info
    """
    missing_count = 0
    for item in [i for i in scan if not i.has_package_info]:
        print(f"Missing package info for package {item.package} at {item.full_path}")
        missing_count += 1
    return missing_count


def read_lines(file: str) -> list[str]:
    with open(file) as f:
        return f.readlines()


error_code_failed_check = 1
error_code_invalid_call = 2


def main(command: str, sources_root: str, template_file: str | None = None) -> int:
    if command in ["set-missing", "set-all"] and template_file is None:
        print("Missing template file to write package-info files")
        return 2
    scan = scan_packages(sources_root)
    if command == "set-missing" and template_file is not None:
        template = read_lines(template_file)
        count = write_all_missing(scan, template)
        print(f"Added {count} package-info.java")
        return 0
    elif command == "set-all" and template_file is not None:
        template = read_lines(template_file)
        count = write_all(scan, template)
        print(f"Added {count} package-info.java")
        return 0
    elif command == "check":
        missing_count = count_missing(scan)
        if missing_count > 0:
            error_all_missing(scan)
        print(f"Missing {missing_count} package-info.java files", file=sys.stderr)
        return error_code_failed_check
    else:
        print(f"Unsupported command {command}", file=sys.stderr)
        return error_code_invalid_call


if __name__ == "__main__":
    args = sys.argv[1:]
    if len(args) < 2:
        print("Usage: <command> <sources_root> ?<template_file>", file=sys.stderr)
        exit(2)
    if args[0] not in ["set-all", "set-missing", "check"]:
        print(f"Unknown command {args[0]}", file=sys.stderr)
        exit(2)
    exit(main(args[0], args[1], args[2] if len(args) > 2 else None))


def count_missing(scan: list[PackageScanItem]) -> int:
    res = 0
    for i in scan:
        if not i.has_package_info:
            res += 1
    return res


class Tests(unittest.TestCase):
    maxDiff = None

    def test_scan_packages(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            files = [
                os.path.join(temp_dir, f)
                for f in ["a/package-info.java", "a/b/package-info.java", "c/Main.java"]
            ]
            empty_dirs = [os.path.join(temp_dir, d) for d in ["d/e", "f"]]
            for temp_file in files:
                self.write_lines(temp_file, ["// Create a file"])
            for empty_dir in empty_dirs:
                os.makedirs(empty_dir)

            actual = scan_packages(temp_dir)

            expected = [
                PackageScanItem(os.path.join(temp_dir, "a/"), "a", True),
                PackageScanItem(os.path.join(temp_dir, "a/b/"), "a.b", True),
                PackageScanItem(os.path.join(temp_dir, "c"), "c", False),
                PackageScanItem(os.path.join(temp_dir, "d"), "d", False),
                PackageScanItem(os.path.join(temp_dir, "d/e"), "d.e", False),
                PackageScanItem(os.path.join(temp_dir, "f"), "f", False),
            ]
            self.assertCountEqual(actual, expected)

    def test_set_all(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            already = os.path.join(temp_dir, "already/package-info.java")
            self.write_lines(already, ["// Should be erased"])
            os.makedirs(os.path.join(temp_dir, "missing"))
            template_file = self.create_template_file(temp_dir)

            err_code = main("set-all", temp_dir, template_file)

            self.assertEqual(0, err_code)
            self.assertCountEqual(
                ["already;\n", "// Erasing previous content"],
                self.read_lines(os.path.join(temp_dir, "already/package-info.java")),
            )
            self.assertCountEqual(
                ["missing;\n", "// Erasing previous content"],
                self.read_lines(os.path.join(temp_dir, "missing/package-info.java")),
            )

    def test_set_missing(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            already = os.path.join(temp_dir, "already/package-info.java")
            self.write_lines(already, ["// Should NOT be erased"])
            os.makedirs(os.path.join(temp_dir, "missing"))
            template_file = self.create_template_file(temp_dir)

            err_code = main("set-missing", temp_dir, template_file)

            self.assertEqual(0, err_code)
            self.assertCountEqual(
                ["// Should NOT be erased"],
                self.read_lines(os.path.join(temp_dir, "already/package-info.java")),
            )
            self.assertCountEqual(
                ["missing;\n", "// Erasing previous content"],
                self.read_lines(os.path.join(temp_dir, "missing/package-info.java")),
            )

    def test_check(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            already = os.path.join(temp_dir, "ok/package-info.java")
            self.write_lines(already, ["// Ok"])
            os.makedirs(os.path.join(temp_dir, "missing"))

            err_code = main("check", temp_dir, None)

            self.assertEqual(1, err_code)

    test_template = ["${package};", "// Erasing previous content"]

    def create_template_file(self, temp_dir: str) -> str:
        template_file = os.path.join(temp_dir, "template.test")
        self.write_lines(template_file, self.test_template)
        return template_file

    def write_lines(self, file: str, lines: list[str]) -> None:
        os.makedirs(os.path.dirname(file), exist_ok=True)
        with open(file, "w") as f:
            f.write("\n".join(lines))

    def read_lines(self, file: str) -> list[str]:
        with open(file) as f:
            return f.readlines()
