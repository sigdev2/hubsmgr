#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

if os.name == r'posix':
    class Colors:
        LightRed = '\033[91m'
        LightGreen = '\033[92m'
        LightYellow = '\033[93m'
        LightBlue = '\033[94m'
        Red = '\033[31m'
        Green = '\033[32m'
        Yellow = '\033[33m'
        Blue = '\033[34m'
        BlackOnWhite = '\033[7m'
        End = '\033[0m'
else:
    class Colors:
        LightRed = r''
        LightGreen = r''
        LightYellow = r''
        LightBlue = r''
        Red = r''
        Green = r''
        Yellow = r''
        Blue = r''
        BlackOnWhite = r''
        End = r''

class Logger:
    @staticmethod
    def formatPos(index, count):
        return r'[' + format(index, r'02d') + r'/' + format(count, r'02d') + r']'

    @staticmethod
    def partstart(index, count, text):
        print(Colors.BlackOnWhite + Logger.formatPos(index, count) + r' [START]' +
              Colors.End + r' ' + Colors.LightBlue + text + Colors.End)

    @staticmethod
    def partend(index, count, text):
        print(Colors.BlackOnWhite + Logger.formatPos(index, count) + r' [END]' +
              Colors.End + r' ' + Colors.LightBlue + text + Colors.End)

    @staticmethod
    def start(text):
        print(Colors.BlackOnWhite + r'[START]' +
              Colors.End + r' ' + Colors.LightBlue + text + Colors.End)

    @staticmethod
    def end(text):
        print(Colors.BlackOnWhite + r'[END]' +
              Colors.End + r' ' + Colors.LightBlue + text + Colors.End)

    @staticmethod
    def headerStart(headertype, text):
        print(Colors.Yellow + r'[' + headertype + r']' +
              Colors.End + r' ' + Colors.LightBlue + text + Colors.End)

    @staticmethod
    def headerEnd(text):
        print(Colors.Yellow + r'[END]' + Colors.End + r' ' + Colors.LightBlue + text + Colors.End)

    @staticmethod
    def error(text):
        print(Colors.LightRed + r'[ERROR]' + Colors.End + r' ' + Colors.Red + text + Colors.End)

    @staticmethod
    def warning(text):
        print(Colors.Yellow + r'[WARN]' + Colors.End + r' ' + Colors.Red + text + Colors.End)

    @staticmethod
    def message(msgtype, message):
        print(Colors.Yellow + r'[' + msgtype + r']' + Colors.End + r' ' + message)

    @staticmethod
    def partmessage(index, count, msgtype, message):
        print(Colors.Yellow + Logger.formatPos(index, count) + r' [' + msgtype + r']' +
              Colors.End + r' ' + message)

    @staticmethod
    def operation(optype, message, done):
        Logger.message(optype, message + r' ' + Colors.LightGreen + r'[DONE]' +
                       Colors.End if done else Colors.LightRed + r'[FAILED]' + Colors.End)

    @staticmethod
    def partoperation(index, count, optype, message, done):
        Logger.partmessage(index, count, optype, message + r' ' + Colors.LightGreen + r'[DONE]' +
                           Colors.End if done else Colors.LightRed + r'[FAILED]' + Colors.End)

    @staticmethod
    def item(itemtype, source, name, value):
        Logger.message(itemtype, source + r': ' +
                       Colors.LightBlue + name + Colors.End +
                       r' = ' + Colors.LightGreen + value + Colors.End)
