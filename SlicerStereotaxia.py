# -*- coding: utf-8 -*-
# Estereotaxia version 21.0324
import os
import logging
import math
import ast   # para eval seguras
from importlib import reload  

from __main__ import vtk, qt, ctk, slicer
from slicer.ScriptedLoadableModule import *

from Recursos import Maquina_Russell_Brown
from Recursos import utilitarios as util
from Recursos import gestion_Fiduciarios 

reload(util)
reload(Maquina_Russell_Brown)
reload(gestion_Fiduciarios)

gest = gestion_Fiduciarios.gestion_Fiduciarios()

class SlicerStereotaxia(ScriptedLoadableModule):
    """Uses ScriptedLoadableModule base class"""

    def __init__(self, parent):
        ScriptedLoadableModule.__init__(self, parent)
        self.parent.title = "SlicerStereotaxia"
        self.parent.categories = ["Estereotaxia"]
        self.parent.dependencies = []
        self.parent.contributors = ["Dr. Miguel Ibanez; Dr. Dante Lovey; Dr. Lucas Vera; Dra. Elena Zema; Dr. Jorge Beninca."]
        self.parent.helpText = "Esta es la Version 21.0203"
        self.parent.acknowledgementText = " Este modulo fue desarrollado originalmente por Jorge A.Beninca, durante los meses de Enero a Julio 2015, en el dpto de Neurocirugia del Hospital de Ninos Dr. Orlando Alassia."

