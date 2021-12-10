# -*- coding: utf-8 -*-
# SlicerStereotaxia version 21.0520
import os
import logging
import math
import time
import ast   # para eval seguras
from importlib import reload  

from __main__ import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *

from Recursos import Maquina_Russell_Brown
from Recursos import utilitarios
from Recursos import gestion_Fiduciarios 

reload(Maquina_Russell_Brown)
reload(utilitarios)
reload(gestion_Fiduciarios)


class SlicerStereotaxia(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class"""

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "SlicerStereotaxia"
        self.parent.categories = ["Stereotaxia"]
        self.parent.dependencies = []
        self.parent.contributors = ["Dr. Miguel Ibanez; Dr. Dante Lovey; Dr. Lucas Vera; Dra. Elena Zema; Dr. Jorge Beninca."]
        self.parent.helpText = "Esta es la Version 21.0203"
        self.parent.acknowledgementText = " Este modulo fue desarrollado originalmente por Jorge A.Beninca, durante los meses de Enero a Julio 2015, en el dpto de Neurocirugia del Hospital de Ninos Dr. Orlando Alassia."

class SlicerStereotaxiaWidget(ScriptedLoadableModuleWidget):
    """Uses ScriptedLoadableModuleWidget base class"""
    def __init__(self, parent=None):
        ScriptedLoadableModuleWidget.__init__(self, parent)
        self.logica = registracionLogic()
        self.utiles = utilitarios.util()
        self.gest = gestion_Fiduciarios.gestion()
        self.maqui = Maquina_Russell_Brown.calculus()
        self.marco = Maquina_Russell_Brown.Marco_Micromar()
    
    def setup(self):
        ScriptedLoadableModuleWidget.setup(self)
        self.Registracion_Bton = ctk.ctkCollapsibleButton()
        self.Registracion_Bton.text = "Registracion del Paciente"
        self.Registracion_Bton.collapsed = False
        self.Planificacion_Bton = ctk.ctkCollapsibleButton()
        self.Planificacion_Bton.text = "Plan de la Cirugia"
        self.Planificacion_Bton.collapsed = True
        #
        # Define Butones Layout Registracion
        #
        self.Lbl1 = qt.QLabel("")
        self.Lbl1.setAlignment(qt.Qt.AlignCenter)
        self.Bton1 = qt.QPushButton("Inicializa")
        self.Bton1.toolTip = "Inicia todas las variables.-"
        self.Bton2 = qt.QPushButton("Registración")
        self.Bton2.toolTip = "Marca los 9 fiduciarios f.-"
        self.Bton3 = qt.QPushButton("Entry ")
        self.Bton3.toolTip = "Marca el punto de Entrada.-"
        self.Bton4 = qt.QPushButton("Target")
        self.Bton4.toolTip = "Marca el fiduciario Target y realiza los calculos.-"
        self.Bton5 = qt.QPushButton("Guarda la sesion")
        self.Bton5.toolTip = "Guarda los datos y las imágenes.-"
        self.Lbl2 =qt.QLabel("Resultados:")
        self.Bton9 = qt.QPushButton("Pruebas ")
        self.Bton9.toolTip = "corre pruebas.-"
        
        self.textEdit = qt.QTextEdit("")
        self.textEdit.setMaximumSize(500, 50)

        self.etiqueta_v = qt.QLabel("Visualiza :")
        self.etiqueta_v.setAlignment(qt.Qt.AlignCenter)       
        
        self.Bton10 = qt.QPushButton("Volumen")
        self.Bton10.toolTip = "Visibiliza el volumen 3D"
        self.Bton11 = qt.QPushButton("Fiduciarios")
        self.Bton11.toolTip = "Visibiliza los fiduciarios"
        self.Bton12 = qt.QPushButton("N-Locadores")
        self.Bton12.toolTip = "Visibiliza los Localizadores N"
        self.Bton13 = qt.QPushButton("Fantasma")
        self.Bton13.toolTip = "Visibiliza Marco Micromar"
        self.Bton14 = qt.QPushButton("Arco")
        self.Bton14.toolTip = "Visibiliza el Arco"
        self.mensa = qt.QLabel("Mensajes...")
        #
        #  Define widgets del Layout Planificacion
        #
        self.etiqueta_x = qt.QLabel(" Target X :")
        self.Sli_x = ctk.ctkSliderWidget()
        self.Sli_x.singleStep = 0.5
        self.Sli_x.minimum = -150
        self.Sli_x.maximum = 150
        self.Sli_x.setToolTip("Establece el valor del desplazamiento en el eje X (positivo a la derecha).")
        cajita_x = qt.QHBoxLayout()
        cajita_x.addWidget(self.etiqueta_x)
        cajita_x.addWidget(self.Sli_x)

        self.etiqueta_y = qt.QLabel(" Target Y :")
        self.Sli_y = ctk.ctkSliderWidget()
        self.Sli_y.singleStep = 0.5
        self.Sli_y.minimum = -150
        self.Sli_y.maximum = 150
        self.Sli_y.setToolTip("Establece el valor del desplazamiento en el eje Y (+ hacia adelante).")
        cajita_y = qt.QHBoxLayout()
        cajita_y.addWidget(self.etiqueta_y)
        cajita_y.addWidget(self.Sli_y)

        self.etiqueta_z = qt.QLabel(" Target Z :")
        self.Sli_z = ctk.ctkSliderWidget()
        self.Sli_z.singleStep = 0.5
        self.Sli_z.minimum = -150
        self.Sli_z.maximum = 150
        self.Sli_z.setToolTip("Establece el valor del desplazamiento en el eje Z (+ hacia arriba).")

        cajita_z = qt.QHBoxLayout()
        cajita_z.addWidget(self.etiqueta_z)
        cajita_z.addWidget(self.Sli_z)

        cajita_Target = qt.QHBoxLayout()

        self.etiqueta_f = qt.QLabel(" Arco a la Derecha  :  ")
        self.etiqueta_g = qt.QLabel("        ")
        self.flag_Der_Izq = qt.QCheckBox()
        self.flag_Der_Izq.setToolTip("Si esta marcada, el arco estara a la derecha, sino a la izquierda.")

        self.etiqueta_a = qt.QLabel("Angulo Alfa")
        self.etiqueta_a.setAlignment(qt.Qt.AlignRight)
        #self.spin_a = qt.QLabel()
        self.spin_a = qt.QSpinBox()
        self.spin_a.setToolTip("Establece el valor del angulo Alfa.")
        self.spin_a.minimum = 0
        self.spin_a.maximum = 180
        #self.spin_a.singleStep = 0.5
        self.spin_a.setMaximumWidth(70)
        
        self.dial_a = qt.QDial()
        self.dial_a.setNotchesVisible(1)
        self.dial_a.minimum = 0
        self.dial_a.maximum = 180
        #self.dial_a.singleStep = 0.5
        #self.dial_a.tracking = False
        self.dial_a.setMinimumSize(120, 120)

        self.etiqueta_b = qt.QLabel("Angulo Beta")
        self.etiqueta_b.setAlignment(qt.Qt.AlignRight)
        #self.spin_b = qt.QLineEdit()
        self.spin_b = qt.QSpinBox()
        self.spin_b.setToolTip("Establece el valor del angulo Beta.")
        self.spin_b.minimum = 0
        self.spin_b.maximum = 105
        #self.spin_b.singleStep = 0.5
        self.spin_b.setMaximumWidth(70)
        self.spin_b.setAlignment(qt.Qt.AlignCenter)
        
        self.dial_b = qt.QDial()
        self.dial_b.setNotchesVisible(1)
        self.dial_b.minimum = 0
        self.dial_b.maximum = 105
        #self.dial_b.singleStep = 0.5
        #self.dial_b.tracking = False
        self.dial_b.setMinimumSize(120, 120)

        cajita_Mensa = qt.QHBoxLayout()
        #cajita_Mensa.addWidget(self.mensa)
        cajita_Grilla1 = qt.QGridLayout()
        cajita_Grilla1.addWidget(self.etiqueta_g, 0, 2)
        cajita_Grilla1.addWidget(self.etiqueta_g, 0, 3)
        cajita_Grilla1.addWidget(self.etiqueta_f, 0, 0)
        cajita_Grilla1.addWidget(self.flag_Der_Izq, 0, 1)

        cajita_Grilla = qt.QGridLayout()
        cajita_Grilla.addWidget(self.etiqueta_a, 3, 0)
        cajita_Grilla.addWidget(self.spin_a, 2, 1)
        cajita_Grilla.addWidget(self.dial_a, 2, 0)
        cajita_Grilla.addWidget(self.etiqueta_b, 3, 2)
        cajita_Grilla.addWidget(self.spin_b, 2, 3)
        cajita_Grilla.addWidget(self.dial_b, 2, 2)

        cajita_1 = qt.QGridLayout()
        cajita_1.addWidget(self.etiqueta_g, 0, 0)
        cajita_1.addWidget(self.etiqueta_v, 1, 0)

        cajita_1.addWidget(self.Bton10, 1, 1)
        cajita_1.addWidget(self.Bton11, 1, 2)
        cajita_1.addWidget(self.Bton12, 1, 3)
        cajita_1.addWidget(self.Bton13, 1, 4)
        cajita_1.addWidget(self.Bton14, 1, 5)

        Layout1 = qt.QGridLayout(self.Registracion_Bton)
        Layout1.addWidget(self.Lbl1, 0, 0)
        #Layout1.addWidget(self.Bton1, 1, 0)
        Layout1.addWidget(self.Bton2, 2, 0)
        #Layout1.addWidget(self.Bton3, 3, 0)
        Layout1.addWidget(self.Bton4, 4, 0)
        Layout1.addWidget(self.Bton5, 5, 0)
        #Layout1.addWidget(self.Bton9, 7, 0)
        Layout1.addWidget(self.Lbl2, 8 ,0)
        Layout1.addWidget(self.textEdit, 9, 0)        
        
        Layout2 = qt.QVBoxLayout(self.Planificacion_Bton)
        Layout2.addLayout(cajita_Grilla1)
        Layout2.addLayout(cajita_x)
        Layout2.addLayout(cajita_y)
        Layout2.addLayout(cajita_z)
        Layout2.addLayout(cajita_Target)
        Layout2.addLayout(cajita_Grilla)
        Layout2.addLayout(cajita_1)

        self.layout.addWidget(self.Registracion_Bton)
        self.layout.addWidget(self.Planificacion_Bton)
        self.layout.addStretch(1)   # Add vertical spacer
        #
        # conexiones de los botones con las funciones
        #
        self.Registracion_Bton.clicked.connect(self.colapso_Reg)
        self.Planificacion_Bton.clicked.connect(self.colapso_Plan)

        self.Bton1.clicked.connect(lambda: self.selectora_botones("Inicializa"))
        self.Bton2.clicked.connect(lambda: self.selectora_botones("Registracion"))
        self.Bton3.clicked.connect(lambda: self.selectora_botones("Entry"))
        self.Bton4.clicked.connect(lambda: self.selectora_botones("Target"))
        self.Bton5.clicked.connect(lambda: self.selectora_botones("Guarda"))
        self.Bton9.clicked.connect(lambda: self.selectora_botones("Pruebas"))

        self.Bton10.clicked.connect(lambda: self.visibilidad_modelos("toggle", "Volumen"))
        self.Bton11.clicked.connect(lambda: self.visibilidad_modelos("toggle", "f"))
        self.Bton12.clicked.connect(lambda: self.visibilidad_modelos("toggle", "N_Locators",))
        self.Bton13.clicked.connect(lambda: self.visibilidad_modelos("toggle", "Fantasma_Modelo"))
        self.Bton14.clicked.connect(lambda: self.visibilidad_modelos("toggle", "Arco"))
        #
        # sliders controlando los desplazamientos y angulos
        #
        self.Sli_x.valueChanged.connect(self.onCambioSliders)
        self.Sli_y.valueChanged.connect(self.onCambioSliders)
        self.Sli_z.valueChanged.connect(self.onCambioSliders)
        self.flag_Der_Izq.stateChanged.connect(self.onCambioDerIzq)
        
        self.dial_a.valueChanged.connect(self.spin_a.setValue)
        self.dial_b.valueChanged.connect(self.spin_b.setValue)
        self.spin_a.valueChanged.connect(self.dial_a.setValue)
        self.spin_b.valueChanged.connect(self.dial_b.setValue)
        self.dial_a.valueChanged.connect(self.onCambioDial)
        self.dial_b.valueChanged.connect(self.onCambioDial)
        
        ############################  Manejo del widget #######################
        self.selectora_botones("Inicializa")
        #######################################################################
       
    def colapso_Reg(self):
        print("se oprimio Registracion")
        self.Planificacion_Bton.collapsed  = not self.Registracion_Bton.collapsed
        self.collapsed_botones()
        
    def colapso_Plan(self):
        print("se oprimio Planificacion")
        self.Registracion_Bton.collapsed  = not self.Planificacion_Bton.collapsed
        self.collapsed_botones()
        
    def collapsed_botones(self):
        param = slicer.util.getNode("Param_data")
        if self.Planificacion_Bton.collapsed:
            print("vino a Modo Registracion.-")
            slicer.app.layoutManager().setLayout(6)  # Red panel
            return 
        elif self.Registracion_Bton.collapsed:
            print("vino a Modo Planificacion.-")
            try:    
                if param.GetParameter("Registered_flag") == "False":
                    texto = "ERROR: no hay volumenes registrados aun!"
                    slicer.util.warningDisplay(texto, windowTitle="Error", parent=None, standardButtons=None)     
                    self.Registracion_Bton.collapsed = False  
                    self.Planificacion_Bton.collapsed = True
                    return
            except:
                texto = "ERROR: no hay volumenes registrados aun!"
                slicer.util.warningDisplay(texto, windowTitle="Error", parent=None, standardButtons=None)     
                return    
            self.Actualiza_elementos_del_Widget()
            self.Establece_Isocentro_y_Arco()
            slicer.app.layoutManager().setLayout(4)  # 3d panel
            
    def selectora_botones(self, modo):
        if modo == "Guarda":
            self.logica.guarda()
            return     
        
        self.limpia_widget()
        self.logica.grafica_path(False)
        if modo == "Inicializa":
            slicer.mrmlScene.Clear(0)
            self.logica.Establece_Escena()
            
            ####
            #modulo = slicer.util.modulePath("SlicerStereotaxia")
            #moduloPath = os.path.split(modulo)[0]
            #slicer.util.loadVolume(moduloPath + "/Paciente.nrrd")
            ####
        
            self.logica.Inicializa_Escena()
            self.Actualiza_elementos_del_Widget()
            self.Establece_Isocentro_y_Arco()
            slicer.app.layoutManager().setLayout(4)  # 3D panel
        
        elif modo == "Registracion":
            nodo_volu = self.utiles.obtiene_nodo_de_widget("Red")
            if nodo_volu == None:
                texto = "ERROR: no hay volumenes cargados"
                slicer.util.warningDisplay(texto, windowTitle="Error", parent=None, standardButtons=None)
                return
 
            self.logica.Inicializa_Escena()
            self.utiles.cambia_window_level("Red", 100, 50)
            slicer.app.layoutManager().setLayout(6)  # RED panel
     
            param = slicer.util.getNode("Param_data")
            self.mixObservador_4 = slicer.util.VTKObservationMixin()
            self.mixObservador_4.addObserver(param, vtk.vtkCommand.AnyEvent, self.actualiza_widget)
            self.logica.Obtiene_9_Fiduciarios_f()
        
        elif modo == "Entry":
            slicer.app.layoutManager().setLayout(6)  # RED panel
            self.logica.Obtiene_1_Fiduciario_Entry()
        
        elif modo == "Target":
            slicer.app.layoutManager().setLayout(6)  # RED panel
            self.logica.Obtiene_1_Fiduciario_Target()

               
    def onCambioSliders(self):
        #print("vino a cambio sliders")
        param = slicer.util.getNode("Param_data")
        param.SetParameter("Target", str([self.Sli_x.value, self.Sli_y.value, self.Sli_z.value]))
        if self.Sli_x.value < 0:
            param.SetParameter("Target_Der_Izq_flag", str(False))
            self.flag_Der_Izq.checked = False
        else:
            param.SetParameter("Target_Der_Izq_flag", str(True))
            self.flag_Der_Izq.checked = True
        registracionLogic().Actualiza_Target()
        self.Establece_Isocentro_y_Arco()

    def onCambioDial(self):
        #print("vino a cambio dial")
        param = slicer.util.getNode("Param_data")
        param.SetParameter("Target_Angulo_Alfa", str(self.dial_a.value))
        param.SetParameter("Target_Angulo_Beta", str(self.dial_b.value))
        #self.Actualiza_elementos_del_Widget()
        self.Establece_Isocentro_y_Arco()
    
    def onCambioDerIzq(self):
        #print("vino a cambio flag der / izq")
        param = slicer.util.getNode("Param_data")
        param.SetParameter("Target_Der_Izq_flag", str(self.flag_Der_Izq.checked))
        self.Establece_Isocentro_y_Arco()

    def onCambioWidgets(self):
        param = slicer.util.getNode("Param_data")
        param.SetParameter("Target", str([self.Sli_x.value, self.Sli_y.value, self.Sli_z.value]))
        if self.Sli_x.value < 0:
            param.SetParameter("Target_Der_Izq_flag", str(False))
            self.flag_Der_Izq.checked = False
        else:
            param.SetParameter("Target_Der_Izq_flag", str(True))
            self.flag_Der_Izq.checked = True
        param.SetParameter("Target_Angulo_Alfa", str(self.dial_a.value))
        param.SetParameter("Target_Angulo_Beta", str(self.dial_b.value))
        param.SetParameter("Target_Der_Izq_flag", str(self.flag_Der_Izq.checked))
        
        self.logica.Actualiza_Target()
        self.Actualiza_elementos_del_Widget()
        self.Establece_Isocentro_y_Arco()

    def Bloquea_senales_del_Widget(self, modo): # True o False
        self.dial_a.blockSignals(modo)
        self.Sli_x.blockSignals(modo)
        self.Sli_y.blockSignals(modo)
        self.Sli_z.blockSignals(modo)
        self.dial_a.blockSignals(modo)
        self.dial_b.blockSignals(modo)
        self.spin_a.blockSignals(modo)
        self.spin_b.blockSignals(modo)
        self.flag_Der_Izq.blockSignals(modo)

    def Actualiza_elementos_del_Widget(self):
        self.Bloquea_senales_del_Widget(True)
        param = slicer.util.getNode("Param_data")
        self.Sli_x.value = ast.literal_eval(param.GetParameter("Target"))[0]
        self.Sli_y.value = ast.literal_eval(param.GetParameter("Target"))[1]
        self.Sli_z.value = ast.literal_eval(param.GetParameter("Target"))[2]
        self.dial_a.value = ast.literal_eval(param.GetParameter("Target_Angulo_Alfa"))
        self.dial_b.value = ast.literal_eval(param.GetParameter("Target_Angulo_Beta"))
        self.spin_a.value = ast.literal_eval(param.GetParameter("Target_Angulo_Alfa"))
        self.spin_b.value = ast.literal_eval(param.GetParameter("Target_Angulo_Beta"))
        self.flag_Der_Izq.checked = ast.literal_eval(param.GetParameter("Target_Der_Izq_flag")) 
        self.Bloquea_senales_del_Widget(False)

    def limpia_widget(self):
        self.textEdit.setPlainText("")

    def actualiza_widget(self, param, event):
        print("vino al callback actualiza widget !!!!!!!!!!!")
        print(event)
        self.limpia_widget()
        if param.GetParameter("Registered_flag") != "True":
            return
        self.textEdit.append("Target = " +  param.GetParameter("Target"))
        #self.textEdit.append("Entry = " +  param.GetParameter("T_Entry"))
        #self.textEdit.append("Trayectoria = " + param.GetParameter("Path_length") + " mm.")
        #self.textEdit.append("angulo Alfa = " + param.GetParameter("Target_Angulo_Alfa") )
        #self.textEdit.append("angulo Beta = " + param.GetParameter("Target_Angulo_Beta") )
    
    def Establece_Isocentro_y_Arco(self):
        param = slicer.util.getNode("Param_data")
        Target = ast.literal_eval(param.GetParameter("Target"))
        ang_Alfa = ast.literal_eval(param.GetParameter("Target_Angulo_Alfa"))
        ang_Beta = ast.literal_eval(param.GetParameter("Target_Angulo_Beta"))
        der_izq = ast.literal_eval(param.GetParameter("Target_Der_Izq_flag"))
        
        ang_Alfa_corregido = 90 - ang_Alfa         # correccion para graficar
        ang_Beta_corregido = 0 - ang_Beta          # correccion para graficar
        
        """ modifica las transformadas para el arco y la aguja de puncion.-"""
        
        transfo_0 = vtk.vtkTransform()
        if der_izq != 1:  # coloca el arco a la izquierda
            transfo_0.RotateZ(180)
        node_0 = slicer.util.getNode('Transformada_Der_Izq')
        node_0.SetMatrixTransformToParent(transfo_0.GetMatrix())
        
        transfo_1 = vtk.vtkTransform()
        transfo_1.Translate(Target[0], Target[1], Target[2])
        node_1 = slicer.util.getNode('Transformada_Isocentro')
        node_1.SetMatrixTransformToParent(transfo_1.GetMatrix())

        transfo_2 = vtk.vtkTransform()
        if der_izq:
            transfo_2.RotateX(ang_Alfa_corregido)
        else:
            transfo_2.RotateX(-ang_Alfa_corregido)
        node_2 = slicer.util.getNode('Transformada_angulo_Alfa')
        node_2.SetMatrixTransformToParent(transfo_2.GetMatrix())
        
        transfo_3 = vtk.vtkTransform()
        transfo_3.RotateY(ang_Beta_corregido)
        node_3 = slicer.util.getNode('Transformada_angulo_Beta')
        node_3.SetMatrixTransformToParent(transfo_3.GetMatrix())
        
        if der_izq:
            print("Arco a la derecha.")
        else:
            print("Arco a la izquierda.")
        
        print("Desplazamiento X, Y, Z =", Target, " mm.", end="\r")
        #print("Desplazamiento X, Y, Z =", Target[0], ",", Target[1], ",", Target[2], " mm.", end="\r")
        print("Angulo Alfa = ",  ang_Alfa, ", Beta = ", ang_Beta, " grados.")
        print()

        texto1 = "Target =  " + \
        str(round(Target[0], 1)) + ",  " +\
        str(round(Target[1], 1)) + ",  " +\
        str(round(Target[2], 1))
        self.anota_en_esquina_3D(texto1, 2)
        #texto2 = "Angulos Alfa = "+  str(ang_Alfa) + ", Beta = " + str(ang_Beta) +  " grados."
        #self.anota_en_esquina_3D(texto2, 3)
   
    def anota_en_esquina_3D(self, texto, esquina):
        lm = slicer.app.layoutManager()
        re = lm.threeDWidget(0)
        vi = re.threeDView()
        ca = vi.cornerAnnotation()
        ca.GetTextProperty().SetColor(1, 1, 0)
        ca.SetText(esquina, texto)

    def visibilidad_modelos(self, modo, nombre_modelo):
        if nombre_modelo == "Volumen":
            nombre_modelo= self.utiles.obtiene_nodo_de_widget("Red").GetName()
            #print(nombre_modelo)
        modelo = slicer.util.getNode(nombre_modelo)
        modelo.SetDisplayVisibility(not modelo.GetDisplayVisibility())  # invierte visibilidad
        print("Visibilidad ", nombre_modelo, ": ", bool(modelo.GetDisplayVisibility()))
        if nombre_modelo == "Arco":
            nombre_modelo_2 = "Aguja_de_Puncion" #? Loop ???
            modelo = slicer.util.getNode(nombre_modelo_2)
            modelo.SetDisplayVisibility(not modelo.GetDisplayVisibility())  # invierte visibilidad
            print("Visibilidad ", nombre_modelo_2, ": ", bool(modelo.GetDisplayVisibility()))

 
class registracionLogic(ScriptedLoadableModuleLogic):
    """Esta clase implemtenta todos los computos de
    registracion y calculo que requiere el modulo"""
    def __init__(self):
        self.utiles = utilitarios.util()
        self.gest = gestion_Fiduciarios.gestion()
        self.maqui = Maquina_Russell_Brown.calculus()
        self.marco = Maquina_Russell_Brown.Marco_Micromar()

        self.modulo = slicer.util.modulePath("SlicerStereotaxia")
        self.rootPath = slicer.mrmlScene.GetRootDirectory()
        self.moduloPath = os.path.split(self.modulo)[0]
        self.archivoPath = self.moduloPath + "/Archivo"
        self.escenaPath = self.moduloPath + "/Espacio_Marco/_Marco_Scene.mrml"
       
    def Establece_Escena(self):
        print("------------------------------------------------")
        print("                Abre una sesion                 ")
        print("------------------------------------------------")
        #slicer.mrmlScene.Clear(0)
        print("root path: ", self.rootPath)
        print("modulo: ", self.modulo)
        print("modulo path:", self.moduloPath)
        print("escena en uso: ", self.escenaPath)
        slicer.app.layoutManager().setLayout(4)  # 3d panel        
        try:
            # comprueba si fue cargada la escena previamente
            nodo1 = slicer.util.getNode("Arco") 
            nodo = slicer.util.getNode("Transformada_Isocentro")
            print("La Escena ha sido cargada previamente")
        except:
            print("se carga Escena por primera vez")
            slicer.util.loadScene(self.escenaPath)
            self.utiles.Genera_Nodo("vtkMRMLScriptedModuleNode", "Param_data")
             
    def Inicializa_Escena(self):
        print("------------------------------------------------")
        print("    Inicializa  nodos en una Escena ya abierta  ")
        print("------------------------------------------------")
 
        self.utiles.Borra_nodos_por_clase("vtkMRMLMarkupsFiducialNode")
        self.utiles.Borra_nodos_por_clase("vtkMRMLMarkupsLineNode")
        #self.utiles.impri_layout_2D("Red", "", 0)
        
        #nodo_volu = self.utiles.obtiene_nodo_de_widget("Red")
        param = slicer.util.getNode("Param_data")
        #param.SetParameter(" Nombre_del_Paciente", nodo_volu.GetName())
        param.SetParameter("Fiduciarios_Marco", str(Maquina_Russell_Brown.Marco_Micromar.P[1:9]))  
        param.SetParameter("Target", str([0.0, 0.0, 0.0]))
        param.SetParameter("T_Entry", str([0.0, 0.0, 0.0]))
        param.SetParameter("Target_Angulo_Alfa", str(90))
        param.SetParameter("Target_Angulo_Beta", str(45))
        param.SetParameter("Target_Der_Izq_flag", str(True))
        param.SetParameter("Registered_flag", "False")
        
    def Obtiene_9_Fiduciarios_f(self):
        print("vino a marcacion de 9 fiduciarios")
        nodo_volu = self.utiles.obtiene_nodo_de_widget("Red")
        param = slicer.util.getNode("Param_data")
        param.SetParameter(" Nombre_del_Paciente", nodo_volu.GetName())
        transformada = self.utiles.Genera_Nodo("vtkMRMLLinearTransformNode", "Transformada_Correctora_del_Volumen")
        nodo_volu.SetAndObserveTransformNodeID(transformada.GetID())
        # centra el volumen y aproxima a zero
        print("El volumen con que se trabaja es = ", nodo_volu.GetName())
        print("el origen del volumen es =")
        print(nodo_volu.GetOrigin())
        self.utiles.modifica_origen_de_volumen(nodo_volu, [100,100,-100])
        self.utiles.centra_nodo_de_widget("Red")
        print("Coloca volumen '", nodo_volu.GetName(), "' en transformada.-")
        self.utiles.Renderiza_3D_Volumen(nodo_volu)
        print("Se ha renderizado volumen:", nodo_volu.GetName())
            
        transformada = self.utiles.Genera_Nodo("vtkMRMLLinearTransformNode", "Transformada_Correctora_del_Volumen")
        nodo_volu.SetAndObserveTransformNodeID(transformada.GetID())
        self.grafica_path(False)
        self.utiles.centra_nodo_de_widget("Red")
        self.utiles.cambia_window_level("Red", 100, 50)
        
        self.gest.moduloPath = self.moduloPath  
        self.gest.Inicializa_nodo("Target")
        self.gest.Inicializa_nodo("Entry")
        nodo_fidu = self.gest.Inicializa_nodo("f")
        nodo_fidu.SetAndObserveTransformNodeID(transformada.GetID())

        nodo_fidu.GetDisplayNode().SetGlyphType(1)
        nodo_fidu.GetDisplayNode().SetSelectedColor(0.0, 1.0, 0.0)
        nodo_fidu.GetDisplayNode().SetActiveColor(1.0, 0.0, 0.0)
            
        self.mixObservador_1 = slicer.util.VTKObservationMixin()
        self.mixObservador_1.addObserver(nodo_fidu, vtk.vtkCommand.UserEvent, self.main)
        self.gest.Marcacion_Fiduciarios("f", 9)
        
    def Obtiene_1_Fiduciario_Target(self):
        print("vino a marcacion de 1 Target")
        param = slicer.util.getNode("Param_data")
        if param.GetParameter("Registered_flag") != "True":
            texto = "  Error: no se puede marcar el Target antes de Registrar !!!   "
            slicer.util.warningDisplay(texto, windowTitle="Error", parent=None, standardButtons=None)
            return
        
        registracionLogic().grafica_path(False)
        self.utiles.cambia_window_level("Red", 100, 50)
            
        nodo_fidu = self.gest.Inicializa_nodo("Target")
        nodo_fidu.GetDisplayNode().SetGlyphType(2)
        #nodo_fidu.GetDisplayNode().SetColor(1.0, 1.0, 0.0)
        nodo_fidu.GetDisplayNode().SetSelectedColor(1.0, 1.0, 0.0)
        nodo_fidu.GetDisplayNode().SetActiveColor(1.0, 1.0, 0.0)
        
        self.mixObservador_1 = slicer.util.VTKObservationMixin()
        self.mixObservador_1.addObserver(nodo_fidu, vtk.vtkCommand.UserEvent, self.main)
        self.gest.Marcacion_Fiduciarios("Target", 1)

    def Obtiene_1_Fiduciario_Entry(self):
        print("vino a marcacion de 1 Entry")
        param = slicer.util.getNode("Param_data")
        if param.GetParameter("Registered_flag") != "True":
            texto = "  Error: no se puede marcar el Entry sin Registrar previamente!!!   "
            slicer.util.warningDisplay(texto, windowTitle="Error", parent=None, standardButtons=None)
            return
        
        if ast.literal_eval(param.GetParameter("Target")) == [0, 0, 0]:
            texto = "  Es preferible marcar previamente el Target.-   "
            slicer.util.warningDisplay(texto, windowTitle="Error", parent=None, standardButtons=None)
     
        registracionLogic().grafica_path(False)
        self.utiles.cambia_window_level("Red", 100, 50)
        
        nodo_fidu = self.gest.Inicializa_nodo("Entry")
        nodo_fidu.GetDisplayNode().SetGlyphType(2)
        nodo_fidu.GetDisplayNode().SetColor(1.0, 1.0, 0.0)
        nodo_fidu.GetDisplayNode().SetSelectedColor(1.0, 1.0, 0.0)
        nodo_fidu.GetDisplayNode().SetActiveColor(1.0, 1.0, 0.0)
        
        self.mixObservador_1 = slicer.util.VTKObservationMixin()
        self.mixObservador_1.addObserver(nodo_fidu, vtk.vtkCommand.UserEvent, self.main)
        self.gest.Marcacion_Fiduciarios("Entry", 1)

    def main(self, obj, evento):
        print("vino a callback main desde :", type(obj), evento)
        if evento != "UserEvent":
            texto = "No viene a MAIN desde donde debiera ! !" + str(evento)
            slicer.util.warningDisplay(texto, windowTitle="Error", parent=None, standardButtons=None)
            return

        self.mixObservador_1.removeObservers()      
        param = slicer.util.getNode("Param_data")
        #
        #     procedimiento de REGISTRACION
        #
        if self.gest.nombre_Nodo == "f":
            nodo_fidu = slicer.util.getNode(self.gest.nombre_Nodo)
            fiduciarios_TAC = self.gest.Lectura_Fiduciarios(nodo_fidu)
            matriz_RB = self.maqui.Ecuaciones_Russell_Brown(fiduciarios_TAC)
            array_M_RB = slicer.util.arrayFromVTKMatrix(matriz_RB).tolist()
            fiduciarios_3D = self.maqui.Multiplica_lista_de_puntos(fiduciarios_TAC, matriz_RB)
         
            matriz_4x4  = self.maqui.Analisis_por_ICP(fiduciarios_TAC, fiduciarios_3D)
            array_M_3D = slicer.util.arrayFromVTKMatrix(matriz_RB).tolist()
            
            transformada = vtk.vtkTransform()
            transformada.SetMatrix(matriz_4x4)

            nodo = slicer.util.getNode("Transformada_Correctora_del_Volumen")
            nodo.SetAndObserveTransformToParent(transformada)
            self.utiles.centra_nodo_de_widget("Red")

            param.SetParameter("Fiduciarios_3D", str(self.utiles.redondea_lista_de_puntos(fiduciarios_3D, 2)))
            param.SetParameter("Array_Matrix_3D", str(array_M_3D))
            param.SetParameter("Fiduciarios_TAC", str(self.utiles.redondea_lista_de_puntos(fiduciarios_TAC, 2)))
            param.SetParameter("Array_Matrix_RB", str(array_M_RB))
            param.SetParameter("Registered_flag", "True")
            param.SetParameter("Transfo_Position", str(self.utiles.redondea(transformada.GetPosition(), 2)))
            param.SetParameter("Transfo_Orientation", str(self.utiles.redondea(transformada.GetOrientation(), 2)))
            
            print("Fiduciarios_TAC = " + param.GetParameter("Fiduciarios_TAC"))
            print("Matrix_RB = ", matriz_RB)
            print("Matriz 4x4 = ", matriz_4x4)
            print("Position= ", param.GetParameter("Transformada_Position" ))
            print("Orientation= ", param.GetParameter("Transformada_Orientation"))
            print("Registered_flag = ", param.GetParameter("Registered_flag"))

        # procedimiento del Target   
        elif self.gest.nombre_Nodo == "Target":
            nodo_fidu = slicer.util.getNode(self.gest.nombre_Nodo)
            Target = self.gest.Lectura_Fiduciarios(nodo_fidu)[0]  # toma el segundo t�rmino
            param.SetParameter("Target", str(self.utiles.redondea(Target, 1)))
            self.grafica_path(True)

            texto = "Target = " + param.GetParameter("Target")
            nodo_fidu.SetNthMarkupLabel(0, texto)
            self.utiles.impri_layout_2D("Red", texto, 2)
            
            print()
            print("----------------------------------------------")
            print(texto)
            print("----------------------------------------------")
            
        elif self.gest.nombre_Nodo == "Entry":   # procedimiento del Target
            nodo_fidu = slicer.util.getNode(self.gest.nombre_Nodo)
            Entry = self.gest.Lectura_Fiduciarios(nodo_fidu)[0]  # toma el segundo termino
            param.SetParameter("T_Entry", str(self.utiles.redondea(Entry, 1)))
            self.grafica_path(True)    

            texto = "Entry = " + param.GetParameter("T_Entry")
            nodo_fidu.SetNthMarkupLabel(0, texto)
            self.utiles.impri_layout_2D("Red", texto, 7)
            
            print()
            print("-------------------------------------------")
            print(texto)
            print("-------------------------------------------")
            
    def grafica_path(self, modo):
        print("vino a grafica path")
        if modo == False:
            self.utiles.Borra_nodo("Path")
            return

        param = slicer.util.getNode("Param_data")
        Target = ast.literal_eval(param.GetParameter("Target"))
        Entry = ast.literal_eval(param.GetParameter("T_Entry"))
        
        if Entry == [0, 0, 0]:
            return
        if Entry == Target:
            return
        if (Entry[0]>=0) != (Target[0]>=0):   #(a>0) == (b>0)  
            texto = "ATENCION: el PATH atraviesa la línea media !  "
            slicer.util.warningDisplay(texto, windowTitle="Error", parent=None, standardButtons=None)
            
        Alfa, Beta = self.utiles.calcula_angulos(Entry, Target)
        largo_path = self.utiles.grafica_linea(Entry, Target)        # grafica path

        param.SetParameter("Target_Angulo_Alfa", str(round(Alfa, 2)))
        param.SetParameter("Target_Angulo_Beta", str(round(Beta, 2)))
        param.SetParameter("Path_length", str(round(largo_path, 2)))
        
        if Entry[0] >= 0:
            param.SetParameter("Target_Der_Izq_flag", str(True))
        else:
            param.SetParameter("Target_Der_Izq_flag", str(False))
        
        texto = "Alfa : " + param.GetParameter("Target_Angulo_Alfa")
        texto = texto + ",  Beta : "+ param.GetParameter("Target_Angulo_Beta") 
        texto = texto + ", long : " + param.GetParameter("Path_length")
        self.utiles.impri_layout_2D("Red", texto, 3)
        
        print("ángulo_Alfa = ", param.GetParameter("Target_Angulo_Alfa"), "grados.")  #plano lateral
        print("ángulo_Beta = ", param.GetParameter("Target_Angulo_Beta"), "grados.") # plano frotal 
        print("longitud del path = ", param.GetParameter("Path_length"), "mm.")

    def Actualiza_Target(self):
        print("vino a actualizar el Target")
        param = slicer.util.getNode("Param_data")
        Target = ast.literal_eval(param.GetParameter("Target"))
        try:
            nodo = slicer.util.getNode("Target")
        except:
            print("no hay nodo Target")
            return
        nodo.SetNthFiducialPosition(0, Target[0],Target[1], Target[2])
        texto = "Target = " + str(self.utiles.redondea(Target, 1))
        nodo.SetNthMarkupLabel(0, texto)

    def guarda(self):
        print("vino a save")
        # Create a new directory where the scene will be saved into
        ref_time = time.strftime("%Y%m%d-%H%M%S")
        sceneSaveDirectory = self.moduloPath + "/Archivo/Escena_" + ref_time
        if not os.access(sceneSaveDirectory, os.F_OK):
            os.makedirs(sceneSaveDirectory)
        # Save the scene
        if slicer.app.applicationLogic().SaveSceneToSlicerDataBundleDirectory(sceneSaveDirectory, None):
            logging.info("Scene saved to: {0}".format(sceneSaveDirectory))
        else:
            logging.error("Scene saving failed")
        param = slicer.util.getNode("Param_data")
        param.SetParameter(" Referencia_tiempo", ref_time)
        dictio = {}
        for item in param.GetParameterNames():
            dictio[item] = param.GetParameter(item)
        import json
        #json.dump(dictio, sceneSaveDirectory + "/parametros.json")   
        js = json.dumps(dictio)
        # Open new json file if not exist it will create
        fp = open(sceneSaveDirectory + "/parametros.json", 'a')
        # write to json file
        fp.write(js)
        # close the connection
        fp.close()

