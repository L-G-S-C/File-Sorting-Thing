#!/usr/bin/env python3

# Filename: foldersort.py

"""FolderSort is a simple application meant to organize a folder into subfolder according to their extension, made using Python and PyQt5"""

# TODO:
# IMPLEMENT CONTROLLER CLASS AND PASS ALL CONNECT CALLS TO IT

import sys, os, time

# Import QApplication and required widgets from PyQt5.
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QWidget
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtWidgets import QHBoxLayout
from PyQt5.QtWidgets import QAction
from PyQt5.QtWidgets import QStyle
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtWidgets import QCheckBox
from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import qApp
from PyQt5.QtCore import Qt

__version__ = '0.1'
__author__ = 'Luiz Gustavo Santos da Costa'

# Create a subclass of QMainWindow to setup the sorter's UI.
class SorterUI(QMainWindow):
	"""FolderSort's view (GUI)."""
	def __init__(self):
		"""View initializer."""
		super().__init__()
		# Set some main window's properties
		self.setWindowTitle('FolderSort')
		self.setFixedSize(450, 250)
		# Set the central widget and the general layout
		self.generalLayout = QVBoxLayout()
		self._centralWidget = QWidget(self)
		self.setCentralWidget(self._centralWidget)
		self._centralWidget.setLayout(self.generalLayout)
		# To add
		self._createMenuBar()
		self._createPathSplit()
		self._createFileEditSplit()
		self._createStartProgressSplit()
	
	def _createMenuBar(self):
		"""Create the menubar and add an exit action to it."""
		exitAction = QAction(self.style().standardIcon(QStyle.SP_DialogCancelButton),
							'&Exit', self)
		exitAction.setShortcut('Ctrl+Q')
		exitAction.triggered.connect(qApp.quit)
		self.menubar = self.menuBar()
		# Set a dict to keep track of all menus inside the menubar
		self.menulist = {}
		self.menulist['file'] = self.menubar.addMenu('&File')
		self.menulist['file'].addAction(exitAction)
	
	def _createPathSplit(self):
		"""Create the first section where the path fields and buttons will be in."""
		# Create the list where the displays and buttons will be stored
		self.displays = {}
		self.buttons = {}
		# Create the grid layout
		splitLayout = QGridLayout()
		# Button text | position on the QGridLayout
		buttons = {
			'Set 1': (0, 3),
			'Set 2': (1, 3),
		}
		# Display key | position on the QGridLayout
		displays = {
			'fromDir': (0, 0, 1, 2),
			'toDir': (1, 0, 1, 2),
		}
		# Create the buttons and add them to the grid layout
		for btnText, pos in buttons.items():
			self.buttons[btnText] = QPushButton(btnText[:3])
			self.buttons[btnText].setFixedSize(70, 40)
			splitLayout.addWidget(self.buttons[btnText], pos[0], pos[1])
		
		# Create the buttons and add them to the grid layout
		for key, pos in displays.items():
			self.displays[key] = QLineEdit()
			self.displays[key].setFixedHeight(35)
			self.displays[key].setAlignment(Qt.AlignLeft)
			self.displays[key].setReadOnly(True)
			splitLayout.addWidget(self.displays[key], pos[0], pos[1], pos[2], pos[3])
		self.displays['fromDir'].setText('Directory where your files are')
		self.displays['toDir'].setText('Directory where your files will go')

		# Add splitLayout to the general layout
		self.generalLayout.addLayout(splitLayout)

	def _createFileEditSplit(self):
		"""Create the second section where the checkbox and combo box will be located."""
		# Create the VBoxLayout
		splitLayout = QVBoxLayout()
		# Create the checkbox that will control the mode of operation
		self.checkbox = QCheckBox('Game link mode')
		self.checkbox.stateChanged.connect(self._setSortMode)
		# Create a new action to the File tab in the menubar
		toggleAction = QAction('&Game link mode', self, checkable=True)
		toggleAction.setShortcut('Ctrl+E')
		# Set it to call the toggle method of the checkbox object when clicked to un/check the box
		toggleAction.triggered.connect(self.checkbox.toggle)
		# Add it to the File tab in the menubar
		self.menulist['file'].addAction(toggleAction)
		# Add it to the splitLayout
		splitLayout.addWidget(self.checkbox)
		# Create the combo dict that will hold the values it'll contain
		combo = [
			'Steam',
			'EPIC',
			'RPGMaker',
			'Standalone',
			'Demo',
			'Emulator',
		]
		# Create the Combo Box widget
		self.combobox = QComboBox()
		self.combobox.setFixedWidth(80)
		for item in combo:
			self.combobox.addItem(item)
		# Create the instance's that holds the value of the combo box and give it a default value
		self.combochoice = 'Steam'
		# Create the connection that'll change the instance's paramenter of which choice it'll be selected
		self.combobox.activated[str].connect(self._setComboChoice)
		# Add it to the splitLayout
		splitLayout.addWidget(self.combobox)
		# Add this splitLayout to the general layout
		self.generalLayout.addLayout(splitLayout)
	
	def _setComboChoice(self, text):
		"""Change instance's paramenter according to the combo box current choice"""
		self.combochoice = text
	
	def _setSortMode(self, state):
		"""Change the instance's sortmode variable to alter script functionality from organizing general files or link to games"""
		if state == Qt.Checked:
			self.sortmode = 'game'
		else:
			self.sortmode = 'file'
		
	def _createStartProgressSplit(self):
		"""Create the last section where the Start button and progress bar will be in."""
		# Create the QVBoxLayout
		splitLayout = QVBoxLayout()
		# Create the start button widget and save it to the dict of buttons
		self.buttons['Start'] = QPushButton('Start')
		# Create the progress bar widget and give some default values
		self.proBar = QProgressBar()
		self.proBar.setAlignment(Qt.AlignCenter)
		# Add both widgets to the splitLayout
		splitLayout.addWidget(self.proBar)
		splitLayout.addWidget(self.buttons['Start'])
		# Add splitLayout to the general layout
		self.generalLayout.addLayout(splitLayout)