class SlicerStereotaxiaWidget(ScriptedLoadableModuleWidget):
    """Uses ScriptedLoadableModuleWidget base class"""
    def setup(self):
        self.util = util

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
        self.Lbl1 = qt.QLabel("Calcula coordenadas 3D de fiduciarios 2D de TAC")
        self.Lbl1.setAlignment(qt.Qt.AlignCenter)
        self.Bton1 = qt.QPushButton("Inicializa")
        self.Bton1.toolTip = "Inicia todas las variables.-"
        self.Bton2 = qt.QPushButton("Registración")
        self.Bton2.toolTip = "Marca los 9 fiduciarios f.-"
        self.Bton3 = qt.QPushButton("Entry ")
        self.Bton3.toolTip = "Marca el punto de Entrada.-"
        self.Bton4 = qt.QPushButton("Target")
        self.Bton4.toolTip = "Marca el fiduciario Target y realiza los calculos.-"
        self.Bton5 = qt.QPushButton("Guarda")
        self.Bton5.toolTip = "Guarda los datos y las imágenes.-"
        
        self.Bton9 = qt.QPushButton("Pruebas ")
        self.Bton9.toolTip = "corre pruebas.-"
        
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
        Layout1.addWidget(self.Bton1, 1, 0)
        Layout1.addWidget(self.Bton2, 2, 0)
        Layout1.addWidget(self.Bton3, 3, 0)
        Layout1.addWidget(self.Bton4, 4, 0)
        Layout1.addWidget(self.Bton5, 5, 0)
        
        #Layout1.addWidget(self.Bton9, 6, 1)
        
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
        registracionLogic().Establece_Escena()#set observer de cambio del target
        #self.selectora_botones("Inicializa")
       # #####################################################################
       
    def colapso_Reg(self):
        print("se oprimio Registracion")
        self.Planificacion_Bton.collapsed  = not self.Registracion_Bton.collapsed
        self.collapsed_botones()
        
    def colapso_Plan(self):
        print("se oprimio Planificacion")
        self.Registracion_Bton.collapsed  = not self.Planificacion_Bton.collapsed
        self.collapsed_botones()
        
    def collapsed_botones(self):
        transfe = slicer.util.getNode("Transfe_data")
        if self.Planificacion_Bton.collapsed:
            print("vino a Modo Registracion.-")
            slicer.app.layoutManager().setLayout(6)  # Red panel
            return 
        elif self.Registracion_Bton.collapsed:
            print("vino a Modo Planificacion.-")    
            if transfe.GetParameter("Registered_flag") == "False":
                texto = "ERROR: no hay volumenes registrados aun!"
                slicer.util.warningDisplay(texto, windowTitle="Error", parent=None, standardButtons=None)     
                self.Registracion_Bton.collapsed = False  
                self.Planificacion_Bton.collapsed = True
                return
        
            self.Actualiza_elementos_del_Widget()
            self.Establece_Isocentro_y_Arco()
            slicer.app.layoutManager().setLayout(4)  # 3d panel
            
    def selectora_botones(self, modo):
        if modo == "Inicializa":
            #slicer.mrmlScene.Clear(0)
            registracionLogic().Inicializa_Escena()
            self.Actualiza_elementos_del_Widget()
            self.Establece_Isocentro_y_Arco()
        elif modo == "Registracion":
            print("vino a registracion ")
            slicer.app.layoutManager().setLayout(6)  # RED panel
            registracionLogic().Obtiene_9_Fiduciarios()
        elif modo == "Entry":
            print("vino a Entry ")
            slicer.app.layoutManager().setLayout(6)  # RED panel
            registracionLogic().Obtiene_1_Fiduciario_Entry()
        elif modo == "Target":
            print("vino a Target ")
            slicer.app.layoutManager().setLayout(6)  # RED panel
            registracionLogic().Obtiene_1_Fiduciario_Target()
        elif modo == "Guarda":
            registracionLogic().guarda()
        elif modo == "Pruebas":
            print("vino a Pruebas")
            pass    

    ######################### fin manejo de widget #############################

    def onCambioSliders(self):
        print("vino a cambio sliders")
        transfe = slicer.util.getNode("Transfe_data")
        transfe.SetParameter("Target", str([self.Sli_x.value, self.Sli_y.value, self.Sli_z.value]))
        if self.Sli_x.value < 0:
            transfe.SetParameter("Target_Der_Izq_flag", str(False))
            self.flag_Der_Izq.checked = False
        else:
            transfe.SetParameter("Target_Der_Izq_flag", str(True))
            self.flag_Der_Izq.checked = True
        registracionLogic().Actualiza_Target()
        self.Establece_Isocentro_y_Arco()

    def onCambioDial(self):
        print("vino a cambio dial")
        transfe = slicer.util.getNode("Transfe_data")
        transfe.SetParameter("Target_Angulo_Alfa", str(self.dial_a.value))
        transfe.SetParameter("Target_Angulo_Beta", str(self.dial_b.value))
        #self.Actualiza_elementos_del_Widget()
        self.Establece_Isocentro_y_Arco()
    
    def onCambioDerIzq(self):
        print("vino a cambio flag der / izq")
        transfe = slicer.util.getNode("Transfe_data")
        transfe.SetParameter("Target_Der_Izq_flag", str(self.flag_Der_Izq.checked))
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
        transfe = slicer.util.getNode("Transfe_data")
        self.Sli_x.value = ast.literal_eval(transfe.GetParameter("Target"))[0]
        self.Sli_y.value = ast.literal_eval(transfe.GetParameter("Target"))[1]
        self.Sli_z.value = ast.literal_eval(transfe.GetParameter("Target"))[2]
        self.dial_a.value = ast.literal_eval(transfe.GetParameter("Target_Angulo_Alfa"))
        self.dial_b.value = ast.literal_eval(transfe.GetParameter("Target_Angulo_Beta"))
        self.spin_a.value = ast.literal_eval(transfe.GetParameter("Target_Angulo_Alfa"))
        self.spin_b.value = ast.literal_eval(transfe.GetParameter("Target_Angulo_Beta"))
        self.flag_Der_Izq.checked = ast.literal_eval(transfe.GetParameter("Target_Der_Izq_flag")) 
        self.Bloquea_senales_del_Widget(False)

    def Establece_Isocentro_y_Arco(self):
        transfe = slicer.util.getNode("Transfe_data")
        Target = ast.literal_eval(transfe.GetParameter("Target"))
        ang_Alfa = ast.literal_eval(transfe.GetParameter("Target_Angulo_Alfa"))
        ang_Beta = ast.literal_eval(transfe.GetParameter("Target_Angulo_Beta"))
        der_izq = ast.literal_eval(transfe.GetParameter("Target_Der_Izq_flag"))
        
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
            nombre_modelo= util.obtiene_nodo_de_widget("Red").GetName()
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
        self.gest = gestion_Fiduciarios.gestion_Fiduciarios()
        self.maqui = Maquina_Russell_Brown
        self.util = util
        self.modulo = slicer.util.modulePath("SlicerEstereotaxia")
        self.rootPath = slicer.mrmlScene.GetRootDirectory()
        self.moduloPath = os.path.split(self.modulo)[0]
        self.escenaPath = self.moduloPath + "/Espacio Simplex/_Main_Scene.mrml"
       
    def Establece_Escena(self):
        print("------------------------------------------------")
        print("                Abre una sesion")
        print("------------------------------------------------")
        #slicer.mrmlScene.Clear(0)
        modulo = slicer.util.modulePath("SlicerEstereotaxia")
        moduloPath = os.path.split(modulo)[0]
        escenaPath = moduloPath + "/Espacio_Marco/_Marco_Scene.mrml"
        print("path modulo en uso:", moduloPath)
        print("escena en uso: ", escenaPath)
        lay = slicer.app.layoutManager()
        lay.setLayout(4)  # 3d panel        
        try:
            # comprueba si fue cargada la escena previamente
            nodo1 = slicer.util.getNode("Arco") 
            nodo = slicer.util.getNode("Transformada_Isocentro")
            print("La Escena ha sido cargada previamente")
        except:
            print("se carga Escena por primera vez")
            slicer.util.loadScene(escenaPath)
        
             
    def Inicializa_Escena(self):
        print("------------------------------------------------")
        print("    Inicializa:  nodos en una Escena ya abierta ")
        print("------------------------------------------------")
        nodo_volu = util.obtiene_nodo_de_widget("Red")
        if nodo_volu == None:
            texto = "ERROR: no hay volumenes cargados"
            slicer.util.warningDisplay(texto, windowTitle="Error", parent=None, standardButtons=None)
            return None

        # centra el volumen y aproxima a zero
        print("El volumen con que se trabaja es = ", nodo_volu.GetName())
        #print("el origen del volumen es =")
        #print(nodo_volu.GetOrigin())
        #util.modifica_origen_de_volumen(nodo_volu, [100,100,-100])
        nodo_transfo = util.Genera_Nodo("vtkMRMLLinearTransformNode", "Transformada_Correctora_del_Volumen")
        nodo_volu.SetAndObserveTransformNodeID(nodo_transfo.GetID())
        util.centra_nodo_de_widget("Red")

        print("Coloca volumen '", nodo_volu.GetName(), "' en transformada.-")
        util.Renderiza_3D_Volumen(nodo_volu)
        print("Se ha renderizado volumen:", nodo_volu.GetName())
        
        util.Borra_nodos_por_clase("vtkMRMLMarkupsFiducialNode")
        util.Borra_nodos_por_clase("vtkMRMLMarkupsLineNode")
        util.impri_layout_2D("Red", "", 0)
        
        transfe = util.Genera_Nodo("vtkMRMLScriptedModuleNode", "Transfe_data")
        transfe.SetParameter(" Nombre_del_Paciente", nodo_volu.GetName())
        transfe.SetParameter("Fiduciarios_Marco", str(Maquina_Russell_Brown.Marco_Micromar.P[1:9]))  
        transfe.SetParameter("Target", str([0.0, 0.0, 0.0]))
        transfe.SetParameter("T_Entry", str([0.0, 0.0, 0.0]))
        transfe.SetParameter("Target_Angulo_Alfa", str(90))
        transfe.SetParameter("Target_Angulo_Beta", str(45))
        transfe.SetParameter("Target_Der_Izq_flag", str(True))
        transfe.SetParameter("Registered_flag", "False")
        
        
    def Obtiene_9_Fiduciarios(self):
        print("vino a marcacion de 9 fiduciarios")
        nodo_volu = util.obtiene_nodo_de_widget("Red")
        if nodo_volu is None:
            texto = "ERROR: no hay volumenes cargados"
            slicer.util.warningDisplay(texto, windowTitle="Error", parent=None, standardButtons=None)
            slicer.app.layoutManager().setLayout(4)  # RED panel
            return
       
        transformada = util.Genera_Nodo("vtkMRMLLinearTransformNode", "Transformada_Correctora_del_Volumen")
        nodo_volu.SetAndObserveTransformNodeID(transformada.GetID())
        registracionLogic().grafica_path(False)
        util.centra_nodo_de_widget("Red")
        util.cambia_window_level("Red", 100, 50)
        
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
        transfe = slicer.util.getNode("Transfe_data")
        if transfe.GetParameter("Registered_flag") != "True":
            texto = "  Error: no se puede marcar el Target antes de Registrar !!!   "
            slicer.util.warningDisplay(texto, windowTitle="Error", parent=None, standardButtons=None)
            return
        
        registracionLogic().grafica_path(False)
        util.cambia_window_level("Red", 100, 50)
            
        nodo_fidu = self.gest.Inicializa_nodo("Target")
        nodo_fidu.GetDisplayNode().SetGlyphType(2)
        nodo_fidu.GetDisplayNode().SetColor(1.0, 1.0, 0.0)
        nodo_fidu.GetDisplayNode().SetSelectedColor(1.0, 1.0, 0.0)
        nodo_fidu.GetDisplayNode().SetActiveColor(1.0, 1.0, 0.0)
        
        self.mixObservador_1 = slicer.util.VTKObservationMixin()
        self.mixObservador_1.addObserver(nodo_fidu, vtk.vtkCommand.UserEvent, self.main)
        self.gest.Marcacion_Fiduciarios("Target", 1)

    def Obtiene_1_Fiduciario_Entry(self):
        print("vino a marcacion de 1 Entry")
        transfe = slicer.util.getNode("Transfe_data")
        if transfe.GetParameter("Registered_flag") != "True":
            texto = "  Error: no se puede marcar el Entry sin Registrar previamente!!!   "
            slicer.util.warningDisplay(texto, windowTitle="Error", parent=None, standardButtons=None)
            return
        
        if ast.literal_eval(transfe.GetParameter("Target")) == [0, 0, 0]:
            texto = "  Es preferible marcar previamente el Target.-   "
            slicer.util.warningDisplay(texto, windowTitle="Error", parent=None, standardButtons=None)
     
        registracionLogic().grafica_path(False)
        util.cambia_window_level("Red", 100, 50)
        
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
        transfe = slicer.util.getNode("Transfe_data")
        #
        # procedimiento de REGISTRACION
        #
        if self.gest.nombre_Nodo == "f":
            nodo_fidu = slicer.util.getNode(self.gest.nombre_Nodo)
            fiduciarios_TAC = self.gest.Lectura_Fiduciarios(nodo_fidu)
            matriz_RB = self.maqui.Ecuaciones_Russell_Brown(fiduciarios_TAC)
            array_M_RB = slicer.util.arrayFromVTKMatrix(matriz_RB).tolist()
            fiduciarios_3D = Maquina_Russell_Brown.Multiplica_lista_de_puntos(fiduciarios_TAC, matriz_RB)
         
            matriz_4x4  = self.maqui.Analisis_por_ICP(fiduciarios_TAC, fiduciarios_3D)
            array_M_3D = slicer.util.arrayFromVTKMatrix(matriz_RB).tolist()
            
            transformada = vtk.vtkTransform()
            transformada.SetMatrix(matriz_4x4)

            nodo = slicer.util.getNode("Transformada_Correctora_del_Volumen")
            nodo.SetAndObserveTransformToParent(transformada)
            util.centra_nodo_de_widget("Red")

            transfe.SetParameter("Fiduciarios_3D", str(util.redondea_lista_de_puntos(fiduciarios_3D, 2)))
            transfe.SetParameter("Array_Matrix_3D", str(array_M_3D))
            transfe.SetParameter("Fiduciarios_TAC", str(util.redondea_lista_de_puntos(fiduciarios_TAC, 2)))
            transfe.SetParameter("Array_Matrix_RB", str(array_M_RB))
            transfe.SetParameter("Registered_flag", "True")
            transfe.SetParameter("Transfo_Position", str(util.redondea(transformada.GetPosition(), 2)))
            transfe.SetParameter("Transfo_Orientation", str(util.redondea(transformada.GetOrientation(), 2)))
            
            print("Fiduciarios_TAC = " + transfe.GetParameter("Fiduciarios_TAC"))
            print("Matrix_RB = ", matriz_RB)
            print("Matriz 4x4 = ", matriz_4x4)
            print("Position= ", transfe.GetParameter("Transformada_Position" ))
            print("Orientation= ", transfe.GetParameter("Transformada_Orientation"))
            print("Registered_flag = ", transfe.GetParameter("Registered_flag"))

        # procedimiento del Target   
        elif self.gest.nombre_Nodo == "Target":
            nodo_fidu = slicer.util.getNode(self.gest.nombre_Nodo)
            Target = self.gest.Lectura_Fiduciarios(nodo_fidu)[0]  # toma el segundo t�rmino
            transfe.SetParameter("Target", str(util.redondea(Target, 1)))
            self.grafica_path(True)

            texto = "Target = " + transfe.GetParameter("Target")
            nodo_fidu.SetNthMarkupLabel(0, texto)
            util.impri_layout_2D("Red", texto, 2)
            
            print()
            print("----------------------------------------------")
            print(texto)
            print("----------------------------------------------")
            
        elif self.gest.nombre_Nodo == "Entry":   # procedimiento del Target
            nodo_fidu = slicer.util.getNode(self.gest.nombre_Nodo)
            Entry = self.gest.Lectura_Fiduciarios(nodo_fidu)[0]  # toma el segundo termino
            transfe.SetParameter("T_Entry", str(util.redondea(Entry, 1)))
            self.grafica_path(True)    

            texto = "Entry = " + transfe.GetParameter("T_Entry")
            nodo_fidu.SetNthMarkupLabel(0, texto)
            util.impri_layout_2D("Red", texto, 7)
            
            print()
            print("-------------------------------------------")
            print(texto)
            print("-------------------------------------------")
            
    def grafica_path(self, modo):
        print("vino a grafica path")
        if modo == False:
            util.Borra_nodo("Path")
            return

        transfe = slicer.util.getNode("Transfe_data")
        Target = ast.literal_eval(transfe.GetParameter("Target"))
        Entry = ast.literal_eval(transfe.GetParameter("T_Entry"))
        
        if Entry == [0, 0, 0]:
            return
        if Entry == Target:
            return
        if (Entry[0]>=0) != (Target[0]>=0):   #(a>0) == (b>0)  
            texto = "ATENCION: el PATH atraviesa la línea media !  "
            slicer.util.warningDisplay(texto, windowTitle="Error", parent=None, standardButtons=None)
            
        Alfa, Beta = util.calcula_angulos(Entry, Target)
        largo_path = util.grafica_linea(Entry, Target)        # grafica path

        transfe.SetParameter("Target_Angulo_Alfa", str(round(Alfa, 2)))
        transfe.SetParameter("Target_Angulo_Beta", str(round(Beta, 2)))
        transfe.SetParameter("Path_length", str(round(largo_path, 2)))
        
        if Entry[0] >= 0:
            transfe.SetParameter("Target_Der_Izq_flag", str(True))
        else:
            transfe.SetParameter("Target_Der_Izq_flag", str(False))
        
        texto = "Alfa : " + transfe.GetParameter("Target_Angulo_Alfa")
        texto = texto + ",  Beta : "+ transfe.GetParameter("Target_Angulo_Beta") 
        texto = texto + ", long : " + transfe.GetParameter("Path_length")
        util.impri_layout_2D("Red", texto, 3)
        
        print("ángulo_Alfa = ", transfe.GetParameter("Target_Angulo_Alfa"), "grados.")  #plano lateral
        print("ángulo_Beta = ", transfe.GetParameter("Target_Angulo_Beta"), "grados.") # plano frotal 
        print("longitud del path = ", transfe.GetParameter("Path_length"), "mm.")

    def Actualiza_Target(self):
        print("vino a actualizar el Target")
        transfe = slicer.util.getNode("Transfe_data")
        Target = ast.literal_eval(transfe.GetParameter("Target"))
        try:
            nodo = slicer.util.getNode("Target")
        except:
            print("no hay nodo Target")
            return
        nodo.SetNthFiducialPosition(0, Target[0],Target[1], Target[2])
        texto = "Target = " + str(util.redondea(Target, 1))
        nodo.SetNthMarkupLabel(0, texto)

    def guarda(self):
        print("vino a save")
        # Create a new directory where the scene will be saved into
        import time
        sceneSaveDirectory = self.moduloPath + "/Archivo/Escena_" + time.strftime("%Y%m%d-%H%M%S")
        if not os.access(sceneSaveDirectory, os.F_OK):
            os.makedirs(sceneSaveDirectory)
        # Save the scene
        if slicer.app.applicationLogic().SaveSceneToSlicerDataBundleDirectory(sceneSaveDirectory, None):
            logging.info("Scene saved to: {0}".format(sceneSaveDirectory))
        else:
            logging.error("Scene saving failed")
        
        transfe = slicer.util.getNode("Transfe_data")
        dictio = {}
        for param in transfe.GetParameterNames():
            #print(param)
            #print(transfe.GetParameter(param))
            dictio[param] = transfe.GetParameter(param)
        import json
        #json.dump(dictio, sceneSaveDirectory + "/parametros.json")   
        js = json.dumps(dictio)
        # Open new json file if not exist it will create
        fp = open(sceneSaveDirectory + "/parametros.json", 'a')
        # write to json file
        fp.write(js)
        # close the connection
        fp.close()

