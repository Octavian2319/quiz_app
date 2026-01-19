"""
Main entry point for Android build
This file is used by Buildozer - it imports and runs the mobile app
"""
from main_mobile import QuizApp

if __name__ == '__main__':
    QuizApp().run()
