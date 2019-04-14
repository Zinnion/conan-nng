#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conans import ConanFile, CMake, tools
import os

class NanomsgConan(ConanFile):
    name = "nng"
    version = "1.1.1"
    description = "Simple high-performance implementation of several scalability protocols"
    topics = ("conan", "nng", "communication", "messaging", "protocols")
    url = "https://github.com/zinnion/conan-nng"
    homepage = "https://github.com/nanomsg/nng"
    author = "Zinnion <mauro@zinnion.com>"
    license = "MIT"
    exports = ["LICENSE.md"]
    exports_sources = ["CMakeLists.txt"]
    settings = "os", "compiler", "build_type", "arch"
    short_paths = True
    generators = "cmake"
    source_subfolder = "source_subfolder"
    build_subfolder = "build_subfolder"
    options = {
       "shared": [True, False],
       "enable_tests": [True, False],
       "enable_tools": [True, False],
       "enable_nngcat": [True, False],
    }

    default_options = (
        "shared=False",
        "enable_tests=False",
        "enable_tools=False",
        "enable_nngcat=False"
    )

    def source(self):
        tools.get("{0}/archive/v{1}.tar.gz".format(self.homepage, self.version))
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self.source_subfolder)

    def configure(self):
        del self.settings.compiler.libcxx
        if self.settings.compiler == "Visual Studio" and float(self.settings.compiler.version.value) < 14:
            raise Exception("ngg could not be built by MSVC <14")

    def configure_cmake(self):
        cmake = CMake(self)
        cmake.definitions["NNG_TESTS"] = self.options.enable_tests
        cmake.definitions["NNG_ENABLE_NNGCAT"] = self.options.enable_nngcat
        cmake.configure(source_folder=self.source_subfolder, build_folder=self.build_subfolder)
        return cmake

    def build(self):
        cmake = self.configure_cmake()
        cmake.build()

    def package(self):
        self.copy(pattern="LICENSE.txt", dst="license", src=self.source_subfolder)
        cmake = self.configure_cmake()
        cmake.install()

    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)

        if self.settings.os == "Windows":
            if not self.options.shared:
                self.cpp_info.libs.append('mswsock')
                self.cpp_info.libs.append('ws2_32')
        elif self.settings.os == "Linux":
            self.cpp_info.libs.append('pthread')
        if not self.options.shared:
            self.cpp_info.defines.append("NNG_STATIC_LIB")
