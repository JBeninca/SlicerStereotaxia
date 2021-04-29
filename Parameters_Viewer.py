# -*- coding: utf-8 -*-
# Estereotaxia_Simplex version 16.1206

import logging
import os
import ast   # para eval seguras

from __main__ import qt, ctk, slicer, vtk
from slicer.ScriptedLoadableModule import *

class Parameters_Viewer(ScriptedLoadableModule):
    """ Este modulo lee el scripted modulo y lo transcribe a
        un text edit en el panel de control.
        es similar a un text.-
    """
    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "Parameters_Viewer"
        self.parent.categories = ["Stereotaxia"]
        self.parent.dependencies = []
        self.parent.contributors = ["Dr. Jorge Beninca."]
        self.parent.helpText = "Esta es la Version 21.0203"
        self.parent.acknowledgementText = ""


class Parameters_ViewerWidget(ScriptedLoadableModuleWidget):
    """Uses ScriptedLoadableModuleWidget base class, available
    """
    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)
        self.Registracion_Bton = ctk.ctkCollapsibleButton()
        self.Registracion_Bton.text = "Muestra Parametros"
        self.layout.addWidget(self.Registracion_Bton)
        self.Grilla1 = qt.QGridLayout(self.Registracion_Bton)
        
        self.Bton1 = qt.QPushButton("Inicializa")
        self.Bton4 = qt.QPushButton("Obtiene Parametros")
        self.Lbl1 = qt.QLabel("Listado Parametros de Estereotaxia :")
        self.textEdit_1 = qt.QTextEdit("")
        self.textEdit_1.setMaximumSize(500, 60)
        self.Lbl2 = qt.QLabel("Contenido de los Parametros : ")
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
        self.Bton4.clicked.connect(lambda: self.lectora_botones("Lectura"))
        
        self.lectora_botones("Inicializa")


    def lectora_botones(self, modo):
        
        if modo == "Inicializa":
            # TODO actualizar cuando cambia el transe node
            print("vino a Inicializa.")
            try:
                transfe = slicer.util.getNode("Param_data")
                print("Ok, se ha cargado el nodo Param_data.-")
            except:
                adv = ("No existe el nodo Param_data, del que se pueda leer.")
                slicer.util.warningDisplay(adv, windowTitle="Error", parent=None, standardButtons=None)
                return
            self.textEdit_1.setPlainText("")
            self.textEdit_2.setPlainText("")
            self.mixObservador_1 = slicer.util.VTKObservationMixin()
            #self.mixObservador_1.removeObservers()
            self.mixObservador_1.addObserver(transfe, vtk.vtkCommand.AnyEvent, self.escribe)
            
        elif modo == "Registracion":
            pass
        elif modo == "Target":
            pass
            
        elif modo == "Lectura":
            # TODO actualizar cuando cambia el transe node
            print("vino a Lectura")
            param = slicer.util.getNode("Param_data")
            param.GetParameterNames()
            self.escribe("directa", 1000)
                    
    def escribe(self, a, event):
        print("vino a rutina de escritura !!!!!!!!!!!!!!!!!!!!!!!!!")
        print("esto lo escribe la App lector de Parametros")
        print( type(a), event)
        param = slicer.util.getNode("Param_data")
        parametros = param.GetParameterNames()
        self.textEdit_1.setPlainText("Parameters = " + str(parametros))
        self.textEdit_2.setPlainText("")
        
        for item in parametros:
            texto = param.GetParameter(item)
            self.textEdit_2.append(item + " = " +texto)




  