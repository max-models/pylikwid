import os
import re
import glob
from setuptools import setup, Extension


def generic_iglob(pattern):
	return glob.iglob(pattern, recursive=True)


def find_file(path_iterator):
	if not path_iterator:
		return None
	for path in path_iterator:
		if os.path.exists(path):
			return path
	return None


def get_hierarchy():
	include_path = None
	library_path = None
	library = None
	prefix_path = os.getenv('LIKWID_PREFIX', None)
	library_pattern = 'lib*/liblikwid.so*'

	if prefix_path is not None:
		library = find_file(generic_iglob(os.path.join(prefix_path, library_pattern)))
		if library is not None:
			library_path = os.path.dirname(library)

	if library is None:
		for path in os.environ.get("PATH", "").split(":"):
			prefix_path = os.path.abspath(os.path.join(path, '..'))
			library = find_file(generic_iglob(os.path.join(prefix_path, library_pattern)))
			if library is not None:
				library_path = os.path.dirname(library)
				break

	if library is None:
		prefix_path = '/usr/local'
		library = find_file(generic_iglob(os.path.join(prefix_path, library_pattern)))
		if library is not None:
			library_path = os.path.dirname(library)

	include_path = os.path.join(prefix_path, 'include') if prefix_path else None
	if include_path and not os.path.exists(os.path.join(include_path, 'likwid.h')):
		include_path = find_file(generic_iglob(os.path.join(prefix_path, '**/likwid.h')))

	if not prefix_path or not os.path.exists(prefix_path):
		raise Exception('Error: the likwid prefix directory was not found')
	if not library or not os.path.exists(library):
		raise Exception('Error: the likwid library was not found')
	if not library_path or not os.path.exists(library_path):
		raise Exception('Error: the likwid library directory was not found')
	if not include_path or not os.path.exists(include_path):
		raise Exception('Error: the likwid include directory was not found')

	m = re.match(r"lib(.*)\.so", os.path.basename(library))
	if m:
		library = m.group(1)
	return prefix_path, library_path, library, include_path


def get_extra_compile_args(include_path):
	extra_args = []
	if os.environ.get("LIKWID_NVMON") not in (None, "0"):
		extra_args.append("-DLIKWID_NVMON")
	header = os.path.join(include_path, 'likwid.h')
	with open(header) as f:
		for line in f:
			if not line.startswith("#define LIKWID_VERSION"):
				continue
			major, release, minor = line.split()[-1].strip('"').split(".")
			extra_args += [
				f"-DLIKWID_MAJOR={major}",
				f"-DLIKWID_RELEASE={release}",
				f"-DLIKWID_MINOR={minor}",
			]
			break
	return extra_args


_, lib_path, lib, inc_path = get_hierarchy()

setup(
	ext_modules=[
		Extension(
			"pylikwid.pylikwid",
			sources=["src/pylikwid/pylikwid.c"],
			include_dirs=[inc_path],
			libraries=[lib],
			library_dirs=[lib_path],
			extra_compile_args=get_extra_compile_args(inc_path),
		)
	]
)
