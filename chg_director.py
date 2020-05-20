#!/usr/bin/python
# -*- coding: UTF-8 -*-

import numpy as np
import cv2
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QMainWindow, QApplication, QPushButton, QWidget, QLabel, QComboBox
from PyQt5.QtGui import QPixmap, QImage
import sys
import time
import os

# get the size of the screen
is_color = False

class Q_Window(QWidget):

    def __init__(self):
        super(Q_Window, self).__init__()
        self.initParas()
        self.initUI()


    def initParas(self):
        self.timer_camera = QtCore.QTimer()
        self.timer_camera_2 = QtCore.QTimer()
        self.timer_recording = QtCore.QTimer()

        # Video resolution
        self.cap = cv2.VideoCapture()
        self.cap_size = [1280, 720]
        self.cap_2 = cv2.VideoCapture()
        self.cap_2_size = [1280, 720]
        self.fps = 25

        self.CAM_1 = 0
        self.CAM_2 = 1

        self.recording = False
        self.recorded_time = 0

        self.save_path = "/home"


    def initUI(self):
        self.image_View = QLabel("image", self)
        self.image_View.resize(640, 480)
        self.image_View.setScaledContents(True)
        self.image_View.move(60, 30)
        jpg = QPixmap('timg.jpeg')
        self.image_View.setPixmap(jpg)

        self.image_View_2 = QLabel("image2", self)
        self.image_View_2.resize(640, 480)
        self.image_View_2.setScaledContents(True)
        self.image_View_2.move(760, 30)
        self.image_View_2.setPixmap(jpg)

        self.det_Button = QPushButton(u'打开输入源一', self)
        self.det_Button.clicked.connect(self.open_camera)
        self.det_Button.resize(200, 40)
        self.det_Button.move(360, 520)

        self.det_Button_2 = QPushButton(u'打开输入源二', self)
        self.det_Button_2.clicked.connect(self.open_camera_2)
        self.det_Button_2.resize(200, 40)
        self.det_Button_2.move(900, 520)

        self.recording_Button = QPushButton(u'开始录制', self)
        self.recording_Button.clicked.connect(self.record)
        self.recording_Button.resize(200, 60)
        self.recording_Button.move(600, 600)

        self.recorded_time_label = QLabel(" ", self)
        self.recorded_time_label.resize(80, 20)
        self.recorded_time_label.move(680, 560)

        self.timer_camera.timeout.connect(self.show_camera)
        self.timer_camera_2.timeout.connect(self.show_camera_2)
        self.timer_recording.timeout.connect(self.show_timer)


        self.radioButton = QtWidgets.QRadioButton(u'录制ROS Bag', self)
        self.radioButton.setObjectName("radioButton")
        self.radioButton.setGeometry(QtCore.QRect(860, 630, 89, 16))
        self.radioButton.setChecked(True)

        self.setGeometry(300, 300, 1460, 700)
        self.setWindowTitle('ChgRecorder')
        self.show()


    def record(self):
        # Start recording
        if self.recording == False:
            # Check if any camera is open
            if self.timer_camera.isActive() == False and self.timer_camera_2.isActive() == False:
                msg = QtWidgets.QMessageBox.warning(self, u"提示", u"需要打开至少一个摄像头",
                                                    buttons=QtWidgets.QMessageBox.Ok,
                                                    defaultButton=QtWidgets.QMessageBox.Ok)
                return
            #Get path
            directory = QtWidgets.QFileDialog.getSaveFileName(self, 
              "getSaveFileName","./",
              "Video Files (*.avi)") 
            if directory[0] =='':
                return

            self.save_path = directory[0]

            self.timer_recording.start(1000)
            self.recording = True

            fourcc = cv2.VideoWriter_fourcc('X','V','I','D')

            # Record camera image if camera is open
            if self.timer_camera.isActive():
                self.video_writer = cv2.VideoWriter(self.save_path+'_cam1.avi',fourcc, self.fps, (self.cap_size[0], self.cap_size[1]),True)

            if self.timer_camera_2.isActive():
                self.video_writer_2 = cv2.VideoWriter(self.save_path+'_cam2.avi',fourcc, self.fps, (self.cap_2_size[0], self.cap_2_size[1]),True)

            self.recording_Button.setText(u'停止录制')

            # Record ROS bag if selected
            if self.radioButton.isChecked()==True:
                command = 'rosbag record -o '+ self.save_path + '_' +' -a'  #replace -a with specific topics
                os.system("gnome-terminal -e '%s'" %command)

        # Stop recording
        else:
            self.timer_recording.stop()
            self.recorded_time = 0
            self.recording = False

            if self.timer_camera.isActive():
                self.video_writer.release()

            if self.timer_camera_2.isActive():
                self.video_writer_2.release()

            msg = QtWidgets.QMessageBox.warning(self, u"提示", u"录制结束",
                                                    buttons=QtWidgets.QMessageBox.Ok,
                                                    defaultButton=QtWidgets.QMessageBox.Ok)
            self.recording_Button.setText(u'开始录制')



    def show_timer(self):
        self.recorded_time += 1
        minute = self.recorded_time / 60
        second = self.recorded_time % 60
        self.recorded_time_label.setText(str(minute)+u'分' + str(second)+u'秒')


    def open_camera(self):
        if self.timer_camera.isActive() == False:
            flag = self.cap.open(self.CAM_1)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.cap_size[0])
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cap_size[1])
            self.cap.set(cv2.CAP_PROP_FPS, self.fps)

            if flag == False:
                msg = QtWidgets.QMessageBox.warning(self, u"Warning", u"请检测相机与电脑是否连接正确",
                                                    buttons=QtWidgets.QMessageBox.Ok,
                                                    defaultButton=QtWidgets.QMessageBox.Ok)

                return
            else:
                flag, image = self.cap.read()
                if flag==True:
                    if image.shape[0] < self.cap_size[1]:
                        self.cap_size[1] = image.shape[0]
                        self.cap_size[0] = image.shape[1]
                        msg = QtWidgets.QMessageBox.warning(self, u"Warning", u"相机不支持设定的分辨率，已经设置为相机默认值",
                                                    buttons=QtWidgets.QMessageBox.Ok,
                                                    defaultButton=QtWidgets.QMessageBox.Ok)
                else:
                    msg = QtWidgets.QMessageBox.warning(self, u"Warning", u"请检测相机与电脑是否连接正确",
                                                    buttons=QtWidgets.QMessageBox.Ok,
                                                    defaultButton=QtWidgets.QMessageBox.Ok)
                    return

                self.timer_camera.start(40)
                self.det_Button.setText(u'关闭输入源')
        # Close if already opened
        else:
            self.close_camera()


    def show_camera(self):
        flag, image = self.cap.read()
        if flag==True:
            show = cv2.resize(image, (640, 480))
            show = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)
            showImage = QtGui.QImage(show.data, show.shape[1], show.shape[0], QtGui.QImage.Format_RGB888)
            self.image_View.setPixmap(QtGui.QPixmap.fromImage(showImage))
            # Record if wanted
            if self.recording == True:
                self.video_writer.write(image)

        else:
            msg = QtWidgets.QMessageBox.warning(self, u"Warning", u"摄像头1出现问题！",
                                                    buttons=QtWidgets.QMessageBox.Ok,
                                                    defaultButton=QtWidgets.QMessageBox.Ok)
            if self.recording == True:
                self.record()
            self.open_camera()


    def close_camera(self):
        if self.recording == False:
            self.timer_camera.stop()
            self.cap.release()
            self.image_View.clear()
            self.det_Button.setText(u'打开输入源')
            jpg = QPixmap('timg.jpeg')
            self.image_View.setPixmap(jpg)
        else:
            msg = QtWidgets.QMessageBox.warning(self, u"Warning", u"请先停止录制！",
                                                buttons=QtWidgets.QMessageBox.Ok,
                                                defaultButton=QtWidgets.QMessageBox.Ok)


    def open_camera_2(self):
        if self.timer_camera_2.isActive() == False:
            flag = self.cap_2.open(self.CAM_2)
            self.cap_2.set(cv2.CAP_PROP_FRAME_WIDTH, self.cap_2_size[0])
            self.cap_2.set(cv2.CAP_PROP_FRAME_HEIGHT, self.cap_2_size[1])
            self.cap_2.set(cv2.CAP_PROP_FPS, self.fps)

            if flag == False:
                msg = QtWidgets.QMessageBox.warning(self, u"Warning", u"请检测输入源与电脑是否连接正确",
                                                    buttons=QtWidgets.QMessageBox.Ok,
                                                    defaultButton=QtWidgets.QMessageBox.Ok)
                return
            else:

                flag, image = self.cap_2.read()
                if flag==True:
                    if image.shape[0] < self.cap_2_size[1]:
                        self.cap_2_size[1] = image.shape[0]
                        self.cap_2_size[0] = image.shape[1]
                        msg = QtWidgets.QMessageBox.warning(self, u"Warning", u"相机不支持设定的分辨率，已经设置为相机默认值",
                                                    buttons=QtWidgets.QMessageBox.Ok,
                                                    defaultButton=QtWidgets.QMessageBox.Ok)
                else:
                    msg = QtWidgets.QMessageBox.warning(self, u"Warning", u"请检测相机与电脑是否连接正确",
                                                    buttons=QtWidgets.QMessageBox.Ok,
                                                    defaultButton=QtWidgets.QMessageBox.Ok)
                    return

                self.timer_camera_2.start(40)
                self.det_Button_2.setText(u'关闭输入源')
        # Close if already opened
        else:
            self.close_camera_2()


    def show_camera_2(self):
        flag, image = self.cap_2.read()

        if flag==True:
            show = cv2.resize(image, (640, 480))
            show = cv2.cvtColor(show, cv2.COLOR_BGR2RGB)
            showImage = QtGui.QImage(show.data, show.shape[1], show.shape[0], QtGui.QImage.Format_RGB888)
            self.image_View_2.setPixmap(QtGui.QPixmap.fromImage(showImage))
            # Record
            if self.recording == True:
                self.video_writer_2.write(image)

        else:
            msg = QtWidgets.QMessageBox.warning(self, u"Warning", u"摄像头2出现问题！",
                                                    buttons=QtWidgets.QMessageBox.Ok,
                                                    defaultButton=QtWidgets.QMessageBox.Ok)
            if self.recording == True:
                self.record()
            self.open_camera_2()


    def close_camera_2(self):
        if self.recording == False:
            self.timer_camera_2.stop()
            self.cap_2.release()
            self.image_View_2.clear()
            self.det_Button_2.setText(u'打开输入源')
            jpg = QPixmap('timg.jpeg')
            self.image_View_2.setPixmap(jpg)
        else:
            msg = QtWidgets.QMessageBox.warning(self, u"Warning", u"请先停止录制！",
                                                buttons=QtWidgets.QMessageBox.Ok,
                                                defaultButton=QtWidgets.QMessageBox.Ok)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Q_Window()
    sys.exit(app.exec_())