# Uhhhh add documentation, sometime, I guess.
class FolderSortCTRL:
	def __init__(self, view):
		self._view = view
		self._connectSignals()
	
	def _connectSignals(self):
		self._view.buttons['Start'].clicked.connect(self._startDecisionSort)
		self._view.buttons['Set 1'].clicked.connect(lambda: self._changeDir(self._view.displays['fromDir']))
		self._view.buttons['Set 2'].clicked.connect(lambda: self._changeDir(self._view.displays['toDir']))
	
	def _changeDir(self, display):
		directory = str(QFileDialog.getExistingDirectory(self._view, "Select Directory"))
		display.setText(directory)
	
	def _largeconvert(nam, ext):
		if ext == ".jpg_large":
			new_file = nam + ".jpg"

		elif ext == ".png_large":
			new_file = nam + ".png"

		temp_path = "Images Extensions"
		return temp_path, new_file

	# VERY OLD CODE, REMEMBER TO REWRITE
	def _startFileSorting(self):
		twitter_exception = ['.jpg_large', '.png_large']
		rar_exception = ['.rar', '.zip', '.7z']
		wad_exception = ['.wad', '.pk3']
		image_exception = ['.png', '.jpg', ".jpeg"]

		filelist = []
		directory = self._view.displays['fromDir'].text()
		targetdir = self._view.displays['toDir'].text()

		with os.scandir(path=directory) as entries:
			for entry in entries:
				filelist.append(entry.name)
		
		total = len(filelist)
		i = 0
		
		for file in filelist:
			if os.path.isdir(file):
				pass
			elif file == os.path.basename(__file__):
				pass
			else:
				head, tail = os.path.splitext(file)

				if tail == '':
					temp_path = 'No Extension'
					new_file = file

				elif tail in image_exception:
					temp_path = 'Images Extensions'
					new_file = file

				elif tail in twitter_exception:
					temp_path, new_file = self._largeconvert(head, tail)

				elif tail in rar_exception:
					temp_path = 'Extension RAR'
					new_file = file

				elif tail in wad_exception:
					temp_path = 'Extension PK3'
					new_file = file

				else:
					temp_path = 'Extension ' + tail.strip(".").upper()
					new_file = file
			if not os.path.exists(f'{targetdir}/{temp_path}'):
				os.mkdir(f'{targetdir}/{temp_path}')
			print(f'Moving file {new_file.upper()} to folder {temp_path.upper()}')
			try:
				os.rename(f'{directory}/{file}', f'{targetdir}/{temp_path}/{new_file}')
			except FileExistsError:
				os.remove(file)
			i += 1
			self._view.proBar.setValue(int((i/total)*100))
		self._view.proBar.reset()
	
	# Made based on code from _startFileSorting method, so it's also very shitty, REMEMBER TO REWRITE
	def _startLinkSorting(self):
		filelist = []
		directory = self._view.displays['fromDir'].text()
		targetdir = self._view.displays['toDir'].text()

		with os.scandir(path=directory) as entries:
			for entry in entries:
				filelist.append(entry.name)
		
		total = len(filelist)
		i = 0
		for file in filelist:
			head, tail = os.path.splitext(file)
			temp_path = f'[{self._view.combobox.currentText()}] {head}'
			new_file = file

			if not os.path.exists(f'{targetdir}/{temp_path}'):
				os.mkdir(f'{targetdir}/{temp_path}')
			print(f'Moving file {new_file.upper()} to folder {temp_path.upper()}')
			try:
				os.rename(f'{directory}/{file}', f'{targetdir}/{temp_path}/{new_file}')
			except FileExistsError:
				os.remove(file)
			i += 1
			self._view.proBar.setValue(int((i/total)*100))
		self._view.proBar.reset()

	def _startDecisionSort(self):
		if self._view.sortmode == 'file':
			self._startFileSorting()
		elif self._view.sortmode == 'game':
			self._startLinkSorting()



# Client code
def main():
	"""Main function."""
	# Create an instance of QApplication
	foldersort = QApplication(sys.argv)
	# Show the sorter's GUI
	view = SorterUI()
	view.show()
	FolderSortCTRL(view=view)
	# Execute the sorter's main loop
	sys.exit(foldersort.exec())

if __name__ == '__main__':
	main()

	

