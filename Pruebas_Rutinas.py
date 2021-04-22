# -*- coding: utf-8 -*-
# Estereotaxia_Simplex version 16.1206

import logging
import os
import ast   # para eval seguras


from __main__ import qt, ctk, slicer, vtk
from slicer.ScriptedLoadableModule import *

class Pruebas_Rutinas(ScriptedLoadableModule):
    """ Este modulo lee el scripted modulo y lo transcribe a
        un text edit en el panel de control.
        es similar a un text.-
    """
    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "Pruebas_Rutinas"
        self.parent.categories = ["Estereotaxia"]
        self.parent.dependencies = []
        self.parent.contributors = ["Dr. Jorge Beninca."]
        self.parent.helpText = "Esta es la Version 21.0203"
        self.parent.acknowledgementText = ""


class Pruebas_RutinasWidget(ScriptedLoadableModuleWidget):
    """Uses ScriptedLoadableModuleWidget base class, available
    """
    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)
        self.Registracion_Bton = ctk.ctkCollapsibleButton()
        self.Registracion_Bton.text = "Registracion y calculo del Target"
        self.layout.addWidget(self.Registracion_Bton)
        self.Grilla1 = qt.QGridLayout(self.Registracion_Bton)
        
        self.Bton1 = qt.QPushButton("Inicializa")
        self.Bton4 = qt.QPushButton("Prueba")
        self.Lbl1 = qt.QLabel("Listado 1 :")
        self.textEdit_1 = qt.QTextEdit("")
        self.textEdit_1.setMaximumSize(500, 60)
        self.Lbl2 = qt.QLabel("Listado 2 :")
        self.textEdit_2 = qt.QTextEdit("")
        self.textEdit_2.setMaximumSize(500, 700)
               
        
        self.Grilla1.addWidget(self.Bton1, 1, 0)
        self.Grilla1.addWidget(self.Bton4, 5, 0)
        self.Grilla1.addWidget(self.Lbl1, 6, 0)
        self.Grilla1.addWidget(self.textEdit_1, 7, 0)
        self.Grilla1.addWidget(self.Lbl2, 8, 0)
        self.Grilla1.addWidget(self.textEdit_2, 9, 0)
        self.layout.addStretch(1)   # Add vertical spacer
        #
        # conecciones con las clases logicas
        #
        self.Bton1.clicked.connect(lambda: self.lectora_botones("Inicializa"))
        self.Bton4.clicked.connect(lambda: self.lectora_botones("Prueba"))
        

    def lectora_botones(self, modo):
        
        if modo == "Inicializa":
            print("vino a Inicializa.")
            #nodo = slicer.util.getNode("MarkupsAngle")
            #print(dir(nodo))
            #print(nodo.GetNumberOfFiducials())
            print(nodo.GetAngleDegrees())
            #print(nodo.GetNthControlPointOrientation(0))
            
        elif modo == "Prueba":
            # TODO actualizar cuando cambia el transe node
            print("vino a Lectura")
            nodo = slicer.util.getNode("Alfa")
            print(nodo)
            pass

            

 