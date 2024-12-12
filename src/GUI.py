import os
import shutil
import datetime
from controller import reorder_activities, IoT_Controller, UsersStatus, IOT_NotConnectedError, IOT_WritingStateError
import config as C
import time
from PIL.ImageQt import ImageQt
from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QLineEdit, QWidget, QComboBox, QLabel
from PyQt6.QtGui import QIcon, QPixmap, QKeyEvent

from inkml_manager import Inkml_Manager

# GUI
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # IoT devices connector
        #self.controller = IoT_Connector()
        self.controller = IoT_Controller()

        # Users status manager
        #self.users_status = UsersStatus(C.RESULTS_PROTOCOL_FOLDER)

        # Init Frame
        self.setWindowIcon(QIcon(C.ICON_IMG))
        self.setWindowTitle("IoT Acquisition Controller")
        self.setMinimumSize(QSize(250, 330))

        # GUI elements

        # LEFT PANE --------------------------------------------------------------------
        self.label_id_IOT_input = QLabel("Select an IoT Device:")
        self.label_id_IOT_input.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        self.label_id_IOT_input.setFixedHeight(20)
        self.label_id_IOT_input.setFixedWidth(200)

        self.IOT_combobox = QComboBox()
        iots_list = self.controller.get_iot_devices()
        self.IOT_combobox.addItems(iots_list)
        if len(iots_list) > 0:
            self.controller.set_iot_address(int(iots_list[0]))
        self.IOT_combobox.setFixedHeight(20)
        self.IOT_combobox.currentIndexChanged.connect(self.select_iot_devices)

        self.reload_iot_button = QPushButton('Reload Devices')
        self.reload_iot_button.clicked.connect(self.click_reload_iot_button)
        self.reload_iot_button.setStyleSheet(f"background-color: {C.COLOR_BKGR_RIOTBUTTON};"+
                                     f"color: {C.COLOR_FRGR_RIOTBUTTON};")
        self.reload_iot_button.setFixedWidth(100)


        self.label_id_subject_input = QLabel("Insert the ID of the Subject:")
        self.label_id_subject_input.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        self.label_id_subject_input.setFixedHeight(20)
        #self.label_id_subject_input.setFixedWidth(60)

        self.id_subject_input = QLineEdit()
        self.id_subject_input.setPlaceholderText("Subject ID...")
        #self.id_subject_input.setInputMask('0000.(A);_')
        self.id_subject_input.editingFinished.connect(self.write_in_input)

        self.label_id_activity_box = QLabel("Select the ID of the Activity:")
        self.label_id_activity_box.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignBottom)
        self.label_id_activity_box.setFixedHeight(20)

        self.id_activity_box = QComboBox()
        self.display_listactivities()
        self.id_activity_box.currentIndexChanged.connect(self.select_activity)
        # list_activities = []
        # for inkml_filename in os.listdir("data\inkml_file"):
        #     list_activities.append(inkml_filename)
        # # with open("data\py_script\list_activities.txt", "r") as list_activities_file:
        # #     for line in list_activities_file.readlines():
        # #         list_activities.append(line.rstrip())
        # self.id_activity_box.addItems(list_activities)

        self.record_next_button = QPushButton("Send NEXT inkml")
        self.record_next_button.clicked.connect(self.click_record_next_button)
        self.record_next_button.setStyleSheet(f"background-color: {C.COLOR_BKGR_SENDNEXTBUTTON};"+
                                     f"color: {C.COLOR_FRGR_SENDNEXTBUTTON};")

        self.send_button = QPushButton("Send inkml to IoT")
        self.send_button.clicked.connect(self.click_send_button)
        self.send_button.setStyleSheet(f"background-color: {C.COLOR_BKGR_SENDBUTTON};"+
                                     f"color: {C.COLOR_FRGR_SENDBUTTON};")


        self.stop_button = QPushButton("Stop Writing")
        self.stop_button.clicked.connect(self.click_stop_button)
        self.stop_button.setStyleSheet(f"background-color: {C.COLOR_BKGR_STOPBUTTON};"+
                                     f"color: {C.COLOR_FRGR_STOPBUTTON};")
        #self.stop_button.setCheckable(True)

        self.undo_button = QPushButton("Delete Last Activity")
        self.undo_button.clicked.connect(self.delete_last_button)
        self.undo_button.setStyleSheet(f"background-color: {C.COLOR_BKGR_UNDOBUTTON};"+
                                     f"color: {C.COLOR_FRGR_UNDOBUTTON};")
        #self.undo_button.setCheckable(True)

        self.label_out = QLabel("Welcome!")
        self.label_out.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.label_out.setWordWrap(True)
        self.set_out_label_NORMAL()
        #self.label_id_activity_box.setFixedHeight(20)
        #self.label_id_activity_box.setFixedWidth(300)

        # RIGHT PANE --------------------------------------------------------------------
        self.doc_preview = QLabel(self)
        if self.id_activity_box.currentText()  == '':
            self.pixmap = QPixmap(C.DEFAULT_IMAGE)
            self.doc_preview.setPixmap(self.pixmap)
            # for fixed size img:
            #self.doc_preview.setPixmap(self.pixmap.scaled(500, 1000, Qt.AspectRatioMode.KeepAspectRatio,  Qt.TransformationMode.FastTransformation ))

        else:
            self.select_activity(self.id_activity_box.currentIndex())
        
        self.doc_preview.setScaledContents(True)


        layout = QHBoxLayout()
        layout_L = QVBoxLayout()
        layout_R = QVBoxLayout()

        # Left Pane
        layout_L.addWidget(self.label_id_IOT_input)
        layout_L.addWidget(self.IOT_combobox)
        layout_L.addWidget(self.reload_iot_button)

        layout_L.addWidget(self.label_id_subject_input)
        layout_L.addWidget(self.id_subject_input)
        layout_L.addWidget(self.label_id_activity_box)
        layout_L.addWidget(self.id_activity_box)
        layout_L.addWidget(self.record_next_button)
        layout_L.addWidget(self.send_button)
        layout_L.addWidget(self.stop_button)
        layout_L.addWidget(self.undo_button)
        layout_L.addWidget(self.label_out)
        
        # right Pane
        layout_R.addWidget(self.doc_preview)

        container_L = QWidget()
        container_L.setLayout(layout_L)
        #container_L.setFixedWidth(300)

        container_R = QWidget()
        container_R.setLayout(layout_R)

        layout.addWidget(container_L)
        layout.addWidget(container_R)

        container = QWidget()
        container.setLayout(layout)

        # Set the central widget of the Window.
        self.setCentralWidget(container)


    # METHODS -------------------------------------------------------------------
    def set_out_label_ALLERT(self):
        self.label_out.setStyleSheet(f"background-color: {C.COLOR_BKGR_OUTLABEL};"+
                                     f"color: {C.COLOR_FRGR_ERROR_OUTLABEL};"+
                                      "padding: 5px;")
    
    def set_out_label_GREEN(self):
        self.label_out.setStyleSheet(f"background-color: {C.COLOR_BKGR_OUTLABEL};"+
                                     f"color: {C.COLOR_FRGR_GREEN_OUTLABEL};"+
                                      "padding: 5px;")
    
    def set_out_label_NORMAL(self):
        self.label_out.setStyleSheet(f"background-color: {C.COLOR_BKGR_OUTLABEL};"+
                                     f"color: {C.COLOR_FRGR_OUTLABEL};"+
                                      "padding: 5px;") 

    
    def select_iot_devices(self, index):
        iot_id = self.IOT_combobox.currentText()
        self.controller.set_iot_address(int(iot_id))

    def click_reload_iot_button(self):
        iots_list = self.controller.get_iot_devices()
        self.IOT_combobox.clear()
        self.IOT_combobox.addItems(iots_list)

    def select_activity(self, index):
        inkml_file_selected = self.id_activity_box.currentText()
        if inkml_file_selected != "":
            inkml_path = os.path.join(C.ACTIVITES_PATH,inkml_file_selected)
            imkml_m = Inkml_Manager(inkml_path)
            img = imkml_m.get_templateImage()
            self.update_image(img)
    
    def update_image(self, img):
        qim = ImageQt(img)
        self.pixmap = QPixmap.fromImage(qim)
        self.doc_preview.setPixmap(self.pixmap)     

    def click_record_next_button(self):

        try:
            #self.print_msg(self._get_status_msg(), format="NORMAL")
            
            id_subject = self._get_id_subject()

            ordered_activities = ["_".join(os.path.splitext(self.id_activity_box.itemText(i))[0].split('_')[1:])                              
                                for i in range(self.id_activity_box.count())]

            usr_folder = os.path.join(C.RESULTS_PROTOCOL_FOLDER, id_subject) 

            # stop current acquisition sending STOP WRITING to IoT tablet
            iot_state = self.controller.get_iot_status()

            if iot_state == self.controller.connector.iot.STATE_WRITING:
                self.click_stop_button()  

            # compute the next activity for curren user
            if not os.path.exists(usr_folder):
                next_activity = ordered_activities[0]
            else:
                activities_state = self.controller.users_status.get_user_status(id_subject)

                next_activity = None
                for is_next_activity in ordered_activities:
                    if is_next_activity in activities_state:
                        if is_next_activity in C.ELEMENTS_TO_RECORD_SPECIFIC:
                            max_activity_rep = C.ELEMENTS_TO_RECORD_SPECIFIC[is_next_activity]
                        else:
                            max_activity_rep = C.ELEMENTS_TO_RECORD

                        if activities_state[is_next_activity] < max_activity_rep:
                            next_activity = is_next_activity
                            break
                    else:
                        next_activity = is_next_activity
                        break
            
            # send nwext activity to IoT tablet
            if next_activity is None:
                self.pixmap = QPixmap(C.END_ACQUISITION_IMAGE)
                self.doc_preview.setPixmap(self.pixmap)
                self.controller.send_inkml(C.END_ACQUISITION_INKML)
                self.controller.send_stop()
                self.print_msg("No other activity planned.", format="GREEN")
            else:
                # set next avtivity in combobox and sent it to IoT
                next_activity_index = ordered_activities.index(next_activity)
                self.id_activity_box.setCurrentIndex(next_activity_index)
                self.select_activity(next_activity_index)
                time.sleep(0.1)
                self.click_send_button()

        except IOT_NotConnectedError as error:
           self.print_msg(f"{error}", format="RED")
            
    def click_send_button(self):
        """
        send inkml file to the IoT selected device
        """
        self.print_msg(self._get_status_msg(), format="NORMAL")
        id_activity = f"{self.id_activity_box.currentText()}"
        inkml_file = os.path.join(C.ACTIVITES_PATH,id_activity)

        try:
            self.controller.send_inkml(inkml_file)
        except IOT_WritingStateError as error:
            out_msg = f"{error}\n\nATTENTION!\nIoT in Writing State (Green led)!!!"
            self.print_msg(out_msg, format="RED")
        except IOT_NotConnectedError as error:
            out_msg = f"{error}"
            self.print_msg(out_msg, format="RED")

        # for f in os.listdir(C.IOT_ACTIVITES_PATH):
        #     os.remove(os.path.join(C.IOT_ACTIVITES_PATH,f))
        # shutil.copyfile(os.path.join(C.ACTIVITES_PATH,id_activity), os.path.join(C.IOT_ACTIVITES_PATH,id_activity))

    def click_stop_button(self):
        id_subject = self._get_id_subject()
        id_activity = self._get_id_activity()

        try:
            # stop message
            self.controller.send_stop()

            if os.path.exists(C.DEFAULT_RES_TMP):
                shutil.rmtree(C.DEFAULT_RES_TMP)
            os.mkdir(C.DEFAULT_RES_TMP)

            # get inkml
            self.controller.download_inkml(C.DEFAULT_RES_TMP)

            # create csv and bmp
            inkmlname = self.controller.get_current_inkml_name()
            manager = Inkml_Manager(os.path.join(C.DEFAULT_RES_TMP, inkmlname))
            manager.save_workImage(dst=C.DEFAULT_RES_TMP)            
            manager.save_csv(dst=C.DEFAULT_RES_TMP)

            # set bmp to gui
            img = manager.get_workImage()
            self.update_image(img)

            # store results
            curr_repetition = self.controller.result_mover(id_subject, id_activity)

            #self.users_status.update_user_status(id_subject, '_'.join(os.path.splitext(id_activity)[0].split('_')[2:]))

            self.print_msg(self._get_status_msg(), format="NORMAL")

        except Exception as error:
            out_msg = f"{error}\n\nATTENTION!\nResults not registered!!!"
            self.print_msg(out_msg, format="RED")

    def delete_last_button(self):
        try:
            self.controller.undo_last()
            msg = "Last activity Deleted!\n\n"
            msg += self._get_status_msg()
            self.print_msg(msg, format="NORMAL")
        except Exception as error:
            self.print_msg(f"{error}", format="RED")


    def write_in_input(self, len_if=10):
        id_subject = self._get_id_subject()
        reorder_activities(id_subject)
        self.display_listactivities()
        if not os.path.exists(os.path.join(C.RESULTS_PROTOCOL_FOLDER, id_subject)):
            os.mkdir(os.path.join(C.RESULTS_PROTOCOL_FOLDER, id_subject))


    def display_listactivities(self):
        list_activities = []
        self.id_activity_box.clear()
        for inkml_filename in os.listdir(C.ACTIVITES_PATH):
            list_activities.append(inkml_filename)

        self.id_activity_box.addItems(list_activities)

    def print_msg(self, msg, format="NORMAL"):
        """
        print a message in the "label_out" field
        
            msg: is the message to print
            format: (NORMAL, GREEN, RED) is the format option
        """

        if format == "RED":
            self.set_out_label_ALLERT()
        elif format == "GREEN":
            self.set_out_label_GREEN()
        else:
            self.set_out_label_NORMAL()

        self.label_out.setText(msg)

    def _get_id_subject(self):
        id_subject = self.id_subject_input.text()
        if id_subject == "":
            id_subject = C.DEFAULT_SUBJ

        if not os.path.exists(os.path.join(C.RESULTS_PROTOCOL_FOLDER, id_subject)):
            os.mkdir(os.path.join(C.RESULTS_PROTOCOL_FOLDER, id_subject))
            
        return id_subject
    
    def _get_id_activity(self):
        return f"{str(self.id_activity_box.currentIndex()).zfill(C.MAX_ID_LEN)}_{self.id_activity_box.currentText()}"
    
    
    def _get_status_msg(self):
        id_subject = self._get_id_subject()
        now = datetime.datetime.now()
        out_msg = str(now)
        #out_msg += f"\nLast Activity:\t{id_activity}\n\n"
        out_msg += f"\n\nStatus (anctivity:repetitions)\n\n"
        out_msg += self.controller.users_status.user_status_2_str(id_subject)

        return out_msg


    # Keyboard Listener
    # def keyPressEvent(self, event):
    #     if isinstance(event, QKeyEvent):
    #         key_text = event.text()
    #         print(f"Last Key Pressed: {key_text}")




if __name__ == "__main__":
    # Init 
    os.makedirs(C.RESULTS_PROTOCOL_FOLDER, exist_ok=True)
    reorder_activities()

    # Run the GUI
    app = QApplication([])

    window = MainWindow()
    window.show()

    app.exec()